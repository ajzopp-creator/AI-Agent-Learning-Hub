"""
FILE: infrastructure/research_catalog_io.py
VERSION: 1.0
DATE: 2026-07-08
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    SQLite bootstrap + write API for models/research/bulk_research.db
    (WO-P300-E2.001). Separate DB, separate module -- never touches the
    live *catalog.db or infrastructure/catalog_writer.py. Same 7-table
    shorthand as the live catalog PLUS symbols.sector,
    pattern_instances.detection_tier, forward_labels.significant_move_15.

    Mirrors the live catalog's Lock + Temp-DB + Atomic Move protocol
    (catalog_writer.py + verify_ingestion.py) but self-contained here
    since the two catalogs' table shapes differ (extra columns) and
    Process Boundary says a schema change in one must never ripple into
    the other's writer. atomic_move() itself IS reused from
    verify_ingestion.py -- it's already shape-agnostic (just moves
    files), so duplicating it would violate DRY for zero isolation
    benefit.

    Bootstrap is idempotent and NON-DESTRUCTIVE by design: unlike
    stage_3c_init_new_catalog.py's live-catalog bootstrap (--force
    deletes and recreates), ensure_research_catalog_exists() only
    creates the file if absent. The research catalog grows across many
    incremental extraction runs (checkpoint-resumable per the WO) --
    an accidental wipe would destroy prior sessions' work with no
    recovery path. If the schema ever needs to change, that is a
    separate migration script, never a flag on this function.

    Layer rules:
        - Pure I/O. No detection logic, no windowing, no spacing rule.
        - Inputs are validated Pydantic records from schemas_bulk.py.
        - Every write function takes an open sqlite3.Connection; caller
          (application/bulk_extract_pipeline.py) owns the transaction
          via utilities.db_connect-style connection_context (bulk uses
          its own thin context manager here since db_connect.py is
          hardcoded to db_utils.get_latest_catalog(), which by design
          never resolves this DB -- see config.py BULK_RESEARCH_DB
          isolation note).

CHANGELOG:
    - 2026-07-08 v1.0: Initial release. Bootstrap DDL (10-table-shape,
      7 base + 3 additive columns) + get_or_create_symbol_with_sector,
      insert_source_file, insert_pattern_instance, insert_pattern_bars_
      batch, insert_forward_labels_batch, research_catalog_checkout/
      checkin, verify_and_promote_research (reuses atomic_move).
"""
from __future__ import annotations

import logging
import sqlite3
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from infrastructure.verify_ingestion import atomic_move  # noqa: E402
from schemas_bulk import (  # noqa: E402
    BulkForwardLabelRecord,
    BulkPatternInstanceRecord,
    BulkSourceFileRecord,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Schema DDL (research catalog: 7-table shorthand + sector/tier/sig_move)
# ─────────────────────────────────────────────────────────────────────────────

RESEARCH_TABLES: tuple[str, ...] = (
    "symbols",
    "source_files",
    "feature_sets",
    "pattern_instances",
    "pattern_bars",
    "pattern_features",
    "forward_labels",
)

_SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS symbols (
    symbol_id   INTEGER PRIMARY KEY,
    ticker      TEXT UNIQUE NOT NULL,
    sector      TEXT
);

CREATE TABLE IF NOT EXISTS source_files (
    source_file_id       INTEGER PRIMARY KEY,
    filename              TEXT UNIQUE NOT NULL,
    symbol_id             INTEGER NOT NULL,
    imported_at           TEXT NOT NULL,
    row_count             INTEGER NOT NULL,
    window_years          INTEGER NOT NULL,
    is_intelliscan_export INTEGER NOT NULL,
    FOREIGN KEY (symbol_id) REFERENCES symbols(symbol_id)
);

CREATE TABLE IF NOT EXISTS feature_sets (
    feature_set_id  INTEGER PRIMARY KEY,
    feature_version TEXT NOT NULL,
    description     TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pattern_instances (
    pattern_instance_id INTEGER PRIMARY KEY,
    symbol_id           INTEGER NOT NULL,
    source_file_id      INTEGER NOT NULL,
    feature_set_id      INTEGER NOT NULL,
    anchor_date         TEXT NOT NULL,
    window_length        INTEGER NOT NULL,
    data_origin_type    TEXT NOT NULL,
    detection_tier       TEXT NOT NULL,
    FOREIGN KEY (symbol_id)      REFERENCES symbols(symbol_id),
    FOREIGN KEY (source_file_id) REFERENCES source_files(source_file_id),
    FOREIGN KEY (feature_set_id) REFERENCES feature_sets(feature_set_id)
);

CREATE TABLE IF NOT EXISTS pattern_bars (
    pattern_bar_id      INTEGER PRIMARY KEY,
    pattern_instance_id INTEGER NOT NULL,
    bar_offset          INTEGER NOT NULL,
    bar_date             TEXT NOT NULL,
    open REAL, high REAL, low REAL, close REAL, volume REAL,
    stdiff REAL, mtdiff REAL, ltdiff REAL,
    pred_high REAL, pred_low REAL, pred_range REAL,
    williams_emai REAL, psi REAL, roc_pct REAL,
    neural_index TEXT, neural_x_max REAL,
    tc_short REAL, tc_medium REAL, tc_long REAL,
    pred_high_diff REAL, pred_low_diff REAL,
    resistance_level REAL,
    FOREIGN KEY (pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id),
    UNIQUE (pattern_instance_id, bar_offset)
);

CREATE TABLE IF NOT EXISTS pattern_features (
    pattern_feature_id  INTEGER PRIMARY KEY,
    pattern_instance_id INTEGER NOT NULL,
    feature_name         TEXT NOT NULL,
    feature_value        REAL,
    FOREIGN KEY (pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id)
);

CREATE TABLE IF NOT EXISTS forward_labels (
    forward_label_id     INTEGER PRIMARY KEY,
    pattern_instance_id  INTEGER NOT NULL,
    horizon_days          INTEGER NOT NULL,
    future_date           TEXT,
    return_pct             REAL,
    is_profitable         INTEGER,
    significant_move_15   INTEGER NOT NULL,
    FOREIGN KEY (pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id)
);

CREATE INDEX IF NOT EXISTS idx_research_pattern_instances_symbol_anchor
    ON pattern_instances(symbol_id, anchor_date);
CREATE INDEX IF NOT EXISTS idx_research_pattern_bars_pattern_offset
    ON pattern_bars(pattern_instance_id, bar_offset);
CREATE INDEX IF NOT EXISTS idx_research_forward_labels_pattern_horizon
    ON forward_labels(pattern_instance_id, horizon_days);
CREATE INDEX IF NOT EXISTS idx_research_pattern_instances_tier
    ON pattern_instances(detection_tier);
"""

_BOOTSTRAP_FEATURE_VERSION = "bulk_scan_v1"


def ensure_research_catalog_exists(db_path: Path) -> None:
    """Create db_path with the research schema if it does not already
    exist. NEVER deletes or truncates an existing file -- see module
    docstring. Idempotent: safe to call at the top of every extraction
    run."""
    if db_path.exists():
        return
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(_SCHEMA_DDL)
        conn.execute(
            "INSERT INTO feature_sets (feature_version, description, created_at) "
            "VALUES (?, ?, datetime('now'));",
            (_BOOTSTRAP_FEATURE_VERSION, "Bulk scan baseline (WO-P300-E2.001)."),
        )
        conn.commit()
        logger.info("Created research catalog: %s", db_path)
    finally:
        conn.close()


@contextmanager
def research_connection(db_path: Path):
    """Thin connection context for the research DB. Distinct from
    utilities.db_connect.connection_context -- that helper is hardwired
    to db_utils.get_latest_catalog(), which by design (config.py
    isolation note) never resolves bulk_research.db."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Lookup / lookup-or-create
# ─────────────────────────────────────────────────────────────────────────────

def get_or_create_symbol_with_sector(
    conn: sqlite3.Connection, ticker: str, sector: str | None
) -> int:
    """Lookup-then-insert (mirrors catalog_writer.get_or_create_symbol,
    EC-065 pattern). sector is set on first insert only -- an existing
    row's sector is never overwritten by a later call, since sector_map.csv
    is operator-maintained and any drift should be a deliberate edit,
    not a side effect of ingest order."""
    row = conn.execute(
        "SELECT symbol_id FROM symbols WHERE ticker = ?", (ticker,)
    ).fetchone()
    if row is not None:
        return row[0]
    cursor = conn.execute(
        "INSERT INTO symbols (ticker, sector) VALUES (?, ?)", (ticker, sector)
    )
    return cursor.lastrowid


def get_feature_set_id(conn: sqlite3.Connection, feature_version: str) -> int:
    row = conn.execute(
        "SELECT feature_set_id FROM feature_sets WHERE feature_version = ?",
        (feature_version,),
    ).fetchone()
    if row is None:
        raise ValueError(
            f"feature_set {feature_version!r} not found in research catalog."
        )
    return row[0]


# ─────────────────────────────────────────────────────────────────────────────
# Inserts
# ─────────────────────────────────────────────────────────────────────────────

def insert_source_file(conn: sqlite3.Connection, record: BulkSourceFileRecord) -> int:
    """Dedup key is filename (same convention as live catalog). Raises
    ValueError on a repeat filename -- caller uses this to skip a file
    already ingested (checkpoint resume also short-circuits earlier via
    completed_filenames, this is the DB-level backstop)."""
    existing = conn.execute(
        "SELECT source_file_id FROM source_files WHERE filename = ?",
        (record.filename,),
    ).fetchone()
    if existing is not None:
        raise ValueError(
            f"source_file already ingested: {record.filename!r} "
            f"(existing source_file_id = {existing[0]})"
        )
    cursor = conn.execute(
        "INSERT INTO source_files "
        "(filename, symbol_id, imported_at, row_count, window_years, "
        " is_intelliscan_export) VALUES (?, ?, ?, ?, ?, ?)",
        (
            record.filename,
            record.symbol_id,
            record.imported_at.isoformat(),
            record.row_count,
            record.window_years,
            1 if record.is_intelliscan_export else 0,
        ),
    )
    return cursor.lastrowid


def insert_pattern_instance(
    conn: sqlite3.Connection, record: BulkPatternInstanceRecord
) -> int:
    cursor = conn.execute(
        "INSERT INTO pattern_instances "
        "(symbol_id, source_file_id, feature_set_id, anchor_date, "
        " window_length, data_origin_type, detection_tier) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            record.symbol_id,
            record.source_file_id,
            record.feature_set_id,
            record.anchor_date.isoformat(),
            record.window_length,
            record.data_origin_type.value,
            record.detection_tier.value,
        ),
    )
    return cursor.lastrowid


_PATTERN_BAR_COLUMNS: tuple[str, ...] = (
    "pattern_instance_id", "bar_offset", "bar_date",
    "open", "high", "low", "close", "volume",
    "stdiff", "mtdiff", "ltdiff",
    "pred_high", "pred_low", "pred_range",
    "williams_emai", "psi", "roc_pct",
    "neural_index", "neural_x_max",
    "tc_short", "tc_medium", "tc_long",
    "pred_high_diff", "pred_low_diff", "resistance_level",
)


def insert_pattern_bars_batch(
    conn: sqlite3.Connection,
    pattern_instance_id: int,
    bars: list,
    resistance_level: float,
) -> int:
    """Batch-insert the full detection window. `bars` must already be
    the sliced window (caller's responsibility, per BULK_WINDOW_LENGTH);
    bar_offset runs 0..len(bars)-1 in window order (bulk instances do
    not use the live catalog's negative-offset launch-anchor convention
    -- there is no single "launch bar" concept here, just a fixed-length
    detection window). resistance_level is stamped on every bar row
    (audit trail -- the swing-high computed once at detection time)."""
    if not bars:
        return 0
    cols = ", ".join(_PATTERN_BAR_COLUMNS)
    placeholders = ", ".join("?" * len(_PATTERN_BAR_COLUMNS))
    sql = f"INSERT INTO pattern_bars ({cols}) VALUES ({placeholders})"
    rows = [
        (
            pattern_instance_id, i, b.bar_date.isoformat(),
            b.open, b.high, b.low, b.close, b.volume,
            b.stdiff, b.mtdiff, b.ltdiff,
            b.pred_high, b.pred_low, b.pred_range,
            b.williams_emai, b.psi, b.roc_pct,
            b.neural_index, b.neural_x_max,
            b.tc_short, b.tc_medium, b.tc_long,
            b.pred_high_diff, b.pred_low_diff, resistance_level,
        )
        for i, b in enumerate(bars)
    ]
    conn.executemany(sql, rows)
    return len(rows)


def insert_forward_labels_batch(
    conn: sqlite3.Connection,
    pattern_instance_id: int,
    records: list[BulkForwardLabelRecord],
) -> int:
    if not records:
        return 0
    sql = (
        "INSERT INTO forward_labels "
        "(pattern_instance_id, horizon_days, future_date, return_pct, "
        " is_profitable, significant_move_15) VALUES (?, ?, ?, ?, ?, ?)"
    )
    rows = [
        (
            pattern_instance_id, r.horizon_days, r.future_date.isoformat(),
            r.return_pct, 1 if r.is_profitable else 0,
            1 if r.significant_move_15 else 0,
        )
        for r in records
    ]
    conn.executemany(sql, rows)
    return len(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Checkout / Checkin (mirrors catalog_writer.py, verify_ingestion.py)
# ─────────────────────────────────────────────────────────────────────────────

def research_catalog_checkout(conn: sqlite3.Connection) -> dict[str, int]:
    fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    if fk != 1:
        raise RuntimeError("PRAGMA foreign_keys is OFF on this connection.")
    counts = {
        t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in RESEARCH_TABLES
    }
    logger.info("research_catalog_checkout: %s", counts)
    return counts


def _check_no_hollow_instances(conn: sqlite3.Connection) -> tuple[int, list[int]]:
    sql = """
        SELECT pi.pattern_instance_id
          FROM pattern_instances pi
         WHERE NOT EXISTS (
                   SELECT 1 FROM pattern_bars pb
                    WHERE pb.pattern_instance_id = pi.pattern_instance_id
               )
            OR NOT EXISTS (
                   SELECT 1 FROM forward_labels fl
                    WHERE fl.pattern_instance_id = pi.pattern_instance_id
               )
    """
    rows = conn.execute(sql).fetchall()
    ids = [r[0] for r in rows]
    return len(ids), ids


@dataclass
class ResearchVerificationResult:
    passed: bool
    failures: list[str] = field(default_factory=list)
    post_counts: dict[str, int] = field(default_factory=dict)
    backup_path: Path | None = None
    master_promoted: bool = False


def verify_and_promote_research(
    temp_path: Path,
    master_path: Path,
    expected_delta: dict[str, int],
    pre_counts: dict[str, int],
) -> ResearchVerificationResult:
    """Same contract as verify_ingestion.verify_and_promote, sized for
    the research catalog's table set. Reuses atomic_move directly
    (file-move logic is identical regardless of schema shape)."""
    if not temp_path.exists():
        return ResearchVerificationResult(
            passed=False, failures=[f"temp DB not found: {temp_path}"]
        )

    failures: list[str] = []
    with research_connection(temp_path) as conn:
        post_counts = {
            t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in RESEARCH_TABLES
        }
        for table, expected in expected_delta.items():
            actual = post_counts[table] - pre_counts.get(table, 0)
            if actual != expected:
                failures.append(
                    f"{table}: expected +{expected}, got +{actual}"
                )
        hollow_count, hollow_ids = _check_no_hollow_instances(conn)
        if hollow_count > 0:
            failures.append(
                f"hollow pattern_instances: {hollow_count} IDs {hollow_ids[:10]}"
            )

    if failures:
        logger.error("verify_and_promote_research FAILED: %s", failures)
        return ResearchVerificationResult(
            passed=False, failures=failures, post_counts=post_counts
        )

    backup_path = atomic_move(temp_path, master_path)
    logger.info(
        "Promoted temp -> research master. master=%s backup=%s",
        master_path, backup_path,
    )
    return ResearchVerificationResult(
        passed=True,
        post_counts=post_counts,
        backup_path=backup_path,
        master_promoted=True,
    )
