"""signal_builder.py — pure construction logic for signal packets.

Generates signal IDs and filenames and assembles a validated
P400SignalRecord. No file or network I/O occurs here; the sequence
number is supplied by the infrastructure layer.
"""

from __future__ import annotations

import config
from schemas import P400SignalRecord, SignalContext, SignalMetadata


def build_signal_id(session_date: str, symbol: str, seq: int) -> str:
    """Return a signal ID like 'P115-2026-06-03-AMTM-001'."""
    return config.SIGNAL_ID_PATTERN.format(date=session_date, symbol=symbol, seq=seq)


def build_filename(session_date: str, symbol: str, seq: int) -> str:
    """Return the .json filename for a signal.

    Seq 1  -> '2026-06-03_AMTM_signal.json' (schema-doc form).
    Seq >=2 -> '2026-06-03_AMTM_signal_002.json' (no overwrite).
    """
    base = config.FILENAME_BASE.format(date=session_date, symbol=symbol)
    if seq > 1:
        base = f"{base}_{seq:03d}"
    return f"{base}{config.FILENAME_EXT}"


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
    signal_source: str = config.DEFAULT_SOURCE,
) -> P400SignalRecord:
    """Assemble and validate one complete signal packet."""
    context = SignalContext(
        atm_at_signal=atm_at_signal,
        close_at_signal=close_at_signal,
        trailing_volume_30d=trailing_volume_30d,
        signal_rationale=signal_rationale,
    )
    metadata = SignalMetadata(
        p115_session_date=session_date,
        p115_chart_timeframe=chart_timeframe,
        signal_source_link=signal_source_link,
    )
    return P400SignalRecord(
        signal_id=build_signal_id(session_date, symbol, seq),
        signal_timestamp=signal_timestamp,
        signal_source=signal_source,
        strategy=strategy,
        symbol=symbol,
        guideline_entry=guideline_entry,
        guideline_stop=guideline_stop,
        guideline_target=guideline_target,
        signal_horizon=signal_horizon,
        confidence_level=confidence_level,
        context=context,
        signal_metadata=metadata,
    )