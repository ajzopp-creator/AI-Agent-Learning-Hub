"""stock_fields.py -- build the write_p400_record() kwargs dict for a
plain stock evaluate/spec result (WO-P400-E3.006).

Shared by commands.py cmd_evaluate() and cmd_spec() so the stock-path
cache-field mapping lives in exactly one place, matching the pattern
already used for options (record_writer._build_options_fields) and
spread (record_writer._build_spread_fields).
"""

from __future__ import annotations


def build_stock_fields(result, packet, trade_mode_value: str) -> dict:
    """Assemble write_p400_record() kwargs from a stock EvaluationResult.

    position_size falls back to 0 if sizing was never computed (e.g. an
    early BLOCK before the sizing stage runs).
    """
    return dict(
        symbol=result.symbol,
        verdict=result.verdict,
        risk_mode=result.posture.risk_mode,
        entry_price=result.effective_entry,
        stop_price=result.effective_stop,
        target_1=packet.guideline_target,
        position_size=(result.sizing.shares if result.sizing else 0),
        signal_source=packet.signal_source,
        trade_mode_value=trade_mode_value,
        drop_reason=None,
        signal_date=packet.signal_metadata.session_date,
    )