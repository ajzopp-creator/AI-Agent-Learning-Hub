"""
FILE: domain/pattern_detector.py
VERSION: 1.0
DATE: 2026-07-08
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure-Python decode of the IntelliScan "Potential Crossover v12" scan
    (WO-P300-E2.001 Phase 1), evaluated against an in-memory bar window.
    No I/O, no DB, no print -- strictly testable in isolation.

    9 conditions, evaluated at the most recent bar in the window
    (current_idx):
      1. MT crossover up exactly 1 bar ago (mtdiff: <=0 -> >0)
      2. ST Diff trending up
      3. MT Diff trending up
      4. LT Diff trending up
      5. Neural Index up
      6. Predicted range direction up (pred_high_diff > 0 AND
         pred_low_diff > 0) -- diffs computed vs. the prior bar's
         predicted levels, not the raw pred_high/pred_low fields.
      7. Last Triple Cross crossover was DOWN (reversal context)
      8. Predicted High > Close
      9. Close < swing-high resistance -- IntelliScan's Verified
         Resistance Zone is proprietary and not reproducible from grid
         exports; approximated via nearest pivot high above close
         within BULK_SWING_HIGH_LOOKBACK_BARS. Tagged approximate at
         every call site that consumes it.

    STRICT = all 9 AND. RELAXED = all except condition 7 (continuation
    variant -- drops the reversal-context requirement per WO). STRICT
    implies RELAXED; a bar that passes STRICT is tagged STRICT only,
    never double-counted as both.

    Optionable (per the WO's .isc decode) is IntelliScan display
    metadata, not a detection condition -- correctly absent here.

CHANGELOG:
    - 2026-07-08 v1.0: Initial release. Functions: _trend_up,
      find_swing_high_resistance, detect_pattern. DetectionResult
      dataclass carries tier, resistance level, and per-condition
      pass/fail for audit trail (WO acceptance criteria require
      reproducing the sample-file simulation exactly).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import (  # noqa: E402
    BULK_SWING_HIGH_LOOKBACK_BARS,
    BULK_SWING_HIGH_PIVOT_BARS,
    BULK_TREND_CHECK_BARS,
)
from schemas import VPBarRaw  # noqa: E402
from schemas_bulk import DetectionTier  # noqa: E402


@dataclass(frozen=True)
class DetectionResult:
    """
    Outcome of evaluating all 9 conditions at one bar. conditions_passed
    is keyed 1-9 matching the WO's numbering, for audit trail and for
    reproducing the WO's sample-file detection counts exactly.
    """
    tier: DetectionTier
    resistance_level: float
    conditions_passed: dict[int, bool] = field(default_factory=dict)


def _trend_up(values: list[float]) -> bool:
    """
    True if `values` (oldest-first, length BULK_TREND_CHECK_BARS + 1)
    is strictly increasing across every consecutive pair. Shared by
    conditions 2/3/4 (ST/MT/LT Diff trend).
    """
    if len(values) < 2:
        raise ValueError("_trend_up requires at least 2 values")
    return all(values[i] < values[i + 1] for i in range(len(values) - 1))


def find_swing_high_resistance(
    bars: list[VPBarRaw],
    current_idx: int,
    lookback_bars: int = BULK_SWING_HIGH_LOOKBACK_BARS,
    pivot_bars: int = BULK_SWING_HIGH_PIVOT_BARS,
) -> float | None:
    """
    Approximates IntelliScan's Verified Resistance Zone (condition 9).
    A pivot high is a bar whose `high` exceeds the `high` of every bar
    within `pivot_bars` on both sides. Returns the nearest (highest
    index, i.e. most recent) pivot high whose price sits above the
    current bar's close, searching back `lookback_bars` from
    current_idx. Returns None if no qualifying pivot exists (true
    price-discovery case -- no visible resistance).
    """
    current_close = bars[current_idx].close
    earliest = max(pivot_bars, current_idx - lookback_bars)

    candidates: list[tuple[int, float]] = []
    for i in range(current_idx - pivot_bars, earliest - 1, -1):
        if i - pivot_bars < 0 or i + pivot_bars > current_idx:
            continue
        window_highs = [bars[j].high for j in range(i - pivot_bars, i + pivot_bars + 1)]
        pivot_high = bars[i].high
        if pivot_high == max(window_highs) and pivot_high > current_close:
            candidates.append((i, pivot_high))

    if not candidates:
        return None
    # Nearest = highest index (most recent pivot), not highest price.
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return candidates[0][1]


def _evaluate_conditions(
    bars: list[VPBarRaw],
    current_idx: int,
) -> tuple[dict[int, bool], float | None]:
    """
    Evaluates all 9 Potential Crossover v12 conditions at bars[current_idx].
    Returns (conditions_passed keyed 1-9, resistance_level_or_None).
    Split out of detect_pattern to stay under the 50-line function limit.
    """
    cur = bars[current_idx]
    prev = bars[current_idx - 1]
    trend_window = BULK_TREND_CHECK_BARS + 1
    slice_start = current_idx - trend_window + 1

    conditions: dict[int, bool] = {}

    # 1. MT crossover up exactly 1 bar ago: mtdiff <=0 -> >0
    conditions[1] = (prev.mtdiff <= 0) and (cur.mtdiff > 0)

    # 2/3/4. ST/MT/LT Diff trending up over the check window
    conditions[2] = _trend_up([b.stdiff for b in bars[slice_start: current_idx + 1]])
    conditions[3] = _trend_up([b.mtdiff for b in bars[slice_start: current_idx + 1]])
    conditions[4] = _trend_up([b.ltdiff for b in bars[slice_start: current_idx + 1]])

    # 5. Neural Index up (vs. prior bar)
    conditions[5] = cur.neural_index > prev.neural_index

    # 6. Predicted range direction up -- diffs vs. prior bar's predictions
    conditions[6] = (
        (cur.pred_high - prev.pred_high) > 0
        and (cur.pred_low - prev.pred_low) > 0
    )

    # 7. Last Triple Cross crossover was DOWN (reversal context)
    conditions[7] = _last_triple_cross_was_down(bars, current_idx)

    # 8. Predicted High > Close
    conditions[8] = cur.pred_high > cur.close

    # 9. Close < swing-high resistance (approximate)
    resistance = find_swing_high_resistance(bars, current_idx)
    conditions[9] = resistance is not None and cur.close < resistance

    return conditions, resistance


def detect_pattern(
    bars: list[VPBarRaw],
    current_idx: int,
) -> DetectionResult | None:
    """
    Evaluates all 9 Potential Crossover v12 conditions at bars[current_idx]
    via _evaluate_conditions, then resolves the STRICT/RELAXED tier.
    Requires at least BULK_TREND_CHECK_BARS + 2 bars of history before
    current_idx. Returns None if neither tier's conditions are fully met.
    """
    min_history = BULK_TREND_CHECK_BARS + 2
    if current_idx < min_history:
        return None

    conditions, resistance = _evaluate_conditions(bars, current_idx)

    strict_pass = all(conditions[i] for i in range(1, 10))
    relaxed_pass = all(conditions[i] for i in range(1, 10) if i != 7)

    if strict_pass:
        tier = DetectionTier.STRICT
    elif relaxed_pass:
        tier = DetectionTier.RELAXED
    else:
        return None

    return DetectionResult(
        tier=tier,
        resistance_level=resistance if resistance is not None else 0.0,
        conditions_passed=conditions,
    )


def _last_triple_cross_was_down(bars: list[VPBarRaw], current_idx: int) -> bool:
    """
    Scans backward from current_idx for the most recent sign flip in
    triple_cross_short. A flip from >0 to <=0 counts as the last
    crossover being DOWN. Returns False if no flip is found within the
    available history (condition 7 fails rather than raising -- absence
    of a decodable crossover is not a match).
    """
    for i in range(current_idx, 0, -1):
        prev_sign = bars[i - 1].triple_cross_short
        cur_sign = bars[i].triple_cross_short
        if prev_sign > 0 and cur_sign <= 0:
            return True
        if prev_sign <= 0 and cur_sign > 0:
            return False
    return False
