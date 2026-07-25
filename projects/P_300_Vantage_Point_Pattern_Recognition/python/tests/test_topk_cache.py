"""
tests/test_topk_cache.py

Permanent regression tests for domain/topk_cache.py (Regression Test
Governance, python-project-architecture skill). Each test encodes one
verified invariant; this file grows, never shrinks, per future fix.

Run standalone: python tests/test_topk_cache.py
Prints PASS on success, or FAIL: <reason> + non-zero exit on failure.

Guarantees covered (WO-P300-E4.006, 2026-07-19):
  - _displace(): closer evicts the worst slot, farther is a no-op,
    under-K appends without evicting, exact ties raise TopKTieError
    (Finding 3's rule) instead of silently picking a winner.
  - update_for_new_batch() returns EVERY must_check pid, not just the
    ones whose cache was actually displaced -- the real correctness
    bug found and fixed during this WO's build (a must_check pid's
    corpus_size/baseline changes regardless of whether displacement
    touched its cache; see domain/topk_cache.py's own docstring). Test
    uses a monkeypatched similarity.rank_by_distance so the fixture
    proves NO displacement occurs, then asserts the pid is still
    returned -- this is the exact scenario the bug silently dropped.
  - _partition_unaffected() (domain/eval_incremental.py) partitions
    correctly on the min-new-date boundary this WO's admission logic
    depends on (M-082 -- pinning the contract, not re-deriving it).
"""
import sys
from datetime import date
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PYTHON_DIR))

from domain import similarity  # noqa: E402
from domain.eval_incremental import _partition_unaffected  # noqa: E402
from domain.topk_cache import TopKTieError, _displace, update_for_new_batch  # noqa: E402
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from schemas_eval import TopKMatch  # noqa: E402


def _match(pid: int, rank: int, matched: int, dist: float) -> TopKMatch:
    return TopKMatch(
        pattern_instance_id=pid, rank=rank, matched_pid=matched,
        composite_distance=dist,
    )


def test_displace_appends_when_under_k():
    current = [_match(1, 1, 10, 0.5)]
    result = _displace(current, 1, 20, 0.9)
    assert len(result) == 2
    assert [m.matched_pid for m in result] == [10, 20]
    assert [m.rank for m in result] == [1, 2]


def test_displace_closer_evicts_worst():
    full = [_match(1, i + 1, 100 + i, float(i)) for i in range(20)]
    result = _displace(full, 1, 999, 0.5)
    assert len(result) == 20
    assert 999 in [m.matched_pid for m in result]
    assert 119 not in [m.matched_pid for m in result]  # old worst (dist=19.0) evicted
    assert [m.rank for m in result] == list(range(1, 21))
    dists = [m.composite_distance for m in result]
    assert dists == sorted(dists)


def test_displace_no_op_when_farther_than_worst():
    full = [_match(1, i + 1, 100 + i, float(i)) for i in range(20)]
    result = _displace(full, 1, 999, 50.0)
    assert [m.matched_pid for m in result] == [m.matched_pid for m in full]


def test_displace_raises_on_exact_tie_at_worst_slot():
    full = [_match(1, i + 1, 100 + i, float(i)) for i in range(20)]
    worst_dist = full[-1].composite_distance
    try:
        _displace(full, 1, 999, worst_dist)
        raise AssertionError("expected TopKTieError on exact tie")
    except TopKTieError:
        pass


def test_partition_unaffected_splits_on_min_new_date():
    meta = {
        1: PatternMetadata(1, "SPY", date(2026, 1, 1), 5),
        2: PatternMetadata(2, "SPY", date(2026, 1, 10), 5),
        3: PatternMetadata(3, "SPY", date(2026, 1, 20), 5),
    }
    new_pids = {3}
    safe, must_rescore = _partition_unaffected(meta, new_pids, date(2026, 1, 20))
    assert safe == [1, 2]  # both dated <= min_new_date (2026-01-20)
    assert set(must_rescore) == {3}


def test_partition_unaffected_pid_after_min_new_date_must_rescore():
    meta = {
        1: PatternMetadata(1, "SPY", date(2026, 1, 1), 5),
        2: PatternMetadata(2, "SPY", date(2026, 1, 15), 5),
    }
    new_pids = {1}
    safe, must_rescore = _partition_unaffected(meta, new_pids, date(2026, 1, 1))
    assert safe == []
    assert set(must_rescore) == {1, 2}  # pid 2 (2026-01-15) > min_new_date (2026-01-01)


def test_update_for_new_batch_returns_unchanged_must_check_pids():
    """Pins the corpus/baseline correctness fix: a must_check pid whose
    cache is NOT displaced must still appear in existing_must_check_
    topk, because its corpus_size/baseline changed regardless. Forces
    zero displacement via a monkeypatched rank_by_distance returning a
    distance far worse than the existing worst slot."""
    meta = {
        1: PatternMetadata(1, "SPY", date(2026, 1, 1), 5),   # will be new
        2: PatternMetadata(2, "SPY", date(2026, 1, 15), 5),  # existing, must_check
    }
    windows = {1: [object()], 2: [object()]}
    existing_cache = {2: [_match(2, i + 1, 900 + i, float(i)) for i in range(20)]}

    original = similarity.rank_by_distance
    try:
        # Every call returns one far-away candidate -- never displaces pid 2's worst slot.
        similarity.rank_by_distance = lambda candidate, hist: [
            (pid, 9999.0, {}) for pid in hist
        ]
        new_topk, existing_topk = update_for_new_batch({1}, meta, windows, existing_cache)
    finally:
        similarity.rank_by_distance = original

    assert 2 in existing_topk, (
        "must_check pid missing from result -- regression: a pid whose "
        "cache wasn't displaced must still be returned (corpus/baseline "
        "changed regardless of displacement)"
    )
    assert [m.matched_pid for m in existing_topk[2]] == [
        m.matched_pid for m in existing_cache[2]
    ], "cache content should be unchanged (no real displacement), only re-returned"
    assert 1 in new_topk


def main() -> int:
    tests = [
        test_displace_appends_when_under_k,
        test_displace_closer_evicts_worst,
        test_displace_no_op_when_farther_than_worst,
        test_displace_raises_on_exact_tie_at_worst_slot,
        test_partition_unaffected_splits_on_min_new_date,
        test_partition_unaffected_pid_after_min_new_date_must_rescore,
        test_update_for_new_batch_returns_unchanged_must_check_pids,
    ]
    for test in tests:
        try:
            test()
            print(f"  OK    {test.__name__}")
        except AssertionError as err:
            print(f"  FAIL  {test.__name__}: {err}")
            print(f"FAIL: {test.__name__}")
            return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
