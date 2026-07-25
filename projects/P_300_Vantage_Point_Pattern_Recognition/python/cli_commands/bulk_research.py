"""
FILE: cli_commands/bulk_research.py
VERSION: 1.0
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: cli
DESCRIPTION:
    Bulk research-catalog command handlers + argparse registration --
    bulk-extract, phase5-analysis, scanner-loop, mine-patterns. All
    four are report-only or research-catalog-only: none of them ever
    touch the live *catalog.db. Split out of the former monolithic
    cli.py (WO-P300-E4.001, command-registry refactor) -- pure cut-
    and-paste, no behavior change.

    Deliberately separate from cli_commands/bulk_promote.py (merge-
    research-catalog, ingest-mined, archive-mined) even though the
    WO's original draft planned one combined bulk.py -- that single
    file measured out to ~285-290 lines at build time, uncomfortably
    close to the 300 hard cap with zero room for the next bulk
    subcommand (the exact problem this WO exists to solve, one level
    down). The two-way split is also a real Process Boundary Standard
    distinction: this file's four commands never write to the live
    catalog; bulk_promote.py's three commands build staging copies
    specifically meant to eventually promote to it -- different
    reasons to change.

CHANGELOG:
    - 2026-07-20 v1.0 (WO-P300-E4.001): split from cli.py v1.14.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import (  # noqa: E402
    BULK_CHECKPOINT_FILE, BULK_RESEARCH_DB, BULK_TEMP_DB, DATA_BULK,
)


def _cmd_bulk_extract(args: argparse.Namespace) -> int:
    """Run Pipeline A-Bulk end-to-end (WO-P300-E2.001).

    Always returns 0 -- per-file failures are captured in the returned
    checkpoint's last_error and left for retry on the next run, not
    treated as a CLI-level failure (a research pipeline processing many
    files is expected to have partial-progress runs as normal
    operation)."""
    from application.bulk_extract_pipeline import run_bulk_extraction

    input_dir = Path(args.input_dir) if args.input_dir else DATA_BULK
    master_db = Path(args.master_db) if args.master_db else BULK_RESEARCH_DB
    temp_db = Path(args.temp_db) if args.temp_db else BULK_TEMP_DB
    checkpoint_path = (
        Path(args.checkpoint) if args.checkpoint else BULK_CHECKPOINT_FILE
    )

    checkpoint = run_bulk_extraction(
        input_dir=input_dir,
        master_db=master_db,
        temp_db=temp_db,
        checkpoint_path=checkpoint_path,
    )
    print()
    print(f"BULK EXTRACT COMPLETE -- master={master_db}")
    print(f"files queued={checkpoint.total_files_queued}  "
          f"completed={len(checkpoint.completed_filenames)}")
    print(f"STRICT={checkpoint.strict_detections_total}  "
          f"RELAXED={checkpoint.relaxed_detections_total}")
    if checkpoint.last_error:
        print(f"last_error (will retry next run): {checkpoint.last_error}")
    return 0


def _cmd_mine_patterns(args: argparse.Namespace) -> int:
    """Run Phase 1 of the Outcome-First Pattern Miner (WO-P300-E3.002).
    Report-only -- never touches any catalog.db."""
    from application.mine_patterns_pipeline import run_mine_patterns
    from config import DATA_BULK_MINE

    input_dir = Path(args.input_dir) if args.input_dir else DATA_BULK_MINE
    reports_dir = Path(args.reports_dir) if args.reports_dir else None

    result = run_mine_patterns(input_dir=input_dir, reports_dir=reports_dir)
    print()
    print(f"MINE PATTERNS COMPLETE -- input={input_dir}")
    print(f"files scanned={result.files_scanned}  candidates={result.candidates_found} "
          f"(uptrend={result.uptrend_count} breakdown={result.breakdown_count})")
    print(f"report={result.report_path}")
    print(f"csv={result.csv_path}")
    if result.parse_failures:
        print(f"parse failures: {result.parse_failures}")
    return 0


def _cmd_scanner_loop(args: argparse.Namespace) -> int:
    """Run the Scanner Loop end-to-end (WO-P300-E3.001). Report-only --
    never touches any catalog.db. Always returns 0 (per-file parse
    failures are logged and left for operator inspection, not treated
    as a CLI-level failure -- same posture as bulk-extract)."""
    from application.scanner_loop import run_scanner_loop
    from config import DATA_BULK_NIGHTLY_SCAN

    input_dir = Path(args.input_dir) if args.input_dir else DATA_BULK_NIGHTLY_SCAN
    reports_dir = Path(args.reports_dir) if args.reports_dir else None

    result = run_scanner_loop(input_dir=input_dir, reports_dir=reports_dir)
    print()
    print(f"SCANNER LOOP COMPLETE -- input={input_dir}")
    print(f"files scanned={result.files_scanned}  STRICT hits={result.strict_hits}")
    print(f"report={result.report_path}")
    if result.parse_failures:
        print(f"parse failures (left in place, not archived): {result.parse_failures}")
    if result.archive_failures:
        print(f"archive failures (see log above): {result.archive_failures}")
    return 0


def _cmd_phase5_analysis(args: argparse.Namespace) -> int:
    """Run WO-P300-E2.002 Phase 5 end-to-end. Unlike bulk-extract,
    returns 1 on failure -- a missing sector_map entry or a verification
    mismatch is a real stop, not a per-file retry case."""
    from application.phase5_analysis import run_phase5_analysis

    master_db = Path(args.master_db) if args.master_db else BULK_RESEARCH_DB
    try:
        result = run_phase5_analysis(
            master_path=master_db, run_backfill=not args.no_backfill
        )
    except Exception as e:
        print(f"Phase 5 analysis failed: {e}", file=sys.stderr)
        return 1

    print()
    print(f"PHASE 5 ANALYSIS COMPLETE -- master={master_db}")
    if result.backfill is not None:
        print(f"backfill: {result.backfill.rows_updated} updated, "
              f"{result.backfill.rows_unchanged} unchanged")
    print(f"rows_analyzed={result.rows_analyzed}  "
          f"sector_stats_cells={result.cells_computed}")
    print(f"report: {result.report_path}")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Registers bulk-extract, scanner-loop, mine-patterns, phase5-analysis."""
    p_bulk = subparsers.add_parser(
        "bulk-extract",
        help="Run Pipeline A-Bulk over data/bulk/ into the research catalog.",
    )
    p_bulk.add_argument(
        "--input-dir", default=None,
        help="Bulk XLSX input dir override; defaults to config.DATA_BULK.",
    )
    p_bulk.add_argument(
        "--master-db", default=None,
        help="Research catalog master path override; defaults to "
             "config.BULK_RESEARCH_DB.",
    )
    p_bulk.add_argument(
        "--temp-db", default=None,
        help="Temp working DB override; defaults to config.BULK_TEMP_DB.",
    )
    p_bulk.add_argument(
        "--checkpoint", default=None,
        help="Checkpoint file override; defaults to config.BULK_CHECKPOINT_FILE. "
             "ALWAYS override this alongside --master-db/--temp-db when testing "
             "against scratch paths (M-075).",
    )
    p_bulk.set_defaults(func=_cmd_bulk_extract)

    p_scan = subparsers.add_parser(
        "scanner-loop",
        help="Run the nightly Scanner Loop over data/bulk/nightly_scan/. "
             "Report-only -- never writes to any catalog.db.",
    )
    p_scan.add_argument(
        "--input-dir", default=None,
        help="Nightly-scan XLSX input dir override; defaults to "
             "config.DATA_BULK_NIGHTLY_SCAN.",
    )
    p_scan.add_argument(
        "--reports-dir", default=None,
        help="Report output dir override; defaults to "
             "config.SCANNER_REPORTS_DIR.",
    )
    p_scan.set_defaults(func=_cmd_scanner_loop)

    p_mine = subparsers.add_parser(
        "mine-patterns",
        help="Phase 1 of the Outcome-First Pattern Miner: scan "
             "data/bulk/mine/ for >=15%% forward moves. Report-only.",
    )
    p_mine.add_argument(
        "--input-dir", default=None,
        help="Mine XLSX input dir override; defaults to "
             "config.DATA_BULK_MINE.",
    )
    p_mine.add_argument(
        "--reports-dir", default=None,
        help="Report/CSV output dir override; defaults to "
             "config.MINE_REPORTS_DIR.",
    )
    p_mine.set_defaults(func=_cmd_mine_patterns)

    p_p5 = subparsers.add_parser(
        "phase5-analysis",
        help="Run WO-P300-E2.002 Phase 5 sector-stratified analysis.",
    )
    p_p5.add_argument(
        "--master-db", default=None,
        help="Research catalog master path override; defaults to "
             "config.BULK_RESEARCH_DB.",
    )
    p_p5.add_argument(
        "--no-backfill", action="store_true",
        help="Skip the sector backfill step (stats-only re-run against "
             "an already-backfilled catalog).",
    )
    p_p5.set_defaults(func=_cmd_phase5_analysis)
