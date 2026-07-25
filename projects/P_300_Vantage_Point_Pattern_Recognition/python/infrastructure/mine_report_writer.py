"""
FILE: infrastructure/mine_report_writer.py
VERSION: 1.0
DATE: 2026-07-13
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Formats domain/pattern_miner.py's MinedCandidate output (WO-P300-
    E3.002 Phase 1) into a human-readable markdown report and a
    machine-readable candidates CSV, and reads an operator-approved
    CSV back in for Phase 2 (WO's file #3 of 9 -- report + CSV writer
    + approved-CSV reader). Formatting/IO only, no mining logic --
    same split as scanner_report_writer.py.

    Read-only artifact set. No DB write of any kind, here or anywhere
    else in Phase 1's code -- a mined candidate never enters the
    catalog automatically. The CSV's `keep` column defaults YES (per
    the WO's ~15 sec/symbol approve/reject workflow) but nothing acts
    on it until Phase 2 explicitly reads the file back via
    read_approved_candidates_csv().

CHANGELOG:
    - 2026-07-13 v1.0: Initial release (WO-P300-E3.002 file #3 of 9).
"""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import MINE_CANDIDATES_CSV, MINE_REPORTS_DIR  # noqa: E402

_CSV_FIELDS = [
    "symbol", "anchor_date", "pattern_class", "horizon_days", "move_pct",
    "standard_horizon", "bars_since_crossover", "entry_tier", "keep",
]


@dataclass(frozen=True)
class MineCandidateRow:
    """One mined candidate with its symbol attached (pattern_miner.py's
    MinedCandidate is deliberately symbol-less -- the caller knows the
    symbol from the file being scanned). Formatting layer's own input
    contract, not a DB row model -- this WO persists nothing to any
    catalog in Phase 1."""
    symbol: str
    anchor_date: date
    pattern_class: str
    horizon_days: int
    move_pct: float
    standard_horizon: bool
    bars_since_crossover: int
    entry_tier: str
    keep: str = "YES"


def format_mine_report(rows: list[MineCandidateRow]) -> str:
    """Render candidates as a markdown table, most recent anchor_date
    first. Extended-horizon (standard_horizon=False) rows are flagged
    inline -- transparency per the WO's design note, not exclusion."""
    if not rows:
        return "# Mine Candidates\n\nNo candidates this run.\n"

    ordered = sorted(rows, key=lambda r: r.anchor_date, reverse=True)
    uptrend_n = sum(1 for r in rows if r.pattern_class == "uptrend")
    breakdown_n = len(rows) - uptrend_n
    lines = [
        "# Mine Candidates",
        f"\n{len(rows)} candidate(s) -- {uptrend_n} uptrend / {breakdown_n} "
        "breakdown. Outcome-first mining, review before approving the CSV "
        "for Phase 2 ingest. Not written to any catalog.\n",
        "| Symbol | Anchor Date | Class | Horizon | Move % | Std | Tier |"
        " Bars-Since-Xover |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in ordered:
        std_flag = "std" if r.standard_horizon else "EXT"
        lines.append(
            f"| {r.symbol} | {r.anchor_date.isoformat()} | {r.pattern_class} | "
            f"{r.horizon_days}d | {r.move_pct*100:+.2f}% | {std_flag} | "
            f"{r.entry_tier} | {r.bars_since_crossover} |"
        )
    return "\n".join(lines) + "\n"


def write_mine_report(rows: list[MineCandidateRow], target_dir: Path | None = None) -> Path:
    """Writes the markdown report to <target_dir>/mine_<stamp>.md.
    Default target_dir is MINE_REPORTS_DIR, created if absent."""
    out_dir = target_dir if target_dir is not None else MINE_REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"mine_{stamp}.md"
    out_path.write_text(format_mine_report(rows), encoding="utf-8")
    return out_path


def write_mine_candidates_csv(
    rows: list[MineCandidateRow], target_dir: Path | None = None
) -> Path:
    """Writes the machine-readable candidates CSV to
    <target_dir>/MINE_CANDIDATES_CSV -- a STABLE filename (not
    timestamped like the markdown report), overwritten each run, since
    this is the single working file the operator edits keep=YES/NO on
    before Phase 2 reads it back. Default target_dir is
    MINE_REPORTS_DIR."""
    out_dir = target_dir if target_dir is not None else MINE_REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / MINE_CANDIDATES_CSV

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for r in sorted(rows, key=lambda r: (r.symbol, r.anchor_date)):
            writer.writerow({
                "symbol": r.symbol,
                "anchor_date": r.anchor_date.isoformat(),
                "pattern_class": r.pattern_class,
                "horizon_days": r.horizon_days,
                "move_pct": f"{r.move_pct:.6f}",
                "standard_horizon": r.standard_horizon,
                "bars_since_crossover": r.bars_since_crossover,
                "entry_tier": r.entry_tier,
                "keep": r.keep,
            })
    return out_path


def read_approved_candidates_csv(csv_path: Path) -> list[MineCandidateRow]:
    """Phase 2 input (WO file #6, not built yet). Reads a (possibly
    operator-edited) candidates CSV back, returning only rows with
    keep == 'YES' (case-insensitive) -- everything else was explicitly
    rejected or left at default and is skipped. Raises FileNotFoundError
    if csv_path doesn't exist; raises ValueError on a malformed row
    rather than silently skipping bad data."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Approved candidates CSV not found: {csv_path}")

    approved: list[MineCandidateRow] = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # header is line 1
            if row.get("keep", "").strip().upper() != "YES":
                continue
            try:
                approved.append(MineCandidateRow(
                    symbol=row["symbol"],
                    anchor_date=date.fromisoformat(row["anchor_date"]),
                    pattern_class=row["pattern_class"],
                    horizon_days=int(row["horizon_days"]),
                    move_pct=float(row["move_pct"]),
                    standard_horizon=row["standard_horizon"].strip().lower() == "true",
                    bars_since_crossover=int(row["bars_since_crossover"]),
                    entry_tier=row["entry_tier"],
                    keep=row["keep"],
                ))
            except (KeyError, ValueError) as exc:
                raise ValueError(f"Malformed row at line {i} in {csv_path}: {exc}") from exc
    return approved
