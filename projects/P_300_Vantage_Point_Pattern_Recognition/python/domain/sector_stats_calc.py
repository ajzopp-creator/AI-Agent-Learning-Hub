"""
FILE: domain/sector_stats_calc.py
VERSION: 1.0
DATE: 2026-07-10
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure stats computation for WO-P300-E2.002 Phase 5. Groups raw
    catalog rows into (sector_label x detection_tier x horizon_days)
    cells and computes n / win_rate / mean_return_pct / std_return_pct
    per cell, flagging cells under SECTOR_MIN_N_THRESHOLD (Decision 4).

    ETF rows (asset_class=ASSET_CLASS_ETF) are bucketed under
    SECTOR_ETF_LABEL ("Index/Diversified") instead of their (None)
    sector -- never folded into a real sector, per Decision 5. STOCK
    rows use their real sector as sector_label directly.

    Only combinations actually present in the input produce a row --
    a sector/tier/horizon combo with zero instances is simply absent,
    not an error (Decision 4 scope note: missing GICS sectors entirely,
    because nothing's licensed yet, are absent from the report).

    mean_return_pct / std_return_pct are converted to PERCENT space
    here, once, at this boundary -- unlike forward_labels.return_pct's
    raw decimal-fraction storage (M-020). This module produces a
    report/display artifact, not a ledger row; downstream (report
    writer) reads the percent value directly and never reconverts.

    No I/O, no DB, no print -- strictly testable in isolation.

CHANGELOG:
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.002 file #4 of 11).
"""
from __future__ import annotations

import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import ASSET_CLASS_ETF, ASSET_CLASS_STOCK, SECTOR_ETF_LABEL, SECTOR_MIN_N_THRESHOLD  # noqa: E402
from schemas_sector_analysis import SectorStatsRecord  # noqa: E402


@dataclass(frozen=True)
class SectorAnalysisInputRow:
    """
    One joined (symbol x pattern_instance x forward_label) row, already
    resolved to a sector_label-ready shape by the infrastructure layer.
    sector is None only for asset_class=ETF rows (Decision 5) -- STOCK
    rows always carry a real sector by the time they reach here
    (Decision 2 zero-tolerance is enforced upstream at ingest/backfill,
    not re-checked in this pure-math layer).
    """
    sector: str | None
    asset_class: str            # ASSET_CLASS_STOCK / ASSET_CLASS_ETF
    detection_tier: str         # BULK_TIER_STRICT / BULK_TIER_RELAXED
    horizon_days: int
    return_pct: float           # decimal fraction (M-020), converted below
    is_profitable: bool


def _sector_label(row: SectorAnalysisInputRow) -> str:
    if row.asset_class == ASSET_CLASS_ETF:
        return SECTOR_ETF_LABEL
    if row.sector is None:
        raise ValueError(
            f"STOCK row with sector=None reached sector_stats_calc -- "
            f"upstream Decision 2 enforcement failed silently (asset_class="
            f"{row.asset_class!r})"
        )
    return row.sector


def compute_sector_stats(
    rows: list[SectorAnalysisInputRow],
    computed_at: datetime,
) -> list[SectorStatsRecord]:
    """
    Group rows into (sector_label, detection_tier, horizon_days) cells
    and compute stats per cell. Returns rows sorted deterministically
    (sector_label, tier, horizon) for reproducible report output.
    """
    groups: dict[tuple[str, str, int], list[SectorAnalysisInputRow]] = defaultdict(list)
    for row in rows:
        key = (_sector_label(row), row.detection_tier, row.horizon_days)
        groups[key].append(row)

    results: list[SectorStatsRecord] = []
    for (sector_label, tier, horizon), cell_rows in groups.items():
        n = len(cell_rows)
        returns_pct = [r.return_pct * 100.0 for r in cell_rows]
        win_rate = sum(1 for r in cell_rows if r.is_profitable) / n
        mean_return_pct = statistics.mean(returns_pct)
        std_return_pct = statistics.stdev(returns_pct) if n >= 2 else None

        results.append(SectorStatsRecord(
            sector_label=sector_label,
            detection_tier=tier,
            horizon_days=horizon,
            n=n,
            win_rate=win_rate,
            mean_return_pct=mean_return_pct,
            std_return_pct=std_return_pct,
            below_min_n=(n < SECTOR_MIN_N_THRESHOLD),
            computed_at=computed_at,
        ))

    results.sort(key=lambda r: (r.sector_label, r.detection_tier, r.horizon_days))
    return results
