"""
FILE: cli_commands/pipeline_a.py
VERSION: 1.0
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: cli
DESCRIPTION:
    Pipeline A (live-catalog ingest) command handlers + argparse
    registration -- add-pattern, archive-pattern. Split out of the
    former monolithic cli.py (WO-P300-E4.001, command-registry
    refactor) -- pure cut-and-paste, no behavior change. Each category
    module owns both its handlers and its own subparser registration
    via register(subparsers); cli_commands/main.py loops every category
    module calling register(). No .bat file needs editing -- top-level
    `python cli.py <command>` invocation is unchanged (see cli.py's own
    docstring for the shim design).

CHANGELOG:
    - 2026-07-20 v1.0 (WO-P300-E4.001): split from cli.py v1.14 (lines
      ~200-230, ~530-555 of the pre-refactor file). Handler bodies and
      argparse wiring byte-identical to the original -- verified by
      AST-level diff during build, not just visual inspection.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from application.add_pattern_pipeline import ingest_pattern_file  # noqa: E402
from utilities.archive_pattern_file import run_archive as run_archive_pattern  # noqa: E402


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


def register(subparsers: argparse._SubParsersAction) -> None:
    """Registers add-pattern and archive-pattern subcommands."""
    p_add = subparsers.add_parser(
        "add-pattern", help="Ingest one VP Pattern XLSX via Pipeline A."
    )
    p_add.add_argument("--xlsx", required=True, help="Path to Pattern XLSX.")
    p_add.add_argument(
        "--master", default=None,
        help="Catalog master path override; defaults to get_latest_catalog().",
    )
    p_add.set_defaults(func=_cmd_add_pattern)

    p_arch_pat = subparsers.add_parser(
        "archive-pattern",
        help="Archive an ingested Pattern XLSX to the monthly zip in data/processed/.",
    )
    p_arch_pat.add_argument(
        "--xlsx", required=True,
        help="Path to the Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx to archive.",
    )
    p_arch_pat.set_defaults(func=_cmd_archive_pattern)
