"""
FILE: infrastructure/scanner_report_writer.py
VERSION: 1.0
DATE: 2026-07-12
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Formats Scanner Loop STRICT hits (WO-P300-E3.001) into a
    human-readable markdown watchlist, written to
    outputs/reports/scanner/. Report is generated FROM the hits
    application/scanner_loop.py already computed -- this module does
    no detection or math, only formatting (same split as
    sector_report_writer.py).

    Read-only artifact. No DB write of any kind, here or anywhere else
    in this WO -- the detector's opinion never enters the analog pool
    automatically (the design boundary that keeps this WO out of
    WO-P300-E2.003's rejected-merge territory).

CHANGELOG:
    - 2026-07-12 v1.0: Initial release (WO-P300-E3.001 file #2 of 5).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import SCANNER_REPORTS_DIR  # noqa: E402


@dataclass(frozen=True)
class ScannerHit:
    """One STRICT detection surfaced by the nightly scan. Formatting
    layer's own input contract -- not a DB row model, since this WO
    persists nothing (report-only by design)."""
    symbol: str
    source_filename: str
    anchor_date: date
    resistance_level: float
    conditions_passed: dict[int, bool] = field(default_factory=dict)


def format_scanner_report(hits: list[ScannerHit]) -> str:
    """Render STRICT hits as a markdown table, most recent anchor_date
    first. Each row's conditions_passed renders as a compact 1-9
    pass/fail string for audit trail (same rationale as every other
    detection report in this project)."""
    if not hits:
        return (
            "# Scanner Watchlist\n\nNo STRICT hits this run.\n"
        )

    ordered = sorted(hits, key=lambda h: h.anchor_date, reverse=True)
    lines = [
        "# Scanner Watchlist",
        f"\n{len(hits)} STRICT hit(s). Detector opinion only -- review by "
        "eye before any AddPattern action. Not written to any catalog.\n",
        "| Symbol | Anchor Date | Resistance | Conditions 1-9 | Source File |",
        "|---|---|---|---|---|",
    ]
    for h in ordered:
        cond_str = "".join(
            "1" if h.conditions_passed.get(i, False) else "0"
            for i in range(1, 10)
        )
        lines.append(
            f"| {h.symbol} | {h.anchor_date.isoformat()} | "
            f"{h.resistance_level:.2f} | {cond_str} | {h.source_filename} |"
        )
    return "\n".join(lines) + "\n"


def write_scanner_report(
    hits: list[ScannerHit], target_dir: Path | None = None
) -> Path:
    """Writes the report to <target_dir>/scanner_<stamp>.md. Default
    target_dir is SCANNER_REPORTS_DIR, created if absent (mirrors
    sector_report_writer.py's SECTOR_REPORTS_DIR convention)."""
    out_dir = target_dir if target_dir is not None else SCANNER_REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"scanner_{stamp}.md"
    out_path.write_text(format_scanner_report(hits), encoding="utf-8")
    return out_path
