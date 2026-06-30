"""emit_signal.py -- orchestration for P_115 signal emission via P_800.

WO-P115-E1.001 / WO-P800-E2.001: P_115 emits SIGNAL_V2 packets via P_800
vault_interface. No direct file I/O. P_115 produces signals; P_800 owns I/O.

CHANGELOG:
  v2.2  2026-06-16  Added stop enrichment params: intelliscan_support_1,
                    intelliscan_support_2. Computes atr_adjusted_stop from
                    atm_at_signal. WO-P115-E2.001.
  v2.1  2026-06-11  Migrated from write_to_vault("P400SIG") to
                    write_to_vault("SIGNAL_V2"). signal_builder now returns
                    a plain dict matching SignalV2 schema (stock variant).
  v2.0  2026-06-04  Removed signal_writer.py dependency. Emitted via P400SIG.
  v1.0  (legacy)    Direct file I/O via signal_writer.py (removed).
"""

from __future__ import annotations

import config
from domain.signal_builder import build_record

from shared_resources.python_utils.vault_interface import write_to_vault


def emit_signal(
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
    atm_at_signal: float | None = None,
    intelliscan_support_1: float | None = None,
    intelliscan_support_2: float | None = None,
    signal_source: str = config.DEFAULT_SOURCE,
) -> bool:
    """Build and emit one SIGNAL_V2 stock packet via P_800.

    P_800 owns all I/O and routing. P_115 only produces signals.

    Stop enrichment (WO-P115-E2.001):
        atr_adjusted_stop is computed here from guideline_entry and
        atm_at_signal (entry - 1x ATR). None if atm_at_signal is None.

        intelliscan_support_1: Chart structural stop supplied by caller
            (support level, consolidation base, or pattern invalidation point).
        intelliscan_support_2: Secondary structural level supplied by caller
            (next major support below S1; None if not identifiable).

    Args:
        symbol: Uppercase ticker.
        session_date: YYYY-MM-DD of the generating session.
        signal_timestamp: ISO 8601 UTC timestamp of signal generation.
        strategy: Strategy label (e.g. "dip_buy").
        guideline_entry: Recommended entry price.
        guideline_stop: Recommended stop-loss price (chart structural stop).
        guideline_target: Recommended profit target price.
        signal_horizon: e.g. "3-5 days".
        confidence_level: HIGH | MEDIUM | LOW.
        close_at_signal: Closing price at time of signal.
        trailing_volume_30d: 30-day average daily volume.
        signal_rationale: Short thesis summary.
        chart_timeframe: e.g. "1D".
        signal_source_link: Path to upstream .md audit note.
        atm_at_signal: ATR(14) at signal time (optional).
        intelliscan_support_1: Chart structural stop (optional).
        intelliscan_support_2: Secondary structural level (optional).
        signal_source: Originating strategy ID (default P_115).

    Returns:
        True if written, False if skipped (e.g. overwrite=False and exists).

    Raises:
        ValueError: If validation fails.
        OSError: If vault write fails.
    """
    atr_adjusted_stop: float | None = (
        round(guideline_entry - atm_at_signal, 4)
        if atm_at_signal is not None
        else None
    )

    packet = build_record(
        symbol=symbol,
        session_date=session_date,
        signal_timestamp=signal_timestamp,
        strategy=strategy,
        guideline_entry=guideline_entry,
        guideline_stop=guideline_stop,
        guideline_target=guideline_target,
        signal_horizon=signal_horizon,
        confidence_level=confidence_level,
        close_at_signal=close_at_signal,
        trailing_volume_30d=trailing_volume_30d,
        signal_rationale=signal_rationale,
        chart_timeframe=chart_timeframe,
        signal_source_link=signal_source_link,
        atm_at_signal=atm_at_signal,
        atr_adjusted_stop=atr_adjusted_stop,
        intelliscan_support_1=intelliscan_support_1,
        intelliscan_support_2=intelliscan_support_2,
        signal_source=signal_source,
        seq=1,
    )

    return write_to_vault(config.VAULT_SCHEMA, packet, overwrite=True)