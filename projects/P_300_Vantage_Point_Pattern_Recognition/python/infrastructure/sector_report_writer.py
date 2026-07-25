"""
FILE: infrastructure/sector_report_writer.py
VERSION: 1.0
DATE: 2026-07-10
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Formats sector_stats rows (already computed + persisted by
    domain/sector_stats_calc.py + infrastructure/sector_stats_io.py)
    into a human-readable markdown report, written to
    outputs/reports/sector_analysis/. Report is generated FROM the
    sector_stats table, not computed fresh here (Decision 3) -- this
    module does no math, only formatting.

    Cells with below_min_n=True render with a low-confidence flag
    (Decision 4: flag, don't exclude) rather than being dropped or
    shown with equal-confidence formatting.

CHANGELOG:
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.002 file #8 of 11).
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import REPORTS_DIR, SECTOR_MIN_N_THRESHOLD  # noqa: E402
from schemas_sector_analysis import SectorStatsRecord  # noqa: E402

SECTOR_REPORTS_DIR: Path = REPORTS_DIR / "sector_analysis"


def format_sector_stats_report(records: list[SectorStatsRecord]) -> str:
    """Render sector_stats rows as a markdown table, one section per
    sector_label (real GICS sectors first, then the ETF/Index bucket
    last -- alphabetical sort already puts most sector names before
    "Index/Diversified", so no special-case ordering needed)."""
    if not records:
        return "# Sector Analysis Report\n\nNo sector_stats rows found -- run the analysis first.\n"

    lines = [
        "# Sector Analysis Report",
        f"\nGenerated from {len(records)} sector_stats rows. "
        f"Cells below N={SECTOR_MIN_N_THRESHOLD} are flagged low-confidence "
        "(shown, not excluded, per Decision 4).\n",
        "| Sector | Tier | Horizon | N | Win Rate | Mean Return % | Std Dev % | Flag |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in records:
        flag = "LOW-N" if r.below_min_n else ""
        wr = f"{r.win_rate:.1%}" if r.win_rate is not None else "--"
        mean = f"{r.mean_return_pct:+.2f}%" if r.mean_return_pct is not None else "--"
        std = f"{r.std_return_pct:.2f}%" if r.std_return_pct is not None else "--"
        lines.append(
            f"| {r.sector_label} | {r.detection_tier} | {r.horizon_days}d | "
            f"{r.n} | {wr} | {mean} | {std} | {flag} |"
        )
    return "\n".join(lines) + "\n"


def write_sector_stats_report(
    records: list[SectorStatsRecord], target_dir: Path | None = None
) -> Path:
    """Writes the report to <target_dir>/sector_analysis_<stamp>.md.
    Default target_dir is SECTOR_REPORTS_DIR, created if absent
    (mirrors eval_io.py's EVAL_REPORTS_DIR convention)."""
    out_dir = target_dir if target_dir is not None else SECTOR_REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"sector_analysis_{stamp}.md"
    out_path.write_text(format_sector_stats_report(records), encoding="utf-8")
    return out_path
