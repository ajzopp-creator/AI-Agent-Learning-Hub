"""
FILE: similarity.py
VERSION: 1.0
DATE: 2026-05-17
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure-math similarity engine for Pipeline B. Computes DTW distance
    per normalized feature column between a live candidate's window
    and each catalog PATTERN_IDENT window; sums the per-feature
    distances equal-weight (Stage 6 decision B); returns a ranked list
    of candidates ascending by composite distance.

    Layer rules:
        - No I/O. No DB. No logging. No print() outside __main__.
          Pure functions consuming NormalizedBar lists and primitive
          types, producing typed numbers / dicts / lists.
        - config.SIMILARITY_FEATURES is the single source of truth for
          the 10 normalized columns scored (architecture §9.3).
          Per-feature weighting is a Stage 8 Backlog parameter-sweep
          candidate; for now every feature contributes equal weight.
        - DTW handles variable-length sequences natively — candidate
          and historical patterns can have different window_length
          (each within 5–20 bars per architecture §1.5).

    Caller (typically application/daily_evaluate_pipeline.py) takes
    the first TOP_K_MATCHES tuples from rank_by_distance, loads the
    forward labels and metadata for those pids, then assembles
    MatchResult objects.

CHANGELOG:
    - 2026-05-17 v1.0: Initial release. Stage 6 file #4 of 9.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from numba import njit

# sys.path bootstrap so direct invocation finds config + schemas.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import SIMILARITY_FEATURES  # noqa: E402
from schemas_pipeline_b import NormalizedBar  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# DTW core — single feature column
# ─────────────────────────────────────────────────────────────────────────────

def _dtw_core(seq_a: np.ndarray, seq_b: np.ndarray) -> float:
    """Numba-compiled DTW grid -- abs-diff cost, min-of-3 recurrence,
    rolling-row reduction. Same algorithm and operation order as the
    pre-JIT pure-Python version: fastmath OFF, no reordering, no
    behavior change (WO-P300-E4.005 Phase 2a, byte-identity verified
    against a 39-candidate real-catalog baseline before promote).
    Not called directly -- see dtw_distance() below.
    """
    m = seq_a.shape[0]
    n = seq_b.shape[0]
    if n < m:
        seq_a, seq_b = seq_b, seq_a
        m, n = n, m
    prev_row = np.full(n + 1, np.inf)
    prev_row[0] = 0.0
    for i in range(1, m + 1):
        curr_row = np.full(n + 1, np.inf)
        a_i = seq_a[i - 1]
        for j in range(1, n + 1):
            cost = abs(a_i - seq_b[j - 1])
            curr_row[j] = cost + min(
                prev_row[j],
                curr_row[j - 1],
                prev_row[j - 1],
            )
        prev_row = curr_row
    return prev_row[n]


_dtw_core = njit(cache=True, fastmath=False)(_dtw_core)


def dtw_distance(seq_a: list[float], seq_b: list[float]) -> float:
    """Dynamic-time-warping distance between two 1-D sequences.

    Classic full-grid DTW with abs-difference cost. O(m*n) time,
    O(min(m,n)+1) space via rolling-row reduction. Handles unequal
    lengths natively — pattern windows may be 5–20 bars on either side.

    Grid computation runs through a numba-compiled kernel (_dtw_core)
    for speed; this wrapper's contract (signature, validation, return
    value) is unchanged from the pre-JIT version.

    Args:
        seq_a: numeric sequence (length m >= 1)
        seq_b: numeric sequence (length n >= 1)

    Returns:
        Sum of absolute differences along the minimum-cost monotonic
        alignment path. Identical sequences score 0.0; result is
        non-negative in all cases.

    Raises:
        ValueError: if either sequence is empty.
    """
    m = len(seq_a)
    n = len(seq_b)
    if m == 0 or n == 0:
        raise ValueError(
            f"DTW requires non-empty sequences; got len(a)={m}, len(b)={n}"
        )
    arr_a = np.asarray(seq_a, dtype=np.float64)
    arr_b = np.asarray(seq_b, dtype=np.float64)
    return float(_dtw_core(arr_a, arr_b))


# ─────────────────────────────────────────────────────────────────────────────
# Multi-feature scoring
# ─────────────────────────────────────────────────────────────────────────────

def per_feature_distances(
    candidate_bars: list[NormalizedBar],
    historical_bars: list[NormalizedBar],
) -> dict[str, float]:
    """Compute one DTW distance per SIMILARITY_FEATURE column.

    Extracts each of the 10 normalized columns from both bar lists,
    runs DTW per column, returns the dict keyed by feature name.
    Caller composes into a single score via composite_distance().
    """
    if not candidate_bars or not historical_bars:
        raise ValueError(
            "Both candidate_bars and historical_bars must be non-empty"
        )
    out: dict[str, float] = {}
    for feat in SIMILARITY_FEATURES:
        cand_col = [getattr(b, feat) for b in candidate_bars]
        hist_col = [getattr(b, feat) for b in historical_bars]
        out[feat] = dtw_distance(cand_col, hist_col)
    return out


def composite_distance(per_feat: dict[str, float]) -> float:
    """Equal-weight sum of per-feature DTW distances (Stage 6 decision B).

    Requires every SIMILARITY_FEATURE present in `per_feat`. Missing
    keys raise — silent partial sums would silently bias ranking and
    are exactly the M-009-class drift this contract is meant to prevent.
    """
    missing = [f for f in SIMILARITY_FEATURES if f not in per_feat]
    if missing:
        raise ValueError(
            f"composite_distance missing features: {missing}"
        )
    return sum(per_feat[f] for f in SIMILARITY_FEATURES)


# ─────────────────────────────────────────────────────────────────────────────
# Ranking
# ─────────────────────────────────────────────────────────────────────────────

def rank_by_distance(
    candidate_bars: list[NormalizedBar],
    historical_windows: dict[int, list[NormalizedBar]],
) -> list[tuple[int, float, dict[str, float]]]:
    """Score every historical window vs the candidate; rank ascending.

    Returns one tuple per historical pattern:
        (pattern_instance_id, composite_distance, per_feature_distances)

    Sorted by composite_distance ascending — closest analogs first.
    Caller (application/daily_evaluate_pipeline.py) slices the first
    TOP_K_MATCHES entries, loads forward_labels + metadata for those
    pids, then assembles MatchResult objects.

    Pids mapped to empty bar lists are skipped defensively — should
    never happen if catalog_reader.bulk_load_normalized_windows is
    the producer, but the guard avoids a silent crash if the source
    changes later.
    """
    if not candidate_bars:
        raise ValueError("candidate_bars is empty")
    scored: list[tuple[int, float, dict[str, float]]] = []
    for pid, hist_bars in historical_windows.items():
        if not hist_bars:
            continue
        per_feat = per_feature_distances(candidate_bars, hist_bars)
        composite = composite_distance(per_feat)
        scored.append((pid, composite, per_feat))
    scored.sort(key=lambda triple: triple[1])
    return scored


# ─────────────────────────────────────────────────────────────────────────────
# Smoke harness — `python domain/similarity.py`
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Synthetic tests: no catalog dependency, no NormalizedBar
    # construction; exercises DTW core + composite_distance contract.

    # 1. Identical sequences → distance 0.
    a = [0.0, 1.0, 2.0, 3.0, 4.0]
    b = [0.0, 1.0, 2.0, 3.0, 4.0]
    print(f"DTW identical:        {dtw_distance(a, b)} (expect 0.0)")

    # 2. Element-wise shifted by 0.5 → 5 * 0.5 = 2.5 along the diagonal.
    c = [0.0, 1.0, 2.0, 3.0, 4.0]
    d = [0.5, 1.5, 2.5, 3.5, 4.5]
    print(f"DTW shifted-by-0.5:   {dtw_distance(c, d)} (expect 2.5)")

    # 3. Unequal length, monotonically increasing on both sides.
    #    Minimum-cost path matches the 3 a-points to a-aligned f-points;
    #    warping absorbs the extra f-points at zero cost.
    e = [0.0, 1.0, 2.0]
    f = [0.0, 0.5, 1.0, 1.5, 2.0]
    print(f"DTW unequal-length:   {dtw_distance(e, f)} (expect 1.0)")

    # 4. composite_distance equal-weight sum.
    per_feat = {feat: 0.5 for feat in SIMILARITY_FEATURES}
    expected_sum = len(SIMILARITY_FEATURES) * 0.5
    print(
        f"composite equal-wt:   {composite_distance(per_feat)} "
        f"(expect {expected_sum})"
    )

    # 5. composite_distance with missing feature → raises.
    try:
        composite_distance({SIMILARITY_FEATURES[0]: 1.0})
        print("FAIL: missing-feature case should have raised")
    except ValueError as err:
        print(f"composite missing:    OK — raised ValueError ({err})")

    # 6. DTW empty-sequence guard.
    try:
        dtw_distance([], [1.0])
        print("FAIL: empty-sequence case should have raised")
    except ValueError as err:
        print(f"DTW empty guard:      OK — raised ValueError ({err})")
