"""
FILE: cli_commands/utility.py
VERSION: 1.0
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: cli
DESCRIPTION:
    Read-only diagnostic + ledger command handlers + argparse
    registration -- catalog-summary, integrity-check, inspect-pattern,
    ledger-fill, ledger-calibration. None of these have a pipeline role
    (Pipeline A, B, or bulk) -- they inspect, validate, or report on
    state that already exists. Split out of the former monolithic
    cli.py (WO-P300-E4.001, command-registry refactor) -- pure cut-
    and-paste, no behavior change.

CHANGELOG:
    - 2026-07-20 v1.0 (WO-P300-E4.001): split from cli.py v1.14.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from application.ledger_fill import fill_ledger  # noqa: E402
from utilities.catalog_summary import run_summary  # noqa: E402
from utilities.inspect_pattern import run_inspect  # noqa: E402
from utilities.ledger_calibration import calibrate_ledger  # noqa: E402
from utilities.vp_export_integrity_check import run_integrity_check  # noqa: E402


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


def register(subparsers: argparse._SubParsersAction) -> None:
    """Registers catalog-summary, integrity-check, inspect-pattern,
    ledger-fill, ledger-calibration."""
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

    p_lfill = subparsers.add_parser(
        "ledger-fill",
        help="Fill realized outcomes for unfilled ledger rows.",
    )
    p_lfill.add_argument(
        "--dry-run", action="store_true",
        help="Log fills but don't write to DB.",
    )
    p_lfill.set_defaults(func=_cmd_ledger_fill)

    p_lcal = subparsers.add_parser(
        "ledger-calibration",
        help="Generate calibration report (predicted vs realized returns).",
    )
    p_lcal.set_defaults(func=_cmd_ledger_calibration)
