"""
FILE: cli_commands/main.py
VERSION: 1.1
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: cli
DESCRIPTION:
    Real entry point for the P_300 command-line interface, replacing
    the former monolithic cli.py's build_parser()/main() (WO-P300-
    E4.001, command-registry refactor). `python python\cli.py <command>`
    is UNCHANGED from an operator's perspective -- cli.py is now a thin
    shim importing main() from here (see cli.py's own docstring). No
    .bat file needs editing.

    NOTE 2026-07-28: this docstring previously said cli.py sits "at the
    project root". It does not -- the real path is python\cli.py, as
    confirmed during the WO-P300-E5.005 promote run when a command
    built against the root path failed. Corrected here rather than left
    to mislead the next reader.

    18 commands total, across 6 category modules -- each module owns
    both its handlers and its own subparser registration via
    register(subparsers); this file just loops them:

        pipeline_a    -- add-pattern, archive-pattern
        pipeline_b    -- daily-evaluate, archive-eval
        bulk_research -- bulk-extract, scanner-loop, mine-patterns,
                         phase5-analysis (report-only / research-
                         catalog-only, never touch the live catalog.db)
        bulk_promote  -- merge-research-catalog, ingest-mined,
                         archive-mined (staging-build + explicit
                         promote-to-live commands)
        promote_gate  -- promote-gate (decide-only quality gate; reads
                         two walk-forward reports, never writes a
                         catalog. exit 0=promote / 2=stop / 1=error)
        utility       -- catalog-summary, integrity-check,
                         inspect-pattern, check-pattern, ledger-fill,
                         ledger-calibration

    Run `python cli.py <command> --help` for a given command's full
    argument list; run `python cli.py --help` for the command index.
    Each handler's own docstring (in its category module) carries the
    detailed behavior notes the pre-refactor monolithic file used to
    keep all in one place.

CHANGELOG:
    - 2026-07-28 v1.1 (WO-P300-E5.005): registered promote_gate as a
      6th category module. Command inventory corrected 16 -> 18, NOT
      16 -> 17: the count was already wrong before this WO. `utility`
      owns SIX commands, not five -- `check-pattern` (the pre-export
      duplicate check) was registered at some earlier point and never
      added to this index, so the stated 16 undercounted the real 17.
      Caught only because a live parser count returned 18 against an
      asserted 17. Verified by enumerating add_parser() calls across
      every category module rather than by incrementing the previous
      number -- which is exactly how the original error propagated.
      Also corrected the cli.py path claim in DESCRIPTION -- it is
      python\cli.py, not project root.
    - 2026-07-20 v1.0 (WO-P300-E4.001): replaces cli.py v1.14's
      build_parser()/main(). Command inventory corrected 15 -> 16 --
      the WO's original 2026-07-14 category table never listed
      archive-mined (added to cli.py the same day the WO was filed);
      resolved by placing it in bulk_promote.py, paired with
      ingest-mined (see that module's docstring).
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import LOG_FORMAT, LOG_LEVEL  # noqa: E402

from cli_commands import (  # noqa: E402
    bulk_promote, bulk_research, pipeline_a, pipeline_b, promote_gate,
    utility,
)

CATEGORY_MODULES = [
    pipeline_a, pipeline_b, bulk_research, bulk_promote, promote_gate,
    utility,
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="P_300 command-line entry point.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for mod in CATEGORY_MODULES:
        mod.register(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, stream=sys.stdout)
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
