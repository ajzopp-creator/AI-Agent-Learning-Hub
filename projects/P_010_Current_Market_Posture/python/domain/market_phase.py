"""
P_010 Market Health -- domain/market_phase.py

Pure rule-table function. Given two IndexHealth records (SPY + QQQ),
return the most restrictive market phase plus a one-line reason.

Spec reference: docs/P_010_MarketHealth_Spec_v1_1.md Section 7
"""

from typing import Optional

from market_health.config import (
    FTD_FRESH_DAYS,
    PHASE_DIST_CAUTION_MAX,
    PHASE_DIST_DETERIORATING_MAX,
    PHASE_DIST_HEALTHY_MAX,
)
from market_health.schemas import IndexHealth, MarketPhase


def derive_phase(
    spy: IndexHealth,
    qqq: IndexHealth,
) -> tuple[MarketPhase, str]:
    """
    Most-restrictive-wins phase derivation.

    Order of checks (first match wins, top is most restrictive):
      1. CORRECTION             -- max_dist_count >= 5
      2. DETERIORATING          -- max_dist_count == 4
      3. UPTREND_UNDER_PRESSURE -- fresh FTD on either index AND dist count == 3
      4. CONFIRMED_UPTREND      -- fresh FTD on either index AND dist count <= 2
      5. RALLY_ATTEMPT          -- either index in active attempt
      6. NEUTRAL                -- everything else
    """
    max_dist = max(spy.dist_count, qqq.dist_count)
    fresh_ftd = _has_fresh_ftd(spy) or _has_fresh_ftd(qqq)
    in_attempt = (
        spy.rally_state in ("RALLY_LOW_SET", "RALLY_ATTEMPT")
        or qqq.rally_state in ("RALLY_LOW_SET", "RALLY_ATTEMPT")
    )

    if max_dist > PHASE_DIST_DETERIORATING_MAX:
        return "CORRECTION", f"max_dist_count={max_dist} (>=5)"
    if max_dist == PHASE_DIST_DETERIORATING_MAX:
        return "DETERIORATING", f"max_dist_count={max_dist}"
    if fresh_ftd and max_dist == PHASE_DIST_CAUTION_MAX:
        return (
            "UPTREND_UNDER_PRESSURE",
            f"fresh FTD with dist_count={max_dist}",
        )
    if fresh_ftd and max_dist <= PHASE_DIST_HEALTHY_MAX:
        return "CONFIRMED_UPTREND", f"fresh FTD, dist_count={max_dist}"
    if in_attempt:
        return "RALLY_ATTEMPT", "active rally attempt, no FTD yet"
    return "NEUTRAL", f"no FTD, dist_count={max_dist}"


def _has_fresh_ftd(idx: IndexHealth) -> bool:
    if idx.rally_state != "FTD_CONFIRMED":
        return False
    age: Optional[int] = idx.ftd_age_days
    if age is None:
        return False
    return age <= FTD_FRESH_DAYS
