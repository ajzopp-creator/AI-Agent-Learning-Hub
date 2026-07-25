"""
FILE: cli.py
VERSION: 2.0
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: cli
DESCRIPTION:
    Thin shim -- preserves `python cli.py <command> [args...]` exactly
    as every existing .bat file's %CLI% variable already invokes it
    (9 .bat files confirmed via project-wide grep, WO-P300-E4.001
    build session -- zero of them need editing). Real implementation
    now lives in the cli_commands/ package (command-registry pattern):

        python/
        |-- cli.py               <- you are here (this file)
        +-- cli_commands/
            |-- main.py           build_parser() + main(), loops
            |                     every category module's register()
            |-- pipeline_a.py     add-pattern, archive-pattern
            |-- pipeline_b.py     daily-evaluate, archive-eval
            |-- bulk_research.py  bulk-extract, scanner-loop,
            |                     mine-patterns, phase5-analysis
            |-- bulk_promote.py   merge-research-catalog, ingest-mined,
            |                     archive-mined
            +-- utility.py        catalog-summary, integrity-check,
                                  inspect-pattern, ledger-fill,
                                  ledger-calibration

    Run `python cli.py --help` for the full command index, or
    `python cli.py <command> --help` for one command's arguments.
    See cli_commands/main.py's docstring for the full 16-command map,
    and each category module's docstring/handler bodies for per-
    command behavior detail (previously all lived in this file's own
    840-line docstring before the split).

    Deliberately named `cli_commands/`, not `cli/` -- a package named
    identically to this shim script in the same directory is a real
    Python import-ambiguity risk (which one does `import cli` resolve
    to when this script is also on sys.path as `cli.py`?), not just a
    style preference. Same principle as the project SKILL's stdlib-
    collision rule (M-018), applied to a self-collision instead.

WHY THIS SHIM EXISTS (WO-P300-E4.001):
    cli.py had grown to 852 lines / 16 subcommands with no natural
    split point in its flat design -- correctly flagged as an
    exception at 637 lines (WO-P300-E3.001), still growing at 821
    (WO-P300-E3.002), Tony's framing (2026-07-14): "building cli
    continually is not the answer." The command-registry pattern
    gives every future new command a category to land in instead of
    this one file growing forever. Pure reorganization -- no handler's
    internal logic changed, no .bat file's invocation syntax changed.

CHANGELOG:
    - 2026-07-20 v2.0 (WO-P300-E4.001): replaced the monolithic
      build_parser()/main() (16 subcommands, 852 lines) with this
      thin shim + the cli_commands/ package. Every handler's body and
      every argparse registration verified byte-identical to the
      pre-refactor version during build (AST-level diff, not just
      visual review -- see WO-P300-E4.001.md BUILD RECORD). Original
      file preserved at cli.py.pre_E4001_backup_2026-07-20 pending
      Tony's PEH confirmation.
    - Pre-v2.0 history (v1.0-v1.14): see cli_commands/main.py's
      changelog reference, or tasks/todo.md's WO-P300-E4.001 entries.
"""
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from cli_commands.main import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
