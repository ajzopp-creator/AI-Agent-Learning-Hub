"""signal_builder.py -- pure construction logic for SIGNAL_V2 packets.

Builds a SignalV2-compatible dict for stock signals emitted by P_115.
No file or network I/O occurs here. The sequence number is supplied by
the application layer.

CHANGELOG:
  v2.1  2026-06-16  Added three stop enrichment fields: atr_adjusted_stop,
                    intelliscan_support_1, intelliscan_support_2.
                    WO-P115-E2.001 -- chart-derived stop levels for P_400 gate.
  v2.0  2026-06-11  Migrated from P400SignalRecord (v1.0) to SignalV2 dict
                    (WO-P115-E1.001 / WO-P800-E2.001). asset_class fixed to
                    "stock"; position_size defaults to 0; option fields null.
  v1.0  (legacy)    Returned P400SignalRecord Pydantic model.
"""

from __future__ import annotations

import config


def build_signal_id(session_date: str, symbol: str, seq: int) -> str:
    """Return a signal ID like 'P115-2026-06-03-AMTM-001'.

    Args:
        session_date: YYYY-MM-DD of the generating session.
        symbol: Uppercase ticker.
        seq: 1-based sequence number for this symbol+date.

    Returns:
        Formatted signal ID string.
    """
    return config.SIGNAL_ID_PATTERN.format(date=session_date, symbol=symbol, seq=seq)


def build_record(
    *,
    symbol: str,
    session_date: str,
    signal_timestamp: str,
    strategy: str,
    guideline_entry: float,
    guideline_stop: float,
    guideline_target: float,
    signal_horizon: str,
    confidence_level: str,
    close_at_signal: float,
    trailing_volume_30d: float,
    signal_rationale: str,
    chart_timeframe: str,
    signal_source_link: str,
    seq: int,
    atm_at_signal: float | None = None,
    atr_adjusted_stop: float | None = None,
    intelliscan_support_1: float | None = None,
    intelliscan_support_2: float | None = None,
    signal_source: str = config.DEFAULT_SOURCE,
) -> dict:
    """Assemble one SIGNAL_V2 stock packet as a plain dict.

    All option-specific fields are set to None (null in JSON). asset_class
    is always "stock" for P_115 signals. position_size defaults to 0 --
    P_400 will populate final sizing.

    Stop enrichment fields (WO-P115-E2.001):
        atr_adjusted_stop:      entry - 1x ATR(14). P_400 primary Quant-gate input.
        intelliscan_support_1:  Chart structural stop (support level, consolidation
                                base, or pattern invalidation point).
        intelliscan_support_2:  Secondary structural level (next major support below
                                S1 if identifiable; None otherwise).

    Args:
        symbol: Uppercase ticker.
        session_date: YYYY-MM-DD of the generating session.
        signal_timestamp: ISO 8601 UTC timestamp of signal generation.
        strategy: Strategy label (e.g. "dip_buy").
        guideline_entry: Recommended entry price.
        guideline_stop: Recommended stop-loss price.
        guideline_target: Recommended profit target price.
        signal_horizon: e.g. "10-15 trading days" (default: config.DEFAULT_SIGNAL_HORIZON).
        confidence_level: HIGH | MEDIUM | LOW.
        close_at_signal: Closing price at time of signal.
        trailing_volume_30d: 30-day average daily volume.
        signal_rationale: Short thesis summary.
        chart_timeframe: e.g. "1D".
        signal_source_link: Path to upstream .md audit note.
        seq: 1-based sequence number for this symbol+date.
        atm_at_signal: ATR(14) at signal time (optional).
        atr_adjusted_stop: entry - 1x ATR(14) (optional; None if ATR unavailable).
        intelliscan_support_1: Chart structural stop (optional).
        intelliscan_support_2: Secondary structural level (optional).
        signal_source: Originating strategy ID (default P_115).

    Returns:
        Dict matching the SIGNAL_V2 schema (stock variant).
    """
    return {
        "signal_id": build_signal_id(session_date, symbol, seq),
        "signal_timestamp": signal_timestamp,
        "signal_source": signal_source,
        "strategy": strategy,
        "symbol": symbol,
        "asset_class": "stock",
        "guideline_entry": guideline_entry,
        "guideline_stop": guideline_stop,
        "guideline_target": guideline_target,
        "atr_adjusted_stop": atr_adjusted_stop,
        "intelliscan_support_1": intelliscan_support_1,
        "intelliscan_support_2": intelliscan_support_2,
        "signal_horizon": signal_horizon,
        "confidence_level": confidence_level,
        "position_size": 0,
        "strike_price": None,
        "underlying_price": None,
        "option_type": None,
        "expiration_date": None,
        "context": {
            "close_at_signal": close_at_signal,
            "trailing_volume_30d": trailing_volume_30d,
            "signal_rationale": signal_rationale,
            "atm_at_signal": atm_at_signal,
        },
        "signal_metadata": {
            "session_date": session_date,
            "chart_timeframe": chart_timeframe,
            "signal_source_link": signal_source_link,
        },
    }