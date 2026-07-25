"""
FILE: application/mine_patterns_pipeline.py
VERSION: 1.0
DATE: 2026-07-13
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Phase 1 orchestrator for the Outcome-First Pattern Miner (WO-P300-
    E3.002, file #4 of 9). Pure orchestration -- no mining logic of its
    own (domain/pattern_miner.py), no formatting of its own
    (infrastructure/mine_report_writer.py), no DB write of any kind,
    here or anywhere else in Phase 1's code.

    Flow, per *.xlsx file in DATA_BULK_MINE:
        1. Parse via bulk_grid_reader.parse_bulk_file (reused
           unchanged from WO-P300-E2.001) -> bars + symbol from the
           file's own metadata (not the filename -- same posture as
           scanner_loop.py).
        2. Mine via pattern_miner.mine_bars() -- full crossover-gated
           scan, any period (the WO's whole point: Tony exports
           whatever span he wants, the 2-month live-window limitation
           that constrained the old bulk pipeline doesn't apply here).
        3. Attach symbol to each MinedCandidate -> MineCandidateRow.
        4. After all files: write the markdown report + candidates
           CSV via mine_report_writer.

    One bad file does not stop the run -- caught, logged, counted, the
    loop continues (same resilience posture as scanner_loop.py /
    bulk_extract_pipeline.py).

CHANGELOG:
    - 2026-07-13 v1.0: Initial release (WO-P300-E3.002 file #4 of 9).
      Validation-first WO -- 84-anchor ground-truth validation (parts
      5-16, same session) confirmed v2.1 before this file was written;
      see tasks/lessons.md M-085/086/087.
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import DATA_BULK_MINE  # noqa: E402
from domain.pattern_miner import mine_bars  # noqa: E402
from infrastructure.bulk_grid_reader import parse_bulk_file  # noqa: E402
from infrastructure.mine_report_writer import (  # noqa: E402
    MineCandidateRow,
    write_mine_candidates_csv,
    write_mine_report,
)

logger = logging.getLogger(__name__)


@dataclass
class MineRunResult:
    """Summary of one mine_patterns_pipeline run, for the CLI to print.
    Field names match cli.py v1.12's already-shipped _cmd_mine_patterns
    handler exactly -- that CLI shim was written ahead of this file per
    the WO's own delivery order and pins this contract."""
    files_scanned: int = 0
    candidates_found: int = 0
    uptrend_count: int = 0
    breakdown_count: int = 0
    parse_failures: list[str] = field(default_factory=list)
    report_path: Path | None = None
    csv_path: Path | None = None


def _mine_one_file(xlsx_path: Path) -> list[MineCandidateRow]:
    """Parse one file and mine it fully. Raises on parse failure --
    caller decides how to log/count it."""
    parsed = parse_bulk_file(xlsx_path)
    symbol = parsed.metadata.symbol
    candidates = mine_bars(parsed.bars)
    return [
        MineCandidateRow(
            symbol=symbol,
            anchor_date=c.anchor_date,
            pattern_class=c.pattern_class,
            horizon_days=c.horizon_days,
            move_pct=c.move_pct,
            standard_horizon=c.standard_horizon,
            bars_since_crossover=c.bars_since_crossover,
            entry_tier=c.entry_tier,
        )
        for c in candidates
    ]


def run_mine_patterns(
    input_dir: Path = DATA_BULK_MINE,
    reports_dir: Path | None = None,
) -> MineRunResult:
    """Runs Phase 1 against every *.xlsx file in input_dir. Report-only
    -- writes a markdown report + candidates CSV, never touches any
    catalog.db. reports_dir overrides both output locations (defaults
    to MINE_REPORTS_DIR inside the writer functions when None) --
    needed so callers (tests, the --reports-dir CLI flag) can redirect
    output without touching config.py's real constant (same pattern as
    scanner_loop.py's reports_dir, M-080)."""
    result = MineRunResult()
    files = sorted(input_dir.glob("*.xlsx")) if input_dir.exists() else []

    all_rows: list[MineCandidateRow] = []
    for xlsx_path in files:
        try:
            rows = _mine_one_file(xlsx_path)
        except Exception as exc:
            logger.error("Parse/mine failed for %s: %s", xlsx_path.name, exc)
            result.parse_failures.append(xlsx_path.name)
            continue

        result.files_scanned += 1
        all_rows.extend(rows)

    result.candidates_found = len(all_rows)
    result.uptrend_count = sum(1 for r in all_rows if r.pattern_class == "uptrend")
    result.breakdown_count = result.candidates_found - result.uptrend_count

    result.report_path = write_mine_report(all_rows, target_dir=reports_dir)
    result.csv_path = write_mine_candidates_csv(all_rows, target_dir=reports_dir)
    return result
