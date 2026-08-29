"""
FILE: application/backtest_runner.py
VERSION: 1.1
DATE: 2026-08-26
AUTHOR: Tony + Claude
LAYER: application
DESCRIPTION:
    Orchestrates the Break-and-Retest backtest end to end: loads every
    bulk VP export in config.DATA_DIR, runs the FSM (domain) per symbol,
    and logs a per-symbol + aggregate summary. No raw logic here --
    calls infrastructure for I/O and domain for the strategy math only.

CHANGELOG:
    - 2026-08-26 v1.1: Per-file load errors (bad filename, bad row data)
      now log a warning and skip that file instead of crashing the whole
      batch -- a 111-file real-world folder is expected to have at least
      one malformed name (observed: 10_Pattern_APTV).xlsx, stray paren).
    - 2026-08-26 v1.0: Initial build.
"""
from __future__ import annotations

import logging

import config
from domain.strategy_engine import evaluate_zone, summarize_signals, volume_sma
from domain.zone_finder import cluster_zones, compute_atr, find_swing_highs
from infrastructure.data_loader import find_bulk_files, load_bulk_file
from schemas import BreakRetestSignal

logger = logging.getLogger(__name__)


def run_symbol(symbol: str, bars) -> list[BreakRetestSignal]:
    """Runs the full FSM for one symbol's bar history, zone by zone."""
    atr = compute_atr(bars, config.ATR_PERIOD)
    vol_sma = volume_sma(bars, config.VOLUME_SMA_PERIOD)
    swing_highs = find_swing_highs(bars, config.SWING_ORDER)
    zones = cluster_zones(bars, atr, swing_highs, config.ZONE_TOUCH_MIN, config.ZONE_ATR_MULT)

    signals: list[BreakRetestSignal] = []
    for zone in zones:
        raw = evaluate_zone(
            bars, zone, atr, vol_sma, config.VOLUME_SURGE_MULT,
            stop_atr_buffer=config.STOP_ATR_BUFFER,
            min_rr=config.MIN_RR,
            retest_max_bars=config.RETEST_MAX_BARS,
            retest_wick_ratio=config.RETEST_WICK_RATIO,
            max_hold_bars=config.MAX_HOLD_BARS,
        )
        if raw is None:
            continue
        signals.append(
            BreakRetestSignal(
                symbol=symbol,
                zone_low=zone.zone_low,
                zone_high=zone.zone_high,
                breakout_date=bars[raw.breakout_idx].bar_date,
                breakout_close=bars[raw.breakout_idx].close,
                retest_date=bars[raw.retest_idx].bar_date,
                entry_date=bars[raw.entry_idx].bar_date,
                entry_price=raw.entry_price,
                stop_loss=raw.stop_loss,
                take_profit=raw.take_profit,
                exit_date=bars[raw.exit_idx].bar_date,
                exit_price=raw.exit_price,
                r_multiple=raw.r_multiple,
                exit_reason=raw.exit_reason,
                is_win=raw.is_win,
            )
        )
    return signals


def run() -> None:
    """Entry point -- backtests every symbol in config.DATA_DIR and logs results."""
    logging.basicConfig(level=config.LOG_LEVEL, format="%(message)s")
    files = find_bulk_files(config.DATA_DIR, config.FILE_GLOB_PATTERN)
    if not files:
        logger.warning("No files found in %s matching %s", config.DATA_DIR, config.FILE_GLOB_PATTERN)
        return

    all_signals: list[BreakRetestSignal] = []
    skipped: list[str] = []
    for filepath in files:
        try:
            symbol, bars = load_bulk_file(filepath)
        except ValueError as exc:
            logger.warning("SKIPPED %s: %s", filepath.name, exc)
            skipped.append(filepath.name)
            continue

        signals = run_symbol(symbol, bars)
        summary = summarize_signals(signals)
        logger.info(
            "%-6s  signals=%-3d wins=%-3d win_rate=%.1f%%  avg_r=%.2f",
            symbol, summary["total"], summary["wins"], summary["win_rate"] * 100, summary["avg_r"],
        )
        all_signals.extend(signals)

    overall = summarize_signals(all_signals)
    logger.info("-" * 50)
    logger.info(
        "TOTAL   signals=%-3d wins=%-3d win_rate=%.1f%%  avg_r=%.2f",
        overall["total"], overall["wins"], overall["win_rate"] * 100, overall["avg_r"],
    )
    if skipped:
        logger.info("Skipped %d file(s): %s", len(skipped), ", ".join(skipped))
