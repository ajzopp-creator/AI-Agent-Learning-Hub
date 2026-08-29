"""
FILE: tests/test_eval_incremental.py
VERSION: 2.0
DATE: 2026-08-17
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for domain/eval_incremental.py's
    run_cached_post_batch() -- the WO-P300-E5.008 rewrite, replacing
    v1.2's coverage of assemble_incremental_post_batch() /
    compute_reuse_fraction() / the reuse-fraction gate, all three
    removed outright by WO-P300-E4.006 v2.0 (decision #9): the cached
    top-K path is unconditional now, there is no "worth it" decision
    left to test.

    Domain layer only (no I/O, no application import) -- proves
    run_cached_post_batch() correctly ASSEMBLES a WalkForwardBatch from
    safe pids (reused verbatim from pre_batch) + must_check pids (fresh
    via the cached top-K path), and that IncrementalGuardrailError still
    fires on the same internal-invariant break. domain/topk_cache.py's
    OWN cache-admission correctness (_displace, update_for_new_batch's
    must-check completeness) is covered by tests/test_topk_cache.py
    already -- not re-proven here.

    IMPORTANT -- existing_cache is not optional-safe (found while
    scoping this WO): domain/topk_cache.py's _compute_existing_recheck_
    topk only displacement-checks a must_check pid's EXISTING cache
    entry against the new candidates; it never re-scans that pid's full
    prior corpus. An empty {} is only valid when no existing pid is
    must_check (this file's first test). The mixed-date test seeds
    existing_cache via the real topk_cache.seed_full_catalog() over the
    existing-only corpus -- the same production code migrations/
    stage_4a_add_topk_cache.py uses -- or the "matches full re-score"
    assertion would legitimately fail.

    Synthetic fixture only, matches tests/test_eval_scoring.py's
    convention -- run directly via PEH, not pytest.

CHANGELOG:
    - 2026-08-17 v2.0 (WO-P300-E5.008): Rewritten for WO-P300-E4.006's
      v2.0 contract. Removed coverage of assemble_incremental_post_
      batch() / compute_reuse_fraction() / the reuse-fraction gate
      (all three deleted outright, decision #9 -- nothing to test).
      Removed the application-layer fallback test -- v2.0 propagates
      IncrementalGuardrailError uncaught instead of falling back; that
      behavior now lives in tests/test_incremental_post_batch.py
      alongside the real-DB fixture the application layer needs.
      Mixed-date test now seeds existing_cache for real instead of
      relying on {} (see IMPORTANT above -- {} silently produces an
      incomplete top-K for must_check pids, not an error).
    - 2026-07-18 v1.2: Added _test_compute_reuse_fraction() and
      _test_low_reuse_skips_incremental() (both removed above).
    - 2026-07-17 v1.1 (M-100): replaced the v1.0 backdated-insert
      guardrail test with _test_mixed_dates_matches_full_rescore().
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
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from domain.eval_incremental import (  # noqa: E402
    IncrementalGuardrailError, run_cached_post_batch,
)
from domain.eval_scoring import run_walk_forward  # noqa: E402
from domain.topk_cache import seed_full_catalog  # noqa: E402
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


def _test_new_pids_only_matches_full_rescore() -> None:
    """Happy path: all new patterns dated after every existing pattern
    -- no existing pid falls into must_check, so existing_cache is
    never consulted and {} is valid here (unlike the test below)."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)
    new = _make_patterns(3, date(2026, 2, 1), start_pid=101)
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())

    pre_batch = run_walk_forward("fixture", *existing)
    full_rescore = run_walk_forward("fixture", full_meta, full_win, full_lab)
    incremental, _new_topk, _existing_topk = run_cached_post_batch(
        "fixture", full_meta, full_win, full_lab, new_pids, pre_batch,
        existing_cache={},
    )

    if incremental.model_dump_json() == full_rescore.model_dump_json():
        ok(f"incremental batch matches full re-score byte-for-byte "
           f"({incremental.n_patterns} patterns, {len(new_pids)} new, "
           f"existing_cache={{}} valid -- no existing pid is must_check)")
    else:
        fail("incremental batch diverged from full re-score")


def _test_mixed_dates_matches_full_rescore() -> None:
    """M-100's real case: new pattern dates interleaved before/among/
    after existing patterns -- puts existing pids into must_check, so
    existing_cache is seeded with their REAL pre-batch top-K via the
    same seed_full_catalog() production code uses (see module
    docstring's IMPORTANT note -- {} would silently under-count here)."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)  # 01-01..01-10
    new = _make_patterns_at(
        [date(2026, 1, 5), date(2026, 1, 8), date(2026, 2, 1)], start_pid=101,
    )
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())

    pre_batch = run_walk_forward("fixture", *existing)
    full_rescore = run_walk_forward("fixture", full_meta, full_win, full_lab)
    existing_meta, existing_win, _existing_lab = existing
    true_existing_cache = seed_full_catalog(existing_meta, existing_win)

    incremental, _new_topk, _existing_topk = run_cached_post_batch(
        "fixture", full_meta, full_win, full_lab, new_pids, pre_batch,
        existing_cache=true_existing_cache,
    )

    min_new_date = date(2026, 1, 5)
    n_safe = sum(1 for m in existing[0].values() if m.anchor_date <= min_new_date)
    if incremental.model_dump_json() == full_rescore.model_dump_json():
        ok(f"mixed-date incremental batch matches full re-score byte-for-"
           f"byte with a correctly-seeded existing_cache "
           f"({n_safe}/10 existing pids safely reused, not same-day)")
    else:
        fail("mixed-date incremental batch diverged from full re-score")


def _test_internal_invariant_guardrail() -> None:
    """A genuine internal-invariant break: pre_batch is missing a pid
    this module determined was safe to reuse -- must raise, not drop
    it. Guardrail fires before existing_cache is ever touched (see
    domain/eval_incremental.py's run_cached_post_batch), so {} is
    safe here regardless of must_check membership."""
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
        run_cached_post_batch(
            "fixture", full_meta, full_win, full_lab, new_pids, broken_pre_batch,
            existing_cache={},
        )
        fail("guardrail did not fire on a pre_batch missing a safe pid")
    except IncrementalGuardrailError:
        ok("guardrail correctly raises when pre_batch is missing a safe pid")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== new-pids-only matches full re-score (existing_cache={} valid) ===")
    _test_new_pids_only_matches_full_rescore()

    print("\n=== M-100 mixed dates -- matches full re-score, real existing_cache ===")
    _test_mixed_dates_matches_full_rescore()

    print("\n=== guardrail fires on internal invariant break ===")
    _test_internal_invariant_guardrail()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
