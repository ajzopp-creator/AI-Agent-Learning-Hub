"""Tests for WO-P400-E8.002: application/batch_2b_scoring.py's per-symbol
skip when the earnings cache can't confirm a missing symbol clear.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_batch_2b_scoring.py -v
"""

from application import batch_2b_scoring as scoring_mod
from application.earnings_lookup import SOURCE_GATE_UNCERTAIN
from config import TradeMode
from schemas import EarningsEntry
from shared_resources.python_utils.signal_schemas import SignalV2


def _make_packet(symbol: str = "TEST", asset_class: str = "stock") -> SignalV2:
    return SignalV2(
        signal_id=f"P300-2026-06-12-{symbol}-001",
        signal_timestamp="2026-06-12T13:00:00Z",
        signal_source="P_300",
        strategy="pattern_analog",
        symbol=symbol,
        asset_class=asset_class,
        guideline_entry=100.0,
        guideline_stop=95.0,
        guideline_target=110.0,
        signal_horizon="5 trading days",
        confidence_level="HIGH",
        position_size=0,
        context={
            "close_at_signal": 100.0,
            "trailing_volume_30d": 1000000.0,
            "signal_rationale": "test",
            "atm_at_signal": 1.0,
        },
        signal_metadata={
            "session_date": "2026-06-12",
            "chart_timeframe": "1D",
            "signal_source_link": "test",
        },
    )


def test_process_symbol_skips_gate_uncertain_earnings_entry():
    """WO-P400-E8.002: a symbol whose earnings entry is SOURCE_GATE_UNCERTAIN
    (cache too old to confirm clear for today's gate window) must be
    skipped, not silently scored as if earnings were confirmed clear.
    Returns before touching snapshot fetch / evaluate_signal -- cash,
    trade_mode, params, posture are never used on this path."""
    packet = _make_packet("ZZZZ")
    entries = {
        "ZZZZ": EarningsEntry(
            symbol="ZZZZ",
            next_earnings_date=None,
            source=SOURCE_GATE_UNCERTAIN,
            date_confirmed=False,
        )
    }
    skipped = []

    result = scoring_mod._process_symbol(
        packet, entries, cash=0.0, trade_mode=TradeMode.REAL,
        params=None, posture=None, skipped=skipped,
    )

    assert result is None
    assert len(skipped) == 1
    assert skipped[0]["symbol"] == "ZZZZ"
    assert "WO-P400-E8.002" in skipped[0]["reason"]


def test_process_symbol_missing_earnings_entry_still_skips():
    """Existing behavior (WO-P400-E6.004), unchanged by E8.002 -- a symbol
    with NO entry at all in the dict still skips via the original check,
    a distinct path from the new gate-uncertain branch above."""
    packet = _make_packet("YYYY")
    skipped = []

    result = scoring_mod._process_symbol(
        packet, {}, cash=0.0, trade_mode=TradeMode.REAL,
        params=None, posture=None, skipped=skipped,
    )

    assert result is None
    assert len(skipped) == 1
    assert "no earnings calendar entry" in skipped[0]["reason"]
