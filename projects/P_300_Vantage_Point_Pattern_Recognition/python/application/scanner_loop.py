"""
FILE: application/scanner_loop.py
VERSION: 1.1
DATE: 2026-07-12
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Scanner Loop orchestrator (WO-P300-E3.001). Pure orchestration --
    no business logic of its own, no DB write of any kind. Never
    touches live catalog.db or bulk_research.db.

    Flow, per *.xlsx file in DATA_BULK_NIGHTLY_SCAN:
        1. Parse via bulk_grid_reader.parse_bulk_file ->
           BulkPatternFileParse (unchanged, reused as-is from
           WO-P300-E2.001).
        2. Point-in-time detection only -- detect_bulk_pattern() called
           once, at the LAST bar in the file (unlike
           bulk_extract_pipeline.py, which sweeps every eligible bar
           of a multi-year file for the historical research corpus).
           A nightly candidate check only cares about today's bar.
        3. STRICT hits only -- becomes a ScannerHit for the report.
           RELAXED / no-hit files are logged at INFO and otherwise
           dropped (Tony confirmed "Cross Over only", 2026-07-12).
        4. Every file -- hit or not -- archives via
           archive_scanner_file.run_archive() immediately after
           detection, unconditionally. A file that fails to parse is
           NOT archived (left in place for the operator to inspect and
           re-export, same failure posture as AddPattern's rejections).
        5. After all files processed, write the watchlist report via
           scanner_report_writer.write_scanner_report().

    One bad file does not stop the run -- caught, logged, counted, and
    the loop continues to the next file (same resilience posture as
    bulk_extract_pipeline.py's per-file checkpoint handling).

CHANGELOG:
    - 2026-07-12 v1.1: run_scanner_loop() gained a reports_dir override
      (default None -> SCANNER_REPORTS_DIR, threaded through to
      write_scanner_report). Caught during PEH verification (Claude
      Code, 2026-07-12): the initial version had no way to redirect
      report output at all, so the PEH test had to monkeypatch
      scanner_report_writer's module constant to avoid writing a real
      file into production outputs/reports/scanner/ during a scratch
      test run. Same family of gap as bulk_extract_pipeline.py's
      checkpoint_path fix (M-075) -- a test-isolation need surfacing a
      real missing parameter, not just a test bug.
    - 2026-07-12 v1.0: Initial release (WO-P300-E3.001 file #3 of 5).
"""
from __future__ import annotations

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import DATA_BULK_NIGHTLY_SCAN  # noqa: E402
from domain.bulk_pattern_detector import detect_bulk_pattern  # noqa: E402
from infrastructure.bulk_grid_reader import parse_bulk_file  # noqa: E402
from infrastructure.scanner_report_writer import (  # noqa: E402
    ScannerHit,
    write_scanner_report,
)
from schemas_bulk import DetectionTier  # noqa: E402
from utilities.archive_scanner_file import run_archive  # noqa: E402

logger = logging.getLogger(__name__)


@dataclass
class ScannerRunResult:
    """Summary of one scanner_loop run, for the CLI to print."""
    files_scanned: int = 0
    strict_hits: int = 0
    parse_failures: list[str] = field(default_factory=list)
    archive_failures: list[str] = field(default_factory=list)
    report_path: Path | None = None


def _scan_one_file(xlsx_path: Path) -> ScannerHit | None:
    """Parse one file and detect at its last bar only. Returns a
    ScannerHit on a STRICT pass, None on RELAXED/no-hit. Raises on
    parse failure -- caller decides whether to archive."""
    parsed = parse_bulk_file(xlsx_path)
    bars = parsed.bars
    last_idx = len(bars) - 1

    result = detect_bulk_pattern(bars, last_idx)
    if result is None or result.tier != DetectionTier.STRICT:
        logger.info(
            "%s -- no STRICT hit (tier=%s)",
            xlsx_path.name, result.tier if result else "none",
        )
        return None

    return ScannerHit(
        symbol=parsed.metadata.symbol,
        source_filename=xlsx_path.name,
        anchor_date=bars[last_idx].bar_date,
        resistance_level=result.resistance_level,
        conditions_passed=result.conditions_passed,
    )


def run_scanner_loop(
    input_dir: Path = DATA_BULK_NIGHTLY_SCAN,
    reports_dir: Path | None = None,
) -> ScannerRunResult:
    """Runs the full scanner loop against every *.xlsx file in
    input_dir. Report-only -- writes a markdown watchlist, never
    touches any catalog.db. reports_dir overrides the report's write
    location (defaults to SCANNER_REPORTS_DIR inside
    write_scanner_report itself when None) -- needed so callers
    (tests, a future --reports-dir CLI flag) can redirect output
    without touching config.py's real constant."""
    result = ScannerRunResult()
    files = sorted(input_dir.glob("*.xlsx")) if input_dir.exists() else []

    hits: list[ScannerHit] = []
    for xlsx_path in files:
        try:
            hit = _scan_one_file(xlsx_path)
        except Exception as exc:
            logger.error("Parse/detect failed for %s: %s", xlsx_path.name, exc)
            result.parse_failures.append(xlsx_path.name)
            continue  # not archived -- left for operator inspection

        result.files_scanned += 1
        if hit is not None:
            hits.append(hit)
            result.strict_hits += 1

        archive_rc = run_archive(xlsx_path)
        if archive_rc != 0:
            result.archive_failures.append(xlsx_path.name)

    result.report_path = write_scanner_report(hits, target_dir=reports_dir)
    return result
