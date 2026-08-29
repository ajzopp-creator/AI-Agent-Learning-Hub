"""
FILE: domain/strategy_engine.py
VERSION: 1.0
DATE: 2026-08-26
AUTHOR: Tony + Claude
LAYER: domain
DESCRIPTION:
    States 1-3 of the Break-and-Retest FSM (BREAKOUT_PENDING, RETEST_LOOKUP,
    IN_TRADE). Pure logic, no I/O. Long-only -- a resistance zone becomes
    support on a confirmed breakout + retest, per the uploaded spec.

CHANGELOG:
    - 2026-08-26 v1.0: Initial build.
"""
from __future__ import annotations

from typing import Literal, NamedTuple

from domain.zone_finder import Zone

TradeExitReason = Literal["stop", "target", "time"]


class RawSignal(NamedTuple):
    """Zone-agnostic trade result -- application layer adds symbol + zone."""
    breakout_idx: int
    retest_idx: int
    entry_idx: int
    entry_price: float
    stop_loss: float
    take_profit: float
    exit_idx: int
    exit_price: float
    r_multiple: float
    exit_reason: TradeExitReason
    is_win: bool


def volume_sma(bars, period: int) -> list[float | None]:
    """Rolling simple average of volume. First `period` bars are None."""
    sma: list[float | None] = [None] * len(bars)
    for i in range(period - 1, len(bars)):
        window = bars[i - period + 1: i + 1]
        sma[i] = sum(b.volume for b in window) / period
    return sma


def detect_breakout(bars, zone: Zone, vol_sma, vol_mult: float) -> int | None:
    """Scans forward from zone formation for a clean close above zone_high
    on volume >= vol_mult * its SMA. Returns the breakout bar index."""
    for i in range(zone.formed_idx + 1, len(bars)):
        if vol_sma[i] is None:
            continue
        clean_close = bars[i].close > zone.zone_high
        volume_surge = bars[i].volume > vol_mult * vol_sma[i]
        if clean_close and volume_surge:
            return i
    return None


def detect_retest(
    bars, zone: Zone, breakout_idx: int, max_bars: int, wick_ratio: float
) -> int | None:
    """Scans forward from the breakout for a retest + rejection candle.
    Returns None if the setup expires or invalidates, else the rejection
    bar index."""
    window_end = min(breakout_idx + max_bars, len(bars) - 1)
    for i in range(breakout_idx + 1, window_end + 1):
        bar = bars[i]

        if bar.close < zone.zone_low:
            return None  # invalidation -- closed back through the zone

        touches_zone = bar.low <= zone.zone_high and bar.high >= zone.zone_low
        candle_range = bar.high - bar.low
        if candle_range <= 0:
            continue
        body_min = min(bar.open, bar.close)
        lower_wick = body_min - bar.low
        wick_pct = lower_wick / candle_range

        if touches_zone and wick_pct >= wick_ratio:
            return i
    return None


def simulate_trade(
    bars, entry_idx: int, entry_price: float, stop_loss: float,
    min_rr: float, max_hold_bars: int,
) -> tuple[int, float, float, TradeExitReason]:
    """Walks forward bar-by-bar until stop, target, or max hold is hit."""
    risk_per_share = entry_price - stop_loss
    take_profit = entry_price + min_rr * risk_per_share
    window_end = min(entry_idx + max_hold_bars, len(bars) - 1)

    for i in range(entry_idx + 1, window_end + 1):
        bar = bars[i]
        if bar.low <= stop_loss:
            r = (stop_loss - entry_price) / risk_per_share
            return i, stop_loss, r, "stop"
        if bar.high >= take_profit:
            r = (take_profit - entry_price) / risk_per_share
            return i, take_profit, r, "target"

    exit_bar = bars[window_end]
    r = (exit_bar.close - entry_price) / risk_per_share
    return window_end, exit_bar.close, r, "time"


def evaluate_zone(
    bars, zone: Zone, atr, vol_sma, vol_mult: float,
    stop_atr_buffer: float, min_rr: float,
    retest_max_bars: int, retest_wick_ratio: float, max_hold_bars: int,
) -> RawSignal | None:
    """Runs the full State 1-3 sequence for one zone. None if no trade fired."""
    breakout_idx = detect_breakout(bars, zone, vol_sma, vol_mult)
    if breakout_idx is None:
        return None

    retest_idx = detect_retest(bars, zone, breakout_idx, retest_max_bars, retest_wick_ratio)
    if retest_idx is None:
        return None

    entry_idx = retest_idx
    entry_price = bars[entry_idx].close
    bar_atr = atr[entry_idx] or 0.0
    stop_loss = zone.zone_low - stop_atr_buffer * bar_atr
    if stop_loss >= entry_price:
        return None  # degenerate risk (ATR warmup or bad zone) -- skip

    exit_idx, exit_price, r_multiple, exit_reason = simulate_trade(
        bars, entry_idx, entry_price, stop_loss, min_rr, max_hold_bars
    )
    take_profit = entry_price + min_rr * (entry_price - stop_loss)

    return RawSignal(
        breakout_idx=breakout_idx,
        retest_idx=retest_idx,
        entry_idx=entry_idx,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        exit_idx=exit_idx,
        exit_price=exit_price,
        r_multiple=r_multiple,
        exit_reason=exit_reason,
        is_win=r_multiple > 0,
    )


def summarize_signals(signals) -> dict:
    """Aggregate win rate and average R across all fired signals."""
    if not signals:
        return {"total": 0, "wins": 0, "win_rate": 0.0, "avg_r": 0.0}
    wins = sum(1 for s in signals if s.is_win)
    avg_r = sum(s.r_multiple for s in signals) / len(signals)
    return {
        "total": len(signals),
        "wins": wins,
        "win_rate": wins / len(signals),
        "avg_r": avg_r,
    }
