"""
FILE: volatility_divergence.py
VERSION: 1.0
DATE: 2026-05-20
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Compute helper for the post-classification volatility-divergence flag
    on Pipeline B SignalReports. Pure function, no I/O.

    Why this exists: the 2026-05-20 cap-sensitivity audit
    (utilities/cap_sensitivity_audit.py v1.0) showed that of the 10
    normalized similarity features in Stage 6 Decision B, only range_pct
    cleanly tracks cap/volatility class — OII ~0.046 vs SPY ~0.009 daily
    range, ~5x ratio. volume_zscore has larger raw dispersion but encodes
    volume regime, not cap. close_pct_from_anchor encodes trend bias
    (desired similarity signal). So range_pct is the right axis for the
    "your candidate trades nothing like its top-K analogs" warning.

    Why post-filter, not pre-filter: at N=25 catalog, the lone small-cap
    (GLP) would have zero same-class analogs under pre-filter -> top-K
    empty -> signal can't fire. Post-filter keeps Stage 6 Decision B's
    equal-weight DTW untouched and surfaces the divergence as report
    metadata, so the operator sees the mismatch and sizes accordingly.

    Aggregation: per-match median first, then median-of-medians across
    top-K matches. This weights each match equally regardless of its
    window_length (5-20 bars per the schema).

    Severity thresholds (locked 2026-05-20):
        NONE   ratio < 1.5
        MILD   1.5 <= ratio < 2.0
        STRONG ratio >= 2.0

    Degenerate input (either median is 0.0): returns severity NONE with
    ratio=1.0. These are theoretically possible but practically
    near-impossible for real 20-bar windows, and silent no-flag is
    safer than raising at the report-build boundary.

    Layer rules: domain only. No I/O. Imports from schemas_pipeline_b
    for the output type only.

CHANGELOG:
    - 2026-05-20 v1.0: Initial release. Turn 2 of 4 in the Pipeline B
      volatility-divergence-flag change (schemas_pipeline_b.py v1.2 ->
      this file -> daily_evaluate_pipeline.py v1.2 -> report_writer.py
      v1.3).
"""
from __future__ import annotations

import logging
import statistics
import sys
from collections.abc import Sequence
from pathlib import Path

# sys.path bootstrap so this file imports cleanly when invoked directly
# (smoke harness below) or as `from domain.volatility_divergence import ...`.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from schemas_pipeline_b import Severity, VolatilityDivergence  # noqa: E402

# M-011: route logging to stdout for PowerShell visibility.
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Severity thresholds (audit-driven, locked 2026-05-20)
# ─────────────────────────────────────────────────────────────────────────────

_MILD_RATIO_FLOOR: float = 1.5
_STRONG_RATIO_FLOOR: float = 2.0


def _classify_severity(ratio: float) -> Severity:
    """Map a ratio (>= 1.0) to its Severity bucket. Pure."""
    if ratio >= _STRONG_RATIO_FLOOR:
        return Severity.STRONG
    if ratio >= _MILD_RATIO_FLOOR:
        return Severity.MILD
    return Severity.NONE


# ─────────────────────────────────────────────────────────────────────────────
# Public compute function
# ─────────────────────────────────────────────────────────────────────────────

def compute_volatility_divergence(
    candidate_range_pcts: Sequence[float],
    topk_match_range_pcts: Sequence[Sequence[float]],
) -> VolatilityDivergence:
    """Build a VolatilityDivergence from candidate + top-K range_pct values.

    Aggregation: per-match median first, then median-of-medians for top-K.
    Weights each match equally regardless of window_length (5-20 per schema).

    Symmetric ratio: max(candidate_median, topk_median) divided by
    min(candidate_median, topk_median). A small-cap candidate matched
    against mega-cap analogs flags at the same magnitude as the reverse.

    Degenerate guard: if either median is 0.0, return severity NONE with
    ratio=1.0. Silent no-flag is safer than raising at the report-build
    boundary; degenerate 20-bar windows are near-impossible in practice.

    Args:
        candidate_range_pcts: range_pct values from the live candidate's
            bars (typically window_length, e.g. 20 values).
        topk_match_range_pcts: one inner sequence per top-K historical
            match, each containing that match's range_pct values.

    Returns:
        VolatilityDivergence Pydantic, ready to attach to SignalReport.

    Raises:
        ValueError: if candidate_range_pcts is empty or any inner sequence
            in topk_match_range_pcts is empty. The orchestrator should
            never pass empty inputs; raising gives a clearer message than
            statistics.median's StatisticsError.
    """
    if not candidate_range_pcts:
        raise ValueError("candidate_range_pcts must contain at least one value")
    if not topk_match_range_pcts:
        raise ValueError("topk_match_range_pcts must contain at least one match")
    for i, m in enumerate(topk_match_range_pcts):
        if not m:
            raise ValueError(f"topk_match_range_pcts[{i}] is empty")

    candidate_median = statistics.median(candidate_range_pcts)
    per_match_medians = [statistics.median(m) for m in topk_match_range_pcts]
    topk_median = statistics.median(per_match_medians)
    n_topk_matches = len(topk_match_range_pcts)

    # Degenerate-input guard. Log so the orchestrator/operator notice.
    if candidate_median == 0.0 or topk_median == 0.0:
        logger.warning(
            "Degenerate volatility input (candidate_median=%.6f, "
            "topk_median=%.6f); returning severity NONE.",
            candidate_median, topk_median,
        )
        return VolatilityDivergence(
            candidate_median_range_pct=candidate_median,
            topk_median_range_pct=topk_median,
            ratio=1.0,
            severity=Severity.NONE,
            n_topk_matches=n_topk_matches,
        )

    ratio = (
        max(candidate_median, topk_median)
        / min(candidate_median, topk_median)
    )
    severity = _classify_severity(ratio)

    return VolatilityDivergence(
        candidate_median_range_pct=candidate_median,
        topk_median_range_pct=topk_median,
        ratio=ratio,
        severity=severity,
        n_topk_matches=n_topk_matches,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Smoke harness — `python domain/volatility_divergence.py`
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # STRONG case: OII-like candidate (~0.046) vs SPY-cluster top-K (~0.015).
    cand = [0.044, 0.048, 0.046, 0.041, 0.050, 0.045, 0.047]
    topk = [
        [0.014, 0.015, 0.013, 0.016, 0.015],
        [0.011, 0.014, 0.015, 0.013, 0.012],
        [0.018, 0.020, 0.017, 0.019, 0.018],
        [0.014, 0.015, 0.014, 0.013, 0.015],
        [0.020, 0.022, 0.019, 0.021, 0.020],
    ]
    r = compute_volatility_divergence(cand, topk)
    print("STRONG case (expect ratio ~3, severity STRONG):")
    print(f"  candidate_median = {r.candidate_median_range_pct:.4f}")
    print(f"  topk_median      = {r.topk_median_range_pct:.4f}")
    print(f"  ratio            = {r.ratio:.4f}")
    print(f"  severity         = {r.severity.value}")
    print(f"  n_topk_matches   = {r.n_topk_matches}")

    # MILD case: candidate ~0.025 vs top-K ~0.015 (ratio ~1.7).
    cand2 = [0.025, 0.026, 0.024, 0.025, 0.027]
    topk2 = [
        [0.014, 0.015, 0.013, 0.016, 0.015],
        [0.014, 0.014, 0.015, 0.013, 0.014],
        [0.015, 0.016, 0.014, 0.015, 0.015],
    ]
    r2 = compute_volatility_divergence(cand2, topk2)
    print(f"\nMILD case (expect ratio ~1.7, severity MILD):")
    print(f"  ratio    = {r2.ratio:.4f}")
    print(f"  severity = {r2.severity.value}")

    # NONE case: candidate ~0.018 vs top-K ~0.015 (ratio ~1.2).
    cand3 = [0.018, 0.019, 0.017, 0.018, 0.020]
    topk3 = [
        [0.014, 0.015, 0.013, 0.016, 0.015],
        [0.015, 0.014, 0.016, 0.015, 0.015],
        [0.016, 0.017, 0.015, 0.016, 0.016],
    ]
    r3 = compute_volatility_divergence(cand3, topk3)
    print(f"\nNONE case (expect ratio ~1.2, severity NONE):")
    print(f"  ratio    = {r3.ratio:.4f}")
    print(f"  severity = {r3.severity.value}")

    # Degenerate case: zero candidate median -> silent NONE.
    cand4 = [0.0, 0.0, 0.0]
    topk4 = [[0.015, 0.015], [0.014, 0.016]]
    r4 = compute_volatility_divergence(cand4, topk4)
    print(f"\nDegenerate (zero candidate) case (expect severity NONE):")
    print(f"  ratio    = {r4.ratio:.4f}")
    print(f"  severity = {r4.severity.value}")
