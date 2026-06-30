"""
FILE: atr.py
VERSION: 1.0
DATE: 2026-06-10
AUTHOR: Anthony Zoppi + Claude
LAYER: domain (shared hub utility)
DESCRIPTION:
    Average True Range (ATR), Wilder's method -- shared hub utility.

    Computed by each evaluating project at evaluation time, on the OHLC
    bars it already holds, to produce a baseline guideline stop/target.
    Pure math: no I/O, no logging, no project-specific types. Callers pass
    plain (high, low, close) tuples in chronological order (oldest first),
    so this module stays decoupled from any one project's bar schema.

    Formula:
        TrueRange_t = max(
            high_t - low_t,
            abs(high_t - close_{t-1}),
            abs(low_t  - close_{t-1}),
        )
        ATR(period), Wilder RMA:
            seed  = mean(TR_0 .. TR_{period-1})          # first `period` TRs
            ATR_t = (ATR_{t-1} * (period - 1) + TR_t) / period

    Conventions:
        - The first bar has no prior close, so TR_0 = high_0 - low_0.
        - Fewer than `period` bars: returns the simple mean of the available
          True Ranges (graceful degrade for short live-candidate windows).
        - Empty input returns 0.0.

CHANGELOG:
    - 2026-06-10 v1.0: Initial release. Replaces P_300's high-low-only
      simple-average ATR proxy (_compute_atr_from_bars) with full True
      Range + Wilder smoothing. One formula shared across all evaluating
      projects via the editable install (shared_resources.python_utils).
"""
from __future__ import annotations

from collections.abc import Sequence

# One bar as (high, low, close). Callers adapt their own bar type to this.
Bar = tuple[float, float, float]


def true_range(high: float, low: float, prev_close: float) -> float:
    """Return the True Range of one bar given the prior bar's close.

    Args:
        high: Bar high.
        low: Bar low.
        prev_close: Close of the immediately preceding bar.

    Returns:
        max(high - low, abs(high - prev_close), abs(low - prev_close)).
    """
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def compute_atr_wilder(bars: Sequence[Bar], period: int = 14) -> float:
    """Compute ATR over a bar window using Wilder's smoothing.

    Args:
        bars: Sequence of (high, low, close) tuples in chronological order,
            oldest first.
        period: ATR lookback. Default 14.

    Returns:
        The Wilder ATR as a float. Returns 0.0 for empty input. With fewer
        than `period` bars, returns the simple mean of the available True
        Ranges.

    Raises:
        ValueError: If period is less than 1.
    """
    if period < 1:
        raise ValueError(f"period must be >= 1, got {period}")
    if not bars:
        return 0.0

    # True Range series. First bar has no prior close -> high - low.
    true_ranges: list[float] = [bars[0][0] - bars[0][1]]
    for i in range(1, len(bars)):
        high, low, _ = bars[i]
        prev_close = bars[i - 1][2]
        true_ranges.append(true_range(high, low, prev_close))

    # Fewer than `period` TRs: simple mean (graceful degrade).
    if len(true_ranges) < period:
        return sum(true_ranges) / len(true_ranges)

    # Wilder seed = mean of the first `period` TRs, then recursive smoothing.
    atr = sum(true_ranges[:period]) / period
    for tr in true_ranges[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr
