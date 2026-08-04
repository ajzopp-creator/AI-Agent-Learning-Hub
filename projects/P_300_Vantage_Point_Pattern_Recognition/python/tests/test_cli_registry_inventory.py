"""
FILE: python/tests/test_cli_registry_inventory.py
VERSION: 1.1
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Guards cli_commands/main.py's module-index docstring against
    drifting out of sync with the real command registry.

    WHY THIS EXISTS. That docstring's command count has now been wrong
    TWICE, both times identically: someone incremented the previously
    stated number instead of counting the registry.

      v1.0 (WO-P300-E4.001): stated 15, real 16 -- `archive-mined` was
           registered but never listed.
      v1.1 (WO-P300-E5.005): stated 16, real 17 -- `check-pattern` was
           registered but never listed. Adding promote-gate produced a
           claimed 17 against a real 18, and that only surfaced because
           a live parser count contradicted the assertion.

    A count in a docstring is a CLAIM, not evidence. This file turns it
    into something checkable, so the next occurrence fails loudly at
    test time rather than being discovered by accident two work orders
    later.

    THREE CHECKS, and the third is the one that actually caught the
    real bug: a command can be registered and functional while being
    absent from the index entirely. Counts alone would stay consistent
    if someone updated the number but not the list.

CHANGELOG:
    - 2026-07-29 v1.1: moved from tests/ (project root) to python/tests/,
      same fix and same reason as test_promote_gate.py this same day --
      see that file's changelog for the full root cause.
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial.

RUN (from python/ as cwd, p140 active):
    python tests/test_cli_registry_inventory.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from cli_commands import main as main_module  # noqa: E402

MAIN_PY = _PYTHON_DIR / "cli_commands" / "main.py"


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _registered_commands() -> list[str]:
    parser = main_module.build_parser()
    for action in parser._actions:
        if getattr(action, "choices", None):
            return sorted(action.choices)
    fail("could not locate the subparser action on the built parser")
    return []


def _docstring() -> str:
    doc = main_module.__doc__
    if not doc:
        fail("cli_commands/main.py has no module docstring")
    return doc


def _test_command_count_matches() -> None:
    doc = _docstring()
    m = re.search(r"(\d+)\s+commands total", doc)
    if not m:
        fail("docstring has no 'N commands total' line to check against")
    claimed = int(m.group(1))
    real = len(_registered_commands())
    if claimed != real:
        fail(
            f"docstring claims {claimed} commands, registry has {real}. "
            f"Count the registry -- do NOT increment the stated number."
        )
    ok(f"docstring command count matches registry ({real})")


def _test_module_count_matches() -> None:
    doc = _docstring()
    m = re.search(r"across\s+(\d+)\s+category modules", doc)
    if not m:
        fail("docstring has no 'across N category modules' line")
    claimed = int(m.group(1))
    real = len(main_module.CATEGORY_MODULES)
    if claimed != real:
        fail(f"docstring claims {claimed} category modules, "
             f"CATEGORY_MODULES has {real}")
    ok(f"docstring module count matches CATEGORY_MODULES ({real})")


def _test_every_command_is_listed() -> None:
    """The check that would have caught check-pattern.

    A command can be registered, working, and completely absent from
    the index. Counts stay self-consistent if someone bumps the number
    without adding the name.
    """
    doc = _docstring()
    missing = [c for c in _registered_commands() if c not in doc]
    if missing:
        fail(
            f"registered but absent from the module index: {missing}. "
            f"Add each to its module's line in the docstring."
        )
    ok("every registered command appears in the module index")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== cli_commands/main.py index vs real registry ===")
    _test_command_count_matches()
    _test_module_count_matches()
    _test_every_command_is_listed()

    print(f"\ncommands: {', '.join(_registered_commands())}")
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
