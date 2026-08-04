"""
FILE: python/tests/test_walkforward_report_io.py
VERSION: 1.1
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for WO-P300-E5.005's report parser,
    infrastructure/walkforward_report_io.py.

    Covers the happy path plus every one of the parser's five raise
    paths, and both failure modes of find_report_pair(). The raise
    paths are the point of this file: the parser's entire design bias
    is fail-loud-never-default, because a parse that silently
    under-counts a class shrinks its denominator, inflates that class's
    accuracy, and makes the auto-promote gate PASS a batch it should
    have STOPPED. Each of those tests asserts an exception is raised --
    a test that only checked the happy path would let every one of them
    regress to a silent default without failing.

    Two tests are cross-checks rather than format validation:
    _test_class_value_mismatch_raises (a BUY row carrying PASS's
    correctness value) and _test_unexpected_signal_class_raises (a
    fourth class appearing). Both would otherwise pass unnoticed while
    corrupting the totals.

    Synthetic fixtures only -- temp-dir TSVs, no real catalog and no
    real report dependency. Matches the project's existing self-running
    test convention (tests/test_*.py run directly), not pytest.

CHANGELOG:
    - 2026-07-29 v1.1: moved from tests/ (project root) to python/tests/,
      same fix and same reason as test_promote_gate.py this same day --
      see that file's changelog for the full root cause.
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial.

RUN (from python/ as cwd, p140 active):
    python tests/test_walkforward_report_io.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from infrastructure.walkforward_report_io import (  # noqa: E402
    find_report_pair, parse_walkforward_report,
)

COLUMNS = [
    "pattern_instance_id", "symbol", "anchor_date", "corpus_size",
    "final_signal_class", "horizon_days", "is_chosen_horizon", "correctness",
]


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _row(pid, cls, chosen, correctness, corpus=100):
    return [str(pid), "TEST", "2026-01-02", str(corpus), cls,
            "5", "True" if chosen else "False", correctness]


def _write_tsv(path: Path, rows: list[list[str]], columns=None) -> Path:
    cols = columns if columns is not None else COLUMNS
    lines = ["\t".join(cols)] + ["\t".join(r) for r in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _good_rows() -> list[list[str]]:
    """3 BUY (2 correct), 2 PASS (1 correct), 1 WATCH, 4 non-chosen.

    Expected: buy 2/3 = 66.67%, pass 1/2 = 50.00%, watch_n=1,
    chosen=6, total=10.
    """
    return [
        _row(1, "BUY", True, "correct_buy"),
        _row(2, "BUY", True, "correct_buy"),
        _row(3, "BUY", True, "false_positive"),
        _row(4, "PASS", True, "correct_pass"),
        _row(5, "PASS", True, "missed"),
        _row(6, "WATCH", True, "neutral"),
        _row(1, "BUY", False, ""),
        _row(2, "BUY", False, ""),
        _row(4, "PASS", False, ""),
        _row(6, "WATCH", False, ""),
    ]


def _expect_raise(fn, label: str) -> None:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        ok(f"{label} -> raised {type(exc).__name__}")
        return
    fail(f"{label} -> NO exception raised (silent default is the bug)")


def _test_happy_path(tmp: Path) -> None:
    m = parse_walkforward_report(_write_tsv(tmp / "good.txt", _good_rows()))
    checks = [
        ("total_rows", m.total_rows, 10), ("chosen_rows", m.chosen_rows, 6),
        ("buy_n", m.buy_n, 3), ("buy_correct", m.buy_correct, 2),
        ("pass_n", m.pass_n, 2), ("pass_correct", m.pass_correct, 1),
        ("watch_n", m.watch_n, 1), ("corpus_size", m.corpus_size, 100),
    ]
    for name, got, want in checks:
        if got != want:
            fail(f"{name}: expected {want}, got {got}")
    if abs(m.buy_precision_pct - 66.6667) > 0.01:
        fail(f"buy_precision_pct: expected ~66.67, got {m.buy_precision_pct}")
    if abs(m.pass_accuracy_pct - 50.0) > 0.01:
        fail(f"pass_accuracy_pct: expected 50.00, got {m.pass_accuracy_pct}")
    ok("happy path -> all counts and percentages correct")


def _test_watch_has_no_accuracy_field() -> None:
    """WATCH is ungraded by design. If someone later adds a
    watch_accuracy_pct field, the startswith() bug that produced a
    permanent 0.00% becomes representable again."""
    from schemas_promote_gate import WalkForwardMetrics
    bad = [f for f in WalkForwardMetrics.model_fields
           if "watch" in f and f != "watch_n"]
    if bad:
        fail(f"WATCH must carry a count only; found extra field(s): {bad}")
    ok("WalkForwardMetrics exposes watch_n only -- no WATCH accuracy field")


def _test_missing_column_raises(tmp: Path) -> None:
    cols = [c for c in COLUMNS if c != "correctness"]
    rows = [r[:-1] for r in _good_rows()]
    p = _write_tsv(tmp / "missing_col.txt", rows, columns=cols)
    _expect_raise(lambda: parse_walkforward_report(p), "missing 'correctness'")


def _test_zero_chosen_rows_raises(tmp: Path) -> None:
    rows = [_row(1, "BUY", False, ""), _row(2, "PASS", False, "")]
    p = _write_tsv(tmp / "no_chosen.txt", rows)
    _expect_raise(lambda: parse_walkforward_report(p), "zero chosen rows")


def _test_unknown_correctness_raises(tmp: Path) -> None:
    rows = _good_rows() + [_row(7, "BUY", True, "wildly_unexpected")]
    p = _write_tsv(tmp / "unknown_val.txt", rows)
    _expect_raise(lambda: parse_walkforward_report(p),
                  "unknown correctness value")


def _test_class_value_mismatch_raises(tmp: Path) -> None:
    """A BUY row carrying PASS's correctness value. Every value is in
    the known enum, so the enum check passes -- only _tally's
    correct+incorrect==n cross-check catches this."""
    rows = _good_rows() + [_row(7, "BUY", True, "correct_pass")]
    p = _write_tsv(tmp / "mismatch.txt", rows)
    _expect_raise(lambda: parse_walkforward_report(p),
                  "BUY row carrying PASS's correctness value")


def _test_unexpected_signal_class_raises(tmp: Path) -> None:
    """A fourth signal class. Counted in no class total, so it would
    vanish silently without the BUY+PASS+WATCH==chosen assertion."""
    rows = _good_rows() + [_row(7, "HOLD", True, "neutral")]
    p = _write_tsv(tmp / "fourth_class.txt", rows)
    _expect_raise(lambda: parse_walkforward_report(p),
                  "unexpected signal class 'HOLD'")


def _test_missing_file_raises(tmp: Path) -> None:
    _expect_raise(lambda: parse_walkforward_report(tmp / "nope.txt"),
                  "nonexistent report path")


def _test_find_pair_happy(tmp: Path) -> None:
    d = tmp / "eval_ok"
    d.mkdir()
    _write_tsv(d / "walkforward_072826catalog_default_20260728_0627.txt",
               _good_rows())
    _write_tsv(d / "walkforward_staging_ingest_mined_default_20260728_0758.txt",
               _good_rows())
    baseline, staging = find_report_pair(d)
    if "staging" not in staging.name or "catalog" not in baseline.name:
        fail(f"pair misidentified: baseline={baseline.name} staging={staging.name}")
    ok("find_report_pair -> correctly identifies baseline vs staging")


def _test_find_pair_stale_raises(tmp: Path) -> None:
    """The real 2026-07-28 hazard: the baseline report was byte-identical
    to 2026-07-25's because no promote landed between them. A failed
    baseline run would leave a days-old file that newest-match globbing
    pairs up silently."""
    d = tmp / "eval_stale"
    d.mkdir()
    old = _write_tsv(d / "walkforward_072826catalog_default_20260725_1617.txt",
                     _good_rows())
    _write_tsv(d / "walkforward_staging_ingest_mined_default_20260728_0758.txt",
               _good_rows())
    three_days = time.time() - (3 * 24 * 3600)
    os.utime(old, (three_days, three_days))
    _expect_raise(lambda: find_report_pair(d), "baseline 3 days older")


def _test_find_pair_missing_staging_raises(tmp: Path) -> None:
    d = tmp / "eval_nostaging"
    d.mkdir()
    _write_tsv(d / "walkforward_072826catalog_default_20260728_0627.txt",
               _good_rows())
    _expect_raise(lambda: find_report_pair(d), "no staging report present")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        print("\n=== parse_walkforward_report: happy path ===")
        _test_happy_path(tmp)
        _test_watch_has_no_accuracy_field()

        print("\n=== parse_walkforward_report: fail-loud paths ===")
        _test_missing_column_raises(tmp)
        _test_zero_chosen_rows_raises(tmp)
        _test_unknown_correctness_raises(tmp)
        _test_class_value_mismatch_raises(tmp)
        _test_unexpected_signal_class_raises(tmp)
        _test_missing_file_raises(tmp)

        print("\n=== find_report_pair ===")
        _test_find_pair_happy(tmp)
        _test_find_pair_stale_raises(tmp)
        _test_find_pair_missing_staging_raises(tmp)

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
