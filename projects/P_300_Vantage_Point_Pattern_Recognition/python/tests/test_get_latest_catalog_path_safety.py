"""
FILE: python/tests/test_get_latest_catalog_path_safety.py
VERSION: 1.1
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for WO-P300-E4.002 (M-095) -- rebuilt
    2026-07-20 after independent review found this file, like
    tests/test_similarity.py, claimed built (M-095's lessons.md entry:
    "New regression test tests/test_get_latest_catalog_path_safety.py")
    but never actually on disk anywhere in the project.

    Static source-scan, not runtime (M-095's own original design) --
    greps application/catalog_merge_pipeline.py and application/
    ingest_mined_pipeline.py, the two files whose Path(get_latest_
    catalog()) call sites crashed a real production promote and got
    migrated to the new Path-typed get_latest_catalog_path() (WO-P300-
    E4.002). Checks two things per file:
      1. The old str-returning get_latest_catalog is no longer
         imported or called at all in either file (whole-word match,
         so it does NOT false-positive on get_latest_catalog_path) --
         a reversion to either the raw-unwrapped form OR the old
         manually-wrapped Path(get_latest_catalog()) form both fail
         this check, since both disappear once migration is complete.
      2. get_latest_catalog_path is actually present and imported in
         both files -- proves the fix landed, not just that the old
         pattern is coincidentally absent.

    Also confirms utilities/db_utils.py defines get_latest_catalog_path
    with a Path return-type annotation, so a future edit can't silently
    drop the typed contract this WO exists to guarantee.

CHANGELOG:
    - 2026-07-29 v1.1: this file REPLACES the 2026-07-14 original that
      lived at this same path -- that original tested for the M-095
      Path(get_latest_catalog()) wrap pattern, which WO-P300-E4.002
      (this file's own subject) superseded with get_latest_catalog_
      path(). The original was independently confirmed FAILING against
      current code before being retired (ran both versions fresh,
      2026-07-29 -- original 2/4 FAIL, this file 6/6 PASS). Also moved
      from tests/ (project root) to python/tests/ to match the
      python-project-architecture skill's documented convention --
      same root cause as test_promote_gate.py's move the same day.
    - 2026-07-20 v1.0: Rebuilt from scratch (independent-review finding
      during WO-P300-E4.002 -- original claimed file never landed).

RUN (from python/ as cwd, p140 active):
    python tests/test_get_latest_catalog_path_safety.py

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

# Whole-word match on "get_latest_catalog" -- does NOT match
# "get_latest_catalog_path" because "_path" continues the identifier
# with no word boundary directly after "catalog".
_OLD_FUNCTION_PATTERN = re.compile(r"\bget_latest_catalog\b")
_NEW_FUNCTION_PATTERN = re.compile(r"\bget_latest_catalog_path\b")

_MIGRATED_FILES = [
    _PYTHON_DIR / "application" / "catalog_merge_pipeline.py",
    _PYTHON_DIR / "application" / "ingest_mined_pipeline.py",
]

_DB_UTILS_FILE = _PYTHON_DIR / "utilities" / "db_utils.py"


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _code_only(text: str) -> str:
    """Drop docstrings/comments so changelog history of the old name
    does not false-positive as a live import/call regression. Intent
    of this test is 'imported or called' (module docstring), not
    'mentioned in CHANGELOG prose'."""
    text = re.sub(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', "", text)
    text = re.sub(r"#.*", "", text)
    return text


def _test_old_form_absent(path: Path) -> None:
    """Neither the raw-unwrapped nor the manually-Path()-wrapped form
    of get_latest_catalog should remain in a migrated file -- both
    disappear together once the call site uses get_latest_catalog_path
    instead."""
    if not path.exists():
        fail(f"{path} does not exist -- cannot verify migration")
    text = _code_only(path.read_text(encoding="utf-8"))
    matches = _OLD_FUNCTION_PATTERN.findall(text)
    if matches:
        fail(
            f"{path.name} still references get_latest_catalog "
            f"({len(matches)} occurrence(s)) -- migration to "
            f"get_latest_catalog_path() has regressed"
        )
    ok(f"{path.name}: no remaining get_latest_catalog references")


def _test_new_form_present(path: Path) -> None:
    """get_latest_catalog_path must actually be present -- proves the
    fix landed, not just that the old pattern happens to be absent."""
    if not path.exists():
        fail(f"{path} does not exist -- cannot verify migration")
    text = _code_only(path.read_text(encoding="utf-8"))
    matches = _NEW_FUNCTION_PATTERN.findall(text)
    if len(matches) < 2:  # at minimum: one import + one call site
        fail(
            f"{path.name} has only {len(matches)} get_latest_catalog_path "
            f"reference(s) -- expected at least an import and a call site"
        )
    ok(f"{path.name}: get_latest_catalog_path present "
       f"({len(matches)} references)")


def _test_db_utils_defines_typed_sibling() -> None:
    """utilities/db_utils.py must define get_latest_catalog_path with
    a Path return-type annotation -- the typed contract this WO exists
    to guarantee, checked at the source, not just at call sites."""
    if not _DB_UTILS_FILE.exists():
        fail(f"{_DB_UTILS_FILE} does not exist")
    text = _DB_UTILS_FILE.read_text(encoding="utf-8")
    if "def get_latest_catalog_path() -> Path:" not in text:
        fail(
            "db_utils.py does not define "
            "'def get_latest_catalog_path() -> Path:' -- typed contract missing"
        )
    ok("db_utils.py defines get_latest_catalog_path() -> Path")


def _test_db_utils_str_contract_unchanged() -> None:
    """get_latest_catalog()'s own str contract must be untouched --
    this WO is additive, not a breaking change (WO's own OUT OF SCOPE)."""
    text = _DB_UTILS_FILE.read_text(encoding="utf-8")
    if "def get_latest_catalog():" not in text:
        fail("db_utils.py's original get_latest_catalog() signature changed")
    if "return str(catalog_files[0])" not in text:
        fail("db_utils.py's get_latest_catalog() no longer returns str")
    ok("db_utils.py: get_latest_catalog()'s original str contract intact")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== db_utils.py contract checks ===")
    _test_db_utils_defines_typed_sibling()
    _test_db_utils_str_contract_unchanged()

    print("\n=== migrated call sites: old form absent ===")
    for path in _MIGRATED_FILES:
        _test_old_form_absent(path)

    print("\n=== migrated call sites: new form present ===")
    for path in _MIGRATED_FILES:
        _test_new_form_present(path)

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
