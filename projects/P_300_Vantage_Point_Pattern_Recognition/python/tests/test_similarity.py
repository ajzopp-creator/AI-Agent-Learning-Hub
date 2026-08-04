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

CHANGELOG:
    - 2026-07-29 v1.1: consolidated with a second, independently-
      rebuilt copy that had drifted to tests/ (project root) --
      2026-07-20's rebuild happened because an independent review
      checked the wrong directory and wrongly concluded this file was
      missing (same root cause as test_get_latest_catalog_path_safety.
      py's duplicate, same day). Both versions' core 6 checks were
      functionally equivalent; kept this file's assert-based style
      (matches the rest of python/tests/) but adopted the duplicate's
      REFERENCE ORACLE DESIGN, which is a real improvement, not
      cosmetic: the duplicate used a full 2-D cost matrix instead of
      this file's original rolling-row reduction, deliberately
      structurally independent of production's own rolling-row
      dtw_distance() implementation, so a bug shared by both
      rolling-row implementations would no longer be invisible to the
      cross-check. Fixture set for the reference-match test is now the
      union of both files' fixtures (12 total, up from 6) rather than
      picking one arbitrarily.
    - 2026-07-18 v1.0 (WO-P300-E4.005 Phase 2a): initial.
"""
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PYTHON_DIR))

from domain.similarity import composite_distance, dtw_distance  # noqa: E402


def _reference_dtw(seq_a, seq_b):
    """Independently-written DTW oracle, test-only (M-082: production
    carries exactly one DTW implementation -- this cross-checks it, it
    does not duplicate it into production). Full 2-D cost matrix,
    deliberately NOT the rolling-row reduction dtw_distance() itself
    uses -- a structurally different code shape computing the same
    recurrence, so a bug in the production rolling-row logic is
    unlikely to also exist here (2026-07-29 v1.1: replaces this file's
    original rolling-row reference, which shared its computational
    shape with production and was weaker for exactly that reason).
    """
    m, n = len(seq_a), len(seq_b)
    grid = [[float("inf")] * (n + 1) for _ in range(m + 1)]
    grid[0][0] = 0.0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = abs(seq_a[i - 1] - seq_b[j - 1])
            grid[i][j] = cost + min(
                grid[i - 1][j], grid[i][j - 1], grid[i - 1][j - 1]
            )
    return grid[m][n]


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
    production. Union of both files' original fixture sets (2026-07-29
    v1.1 consolidation) -- 12 total, covering short/long,
    equal/unequal length, positive/negative/zero values, single-element
    pairs, all-identical sequences, and a longer oscillating
    (non-monotonic) pair."""
    fixtures = [
        ([1.0], [1.0]),
        ([1.0], [5.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0]),
        ([-2.0, -1.0, 0.0, 1.0, 2.0], [2.0, 1.0, 0.0, -1.0, -2.0]),
        (list(range(20)), [float(x) * 0.5 for x in range(5)]),
        ([3.14159, 2.71828, 1.61803], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ([0.0, 1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0]),
        ([2.0, 2.0, 2.0], [2.0, 2.0, 2.0]),
        ([0.0, 2.0, 4.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]),
        ([3.0], [7.5]),
        ([-2.0, -1.0, 0.0, 1.0, 2.0], [-1.0, 0.0, 1.0]),
        (
            [0.0, 3.0, 1.0, 4.0, 1.5, 5.0, 2.0, 6.0],
            [1.0, 2.5, 0.5, 4.5, 2.0, 4.0, 3.0],
        ),
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
