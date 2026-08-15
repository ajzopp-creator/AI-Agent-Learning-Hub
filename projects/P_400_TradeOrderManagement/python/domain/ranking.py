"""ranking.py -- Composite scoring and ordering for the Tier-2B batch runner.

Pure logic only -- no I/O, no network, no print. WO-P400-E5.003 Scope 3.

WHAT THIS IS NOT
----------------
The value produced here is a deterministic composite SCORE. It is not a
probability, not a confidence, and not an estimate of whether a trade will
win. P_400 has no model capable of producing any of those. It orders
already-APPROVED candidates so the strongest setup is read first; it makes
no claim about outcome.

WHY R:R ALONE CANNOT DRIVE THE SORT
-----------------------------------
R:R is a ratio whose denominator is risk-per-share. A very tight stop
inflates it mechanically while making the setup less survivable. Live case,
2026-08-05: INDI screened at R:R 22.78 on a 0.05 stop against 0.31 ATR --
the highest ratio in the batch and the least survivable setup in it. QUANT
blocked it upstream, so it never reaches ranking, but the same distortion
exists in milder form among candidates that DO pass. Hence the R:R ceiling
(scores saturate at 6.0) and the independent ATR-headroom factor.
"""

from __future__ import annotations

import logging
from math import log10
from typing import Dict, List, Tuple

from config import (
    BATCH_RANK_ATR_HEADROOM_CEILING,
    BATCH_RANK_RR_CEILING,
    BATCH_RANK_SPREAD_CEILING_PCT,
    BATCH_RANK_VOLUME_CEILING,
    BATCH_RANK_VOLUME_FLOOR,
    BATCH_RANK_WEIGHT_ATR_HEADROOM,
    BATCH_RANK_WEIGHT_DRIFT,
    BATCH_RANK_WEIGHT_LIQUIDITY,
    BATCH_RANK_WEIGHT_RR,
    BATCH_RANK_WEIGHT_SPREAD,
    ENTRY_DRIFT_THRESHOLD_PCT,
)

logger = logging.getLogger("p400.ranking")


def _norm_rr(rr_at_t1: float) -> float:
    """R:R normalized, saturating at BATCH_RANK_RR_CEILING."""
    return min(max(rr_at_t1, 0.0) / BATCH_RANK_RR_CEILING, 1.0)


def _norm_headroom(atr_headroom: float) -> float:
    """Credit only headroom ABOVE the 1.0x ATR floor.

    Every ranked candidate has already cleared QUANT's stop >= 1x ATR gate,
    so 1.0x earns nothing here -- it is the entry price, not an achievement.
    A stop at 1.05x ATR is one bad tick from the block line; one at 2.4x has
    real room. Scoring the raw multiple would rate those nearly equal.
    """
    span = BATCH_RANK_ATR_HEADROOM_CEILING - 1.0
    return min(max(atr_headroom - 1.0, 0.0) / span, 1.0)


def _norm_spread(spread_pct_of_price: float) -> float:
    """Inverted -- tighter spread scores higher. Zero at/above the ceiling."""
    return max(0.0, 1.0 - (max(spread_pct_of_price, 0.0) / BATCH_RANK_SPREAD_CEILING_PCT))


def _norm_liquidity(avg_volume_20d: float) -> float:
    """Log-scaled between floor and ceiling.

    Log rather than linear because real volume spans orders of magnitude
    (CACC 134k vs TSLA 39M on 2026-08-05); linear scaling would score
    everything below ~2M as effectively zero.
    """
    if avg_volume_20d <= BATCH_RANK_VOLUME_FLOOR:
        return 0.0
    numerator = log10(avg_volume_20d) - log10(BATCH_RANK_VOLUME_FLOOR)
    denominator = log10(BATCH_RANK_VOLUME_CEILING) - log10(BATCH_RANK_VOLUME_FLOOR)
    return min(numerator / denominator, 1.0)


def _norm_drift(drift_pct: float) -> float:
    """Inverted on ABSOLUTE drift -- closer to the analyzed entry scores higher.

    JUDGMENT CALL, flagged for review. config.py line 111 records that
    favorable drift (live below guideline) never blocks because R:R improves,
    which argues for scoring only adverse drift. But 2026-08-05 showed both
    directions invalidating setups: CMPS +11.79% -> ENTRY_MISSED, and HRZN
    -3.66% -> stop above live price, R:R collapsed to 0. Large deviation in
    either direction means the setup is no longer the one the signal
    described. Everything reaching ranking is already APPROVED, so the
    council has ruled the drift acceptable; this only breaks ties among
    acceptable ones. Change to signed if Tony prefers.
    """
    return max(0.0, 1.0 - (abs(drift_pct) / ENTRY_DRIFT_THRESHOLD_PCT))


def score_candidate(
    rr_at_t1: float,
    atr_headroom: float,
    spread_pct_of_price: float,
    avg_volume_20d: float,
    drift_pct: float,
) -> Tuple[float, Dict[str, float]]:
    """Composite score in [0.0, 1.0] plus its per-factor breakdown.

    Returns:
        (score, components) -- components carried so any ordering can be
        audited against its inputs rather than taken on trust.
    """
    components = {
        "rr": _norm_rr(rr_at_t1),
        "atr_headroom": _norm_headroom(atr_headroom),
        "spread": _norm_spread(spread_pct_of_price),
        "liquidity": _norm_liquidity(avg_volume_20d),
        "drift": _norm_drift(drift_pct),
    }
    score = (
        components["rr"] * BATCH_RANK_WEIGHT_RR
        + components["atr_headroom"] * BATCH_RANK_WEIGHT_ATR_HEADROOM
        + components["spread"] * BATCH_RANK_WEIGHT_SPREAD
        + components["liquidity"] * BATCH_RANK_WEIGHT_LIQUIDITY
        + components["drift"] * BATCH_RANK_WEIGHT_DRIFT
    )
    return round(min(max(score, 0.0), 1.0), 4), {k: round(v, 4) for k, v in components.items()}


def order_by_score(scored: List[dict]) -> List[dict]:
    """Sort descending by score, ties broken alphabetically, assign rank 1..N.

    Alphabetical tie-break is arbitrary but DETERMINISTIC -- the same batch
    must produce the same order every run, or the ranked table cannot be
    compared across sessions.

    Args:
        scored: dicts each carrying at least 'symbol' and 'score'.

    Returns:
        Same dicts, ordered, each with 'rank' set.
    """
    ordered = sorted(scored, key=lambda c: (-c['score'], c['symbol']))
    for position, candidate in enumerate(ordered, start=1):
        candidate['rank'] = position
    return ordered