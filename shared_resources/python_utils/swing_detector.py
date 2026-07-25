"""swing_detector.py -- swing-high/swing-low pivot detection, shared hub
utility (WO-P400-E4.003).

Generalized from P_300's find_swing_high_resistance()
(projects\P_300_Vantage_Point_Pattern_Recognition\python\domain\
pattern_detector.py) -- same pivot-window algorithm, plain Bar tuples
instead of VPBarRaw, same pattern as atr.py's generalization. P_300's own
file is untouched by this WO; this is a new shared module, not a
migration.

A pivot high is a bar whose high exceeds the high of every bar within
pivot_bars on both sides. A pivot low is the symmetric case on lows.
Both search backward from current_idx across lookback_bars and return the
nearest (most recent) qualifying pivot, or None if none exists.

price_filter is optional (None = no filter, matches Fibonacci's need for
the swing's actual extremes). P_300's original always filtered swing
highs to price > current_close (resistance above price) -- callers that
want that behavior pass price_filter=lambda p: p > current_close.
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

# One bar as (high, low, close), oldest-first -- same convention as atr.py.
Bar = tuple[float, float, float]


def _find_pivot(
    bars: Sequence[Bar],
    current_idx: int,
    lookback_bars: int,
    pivot_bars: int,
    get_price: Callable[[Bar], float],
    find_max: bool,
    price_filter: Optional[Callable[[float], bool]] = None,
) -> Optional[float]:
    """Shared pivot search. find_max=True looks for pivot highs (window
    max), False looks for pivot lows (window min)."""
    earliest = max(pivot_bars, current_idx - lookback_bars)
    candidates: list[tuple[int, float]] = []

    for i in range(current_idx - pivot_bars, earliest - 1, -1):
        if i - pivot_bars < 0 or i + pivot_bars > current_idx:
            continue
        window = [get_price(bars[j]) for j in range(i - pivot_bars, i + pivot_bars + 1)]
        pivot_price = get_price(bars[i])
        window_extreme = max(window) if find_max else min(window)
        if pivot_price != window_extreme:
            continue
        if price_filter is not None and not price_filter(pivot_price):
            continue
        candidates.append((i, pivot_price))

    if not candidates:
        return None

    # Nearest = most recent pivot (highest index), not most extreme price.
    candidates.sort(key=lambda pair: pair[0], reverse=True)
    return candidates[0][1]


def find_swing_high(
    bars: Sequence[Bar],
    current_idx: int,
    lookback_bars: int,
    pivot_bars: int,
    price_filter: Optional[Callable[[float], bool]] = None,
) -> Optional[float]:
    """Nearest pivot high within lookback_bars of current_idx, or None."""
    return _find_pivot(
        bars, current_idx, lookback_bars, pivot_bars,
        get_price=lambda b: b[0], find_max=True, price_filter=price_filter,
    )


def find_swing_low(
    bars: Sequence[Bar],
    current_idx: int,
    lookback_bars: int,
    pivot_bars: int,
    price_filter: Optional[Callable[[float], bool]] = None,
) -> Optional[float]:
    """Nearest pivot low within lookback_bars of current_idx, or None."""
    return _find_pivot(
        bars, current_idx, lookback_bars, pivot_bars,
        get_price=lambda b: b[1], find_max=False, price_filter=price_filter,
    )