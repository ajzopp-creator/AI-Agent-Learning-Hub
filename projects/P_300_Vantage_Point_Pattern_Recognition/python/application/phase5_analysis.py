"""
FILE: application/phase5_analysis.py
VERSION: 1.0
DATE: 2026-07-10
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Orchestration-only entrypoint for WO-P300-E2.002 Phase 5. Calls, in
    order: (1) sector backfill (infrastructure/sector_backfill_io.py),
    (2) load the joined catalog rows needed for stats (this module's own
    thin query -- deliberately not pushed into research_catalog_io.py,
    which owns writes/lookups for the base 7 tables, not this WO's
    read-shape), (3) compute stats (domain/sector_stats_calc.py),
    (4) persist the sector_stats snapshot (infrastructure/
    sector_stats_io.py), (5) write the human-readable report
    (infrastructure/sector_report_writer.py).

    No business logic here -- every real decision (grouping, stats math,
    DDL, report format) lives in the module that owns it. This file only
    sequences the calls and shapes the DB rows into
    domain.sector_stats_calc.SectorAnalysisInputRow.

CHANGELOG:
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.002 file #9 of 11).
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import BULK_RESEARCH_DB  # noqa: E402
from domain.sector_stats_calc import SectorAnalysisInputRow, compute_sector_stats  # noqa: E402
from infrastructure.research_catalog_io import research_connection  # noqa: E402
from infrastructure.sector_backfill_io import BackfillResult, run_sector_backfill  # noqa: E402
from infrastructure.sector_map_loader import load_sector_map  # noqa: E402
from infrastructure.sector_report_writer import write_sector_stats_report  # noqa: E402
from infrastructure.sector_stats_io import write_sector_stats  # noqa: E402
from schemas_sector_analysis import SectorMapRow  # noqa: E402

logger = logging.getLogger(__name__)


@dataclass
class Phase5Result:
    backfill: BackfillResult | None
    rows_analyzed: int
    cells_computed: int
    report_path: Path


def _load_analysis_rows(
    master_path: Path, sector_map: dict[str, SectorMapRow]
) -> list[SectorAnalysisInputRow]:
    """One joined query across pattern_instances x forward_labels x
    symbols -- everything sector_stats_calc needs, already keyed off
    the just-backfilled sector column plus sector_map.csv's
    asset_class (asset_class isn't stored in the DB at all, only
    sector -- STOCK vs ETF is a sector_map.csv-only distinction)."""
    with research_connection(master_path) as conn:
        cursor = conn.execute(
            "SELECT s.ticker, pi.detection_tier, fl.horizon_days, "
            "fl.return_pct, fl.is_profitable "
            "FROM pattern_instances pi "
            "JOIN symbols s ON s.symbol_id = pi.symbol_id "
            "JOIN forward_labels fl ON fl.pattern_instance_id = pi.pattern_instance_id"
        )
        db_rows = cursor.fetchall()

    rows: list[SectorAnalysisInputRow] = []
    for ticker, tier, horizon, return_pct, is_profitable in db_rows:
        map_row = sector_map.get(ticker)
        if map_row is None:
            # Should be unreachable -- run_sector_backfill's
            # verify_full_coverage call already failed loudly on this
            # exact condition before we got here.
            raise RuntimeError(
                f"symbol {ticker!r} in catalog but missing from sector_map "
                "-- backfill's coverage check should have caught this"
            )
        rows.append(SectorAnalysisInputRow(
            sector=map_row.sector,
            asset_class=map_row.asset_class,
            detection_tier=tier,
            horizon_days=horizon,
            return_pct=return_pct,
            is_profitable=bool(is_profitable),
        ))
    return rows


def run_phase5_analysis(
    master_path: Path = BULK_RESEARCH_DB, run_backfill: bool = True
) -> Phase5Result:
    """Full Phase 5 pipeline. run_backfill=False skips step 1 (e.g. a
    re-run against an already-backfilled catalog with no new symbols
    since the last backfill) -- stats/report always run fresh."""
    backfill_result = run_sector_backfill(master_path) if run_backfill else None

    sector_map = load_sector_map()
    rows = _load_analysis_rows(master_path, sector_map)

    computed_at = datetime.now()
    stats = compute_sector_stats(rows, computed_at)
    written_count = write_sector_stats(stats, master_path)
    report_path = write_sector_stats_report(stats)

    logger.info(
        "Phase 5 analysis complete: %d rows -> %d sector_stats cells "
        "(%d written) -> report %s",
        len(rows), len(stats), written_count, report_path,
    )
    return Phase5Result(
        backfill=backfill_result,
        rows_analyzed=len(rows),
        cells_computed=len(stats),
        report_path=report_path,
    )
