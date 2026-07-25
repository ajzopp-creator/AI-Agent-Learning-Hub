"""
FILE: tests/test_similarity.py
VERSION: 1.0
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for domain/similarity.py -- rebuilt
    2026-07-20 after independent review of WO-P300-E4.005 found this
    file claimed (Phase 2a: "NEW, 113 lines, permanent... 7/7 PASS")
    but absent from disk, with no trace in tests/__pycache__/ either.

    Covers two things:
      1. similarity.py's own __main__ smoke-harness fixtures, promoted
         to real assertions (identical / shifted-by-0.5 / unequal-length
         / composite equal-weight / composite missing-feature raises /
         DTW empty-sequence guard) -- 6 checks.
      2. A pinned, independently-written reference DTW implementation
         (_reference_dtw, test-only -- M-082: production carries
         exactly one DTW implementation, this is not a second one, it
         is a differently-structured oracle used only to cross-check
         the production numba kernel) asserted byte-identical to the
         real dtw_distance() across 6 diverse fixtures -- 1 check.

    7 checks total. _reference_dtw uses a full 2-D cost matrix (not the
    production rolling-row reduction) so the cross-check is structurally
    independent of _dtw_core's implementation, not a restatement of it.

    Synthetic fixture only -- no real catalog dependency, matches the
    project's existing smoke-test convention (tests/smoke_*.py /
    tests/test_eval_scoring.py) rather than pytest; run directly via PEH.

CHANGELOG:
    - 2026-07-20 v1.0: Rebuilt from scratch (WO-P300-E4.005 independent
      review finding -- original claimed file never landed on disk).

RUN (from project root, p140 active):
    python tests/test_similarity.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent / "python"
sys.path.insert(0, str(_PYTHON_DIR))

from config import SIMILARITY_FEATURES  # noqa: E402
from domain.similarity import composite_distance, dtw_distance  # noqa: E402


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _reference_dtw(seq_a: list[float], seq_b: list[float]) -> float:
    """Independently-written DTW oracle, test-only (M-082: production
    carries exactly one DTW implementation -- this cross-checks it,
    it does not duplicate it into production). Full 2-D cost matrix,
    not the rolling-row reduction _dtw_core uses -- deliberately a
    different code shape computing the same recurrence, so a bug in
    the production rolling-row logic is unlikely to also exist here.
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


def _test_identical() -> None:
    """similarity.py __main__ check 1: identical sequences -> 0.0."""
    a = [0.0, 1.0, 2.0, 3.0, 4.0]
    b = [0.0, 1.0, 2.0, 3.0, 4.0]
    result = dtw_distance(a, b)
    if result == 0.0:
        ok(f"identical sequences -> {result} (expect 0.0)")
    else:
        fail(f"identical sequences -> {result}, expected 0.0")


def _test_shifted_by_half() -> None:
    """similarity.py __main__ check 2: uniform +0.5 shift -> 5 * 0.5 = 2.5."""
    a = [0.0, 1.0, 2.0, 3.0, 4.0]
    b = [0.5, 1.5, 2.5, 3.5, 4.5]
    result = dtw_distance(a, b)
    if result == 2.5:
        ok(f"shifted-by-0.5 -> {result} (expect 2.5)")
    else:
        fail(f"shifted-by-0.5 -> {result}, expected 2.5")


def _test_unequal_length() -> None:
    """similarity.py __main__ check 3: 3-pt vs 5-pt monotonic, warping
    absorbs the extra points at zero cost -> 1.0."""
    a = [0.0, 1.0, 2.0]
    b = [0.0, 0.5, 1.0, 1.5, 2.0]
    result = dtw_distance(a, b)
    if result == 1.0:
        ok(f"unequal-length -> {result} (expect 1.0)")
    else:
        fail(f"unequal-length -> {result}, expected 1.0")


def _test_composite_equal_weight() -> None:
    """similarity.py __main__ check 4: composite_distance sums every
    SIMILARITY_FEATURE at equal weight (Stage 6 decision B)."""
    per_feat = {feat: 0.5 for feat in SIMILARITY_FEATURES}
    expected = len(SIMILARITY_FEATURES) * 0.5
    result = composite_distance(per_feat)
    if result == expected:
        ok(f"composite equal-weight -> {result} (expect {expected})")
    else:
        fail(f"composite equal-weight -> {result}, expected {expected}")


def _test_composite_missing_feature_raises() -> None:
    """similarity.py __main__ check 5: a partial per_feat dict must
    raise, never silently under-sum (M-009-class drift guard)."""
    try:
        composite_distance({SIMILARITY_FEATURES[0]: 1.0})
        fail("composite_distance with a missing feature should have raised")
    except ValueError:
        ok("composite_distance raises ValueError on missing feature")


def _test_dtw_empty_guard() -> None:
    """similarity.py __main__ check 6: an empty sequence must raise,
    never silently return a degenerate distance."""
    try:
        dtw_distance([], [1.0])
        fail("dtw_distance with an empty sequence should have raised")
    except ValueError:
        ok("dtw_distance raises ValueError on empty sequence")


def _test_reference_implementation_match() -> None:
    """Production dtw_distance() (numba-JIT rolling-row) must exactly
    match the independent full-matrix reference oracle across 6
    diverse fixtures -- equal-length monotonic, all-identical, unequal
    length, single-element both sides, mixed-sign values, and a
    longer non-monotonic (oscillating) sequence pair."""
    fixtures: list[tuple[str, list[float], list[float]]] = [
        ("equal-length monotonic", [0.0, 1.0, 2.0, 3.0], [1.0, 2.0, 3.0, 4.0]),
        ("all-identical", [2.0, 2.0, 2.0], [2.0, 2.0, 2.0]),
        ("unequal length", [0.0, 2.0, 4.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]),
        ("single-element both sides", [3.0], [7.5]),
        ("mixed-sign values", [-2.0, -1.0, 0.0, 1.0, 2.0], [-1.0, 0.0, 1.0]),
        (
            "longer oscillating",
            [0.0, 3.0, 1.0, 4.0, 1.5, 5.0, 2.0, 6.0],
            [1.0, 2.5, 0.5, 4.5, 2.0, 4.0, 3.0],
        ),
    ]
    for name, seq_a, seq_b in fixtures:
        production = dtw_distance(seq_a, seq_b)
        reference = _reference_dtw(seq_a, seq_b)
        if production != reference:
            fail(
                f"reference mismatch on '{name}': "
                f"production={production}, reference={reference}"
            )
    ok(f"production dtw_distance matches independent reference oracle "
       f"on {len(fixtures)}/{len(fixtures)} diverse fixtures")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== similarity.py __main__ smoke fixtures, as real assertions ===")
    _test_identical()
    _test_shifted_by_half()
    _test_unequal_length()
    _test_composite_equal_weight()
    _test_composite_missing_feature_raises()
    _test_dtw_empty_guard()

    print("\n=== independent reference-implementation cross-check ===")
    _test_reference_implementation_match()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
