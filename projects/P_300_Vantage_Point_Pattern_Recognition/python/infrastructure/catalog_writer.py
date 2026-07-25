"""
FILE: catalog_writer.py
VERSION: 1.0.3
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    SQLite write API for the P_300 catalog. Every function takes an
    open sqlite3.Connection as its first argument — the caller (typically
    application/add_pattern_pipeline.py) owns the connection lifecycle
    via utilities.db_connect.connection_context(). This keeps all writes
    for one pattern inside a single transaction so partial failures roll
    back cleanly.

    Layer rules:
        - Pure I/O. No business logic. No normalization. No labeling.
        - Inputs are validated Pydantic records from schemas.py.
        - Writes against whichever DB path the connection was opened with
          (the temp_working.db during Pipeline A ingest, never master).
        - The Lock + Temp-DB + Atomic Move pattern lives in
          add_pattern_pipeline.py + verify_ingestion.py — not here.

    Idempotency / FK protection:
        - get_or_create_symbol: lookup-then-insert (EC-065)
        - insert_source_file: pre-checks UNIQUE filename (EC-023)
        - catalog_checkout: asserts PRAGMA foreign_keys = ON (M-012)

CHANGELOG:
    - 2026-07-20 v1.0.3 (WFG/PLTR/BOIL/RRC PATTERN_IDENT-doubles cleanup):
      added pattern_exists_for_ticker_anchor() -- lifted from catalog_
      merge_io.py's private _pattern_already_exists (WO-P300-E2.003
      decision 4, unchanged query) so Pipeline A's add_pattern_pipeline.py
      can share the same exact symbol+anchor_date dedup check the bulk
      path already had. Root cause this closes: EC-023 only blocks an
      exact filename match, so a VP re-export with a different end date
      (different filename, same underlying pattern) sailed through
      Pipeline A's dedup entirely -- confirmed as the cause of 4 real
      catalog doubles (WFG/PLTR/BOIL/RRC), found via a TopKTieError on
      2026-07-20's real BulkAddPattern batch.
    - 2026-07-19 v1.0.2 (WO-P300-E4.006, decision #7): CATALOG_TABLES
      grows to 8 -- topk_cache added (writes go through infrastructure/
      topk_cache_io.py, not here). checkout/checkin needed no code
      change -- both already iterate CATALOG_TABLES generically.
    - 2026-05-15 v1.0.1: Renamed `_CATALOG_TABLES` → `CATALOG_TABLES`
      (public) so verify_ingestion can reuse the canonical 7-table list.
    - 2026-05-15 v1.0: Stage 4 file #6 of plan. Composable insert API
      + Catalog Check-Out / Check-In row-count probes.
"""
from __future__ import annotations

import logging
import sqlite3
from datetime import date
import sys
from pathlib import Path

# sys.path bootstrap so `from schemas import ...` resolves on direct invocation.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from schemas import (  # noqa: E402
    ForwardLabelRecord,
    PatternBarRecord,
    PatternInstanceRecord,
    SourceFileRecord,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Module constants
# ─────────────────────────────────────────────────────────────────────────────

# All 8 catalog tables in dependency order (parent → child). Public so
# verify_ingestion and any other module can reuse the canonical list.
# topk_cache added 2026-07-19 (WO-P300-E4.006, decision #7) -- grew
# from 7 to 8; see infrastructure/topk_cache_io.py for its own schema.
CATALOG_TABLES: tuple[str, ...] = (
    "symbols",
    "source_files",
    "feature_sets",
    "pattern_instances",
    "pattern_bars",
    "pattern_features",
    "forward_labels",
    "topk_cache",
)

# pattern_bars insert columns in order. Driver for both the SQL string and
# the value-tuple builder so a column-order drift gets caught at edit time.
_PATTERN_BAR_COLUMNS: tuple[str, ...] = (
    "pattern_instance_id", "bar_offset", "bar_date",
    "open", "high", "low", "close", "volume",
    "stdiff", "mtdiff", "ltdiff",
    "pred_high", "pred_low", "pred_range",
    "williams_emai", "psi", "neural_index",
    "triple_cross_short", "triple_cross_medium", "triple_cross_long",
    "close_pct_from_anchor", "range_pct", "body_pct", "volume_zscore",
    "stdiff_pct", "mtdiff_pct", "ltdiff_pct",
    "pred_high_pct", "pred_low_pct", "pred_range_pct",
)


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _pattern_bar_row(pattern_instance_id: int, r: PatternBarRecord) -> tuple:
    """Build one INSERT tuple for pattern_bars. Order must match _PATTERN_BAR_COLUMNS."""
    return (
        pattern_instance_id, r.bar_offset, r.bar_date.isoformat(),
        r.open, r.high, r.low, r.close, r.volume,
        r.stdiff, r.mtdiff, r.ltdiff,
        r.pred_high, r.pred_low, r.pred_range,
        r.williams_emai, r.psi, r.neural_index,
        r.triple_cross_short, r.triple_cross_medium, r.triple_cross_long,
        r.close_pct_from_anchor, r.range_pct, r.body_pct, r.volume_zscore,
        r.stdiff_pct, r.mtdiff_pct, r.ltdiff_pct,
        r.pred_high_pct, r.pred_low_pct, r.pred_range_pct,
    )


def _forward_label_row(pattern_instance_id: int, r: ForwardLabelRecord) -> tuple:
    """Build one INSERT tuple for forward_labels."""
    return (
        pattern_instance_id,
        r.horizon_days,
        r.future_date.isoformat(),
        r.return_pct,
        1 if r.is_profitable else 0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Lookup / lookup-or-create
# ─────────────────────────────────────────────────────────────────────────────

def get_or_create_symbol(conn: sqlite3.Connection, ticker: str) -> int:
    """Return symbol_id for ticker; create the row if it doesn't exist.
    EC-065 protection: ticker UNIQUE constraint at schema level prevents
    duplicates even under race; this function is the single insertion point."""
    row = conn.execute(
        "SELECT symbol_id FROM symbols WHERE ticker = ?", (ticker,)
    ).fetchone()
    if row is not None:
        return row[0]
    cursor = conn.execute(
        "INSERT INTO symbols (ticker) VALUES (?)", (ticker,)
    )
    return cursor.lastrowid


def get_feature_set_id(conn: sqlite3.Connection, feature_version: str) -> int:
    """Look up an existing feature_set by version string. Raises if missing —
    the bootstrap row (`baseline_v1`) is inserted by stage_3c at catalog init,
    so a missing row indicates catalog corruption."""
    row = conn.execute(
        "SELECT feature_set_id FROM feature_sets WHERE feature_version = ?",
        (feature_version,),
    ).fetchone()
    if row is None:
        raise ValueError(
            f"feature_set {feature_version!r} not found in catalog. "
            f"Stage 3c bootstrap row may be missing — inspect the catalog."
        )
    return row[0]


def pattern_exists_for_ticker_anchor(
    conn: sqlite3.Connection, ticker: str, anchor_date: date
) -> bool:
    """Exact ticker + anchor_date dedup check (WFG/PLTR/BOIL/RRC cleanup,
    2026-07-20). Lifted unchanged from catalog_merge_io.py's private
    _pattern_already_exists (WO-P300-E2.003 decision 4) so every ingest
    path shares one implementation instead of each having its own copy.
    Query is intentionally exact-match (ticker, anchor_date) -- no
    fuzzy/near-duplicate detection here; that stays a human decision
    (Finding 3's own rule, domain/topk_cache.py), not something this
    function silently attempts."""
    row = conn.execute(
        "SELECT 1 FROM pattern_instances pi "
        "JOIN symbols s ON s.symbol_id = pi.symbol_id "
        "WHERE s.ticker = ? AND pi.anchor_date = ?",
        (ticker, anchor_date.isoformat()),
    ).fetchone()
    return row is not None


# ─────────────────────────────────────────────────────────────────────────────
# Inserts
# ─────────────────────────────────────────────────────────────────────────────

def insert_source_file(conn: sqlite3.Connection, record: SourceFileRecord) -> int:
    """Insert one source_files row, return new source_file_id.
    EC-023 protection: pre-check refuses to re-ingest a filename already
    in the catalog. Raises ValueError on duplicate."""
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
        "INSERT INTO source_files (filename, symbol_id, imported_at, row_count) "
        "VALUES (?, ?, ?, ?)",
        (
            record.filename,
            record.symbol_id,
            record.imported_at.isoformat(),
            record.row_count,
        ),
    )
    return cursor.lastrowid


def insert_pattern_instance(
    conn: sqlite3.Connection, record: PatternInstanceRecord
) -> int:
    """Insert one pattern_instances row, return new pattern_instance_id.
    NOT NULL FKs (symbol_id, source_file_id, feature_set_id) are enforced
    structurally — this is the schema-as-protection layer (architecture §2.5)
    that closes EC-027 hollow-record bugs."""
    cursor = conn.execute(
        "INSERT INTO pattern_instances "
        "(symbol_id, source_file_id, feature_set_id, anchor_date, "
        " window_length, data_origin_type) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            record.symbol_id,
            record.source_file_id,
            record.feature_set_id,
            record.anchor_date.isoformat(),
            record.window_length,
            record.data_origin_type.value,
        ),
    )
    return cursor.lastrowid


def insert_pattern_bars_batch(
    conn: sqlite3.Connection,
    pattern_instance_id: int,
    records: list[PatternBarRecord],
) -> int:
    """Batch-insert all bars for one pattern. Returns row count inserted.
    The pattern_instance_id is set by this function — any value on the
    incoming records is ignored."""
    if not records:
        return 0
    cols = ", ".join(_PATTERN_BAR_COLUMNS)
    placeholders = ", ".join("?" * len(_PATTERN_BAR_COLUMNS))
    sql = f"INSERT INTO pattern_bars ({cols}) VALUES ({placeholders})"
    rows = [_pattern_bar_row(pattern_instance_id, r) for r in records]
    conn.executemany(sql, rows)
    return len(rows)


def insert_forward_labels_batch(
    conn: sqlite3.Connection,
    pattern_instance_id: int,
    records: list[ForwardLabelRecord],
) -> int:
    """Batch-insert forward labels for one pattern. Returns row count."""
    if not records:
        return 0
    sql = (
        "INSERT INTO forward_labels "
        "(pattern_instance_id, horizon_days, future_date, return_pct, is_profitable) "
        "VALUES (?, ?, ?, ?, ?)"
    )
    rows = [_forward_label_row(pattern_instance_id, r) for r in records]
    conn.executemany(sql, rows)
    return len(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Catalog Check-Out / Check-In (architecture §2.6)
# ─────────────────────────────────────────────────────────────────────────────

def catalog_checkout(conn: sqlite3.Connection) -> dict[str, int]:
    """Snapshot row counts for all CATALOG_TABLES tables before a write
    op. Also asserts PRAGMA foreign_keys = ON (M-012) — the
    orchestrator's tripwire that the connection came through db_connect."""
    fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    if fk != 1:
        raise RuntimeError(
            "PRAGMA foreign_keys is OFF on this connection. Open the "
            "catalog via utilities.db_connect.get_connection() / "
            "connection_context() — never sqlite3.connect() directly."
        )
    counts: dict[str, int] = {}
    for table in CATALOG_TABLES:
        counts[table] = conn.execute(
            f"SELECT COUNT(*) FROM {table}"  # table names are module-local literals
        ).fetchone()[0]
    logger.info("catalog_checkout: %s", counts)
    return counts


def catalog_checkin(
    conn: sqlite3.Connection,
    pre_counts: dict[str, int],
    expected_delta: dict[str, int] | None = None,
) -> dict[str, int]:
    """Snapshot row counts AFTER the write op. Computes actual delta vs
    pre_counts. If expected_delta is supplied, raises ValueError on any
    mismatch (per-table). Returns post_counts in both cases."""
    post: dict[str, int] = {}
    for table in CATALOG_TABLES:
        post[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    actual_delta = {t: post[t] - pre_counts[t] for t in CATALOG_TABLES}
    logger.info("catalog_checkin: post=%s delta=%s", post, actual_delta)
    if expected_delta is not None:
        mismatches = [
            f"{table}: expected +{exp}, got +{actual_delta[table]}"
            for table, exp in expected_delta.items()
            if actual_delta[table] != exp
        ]
        if mismatches:
            raise ValueError(
                "Catalog Check-In delta mismatch:\n  " + "\n  ".join(mismatches)
            )
    return post
