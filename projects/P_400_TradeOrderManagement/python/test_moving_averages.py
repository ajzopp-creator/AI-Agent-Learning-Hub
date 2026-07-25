"""test_moving_averages.py -- WO-P400-E4.003. Permanent regression suite."""

from __future__ import annotations

from domain.moving_averages import aggregate_bars, compute_trend, sma


def test_sma_known_answer():
    closes = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert sma(closes, 5) == 3.0
    assert sma(closes, 3) == 4.0  # mean of [3,4,5]


def test_sma_insufficient_data_returns_none():
    assert sma([1.0, 2.0], 5) is None


def test_aggregate_bars_known_answer():
    bars = [(10, 8, 9), (12, 9, 11), (11, 10, 10.5), (13, 11, 12), (14, 12, 13)]
    grouped = aggregate_bars(bars, 5)
    assert grouped == [(14, 8, 13)]  # high=max highs, low=min lows, close=last close


def test_aggregate_bars_drops_trailing_partial_group():
    bars = [(10, 8, 9)] * 7  # 7 bars, group size 5 -> one full group, 2 dropped
    grouped = aggregate_bars(bars, 5)
    assert len(grouped) == 1


def test_compute_trend_bullish_crossover():
    # Constructed so SMA50 > SMA200: recent closes high, older closes low.
    closes = [50.0] * 150 + [200.0] * 50
    trend = compute_trend(closes, periods=(20, 50, 100, 200))
    assert trend.primary_trend == "bullish"
    assert "BULLISH" in trend.crossover_state


def test_compute_trend_bearish_crossover():
    closes = [200.0] * 150 + [50.0] * 50
    trend = compute_trend(closes, periods=(20, 50, 100, 200))
    assert trend.primary_trend == "bearish"
    assert "BEARISH" in trend.crossover_state


def test_compute_trend_insufficient_data_is_neutral():
    trend = compute_trend([100.0] * 30, periods=(20, 50, 100, 200))
    assert trend.primary_trend == "neutral"
    assert trend.crossover_state == "insufficient data"