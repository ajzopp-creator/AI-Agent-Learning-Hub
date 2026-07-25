"""
FILE: infrastructure/sector_backfill_io.py
VERSION: 1.0
DATE: 2026-07-10
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    One-time retroactive sector backfill (WO-P300-E2.002 Decision 1) --
    UPDATE symbols SET sector = ? WHERE ticker = ? against
    models/research/bulk_research.db, keyed off sector_map.csv.

    Lock + Temp-DB + Atomic Move (Must-rule #9): copies the master DB to
    a temp file, applies every UPDATE against the copy, verifies zero
    remaining NULL sectors among STOCK symbols, then atomically promotes
    via research_catalog_io.atomic_move -- never writes to master
    in-place. Fails loudly (via sector_map_loader.verify_full_coverage,
    BEFORE the temp copy is even made) if any catalog symbol has no
    sector_map.csv entry, per Decision 2 zero-tolerance.

    Idempotent: a second run against an already-backfilled DB updates
    zero rows (current value already matches sector_map.csv) and still
    verifies clean. ETF rows are backfilled to sector=NULL explicitly
    (an UPDATE is issued even though the value is already NULL by
    default) -- Decision 5's "never left unset by omission" requirement.

CHANGELOG:
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.002 file #6 of 11).
"""
from __future__ import annotations

import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import ASSET_CLASS_STOCK, BULK_RESEARCH_DB  # noqa: E402
from infrastructure.research_catalog_io import (  # noqa: E402
    atomic_move,
    ensure_research_catalog_exists,
    research_connection,
)
from infrastructure.sector_map_loader import load_sector_map, verify_full_coverage  # noqa: E402

logger = logging.getLogger(__name__)


@dataclass
class BackfillResult:
    rows_updated: int
    rows_unchanged: int
    backup_path: Path | None


def run_sector_backfill(master_path: Path = BULK_RESEARCH_DB) -> BackfillResult:
    """Backfill every symbol's sector column from sector_map.csv. Raises
    ValueError (via verify_full_coverage) before touching any file if
    coverage is incomplete. Raises RuntimeError if, after applying every
    update, any STOCK symbol's sector is still NULL (should be
    unreachable given the pre-check, but this is the runtime tripwire,
    same instinct as verify_ingestion's hollow-instance scan)."""
    ensure_research_catalog_exists(master_path)
    sector_map = load_sector_map()

    with research_connection(master_path) as conn:
        tickers = [r[0] for r in conn.execute("SELECT ticker FROM symbols").fetchall()]
    verify_full_coverage(tickers, sector_map)

    temp_path = master_path.with_name(f"temp_{master_path.name}")
    shutil.copy2(master_path, temp_path)

    updated = 0
    unchanged = 0
    with research_connection(temp_path) as conn:
        for ticker in tickers:
            new_sector = sector_map[ticker].sector  # None for ETF rows
            current = conn.execute(
                "SELECT sector FROM symbols WHERE ticker = ?", (ticker,)
            ).fetchone()[0]
            if current == new_sector:
                unchanged += 1
                continue
            conn.execute(
                "UPDATE symbols SET sector = ? WHERE ticker = ?", (new_sector, ticker)
            )
            updated += 1

        still_null_stock = conn.execute(
            "SELECT ticker FROM symbols WHERE sector IS NULL"
        ).fetchall()
    still_null_stock_tickers = [
        r[0] for r in still_null_stock
        if sector_map[r[0]].asset_class == ASSET_CLASS_STOCK
    ]
    if still_null_stock_tickers:
        temp_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"Backfill verification failed -- STOCK symbols still NULL "
            f"after update: {still_null_stock_tickers}"
        )

    backup_path = atomic_move(temp_path, master_path)
    logger.info(
        "Sector backfill complete: %d updated, %d unchanged, backup=%s",
        updated, unchanged, backup_path,
    )
    return BackfillResult(
        rows_updated=updated, rows_unchanged=unchanged, backup_path=backup_path
    )
