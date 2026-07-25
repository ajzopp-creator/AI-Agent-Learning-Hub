"""
FILE: cli_commands/pipeline_b.py
VERSION: 1.0
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: cli
DESCRIPTION:
    Pipeline B (live-catalog evaluation) command handlers + argparse
    registration -- daily-evaluate, archive-eval. Split out of the
    former monolithic cli.py (WO-P300-E4.001, command-registry
    refactor) -- pure cut-and-paste, no behavior change.

CHANGELOG:
    - 2026-07-20 v1.0 (WO-P300-E4.001): split from cli.py v1.14.
      NARRATOR_ENABLED import dropped -- grepped the original file and
      confirmed it was imported but never referenced anywhere in the
      code body (only mentioned in docstring prose); genuinely dead,
      not a behavior change to remove it.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from config import TOP_K_MATCHES  # noqa: E402
from utilities.archive_live_file import run_archive  # noqa: E402


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


def register(subparsers: argparse._SubParsersAction) -> None:
    """Registers daily-evaluate and archive-eval subcommands."""
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

    p_arch = subparsers.add_parser(
        "archive-eval",
        help="Archive an evaluated live XLSX to the monthly zip in data/processed/.",
    )
    p_arch.add_argument(
        "--xlsx", required=True,
        help="Path to the History Grid (SYMBOL).xlsx to archive.",
    )
    p_arch.set_defaults(func=_cmd_archive_eval)
