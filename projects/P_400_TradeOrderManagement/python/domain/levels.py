"""levels.py -- Bollinger Bands, pivot S/R, Fibonacci retracement for the
technical dossier (WO-P400-E4.003). Pure logic, no I/O.

Fibonacci: level = swing_high - fib_ratio * (swing_high - swing_low),
swing_high/swing_low = simple rolling max(high)/min(low) over the lookback
window. Confirmed exact against P_400_2A_Analysis_Chart's actual
ThinkScript source (Tony pasted it 2026-07-24): swingHigh = Highest(high,
fibLookback), swingLow = Lowest(low, fibLookback) -- no pivot/local-extremum
logic at all. An earlier draft used P_300's pivot-window algorithm
(swing_detector.py) on the wrong assumption that "significant swing" meant
a local turning point -- confirmed wrong via live spot-check same day.
That algorithm solves a different problem (P_300 needs the nearest local
resistance pivot); Fibonacci here just needs the window's simple extent.
swing_detector.py dependency dropped entirely for this function.
"""

from __future__ import annotations

import statistics
from typing import NamedTuple, Optional, Sequence

Bar = tuple[float, float, float]  # (high, low, close) -- same convention as atr.py

FIB_RATIOS = (0.236, 0.382, 0.500, 0.618, 0.786)


class BollingerResult(NamedTuple):
    lower: float
    middle: float
    upper: float
    percent_b: float
    band_state: str   # "squeeze" | "expanded" | "normal"


class PivotLevels(NamedTuple):
    pivot: float
    r1: float
    r2: float
    r3: float
    s1: float
    s2: float
    s3: float


class FibResult(NamedTuple):
    swing_high: float
    swing_low: float
    levels: dict   # {0.236: price, 0.382: price, ...}


def compute_bollinger(
    closes: Sequence[float], period: int = 20, num_std: float = 2.0,
    width_lookback: int = 20,
) -> Optional[BollingerResult]:
    """Bollinger Bands with %B and a simple squeeze/expansion read.

    band_state compares current bandwidth (as % of middle) to the mean
    bandwidth over the trailing width_lookback periods before it -- below
    that mean = squeeze, above = expanded, within +-10% = normal. This is
    a simplified read, not TOS's exact proprietary squeeze algorithm.
    """
    if len(closes) < period + width_lookback:
        return None

    def _band_at(end_idx: int) -> tuple[float, float, float]:
        window = closes[end_idx - period:end_idx]
        mid = sum(window) / period
        sd = statistics.pstdev(window)
        return mid - num_std * sd, mid, mid + num_std * sd

    lower, middle, upper = _band_at(len(closes))
    price = closes[-1]
    band_width = upper - lower
    percent_b = (price - lower) / band_width * 100 if band_width > 0 else 50.0

    hist_widths = []
    for i in range(len(closes) - width_lookback, len(closes)):
        lo, mid, up = _band_at(i)
        if mid > 0:
            hist_widths.append((up - lo) / mid)
    current_width_pct = band_width / middle if middle > 0 else 0.0
    avg_hist_width = sum(hist_widths) / len(hist_widths) if hist_widths else current_width_pct

    if current_width_pct < avg_hist_width * 0.9:
        band_state = "squeeze"
    elif current_width_pct > avg_hist_width * 1.1:
        band_state = "expanded"
    else:
        band_state = "normal"

    return BollingerResult(lower=lower, middle=middle, upper=upper,
                            percent_b=percent_b, band_state=band_state)


def compute_pivot_levels(prior_bar: Bar) -> PivotLevels:
    """Classic pivot points from the prior completed period's (high, low, close)."""
    high, low, close = prior_bar
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)
    return PivotLevels(pivot=pivot, r1=r1, r2=r2, r3=r3, s1=s1, s2=s2, s3=s3)


def compute_fibonacci(bars: Sequence[Bar], lookback_bars: int) -> Optional[FibResult]:
    """Fibonacci retracement over a simple rolling window.

    Matches P_400_2A_Analysis_Chart's ThinkScript exactly: swing_high =
    max(high) over the window, swing_low = min(low) over the window. No
    pivot/local-extremum detection -- confirmed that's genuinely all TOS
    does here (2026-07-24, Tony pasted the actual .ts source). Returns
    None if fewer than lookback_bars bars are available (never fabricates
    a window that isn't really there).
    """
    if len(bars) < lookback_bars:
        return None
    window = bars[-lookback_bars:]
    swing_high = max(b[0] for b in window)
    swing_low = min(b[1] for b in window)

    span = swing_high - swing_low
    levels = {ratio: swing_high - ratio * span for ratio in FIB_RATIOS}
    return FibResult(swing_high=swing_high, swing_low=swing_low, levels=levels)