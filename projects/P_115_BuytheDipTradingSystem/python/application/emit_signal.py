"""emit_signal.py — orchestration for P_115 signal emission via P_800.

WO-P115-E1.001 refactor: signal emission now routes through P_800
vault_interface. No direct file I/O. P_115 produces signals; P_800
owns I/O.

CHANGELOG:
  v2.0  2026-06-04  Remove signal_writer.py dependency. Emit via
                    write_to_vault("P400SIG", ...). Architecture fix.
  v1.0  (legacy)    Direct file I/O via signal_writer.py (REMOVED).
"""

from __future__ import annotations

import sys
from pathlib import Path

import config
from domain.signal_builder import build_record

# Resolve Hub root for vault_interface namespace (shared_resources)
_HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
if str(_HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(_HUB_ROOT))

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
    signal_source: str = config.DEFAULT_SOURCE,
) -> bool:
    """Build, validate, and emit one signal packet via P_800.

    P_800 owns all I/O and routing. P_115 only produces signals.
    Returns True if written, False if skipped.

    Raises:
        ValueError: If validation fails.
        OSError: If vault write fails.
    """
    # Sequence numbering now handled by P_800; always emit seq=1
    seq = 1
    record = build_record(
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
        signal_source=signal_source,
        seq=seq,
    )

    # Convert Pydantic model to dict for P_800 vault interface
    signal_packet = record.model_dump(by_alias=True)

    # Emit via P_800 (P_115 no longer writes directly)
    return write_to_vault("P400SIG", signal_packet, overwrite=True)