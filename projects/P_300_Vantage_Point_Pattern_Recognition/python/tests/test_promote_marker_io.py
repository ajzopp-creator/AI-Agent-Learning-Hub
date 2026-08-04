"""
FILE: python/tests/test_promote_marker_io.py
VERSION: 1.1
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for WO-P300-E5.005's marker file,
    infrastructure/promote_marker_io.py.

    THIS COVERS THE ENTIRE STOP PATH. Auto-promote handles the clean
    case, which is most runs. The marker is the whole of what happens
    when the gate BLOCKS a batch -- and a blocked batch is exactly the
    situation this WO exists for. If the marker silently fails to
    write, a stopped batch goes unannounced, INIT Step 0.6 shows
    nothing, and the next ingest-mined run destroys it. That is the
    2026-07-25 failure reproduced, with more machinery in between to
    obscure it.

    Verdicts are built by running the REAL evaluate_promote_gate rather
    than hand-constructing PromoteGateVerdict objects, so these tests
    exercise the actual integration between the domain layer and this
    one. A hand-built verdict could drift from what the gate really
    emits and the tests would never notice.

    THE MOST IMPORTANT CHECK is _test_malformed_marker_raises. None
    means "no problem outstanding". A corrupt file must never be able
    to impersonate that, because the failure would be silent and would
    disarm the mechanism precisely when it is needed.

CHANGELOG:
    - 2026-07-29 v1.1: moved from tests/ (project root) to python/tests/,
      same fix and same reason as test_promote_gate.py this same day --
      see that file's changelog for the full root cause.
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial.

RUN (from python/ as cwd, p140 active):
    python tests/test_promote_marker_io.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from domain.promote_gate import evaluate_promote_gate  # noqa: E402
from infrastructure.promote_marker_io import (  # noqa: E402
    MARKER_FILENAME, build_marker, clear_marker, marker_path, read_marker,
    write_marker,
)
from schemas_promote_gate import WalkForwardMetrics  # noqa: E402

STAGING_DB = r"C:\fake\models\staging_ingest_mined.db"


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _m(buy_pct: float, buy_n: int, pass_pct: float, pass_n: int,
       corpus: int) -> WalkForwardMetrics:
    return WalkForwardMetrics(
        source_path=f"/synthetic/{corpus}.txt",
        source_mtime=datetime(2026, 7, 28, 6, 0, 0),
        total_rows=corpus * 5, chosen_rows=corpus, corpus_size=corpus,
        buy_n=buy_n, buy_correct=int(round(buy_pct / 100 * buy_n)),
        buy_precision_pct=buy_pct,
        pass_n=pass_n, pass_correct=int(round(pass_pct / 100 * pass_n)),
        pass_accuracy_pct=pass_pct,
        watch_n=100,
    )


def _verdict_clean():
    return evaluate_promote_gate(
        _m(69.11, 6983, 61.29, 6593, 16801),
        _m(69.05, 9260, 62.63, 7741, 21247),
    )


def _verdict_stop():
    return evaluate_promote_gate(
        _m(69.0, 5000, 61.0, 5000, 16801),
        _m(60.0, 6000, 61.0, 6000, 21247),
    )


def _verdict_waived():
    return evaluate_promote_gate(
        _m(69.0, 5000, 61.0, 5000, 16801),
        _m(49.0, 120, 41.0, 120, 21247),
    )


def _test_clean_pass_builds_no_marker() -> None:
    """Surfacing every successful run would train the operator to skim
    past Step 0.6, costing the one time it matters."""
    if build_marker(_verdict_clean(), STAGING_DB) is not None:
        fail("a clean PROMOTE must build NO marker")
    ok("clean PROMOTE -> no marker built")


def _test_stop_builds_stop_marker() -> None:
    m = build_marker(_verdict_stop(), STAGING_DB)
    if m is None:
        fail("a STOP verdict must build a marker")
    if m.severity != "STOP":
        fail(f"expected severity STOP, got {m.severity}")
    if m.staging_db_path != STAGING_DB:
        fail("marker must record the staging DB at risk")
    if "destroyed" not in m.next_action.lower():
        fail("STOP next_action must warn the batch will be destroyed")
    ok("STOP verdict -> STOP marker naming the at-risk staging DB")


def _test_waived_builds_waived_marker() -> None:
    m = build_marker(_verdict_waived(), STAGING_DB)
    if m is None:
        fail("a waived PROMOTE must build a marker")
    if m.severity != "WAIVED":
        fail(f"expected severity WAIVED, got {m.severity}")
    if m.decision != "PROMOTE":
        fail("a waived verdict still PROMOTED -- decision must say so")
    if not m.small_n_waived:
        fail("waived marker must carry small_n_waived=True")
    ok("waived PROMOTE -> WAIVED marker, decision still PROMOTE")


def _test_severities_differ_in_guidance() -> None:
    """STOP is action-required; WAIVED is informational. If the two
    read the same, Step 0.6 cannot tell the operator what to do."""
    stop = build_marker(_verdict_stop(), STAGING_DB)
    waived = build_marker(_verdict_waived(), STAGING_DB)
    if stop.next_action == waived.next_action:
        fail("STOP and WAIVED must give different guidance")
    if "no action" not in waived.next_action.lower():
        fail("WAIVED guidance should state no action is required")
    ok("STOP and WAIVED carry distinct next_action guidance")


def _test_write_read_roundtrip(root: Path) -> None:
    original = build_marker(_verdict_stop(), STAGING_DB)
    path = write_marker(root, original)
    if path.name != MARKER_FILENAME:
        fail(f"marker written to unexpected name: {path.name}")
    if not path.exists():
        fail("write_marker did not create the file")
    back = read_marker(root)
    if back is None:
        fail("read_marker returned None for a marker just written")
    if back.severity != original.severity:
        fail("severity did not survive the round trip")
    if abs(back.buy_delta_pp - original.buy_delta_pp) > 1e-9:
        fail("buy_delta_pp did not survive the round trip")
    if back.reasons != original.reasons:
        fail("reasons did not survive the round trip")
    ok("write -> read round-trips severity, deltas, and reasons")


def _test_no_temp_file_left(root: Path) -> None:
    """Atomic write uses a .tmp then os.replace. A leftover .tmp would
    mean the replace never happened."""
    leftovers = list(root.glob("*.tmp"))
    if leftovers:
        fail(f"atomic write left temp file(s) behind: {leftovers}")
    ok("atomic write leaves no .tmp behind")


def _test_absent_marker_reads_none(root: Path) -> None:
    empty = root / "empty_root"
    empty.mkdir()
    if read_marker(empty) is not None:
        fail("read_marker must return None when no marker exists")
    ok("absent marker -> None (no problem outstanding)")


def _test_malformed_marker_raises(root: Path) -> None:
    """The single most important check in this file.

    None means 'no problem outstanding'. If a corrupt marker returned
    None instead of raising, the mechanism would disarm itself silently
    at exactly the moment it is needed.
    """
    bad_root = root / "bad_root"
    bad_root.mkdir()
    marker_path(bad_root).write_text("{ this is not json", encoding="utf-8")
    try:
        read_marker(bad_root)
    except Exception as exc:  # noqa: BLE001
        ok(f"unparseable marker -> raised {type(exc).__name__}, not None")
        return
    fail("unparseable marker returned instead of raising -- "
         "a corrupt file must NEVER read as 'no problem'")


def _test_valid_json_wrong_schema_raises(root: Path) -> None:
    wrong = root / "wrong_root"
    wrong.mkdir()
    marker_path(wrong).write_text('{"hello": "world"}', encoding="utf-8")
    try:
        read_marker(wrong)
    except Exception as exc:  # noqa: BLE001
        ok(f"valid JSON / wrong schema -> raised {type(exc).__name__}")
        return
    fail("valid JSON with the wrong shape must raise, not return")


def _test_clear_marker(root: Path) -> None:
    if not marker_path(root).exists():
        fail("precondition: expected a marker from the round-trip test")
    if clear_marker(root) is not True:
        fail("clear_marker must return True when a marker was present")
    if marker_path(root).exists():
        fail("clear_marker did not remove the file")
    if clear_marker(root) is not False:
        fail("clear_marker must return False when nothing was present")
    ok("clear_marker removes the file; True then False on repeat")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        print("\n=== build_marker: which verdicts produce a marker ===")
        _test_clean_pass_builds_no_marker()
        _test_stop_builds_stop_marker()
        _test_waived_builds_waived_marker()
        _test_severities_differ_in_guidance()

        print("\n=== write / read / clear ===")
        _test_write_read_roundtrip(root)
        _test_no_temp_file_left(root)
        _test_absent_marker_reads_none(root)
        _test_clear_marker(root)

        print("\n=== a corrupt marker must never read as 'no problem' ===")
        _test_malformed_marker_raises(root)
        _test_valid_json_wrong_schema_raises(root)

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
