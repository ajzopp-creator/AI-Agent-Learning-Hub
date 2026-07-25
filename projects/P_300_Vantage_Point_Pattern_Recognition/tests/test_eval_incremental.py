"""
FILE: tests/test_eval_incremental.py
VERSION: 1.2
DATE: 2026-07-18
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for WO-P300-E4.004 (v1.2). Proves the
    min-new-date partition matches a full run_walk_forward() re-score
    for same-day and mixed-date new-pattern mixes; the guardrail fires
    only on a true internal-invariant break and the application layer
    falls back cleanly; compute_reuse_fraction() reports the correct
    fraction; and a reuse fraction below config.INCREMENTAL_MIN_REUSE_
    FRACTION skips the incremental path entirely (verified by poisoning
    assemble_incremental_post_batch to fail loudly if called).

    Synthetic fixture only, matches tests/test_eval_scoring.py's
    convention -- run directly via PEH, not pytest.

CHANGELOG:
    - 2026-07-18 v1.2: Added _test_compute_reuse_fraction() and
      _test_low_reuse_skips_incremental() for the "worth it" threshold
      (config.INCREMENTAL_MIN_REUSE_FRACTION, incremental_post_batch v1.2).
    - 2026-07-17 v1.1 (M-100): replaced the v1.0 backdated-insert
      guardrail test (now a VALID case, not a trigger) with
      _test_mixed_dates_matches_full_rescore(); guardrail + fallback
      tests repurposed to a genuine internal-invariant break.
    - 2026-07-17 v1.0: WO-P300-E4.004. Initial release.

RUN (from project root, p140 active):
    python tests/test_eval_incremental.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent / "python"
sys.path.insert(0, str(_PYTHON_DIR))

import application.incremental_post_batch as incremental_post_batch_module  # noqa: E402
from application.incremental_post_batch import run_incremental_post_batch  # noqa: E402
from domain.eval_incremental import (  # noqa: E402
    IncrementalGuardrailError, assemble_incremental_post_batch,
    compute_reuse_fraction,
)
from domain.eval_scoring import run_walk_forward  # noqa: E402
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from schemas_eval import WalkForwardBatch  # noqa: E402
from schemas_pipeline_b import ForwardLabelLite, NormalizedBar  # noqa: E402


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _bar(close_pct: float) -> NormalizedBar:
    return NormalizedBar(
        bar_offset=0, bar_date=date(2026, 1, 1),
        open=100.0, high=101.0, low=99.0, close=100.0, volume=1_000_000,
        stdiff=0.1, mtdiff=0.2, ltdiff=0.3,
        pred_high=102.0, pred_low=98.0, pred_range=4.0,
        williams_emai=-20.0, psi=60.0, neural_index=1.0,
        triple_cross_short=1.0, triple_cross_medium=1.0, triple_cross_long=1.0,
        close_pct_from_anchor=close_pct, range_pct=0.02, body_pct=0.01,
        volume_zscore=0.0, stdiff_pct=0.001, mtdiff_pct=0.002,
        ltdiff_pct=0.003, pred_high_pct=0.02, pred_low_pct=-0.02,
        pred_range_pct=0.04,
    )


def _make_patterns_at(dates: list[date], start_pid: int):
    """One synthetic pattern per given date -- arbitrary anchor_date mix."""
    metadata: dict[int, PatternMetadata] = {}
    windows: dict[int, list[NormalizedBar]] = {}
    labels: dict[int, dict[int, ForwardLabelLite]] = {}
    for i, d in enumerate(dates):
        pid = start_pid + i
        metadata[pid] = PatternMetadata(
            pattern_instance_id=pid, ticker="TEST", anchor_date=d, window_length=1,
        )
        windows[pid] = [_bar(close_pct=0.01 * pid)]
        profitable = pid % 2 == 0
        labels[pid] = {
            h: ForwardLabelLite(
                return_pct=0.03 if profitable else -0.02, is_profitable=profitable,
            )
            for h in (5, 7, 10, 15, 20)
        }
    return metadata, windows, labels


def _make_patterns(n: int, start: date, start_pid: int = 1):
    """n synthetic patterns from start date, one per day."""
    return _make_patterns_at([start + timedelta(days=i) for i in range(n)], start_pid)


def _merge(existing, new_):
    meta = {**existing[0], **new_[0]}
    win = {**existing[1], **new_[1]}
    lab = {**existing[2], **new_[2]}
    return meta, win, lab


def _test_incremental_matches_full_rescore() -> None:
    """Happy path: all new patterns dated after every existing pattern."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)
    new = _make_patterns(3, date(2026, 2, 1), start_pid=101)
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())

    pre_batch = run_walk_forward("fixture", *existing)
    full_rescore = run_walk_forward("fixture", full_meta, full_win, full_lab)
    incremental = assemble_incremental_post_batch(
        "fixture", full_meta, full_win, full_lab, new_pids, pre_batch,
    )

    if incremental.model_dump_json() == full_rescore.model_dump_json():
        ok(f"incremental batch matches full re-score byte-for-byte "
           f"({incremental.n_patterns} patterns, {len(new_pids)} new)")
    else:
        fail("incremental batch diverged from full re-score")


def _test_mixed_dates_matches_full_rescore() -> None:
    """M-100's real case: new pattern dates interleaved before/among/
    after existing patterns -- must still match a full re-score exactly."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)  # 01-01..01-10
    new = _make_patterns_at(
        [date(2026, 1, 5), date(2026, 1, 8), date(2026, 2, 1)], start_pid=101,
    )
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())

    pre_batch = run_walk_forward("fixture", *existing)
    full_rescore = run_walk_forward("fixture", full_meta, full_win, full_lab)
    incremental = assemble_incremental_post_batch(
        "fixture", full_meta, full_win, full_lab, new_pids, pre_batch,
    )

    min_new_date = date(2026, 1, 5)
    n_safe = sum(1 for m in existing[0].values() if m.anchor_date <= min_new_date)
    if incremental.model_dump_json() == full_rescore.model_dump_json():
        ok(f"mixed-date incremental batch matches full re-score byte-for-"
           f"byte ({n_safe}/10 existing pids safely reused, not same-day)")
    else:
        fail("mixed-date incremental batch diverged from full re-score")


def _test_compute_reuse_fraction() -> None:
    """compute_reuse_fraction() must match the partition's own safe-pid
    count, without scoring anything -- same mixed-dates fixture (5/10)."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)
    new = _make_patterns_at(
        [date(2026, 1, 5), date(2026, 1, 8), date(2026, 2, 1)], start_pid=101,
    )
    full_meta, _, _ = _merge(existing, new)
    new_pids = set(new[0].keys())

    fraction = compute_reuse_fraction(full_meta, new_pids)
    if fraction == 0.5:
        ok(f"compute_reuse_fraction reports {fraction:.1%} (5/10 existing "
           f"pids safe), matches the partition used above")
    else:
        fail(f"compute_reuse_fraction reported {fraction!r}, expected 0.5")


def _test_low_reuse_skips_incremental() -> None:
    """Below config.INCREMENTAL_MIN_REUSE_FRACTION, run_incremental_
    post_batch() must skip assemble_incremental_post_batch() ENTIRELY,
    proven by poisoning the module-level reference so any call fails."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)
    # New pid dated well before all existing -> 0/10 safe -> reuse 0.0.
    new = _make_patterns_at([date(2020, 1, 1)], start_pid=101)
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())

    pre_batch = run_walk_forward("fixture", *existing)
    full_rescore = run_walk_forward("fixture", full_meta, full_win, full_lab)

    original = incremental_post_batch_module.assemble_incremental_post_batch

    def _poison(*_args, **_kwargs):
        fail("assemble_incremental_post_batch called despite 0.0 reuse")

    incremental_post_batch_module.assemble_incremental_post_batch = _poison
    try:
        result = run_incremental_post_batch(
            "fixture", full_meta, full_win, full_lab, new_pids, pre_batch,
        )
    finally:
        incremental_post_batch_module.assemble_incremental_post_batch = original

    if result.model_dump_json() == full_rescore.model_dump_json():
        ok("0.0 reuse fraction skips the incremental path entirely, "
           "result matches a full re-score")
    else:
        fail("low-reuse skip-path result diverged from a full re-score")


def _test_internal_invariant_guardrail() -> None:
    """A genuine internal-invariant break: pre_batch is missing a pid
    this module determined was safe to reuse -- must raise, not drop it."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)
    new = _make_patterns(3, date(2026, 2, 1), start_pid=101)
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())

    real_pre_batch = run_walk_forward("fixture", *existing)
    truncated_results = [r for r in real_pre_batch.results if r.pattern_instance_id != 1]
    broken_pre_batch = WalkForwardBatch(
        catalog_path="fixture", n_patterns=len(truncated_results),
        n_degenerate=real_pre_batch.n_degenerate,
        threshold_overrides=None, results=truncated_results,
    )

    try:
        assemble_incremental_post_batch(
            "fixture", full_meta, full_win, full_lab, new_pids, broken_pre_batch,
        )
        fail("guardrail did not fire on a pre_batch missing a safe pid")
    except IncrementalGuardrailError:
        ok("guardrail correctly raises when pre_batch is missing a safe pid")


def _test_application_layer_falls_back() -> None:
    """run_incremental_post_batch() must never raise -- on the internal-
    invariant guardrail it falls back to a full re-score and returns it.
    Same-day fixture (100% reuse) so the threshold doesn't intercept first."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)
    new = _make_patterns(3, date(2026, 2, 1), start_pid=101)
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())

    real_pre_batch = run_walk_forward("fixture", *existing)
    truncated_results = [r for r in real_pre_batch.results if r.pattern_instance_id != 1]
    broken_pre_batch = WalkForwardBatch(
        catalog_path="fixture", n_patterns=len(truncated_results),
        n_degenerate=real_pre_batch.n_degenerate,
        threshold_overrides=None, results=truncated_results,
    )
    full_rescore = run_walk_forward("fixture", full_meta, full_win, full_lab)

    result = run_incremental_post_batch(
        "fixture", full_meta, full_win, full_lab, new_pids, broken_pre_batch,
    )
    if result.model_dump_json() == full_rescore.model_dump_json():
        ok("application-layer fallback returns a correct full re-score, "
           "no exception raised")
    else:
        fail("application-layer fallback result diverged from a full re-score")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== WO-P300-E4.004 -- incremental matches full re-score (same-day) ===")
    _test_incremental_matches_full_rescore()

    print("\n=== M-100 -- incremental matches full re-score (mixed dates) ===")
    _test_mixed_dates_matches_full_rescore()

    print("\n=== WO-P300-E4.004 v1.2 -- compute_reuse_fraction correctness ===")
    _test_compute_reuse_fraction()

    print("\n=== WO-P300-E4.004 v1.2 -- low reuse fraction skips incremental path ===")
    _test_low_reuse_skips_incremental()

    print("\n=== WO-P300-E4.004 -- guardrail fires on internal invariant break ===")
    _test_internal_invariant_guardrail()

    print("\n=== WO-P300-E4.004 -- application-layer fallback ===")
    _test_application_layer_falls_back()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
