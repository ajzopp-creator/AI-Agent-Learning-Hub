"""test_levels.py -- WO-P400-E4.003. Permanent regression suite.

Fibonacci formula and swing-window logic both verified against real TOS
data during this WO's build -- see domain\levels.py module docstring.
"""

from __future__ import annotations

from domain.levels import compute_bollinger, compute_fibonacci, compute_pivot_levels


def test_pivot_levels_known_answer():
    # prior_bar = (high=110, low=100, close=105)
    pivots = compute_pivot_levels((110.0, 100.0, 105.0))
    assert pivots.pivot == 105.0
    assert pivots.r1 == 110.0
    assert pivots.s1 == 100.0
    assert pivots.r2 == 115.0
    assert pivots.s2 == 95.0
    assert pivots.r3 == 120.0
    assert pivots.s3 == 90.0


def test_bollinger_constant_series_zero_width():
    closes = [100.0] * 40  # period=20 + width_lookback=20
    bb = compute_bollinger(closes, period=20, num_std=2.0, width_lookback=20)
    assert bb.lower == bb.middle == bb.upper == 100.0
    assert bb.percent_b == 50.0
    assert bb.band_state == "normal"


def test_bollinger_insufficient_data_returns_none():
    assert compute_bollinger([100.0] * 10, period=20, num_std=2.0, width_lookback=20) is None


def test_fibonacci_known_answer():
    """Matches TOS's actual logic: swing_high = max(high) over the window,
    swing_low = min(low) over the window -- simple rolling extremes, no
    pivot detection."""
    bars = [(100.0, 90.0, 95.0)] * 58 + [(130.0, 90.0, 100.0), (100.0, 70.0, 80.0)]
    # 60 bars total; max high across all = 130.0 (2nd-to-last bar);
    # min low across all = 70.0 (last bar).
    fib = compute_fibonacci(bars, lookback_bars=60)
    assert fib.swing_high == 130.0
    assert fib.swing_low == 70.0
    span = 130.0 - 70.0
    assert abs(fib.levels[0.236] - (130.0 - 0.236 * span)) < 1e-9
    assert abs(fib.levels[0.500] - 100.0) < 1e-9
    assert abs(fib.levels[0.618] - (130.0 - 0.618 * span)) < 1e-9


def test_fibonacci_only_uses_last_lookback_bars():
    """A high outside the lookback window must not affect the result."""
    old_spike = [(500.0, 500.0, 500.0)]  # way outside the window, must be ignored
    recent = [(100.0, 90.0, 95.0)] * 60
    bars = old_spike + recent
    fib = compute_fibonacci(bars, lookback_bars=60)
    assert fib.swing_high == 100.0  # not 500.0
    assert fib.swing_low == 90.0


def test_fibonacci_insufficient_data_returns_none():
    bars = [(100.0, 90.0, 95.0)] * 30  # fewer than lookback_bars
    assert compute_fibonacci(bars, lookback_bars=60) is None