"""test_oscillators.py -- WO-P400-E4.003. Permanent regression suite."""

from __future__ import annotations

from domain.oscillators import compute_macd, compute_rsi


def test_rsi_all_gains_is_100():
    closes = [float(i) for i in range(1, 20)]  # strictly increasing
    rsi = compute_rsi(closes, period=14)
    assert rsi.value == 100.0
    assert rsi.interpretation == "overbought"


def test_rsi_all_losses_is_0():
    closes = [float(i) for i in range(20, 1, -1)]  # strictly decreasing
    rsi = compute_rsi(closes, period=14)
    assert rsi.value == 0.0
    assert rsi.interpretation == "oversold"


def test_rsi_insufficient_data_returns_none():
    assert compute_rsi([1.0, 2.0, 3.0], period=14) is None


def test_rsi_neutral_band():
    # Alternating up/down of equal magnitude -> avg_gain == avg_loss -> RSI == 50.
    closes = [100.0]
    for i in range(20):
        closes.append(closes[-1] + (1.0 if i % 2 == 0 else -1.0))
    rsi = compute_rsi(closes, period=14)
    assert 45.0 < rsi.value < 55.0
    assert rsi.interpretation == "neutral"


def test_macd_flat_series_is_near_zero():
    """Constant price -> both EMAs converge to the same value -> MACD ~ 0."""
    closes = [100.0] * 60
    macd = compute_macd(closes, fast=12, slow=26, signal=9)
    assert abs(macd.macd_line) < 0.01
    assert abs(macd.histogram) < 0.01


def test_macd_insufficient_data_returns_none():
    assert compute_macd([100.0] * 20, fast=12, slow=26, signal=9) is None


def test_macd_uptrend_is_positive():
    closes = [100.0 + i * 0.5 for i in range(60)]  # steady uptrend
    macd = compute_macd(closes, fast=12, slow=26, signal=9)
    assert macd.macd_line > 0
    assert macd.cross_state == "above signal"