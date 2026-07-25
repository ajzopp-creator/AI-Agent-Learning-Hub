"""
FILE: infrastructure/sector_stats_io.py
VERSION: 1.0
DATE: 2026-07-10
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    sector_stats table (additive -- Decision 3) in
    models/research/bulk_research.db. Does not touch the existing 7
    research-catalog tables (research_catalog_io.py owns those); DDL
    here is scoped to exactly one new table + its index.

    Snapshot semantics: write_sector_stats() is DELETE+INSERT per run,
    not accumulated -- the table always holds exactly the most recent
    analysis run's results. Historical snapshots are covered by the
    project's existing DB-backup pattern (models/research/backups/),
    not by row-versioning inside this table (see WO-P300-E2.002's
    sector_stats design note).

    Lock + Temp-DB + Atomic Move (Must-rule #9): write_sector_stats
    copies master to temp, ensures the table exists on the copy,
    DELETE+INSERTs there, verifies the row count matches len(records)
    exactly, then atomically promotes via research_catalog_io.
    atomic_move. Master is never written in-place.

CHANGELOG:
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.002 file #7 of 11).
"""
from __future__ import annotations

import logging
import shutil
import sqlite3
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import BULK_RESEARCH_DB  # noqa: E402
from infrastructure.research_catalog_io import atomic_move, research_connection  # noqa: E402
from schemas_sector_analysis import SectorStatsRecord  # noqa: E402

logger = logging.getLogger(__name__)

_DDL = """
CREATE TABLE IF NOT EXISTS sector_stats (
    sector_stats_id  INTEGER PRIMARY KEY,
    sector_label     TEXT NOT NULL,
    detection_tier   TEXT NOT NULL,
    horizon_days     INTEGER NOT NULL,
    n                INTEGER NOT NULL,
    win_rate         REAL,
    mean_return_pct  REAL,
    std_return_pct   REAL,
    below_min_n      INTEGER NOT NULL,
    computed_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sector_stats_label_tier_horizon
    ON sector_stats(sector_label, detection_tier, horizon_days);
"""


def ensure_sector_stats_table_exists(conn: sqlite3.Connection) -> None:
    """Additive DDL -- safe to call on every write, touches nothing
    outside this one table + its index."""
    conn.executescript(_DDL)


def query_sector_stats(master_path: Path = BULK_RESEARCH_DB) -> list[SectorStatsRecord]:
    """Read the current snapshot. Returns an empty list if the table
    doesn't exist yet (no analysis run has ever written to it) rather
    than raising -- an empty report is a valid state, not an error."""
    with research_connection(master_path) as conn:
        ensure_sector_stats_table_exists(conn)
        rows = conn.execute(
            "SELECT sector_label, detection_tier, horizon_days, n, win_rate, "
            "mean_return_pct, std_return_pct, below_min_n, computed_at "
            "FROM sector_stats ORDER BY sector_label, detection_tier, horizon_days"
        ).fetchall()
    return [
        SectorStatsRecord(
            sector_label=r[0], detection_tier=r[1], horizon_days=r[2], n=r[3],
            win_rate=r[4], mean_return_pct=r[5], std_return_pct=r[6],
            below_min_n=bool(r[7]), computed_at=r[8],
        )
        for r in rows
    ]


def write_sector_stats(
    records: list[SectorStatsRecord], master_path: Path = BULK_RESEARCH_DB
) -> int:
    """DELETE+INSERT the full snapshot via Lock+Temp-DB+Atomic Move.
    Raises RuntimeError if the post-insert row count doesn't exactly
    match len(records) -- the delta check for a table with no prior
    baseline to diff against (this table's "expected delta" IS its
    total count, since every write replaces the whole snapshot)."""
    if not master_path.exists():
        raise FileNotFoundError(
            f"research catalog not found, cannot write sector_stats: {master_path}"
        )

    temp_path = master_path.with_name(f"temp_{master_path.name}")
    shutil.copy2(master_path, temp_path)

    with research_connection(temp_path) as conn:
        ensure_sector_stats_table_exists(conn)
        conn.execute("DELETE FROM sector_stats")
        conn.executemany(
            "INSERT INTO sector_stats "
            "(sector_label, detection_tier, horizon_days, n, win_rate, "
            " mean_return_pct, std_return_pct, below_min_n, computed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    r.sector_label, r.detection_tier, r.horizon_days, r.n,
                    r.win_rate, r.mean_return_pct, r.std_return_pct,
                    1 if r.below_min_n else 0, r.computed_at.isoformat(),
                )
                for r in records
            ],
        )
        actual_count = conn.execute("SELECT COUNT(*) FROM sector_stats").fetchone()[0]

    if actual_count != len(records):
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"sector_stats write verification failed: expected {len(records)} "
            f"rows, temp DB has {actual_count}"
        )

    backup_path = atomic_move(temp_path, master_path)
    logger.info(
        "sector_stats snapshot written: %d rows, backup=%s",
        actual_count, backup_path,
    )
    return actual_count
