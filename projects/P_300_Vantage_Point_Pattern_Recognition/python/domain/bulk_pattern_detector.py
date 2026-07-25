"""
FILE: domain/bulk_pattern_detector.py
VERSION: 1.0
DATE: 2026-07-08
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure-Python decode of "Potential Crossover v12" (WO-P300-E2.001
    Phase 1), evaluated against BulkBarRaw -- the REAL bulk export bar
    shape, verified against actual VP History Grid files (10/5/3/1-year,
    6-month, SPY/BP, VP-direct and IntelliScan-routed). No I/O, no DB,
    no print -- strictly testable in isolation.

    This is a SEPARATE evaluator from domain/pattern_detector.py, not a
    patched version of it. pattern_detector.py operates on VPBarRaw
    (live catalog schema); this operates on BulkBarRaw (bulk export
    schema). The two raw shapes differ in ways that change condition
    logic, not just field names:

      - Condition 5 (Neural Index up): VPBarRaw.neural_index is a
        numeric score (trend-compared against the prior bar).
        BulkBarRaw.neural_index is TEXT ('up'/'down') -- VP has
        already done the directional call; this checks the text
        directly, no comparison needed.
      - Condition 7 (last Triple Cross crossover DOWN): VPBarRaw's
        triple_cross_short is a small signed diff (sign-flip on that
        one field is the crossover). BulkBarRaw's tc_short/tc_medium/
        tc_long are PRICE LEVELS in the same magnitude as close --
        crossover is a sign-flip of (tc_short - tc_medium), verified
        against real data (SPY 2026-06-29: tc_short crosses below
        tc_medium exactly where a short-term downturn begins).

    Conditions 1-4, 6, 8, 9 carry the same logic as pattern_detector.py,
    just against BulkBarRaw field names. find_swing_high_resistance and
    _trend_up are shape-agnostic (operate on plain floats / bars with
    .high/.close) and are imported from pattern_detector.py rather than
    duplicated.

    STRICT = all 9 AND. RELAXED = all except condition 7. STRICT implies
    RELAXED; a bar passing STRICT is tagged STRICT only.

CHANGELOG:
    - 2026-07-08 v1.0: Initial release. Functions: _tc_crossed_down,
      _evaluate_bulk_conditions, detect_bulk_pattern. Verified conditions
      5 and 7 against real SPY/BP bulk exports before writing (see
      module docstring) -- corrects the assumptions pattern_detector.py
      would have carried if bulk had reused it.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import BULK_TREND_CHECK_BARS  # noqa: E402
from domain.pattern_detector import _trend_up, find_swing_high_resistance  # noqa: E402
from schemas_bulk import BulkBarRaw, DetectionTier  # noqa: E402


@dataclass(frozen=True)
class BulkDetectionResult:
    """
    Outcome of evaluating all 9 conditions at one bulk bar.
    conditions_passed is keyed 1-9 matching the WO's numbering, for
    audit trail and for reproducing the WO's sample-file detection
    counts exactly.
    """
    tier: DetectionTier
    resistance_level: float
    conditions_passed: dict[int, bool] = field(default_factory=dict)


def _tc_crossed_down(bars: list[BulkBarRaw], current_idx: int) -> bool:
    """
    Scans backward from current_idx for the most recent sign flip of
    (tc_short - tc_medium). A flip from >0 to <=0 counts as the last
    Triple Cross crossover being DOWN. Returns False if no flip is
    found within available history (condition 7 fails rather than
    raising -- absence of a decodable crossover is not a match).
    """
    for i in range(current_idx, 0, -1):
        prev_diff = bars[i - 1].tc_short - bars[i - 1].tc_medium
        cur_diff = bars[i].tc_short - bars[i].tc_medium
        if prev_diff > 0 and cur_diff <= 0:
            return True
        if prev_diff <= 0 and cur_diff > 0:
            return False
    return False


def _evaluate_bulk_conditions(
    bars: list[BulkBarRaw],
    current_idx: int,
) -> tuple[dict[int, bool], float | None]:
    """
    Evaluates all 9 Potential Crossover v12 conditions at
    bars[current_idx]. Returns (conditions_passed keyed 1-9,
    resistance_level_or_None). Split out of detect_bulk_pattern to
    stay under the 50-line function limit.
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

    # 5. Neural Index up -- TEXT field, VP has already made the call
    conditions[5] = cur.neural_index == "up"

    # 6. Predicted range direction up -- diffs vs. prior bar's predictions
    conditions[6] = (
        (cur.pred_high - prev.pred_high) > 0
        and (cur.pred_low - prev.pred_low) > 0
    )

    # 7. Last Triple Cross crossover was DOWN -- tc_short vs tc_medium
    conditions[7] = _tc_crossed_down(bars, current_idx)

    # 8. Predicted High > Close
    conditions[8] = cur.pred_high > cur.close

    # 9. Close < swing-high resistance (approximate)
    resistance = find_swing_high_resistance(bars, current_idx)
    conditions[9] = resistance is not None and cur.close < resistance

    return conditions, resistance


def detect_bulk_pattern(
    bars: list[BulkBarRaw],
    current_idx: int,
) -> BulkDetectionResult | None:
    """
    Evaluates all 9 Potential Crossover v12 conditions at
    bars[current_idx] via _evaluate_bulk_conditions, then resolves the
    STRICT/RELAXED tier. Requires at least BULK_TREND_CHECK_BARS + 2
    bars of history before current_idx. Returns None if neither tier's
    conditions are fully met.
    """
    min_history = BULK_TREND_CHECK_BARS + 2
    if current_idx < min_history:
        return None

    conditions, resistance = _evaluate_bulk_conditions(bars, current_idx)

    strict_pass = all(conditions[i] for i in range(1, 10))
    relaxed_pass = all(conditions[i] for i in range(1, 10) if i != 7)

    if strict_pass:
        tier = DetectionTier.STRICT
    elif relaxed_pass:
        tier = DetectionTier.RELAXED
    else:
        return None

    return BulkDetectionResult(
        tier=tier,
        resistance_level=resistance if resistance is not None else 0.0,
        conditions_passed=conditions,
    )
