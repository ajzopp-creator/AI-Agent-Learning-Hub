"""
FILE: tests/test_verify_ingestion.py
VERSION: 1.0
DATE: 2026-07-29
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for infrastructure/verify_ingestion.py's
    verify_and_promote() -- the WO-P300-E5.002 / E5.005 completion-gate
    closure item. The success path has been proven in real production
    (2026-07-29 batch, 1222 patterns, see WO-P300-E5.002's confirmation
    note). The FAIL branch had only ever been proven by code inspection
    (M-051/M-054: a docstring is a claim, not evidence) -- this file
    proves it by actually running it.

    Three checks, smallest input that proves each guarantee (not a full
    end-to-end -- that's PEH's job):
      1. A wrong expected_delta must return passed=False AND leave the
         master file completely untouched (mtime unchanged, row counts
         unchanged) -- the core safety property this WO exists to prove.
      2. A hollow pattern_instance (missing forward_labels) must block
         promote even when the per-table delta count is exactly right --
         proves the hollow scan is a real independent check, not
         redundant with the delta check.
      3. Control: clean data + correct deltas must actually promote
         (atomic_move runs, backup preserved). Without this, checks 1-2
         could just mean the function always fails.

    Uses a minimal 8-table sqlite schema covering exactly what
    verify_and_promote() touches (CATALOG_TABLES row counts +
    pattern_instances -> pattern_bars/forward_labels hollow-check JOIN),
    not the real production schema -- same precedent as
    test_add_pattern_collision.py: a full catalog fixture tests nothing
    extra here and costs significantly more setup code. Real files under
    tempfile.TemporaryDirectory() (not :memory:) because atomic_move()
    uses Path.replace(), which needs real paths on the same volume.
    Never touches the real project catalog.

CHANGELOG:
    - 2026-07-29 v1.0: Initial release (WO-P300-E5.002 / E5.005
      completion-gate closure). Test logic verified pre-delivery against
      a verbatim reconstruction of verify_ingestion.py in a sandbox
      (real run, not inspection) -- including a negative control that
      confirmed the test actually fails when the gate is disabled. Not
      yet run against the real file on disk; that run is what closes
      this WO.

RUN:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\P_300_Vantage_Point_Pattern_Recognition\\python\\tests\\test_verify_ingestion.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from infrastructure.catalog_writer import CATALOG_TABLES  # noqa: E402
from infrastructure.verify_ingestion import verify_and_promote  # noqa: E402


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _create_minimal_catalog(path: Path) -> None:
    """Minimal 8-table schema: just enough for _row_counts() (COUNT(*)
    on every CATALOG_TABLES table) and _check_no_hollow_instances()'s
    pattern_instances -> pattern_bars / forward_labels JOIN to work."""
    conn = sqlite3.connect(str(path))
    conn.execute("CREATE TABLE symbols (symbol_id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE source_files (source_file_id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE feature_sets (feature_set_id INTEGER PRIMARY KEY)")
    conn.execute(
        "CREATE TABLE pattern_instances (pattern_instance_id INTEGER PRIMARY KEY)"
    )
    conn.execute(
        "CREATE TABLE pattern_bars ("
        "  pattern_bar_id INTEGER PRIMARY KEY,"
        "  pattern_instance_id INTEGER NOT NULL"
        ")"
    )
    conn.execute(
        "CREATE TABLE pattern_features (pattern_feature_id INTEGER PRIMARY KEY)"
    )
    conn.execute(
        "CREATE TABLE forward_labels ("
        "  forward_label_id INTEGER PRIMARY KEY,"
        "  pattern_instance_id INTEGER NOT NULL"
        ")"
    )
    conn.execute(
        "CREATE TABLE topk_cache ("
        "  topk_id INTEGER PRIMARY KEY,"
        "  pattern_instance_id INTEGER NOT NULL"
        ")"
    )
    conn.commit()
    conn.close()
    assert set(CATALOG_TABLES) == {
        "symbols", "source_files", "feature_sets", "pattern_instances",
        "pattern_bars", "pattern_features", "forward_labels", "topk_cache",
    }, "CATALOG_TABLES changed shape -- update this fixture to match"


def _seed_clean_pattern(path: Path) -> None:
    """pattern_instance id=1 with BOTH a pattern_bars row and a
    forward_labels row -- the non-hollow case."""
    conn = sqlite3.connect(str(path))
    conn.execute("INSERT INTO pattern_instances (pattern_instance_id) VALUES (1)")
    conn.execute(
        "INSERT INTO pattern_bars (pattern_bar_id, pattern_instance_id) VALUES (1, 1)"
    )
    conn.execute(
        "INSERT INTO forward_labels (forward_label_id, pattern_instance_id) "
        "VALUES (1, 1)"
    )
    conn.commit()
    conn.close()


def _seed_hollow_pattern(path: Path) -> None:
    """pattern_instance id=1 with a pattern_bars row but NO
    forward_labels row -- the hollow case _check_no_hollow_instances
    (EC-027/EC-057) exists to catch."""
    conn = sqlite3.connect(str(path))
    conn.execute("INSERT INTO pattern_instances (pattern_instance_id) VALUES (1)")
    conn.execute(
        "INSERT INTO pattern_bars (pattern_bar_id, pattern_instance_id) VALUES (1, 1)"
    )
    conn.commit()
    conn.close()


def _zero_counts() -> dict[str, int]:
    return {t: 0 for t in CATALOG_TABLES}


def _row_count(path: Path, table: str) -> int:
    conn = sqlite3.connect(str(path))
    n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn.close()
    return n


def _test_fail_branch_blocks_on_delta_mismatch() -> None:
    """The core case this WO exists to prove: a WRONG expected_delta
    must return passed=False and must NOT touch master. Real delta here
    is pattern_instances +1; we tell verify_and_promote() to expect +2."""
    with tempfile.TemporaryDirectory() as tmp:
        master_path = Path(tmp) / "master.db"
        temp_path = Path(tmp) / "staging.db"
        _create_minimal_catalog(master_path)
        _create_minimal_catalog(temp_path)
        _seed_clean_pattern(temp_path)

        mtime_before = master_path.stat().st_mtime
        result = verify_and_promote(
            temp_path, master_path, {"pattern_instances": 2}, _zero_counts(),
        )

        if result.passed:
            fail("expected passed=False on a wrong expected_delta, got True")
        if not any(
            "pattern_instances" in m and "expected +2" in m for m in result.failures
        ):
            fail(f"expected a pattern_instances/+2 mismatch message, got {result.failures}")
        if master_path.stat().st_mtime != mtime_before:
            fail("master was modified despite a FAILED verification")
        if not temp_path.exists():
            fail("temp was moved/deleted despite a FAILED verification")
        if result.master_promoted:
            fail("master_promoted True on a FAILED verification")
        ok("delta mismatch -> passed=False, master untouched, temp left in place")


def _test_fail_branch_blocks_on_hollow_pattern_instance() -> None:
    """A pattern_instance missing forward_labels must block promote even
    when the per-table delta count is exactly right -- the delta check
    alone would pass this; only the hollow scan catches it."""
    with tempfile.TemporaryDirectory() as tmp:
        master_path = Path(tmp) / "master.db"
        temp_path = Path(tmp) / "staging.db"
        _create_minimal_catalog(master_path)
        _create_minimal_catalog(temp_path)
        _seed_hollow_pattern(temp_path)

        mtime_before = master_path.stat().st_mtime
        expected_delta = {
            "pattern_instances": 1, "pattern_bars": 1, "forward_labels": 0,
        }
        result = verify_and_promote(temp_path, master_path, expected_delta, _zero_counts())

        if result.passed:
            fail("expected passed=False on a hollow pattern_instance, got True")
        if not any("hollow" in m for m in result.failures):
            fail(f"expected a hollow-record message, got {result.failures}")
        if master_path.stat().st_mtime != mtime_before:
            fail("master was modified despite a FAILED verification")
        if not temp_path.exists():
            fail("temp was moved/deleted despite a FAILED verification")
        ok("hollow pattern_instance -> passed=False even with correct deltas, master untouched")


def _test_pass_branch_promotes_clean_data() -> None:
    """Control: proves checks 1-2 are measuring a real gate, not a
    function that always fails. Clean data + correct deltas must
    actually promote, and the pre-promote master state must survive in
    the .bak backup."""
    with tempfile.TemporaryDirectory() as tmp:
        master_path = Path(tmp) / "master.db"
        temp_path = Path(tmp) / "staging.db"
        _create_minimal_catalog(master_path)
        _create_minimal_catalog(temp_path)
        _seed_clean_pattern(temp_path)

        expected_delta = {
            "pattern_instances": 1, "pattern_bars": 1, "forward_labels": 1,
        }
        result = verify_and_promote(temp_path, master_path, expected_delta, _zero_counts())

        if not result.passed:
            fail(f"expected passed=True on clean data, got failures={result.failures}")
        if not result.master_promoted:
            fail("expected master_promoted=True on a clean pass")
        if temp_path.exists():
            fail("expected temp to be moved away by atomic_move on a clean pass")
        if not master_path.exists():
            fail("expected master to exist after a clean promote")
        if _row_count(master_path, "pattern_instances") != 1:
            fail("expected master's promoted pattern_instances count to be 1")
        if result.backup_path is None or not result.backup_path.exists():
            fail("expected a .bak backup of the pre-promote (empty) master")
        if _row_count(result.backup_path, "pattern_instances") != 0:
            fail("expected the backup to preserve the PRE-promote (empty) state")
        ok("clean data + correct deltas -> passed=True, master promoted, backup preserved")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== verify_and_promote() FAIL branch (WO-P300-E5.002/E5.005 completion gate) ===")
    _test_fail_branch_blocks_on_delta_mismatch()
    _test_fail_branch_blocks_on_hollow_pattern_instance()

    print("\n=== verify_and_promote() PASS branch (control) ===")
    _test_pass_branch_promotes_clean_data()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
