"""
tests/test_similarity.py

Permanent regression tests for domain/similarity.py (Regression Test
Governance, python-project-architecture skill). Each test encodes one
verified invariant; this file grows, never shrinks, per future fix.

Run standalone: python tests/test_similarity.py
Prints PASS on success, or FAIL: <reason> + non-zero exit on failure.

Guarantees covered (WO-P300-E4.005 Phase 2a, 2026-07-18):
  - test_dtw_matches_reference_on_diverse_fixtures: the numba-jitted
    dtw_distance() is byte-identical to a plain-Python reference DTW
    kept ONLY in this test (M-082 -- production carries exactly one
    DTW implementation; this reference exists solely to pin the
    invariant, never imported by production code).
  - The three DTW + one composite synthetic cases from similarity.py's
    own __main__ smoke harness, reused here rather than re-invented,
    since they are the project's own established known-good values.
  - Empty-sequence and missing-feature error contracts.
"""
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PYTHON_DIR))

from domain.similarity import composite_distance, dtw_distance  # noqa: E402


def _reference_dtw(seq_a, seq_b):
    """Plain-Python DTW, independent of similarity.py's implementation.
    Exists ONLY to pin byte-identity in this test file -- never
    imported by production code (M-082: one production implementation).
    """
    m, n = len(seq_a), len(seq_b)
    if n < m:
        seq_a, seq_b = seq_b, seq_a
        m, n = n, m
    inf = float("inf")
    prev_row = [inf] * (n + 1)
    prev_row[0] = 0.0
    for i in range(1, m + 1):
        curr_row = [inf] * (n + 1)
        a_i = seq_a[i - 1]
        for j in range(1, n + 1):
            cost = abs(a_i - seq_b[j - 1])
            curr_row[j] = cost + min(prev_row[j], curr_row[j - 1], prev_row[j - 1])
        prev_row = curr_row
    return prev_row[n]


def test_dtw_identical_sequences_zero_distance():
    a = [0.0, 1.0, 2.0, 3.0, 4.0]
    assert dtw_distance(a, list(a)) == 0.0


def test_dtw_shifted_by_half():
    a = [0.0, 1.0, 2.0, 3.0, 4.0]
    b = [0.5, 1.5, 2.5, 3.5, 4.5]
    assert dtw_distance(a, b) == 2.5


def test_dtw_unequal_length():
    a = [0.0, 1.0, 2.0]
    b = [0.0, 0.5, 1.0, 1.5, 2.0]
    assert dtw_distance(a, b) == 1.0


def test_dtw_empty_sequence_raises():
    try:
        dtw_distance([], [1.0])
        raise AssertionError("expected ValueError on empty sequence")
    except ValueError:
        pass


def test_composite_distance_equal_weight_sum():
    from config import SIMILARITY_FEATURES
    per_feat = {feat: 0.5 for feat in SIMILARITY_FEATURES}
    assert composite_distance(per_feat) == len(SIMILARITY_FEATURES) * 0.5


def test_composite_distance_missing_feature_raises():
    from config import SIMILARITY_FEATURES
    try:
        composite_distance({SIMILARITY_FEATURES[0]: 1.0})
        raise AssertionError("expected ValueError on missing feature")
    except ValueError:
        pass


def test_dtw_matches_reference_on_diverse_fixtures():
    """The invariant this file exists to protect: JIT output must be
    byte-identical to the pre-JIT algorithm on every shape DTW sees in
    production -- short/long, equal/unequal length, positive/negative/
    zero values (WO-P300-E4.005 Phase 2a)."""
    fixtures = [
        ([1.0], [1.0]),
        ([1.0], [5.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
        ([-2.0, -1.0, 0.0, 1.0, 2.0], [2.0, 1.0, 0.0, -1.0, -2.0]),
        (list(range(20)), [float(x) * 0.5 for x in range(5)]),
        ([3.14159, 2.71828, 1.61803], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    ]
    for seq_a, seq_b in fixtures:
        expected = _reference_dtw(seq_a, seq_b)
        actual = dtw_distance(seq_a, seq_b)
        assert actual == expected, (
            f"MISMATCH seq_a={seq_a} seq_b={seq_b}: "
            f"jit={actual} reference={expected}"
        )


def main() -> int:
    tests = [
        test_dtw_identical_sequences_zero_distance,
        test_dtw_shifted_by_half,
        test_dtw_unequal_length,
        test_dtw_empty_sequence_raises,
        test_composite_distance_equal_weight_sum,
        test_composite_distance_missing_feature_raises,
        test_dtw_matches_reference_on_diverse_fixtures,
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
