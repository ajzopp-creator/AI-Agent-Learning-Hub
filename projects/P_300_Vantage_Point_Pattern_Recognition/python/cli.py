"""
FILE: cli.py
VERSION: 1.6
DATE: 2026-05-29
AUTHOR: Anthony Zophi + Claude
LAYER: cli
DESCRIPTION:
    Unified command-line entry point for the P_300 project. Wraps the
    seven operator-facing flows behind a single command:

        python cli.py add-pattern --xlsx PATH
            Ingest one VP Pattern XLSX via add_pattern_pipeline.
            Exit 0 on successful promotion, 1 on any failure.

        python cli.py archive-pattern --xlsx PATH
            Post-ingest archive step for Pipeline A. Appends the XLSX
            to this month's zip in data/processed/ and deletes the
            original from data/historical_patterns/. Run AFTER
            add-pattern. Exit 0 on success, 1 on any failure.

        python cli.py catalog-summary [--recent N]
            Print catalog health summary via utilities/catalog_summary.
            Exit 0 if no ghost records, 1 otherwise.

        python cli.py integrity-check --xlsx PATH
            Validate a VP export against ingest_manifest.json via
            utilities/vp_export_integrity_check. Run after any VP
            version update before resuming ingest. Exit 0 = safe to
            ingest, 1 = manifest needs an edit.

        python cli.py inspect-pattern --id N [--catalog PATH]
            Print one pattern's header, raw bars, normalized bars, and
            forward labels via utilities/inspect_pattern. Stage 5
            hand-compare regression helper. Read-only. Exit 0 on
            success, 1 if --id not found.

        python cli.py daily-evaluate --xlsx PATH [--window-length 20]
                                     [--top-k 20] [--no-write-file]
                                     [--reports-dir PATH] [--no-narrator]
                                     [--clean]
            Run Pipeline B on one live `History Grid (SYMBOL).xlsx`:
            parse + normalize + match against catalog + classify +
            emit BUY/WATCH/PASS report to stdout. Optional file output
            to config.REPORTS_DIR. Read-only against the catalog
            (Stage 6 decision E -- EVAL_SET is transient in-memory).
            Optional Stage 8 narrator pass via LM Studio (default on
            per config.NARRATOR_ENABLED; --no-narrator forces off).
            --clean suppresses INFO logging and dense report; emits
            minimal banner + signal line only (batch-mode output).
            Exit 0 on success, 1 on any failure.

        python cli.py archive-eval --xlsx PATH
            Post-eval archive step for Pipeline B. Verifies a report
            exists for the symbol in REPORTS_DIR, appends the XLSX to
            this month's zip in data/processed/, and deletes the
            original from data/live/. Run AFTER daily-evaluate.
            Exit 0 on success, 1 on any failure.

    Each subcommand is a thin shim -- the real work lives in the wrapped
    module. cli.py exists to remove the multi-line `python -c` invocation
    friction so daily operations are one-liners.

CHANGELOG:
    - 2026-05-29 v1.6: Added --clean flag to daily-evaluate subcommand.
      Routes through daily_evaluate_pipeline.main() instead of calling
      run_daily_evaluate() directly so --clean, LM Studio status check,
      and print_signal_report_clean() all fire correctly. Fixes
      P_300_DailyEval_v2.bat which was passing --clean to cli.py but
      cli.py had no parser support for it.
    - 2026-05-21 v1.5: Added archive-pattern --xlsx PATH subcommand.
    - 2026-05-20 v1.4: Added archive-eval --xlsx PATH subcommand.
    - 2026-05-19 v1.3: Added --no-narrator flag to daily-evaluate.
    - 2026-05-18 v1.2: Added daily-evaluate subcommand for Pipeline B.
    - 2026-05-16 v1.1: Added inspect-pattern subcommand.
    - 2026-05-15 v1.0: Stage 4 closing file.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from application.add_pattern_pipeline import ingest_pattern_file  # noqa: E402
from config import (  # noqa: E402
    LOG_FORMAT, LOG_LEVEL, NARRATOR_ENABLED, TOP_K_MATCHES,
)
from utilities.archive_live_file import run_archive  # noqa: E402
from utilities.archive_pattern_file import run_archive as run_archive_pattern  # noqa: E402
from utilities.catalog_summary import run_summary  # noqa: E402
from utilities.inspect_pattern import run_inspect  # noqa: E402
from utilities.vp_export_integrity_check import run_integrity_check  # noqa: E402
from application.ledger_fill import fill_ledger  # noqa: E402
from utilities.ledger_calibration import calibrate_ledger  # noqa: E402


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def _cmd_add_pattern(args: argparse.Namespace) -> int:
    """Run Pipeline A end-to-end on the given XLSX."""
    from utilities.db_utils import get_latest_catalog
    xlsx = Path(args.xlsx)
    master = Path(args.master) if args.master else Path(get_latest_catalog())
    result = ingest_pattern_file(xlsx, master)
    if result.passed:
        print()
        print(f"INGEST OK  -- master={master}")
        print(f"backup={result.backup_path}")
        print(f"post_counts={result.post_counts}")
        return 0
    print()
    print(f"INGEST FAILED -- master untouched")
    for msg in result.failures:
        print(f"  - {msg}")
    return 1


def _cmd_archive_pattern(args: argparse.Namespace) -> int:
    """Archive one ingested Pattern XLSX to the monthly zip in data/processed/."""
    return run_archive_pattern(Path(args.xlsx))


def _cmd_catalog_summary(args: argparse.Namespace) -> int:
    """Print catalog health summary."""
    catalog = Path(args.catalog) if args.catalog else None
    return run_summary(catalog, recent_limit=args.recent)


def _cmd_integrity_check(args: argparse.Namespace) -> int:
    """Validate VP export against manifest. Run after VP updates."""
    from config import PARAMETERS_DIR
    xlsx = Path(args.xlsx)
    manifest = (
        Path(args.manifest) if args.manifest
        else PARAMETERS_DIR / "ingest_manifest.json"
    )
    return run_integrity_check(xlsx, manifest)


def _cmd_inspect_pattern(args: argparse.Namespace) -> int:
    """Inspect one pattern_instance_id for Stage 5 hand-compare regression."""
    catalog = Path(args.catalog) if args.catalog else None
    return run_inspect(args.id, catalog)


def _cmd_daily_evaluate(args: argparse.Namespace) -> int:
    """Run Pipeline B end-to-end on one live History Grid XLSX.

    Routes through daily_evaluate_pipeline.main() so --clean, the LM
    Studio status check, and print_signal_report_clean() all fire
    correctly via the same code path as direct invocation.
    """
    from application.daily_evaluate_pipeline import main as _pipeline_main

    # Build an argv list that mirrors what the standalone CLI expects.
    argv = ["--xlsx", args.xlsx]
    argv += ["--window-length", str(args.window_length)]
    argv += ["--top-k", str(args.top_k)]
    if args.no_write_file:
        argv.append("--no-write-file")
    if args.reports_dir:
        argv += ["--reports-dir", args.reports_dir]
    if args.no_narrator:
        argv.append("--no-narrator")
    if args.clean:
        argv.append("--clean")

    return _pipeline_main(argv)


def _cmd_archive_eval(args: argparse.Namespace) -> int:
    """Archive one evaluated live XLSX to the monthly zip in data/processed/."""
    return run_archive(Path(args.xlsx))


def _cmd_ledger_fill(args: argparse.Namespace) -> int:
    """Fill realized outcomes for unfilled ledger rows."""
    try:
        fill_ledger(dry_run=args.dry_run)
        print("Ledger fill completed.")
        return 0
    except Exception as e:
        print(f"Ledger fill failed: {e}", file=sys.stderr)
        return 1


def _cmd_ledger_calibration(args: argparse.Namespace) -> int:
    """Generate calibration report comparing predicted vs realized returns."""
    try:
        report = calibrate_ledger()
        print(report)
        return 0
    except Exception as e:
        print(f"Calibration failed: {e}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="P_300 command-line entry point.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add-pattern
    p_add = subparsers.add_parser(
        "add-pattern", help="Ingest one VP Pattern XLSX via Pipeline A."
    )
    p_add.add_argument("--xlsx", required=True, help="Path to Pattern XLSX.")
    p_add.add_argument(
        "--master", default=None,
        help="Catalog master path override; defaults to get_latest_catalog().",
    )
    p_add.set_defaults(func=_cmd_add_pattern)

    # archive-pattern
    p_arch_pat = subparsers.add_parser(
        "archive-pattern",
        help="Archive an ingested Pattern XLSX to the monthly zip in data/processed/.",
    )
    p_arch_pat.add_argument(
        "--xlsx", required=True,
        help="Path to the Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx to archive.",
    )
    p_arch_pat.set_defaults(func=_cmd_archive_pattern)

    # catalog-summary
    p_sum = subparsers.add_parser(
        "catalog-summary", help="Print catalog health summary."
    )
    p_sum.add_argument(
        "--catalog", default=None,
        help="Catalog path override; defaults to get_latest_catalog().",
    )
    p_sum.add_argument(
        "--recent", type=int, default=5,
        help="Number of most-recent patterns to show (default: 5).",
    )
    p_sum.set_defaults(func=_cmd_catalog_summary)

    # integrity-check
    p_int = subparsers.add_parser(
        "integrity-check",
        help="Validate a VP export against ingest_manifest.json.",
    )
    p_int.add_argument("--xlsx", required=True, help="Path to VP XLSX to check.")
    p_int.add_argument(
        "--manifest", default=None,
        help="Manifest path override; defaults to parameters/ingest_manifest.json.",
    )
    p_int.set_defaults(func=_cmd_integrity_check)

    # inspect-pattern
    p_insp = subparsers.add_parser(
        "inspect-pattern",
        help="Print one pattern's bars + forward labels for hand-compare.",
    )
    p_insp.add_argument(
        "--id", type=int, required=True,
        help="pattern_instance_id to inspect (e.g., --id 1).",
    )
    p_insp.add_argument(
        "--catalog", default=None,
        help="Catalog path override; defaults to get_latest_catalog().",
    )
    p_insp.set_defaults(func=_cmd_inspect_pattern)

    # daily-evaluate (Pipeline B)
    p_eval = subparsers.add_parser(
        "daily-evaluate",
        help="Run Pipeline B on one live History Grid XLSX.",
    )
    p_eval.add_argument(
        "--xlsx", required=True,
        help="Path to History Grid (SYMBOL).xlsx",
    )
    p_eval.add_argument(
        "--window-length", type=int, default=20,
        help="Candidate window size in bars (default 20).",
    )
    p_eval.add_argument(
        "--top-k", type=int, default=TOP_K_MATCHES,
        help=f"Top-K matches to surface (default {TOP_K_MATCHES}).",
    )
    p_eval.add_argument(
        "--no-write-file", action="store_true",
        help="Skip persisting the report to disk; print to terminal only.",
    )
    p_eval.add_argument(
        "--reports-dir", default=None,
        help="Override target directory for the written report.",
    )
    p_eval.add_argument(
        "--no-narrator", action="store_true",
        help=(
            "Skip the Stage 8 LM Studio narration call. Faster for testing "
            "or when LM Studio is down. Signal class unaffected (NFR-1)."
        ),
    )
    p_eval.add_argument(
        "--clean", action="store_true",
        help=(
            "Use clean console output (minimal banner + signal + status). "
            "Designed for batch multi-symbol evaluation. "
            "Details suppressed from console."
        ),
    )
    p_eval.set_defaults(func=_cmd_daily_evaluate)

    # archive-eval
    p_arch = subparsers.add_parser(
        "archive-eval",
        help="Archive an evaluated live XLSX to the monthly zip in data/processed/.",
    )
    p_arch.add_argument(
        "--xlsx", required=True,
        help="Path to the History Grid (SYMBOL).xlsx to archive.",
    )
    p_arch.set_defaults(func=_cmd_archive_eval)

    # ledger-fill
    p_lfill = subparsers.add_parser(
        "ledger-fill",
        help="Fill realized outcomes for unfilled ledger rows.",
    )
    p_lfill.add_argument(
        "--dry-run", action="store_true",
        help="Log fills but don't write to DB.",
    )
    p_lfill.set_defaults(func=_cmd_ledger_fill)

    # ledger-calibration
    p_lcal = subparsers.add_parser(
        "ledger-calibration",
        help="Generate calibration report (predicted vs realized returns).",
    )
    p_lcal.set_defaults(func=_cmd_ledger_calibration)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, stream=sys.stdout)
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
