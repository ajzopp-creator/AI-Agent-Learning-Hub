"""test_evaluate_signal.py — Entry resolution rule tests (WO-P400-E2.009).

Tests Section 6.5: entry missed (adverse drift > 1.5% collapses R:R) and
favorable pullback (live < guideline, R:R improves, no block).
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from shared_resources.python_utils.signal_schemas import SignalV2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_packet(entry: float, stop: float, target: float, symbol: str = "TEST") -> SignalV2:
    return SignalV2(
        signal_id=f"P300-2026-06-12-{symbol}-001",
        signal_timestamp="2026-06-12T13:00:00Z",
        signal_source="P_300",
        strategy="pattern_analog",
        symbol=symbol,
        asset_class="stock",
        guideline_entry=entry,
        guideline_stop=stop,
        guideline_target=target,
        signal_horizon="5 trading days",
        confidence_level="HIGH",
        position_size=0,
        context={
            "close_at_signal": entry,
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


def _make_snapshot(price: float, entry: float, stop: float) -> dict:
    return {
        "symbol": "TEST",
        "price": price,
        "bid": price - 0.01,
        "ask": price + 0.01,
        "price_timestamp": datetime.now(timezone.utc).isoformat(),
        "price_delay_seconds": 5,
        "atr_14": abs(entry - stop),
        "avg_volume_20d": 1000000,
        "data_source": "web",
        "today_volume": None,
        "next_earnings_date": None,
        "binary_events": [],
        "sector": None,
        "iv_rank": None,
        "option_chain_ref": None,
        "market_open": True,
        "guideline_stop_override": None,
    }


def _mock_infra(posture="STANDARD", balance=32669.72, risk=490.04, max_pos=1633.47):
    """Return patch targets for infra reads."""
    posture_mock = MagicMock(risk_mode=posture, avg_posture=0.0)
    params_mock = MagicMock(
        account_balance=balance,
        risk_per_trade=risk,
        max_position=max_pos,
    )
    records_mock = []
    return posture_mock, params_mock, records_mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_entry_missed_adverse_drift_blocks():
    """Adverse drift > 1.5% that collapses R:R below 2.0 returns BLOCKED."""
    # entry=100, stop=98, target=104 -> R:R = 2.0 at guideline
    # live price=102 (+2% drift) -> risk=4, reward=2 -> R:R=0.5 -> BLOCK
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)
    snap = _make_snapshot(price=102.0, entry=100.0, stop=98.0)

    posture_mock, params_mock, records_mock = _mock_infra()

    with patch("application.evaluate_signal.read_posture", return_value=posture_mock), \
         patch("application.evaluate_signal.read_params", return_value=params_mock), \
         patch("application.evaluate_signal.load_book", return_value=records_mock):

        from application.evaluate_signal import evaluate_signal
        result = evaluate_signal(packet, snap, cash_available=5000.0)

    assert result.verdict == "BLOCKED"
    assert "ENTRY_MISSED" in result.council.block_codes[0] or \
           any("ENTRY_MISSED" in str(v.reason_detail) for v in result.council.votes)


def test_favorable_drift_proceeds():
    """Favorable drift (live < guideline) does not block — R:R improves."""
    # entry=100, stop=98, target=104 -> R:R=2.0 at guideline
    # live=99 (-1% drift) -> risk=1, reward=5 -> R:R=5.0 -> no block from drift
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)
    snap = _make_snapshot(price=99.0, entry=100.0, stop=98.0)

    posture_mock, params_mock, records_mock = _mock_infra()

    with patch("application.evaluate_signal.read_posture", return_value=posture_mock), \
         patch("application.evaluate_signal.read_params", return_value=params_mock), \
         patch("application.evaluate_signal.load_book", return_value=records_mock):

        from application.evaluate_signal import evaluate_signal
        result = evaluate_signal(packet, snap, cash_available=5000.0)

    # Should not be blocked by drift — may be blocked by other council gates
    # but not by ADVERSE_DRIFT / ENTRY_MISSED
    drift_blocks = [c for c in result.council.block_codes if "DRIFT" in c or "MISSED" in c]
    assert drift_blocks == [], f"Unexpected drift block on favorable pullback: {drift_blocks}"
    assert result.drift_pct < 0  # confirmed favorable


# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# effective_entry / effective_stop exposure (BLOCKED-write fix support)
# ---------------------------------------------------------------------------

def test_effective_fields_populated_normal_path():
    """EvaluationResult exposes the live entry and effective stop actually used,
    even when the verdict is BLOCKED for a non-drift reason (e.g. Quant stop-tight)."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)
    snap = _make_snapshot(price=99.0, entry=100.0, stop=98.0)

    posture_mock, params_mock, records_mock = _mock_infra()

    with patch("application.evaluate_signal.read_posture", return_value=posture_mock), \
         patch("application.evaluate_signal.read_params", return_value=params_mock), \
         patch("application.evaluate_signal.load_book", return_value=records_mock):

        from application.evaluate_signal import evaluate_signal
        result = evaluate_signal(packet, snap, cash_available=5000.0)

    assert result.effective_entry == 99.0
    assert result.effective_stop == 98.0


def test_effective_fields_populated_entry_missed_path():
    """EvaluationResult exposes effective_entry/effective_stop on the early
    ENTRY_MISSED return path too, not just the normal return."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)
    snap = _make_snapshot(price=102.0, entry=100.0, stop=98.0)

    posture_mock, params_mock, records_mock = _mock_infra()

    with patch("application.evaluate_signal.read_posture", return_value=posture_mock), \
         patch("application.evaluate_signal.read_params", return_value=params_mock), \
         patch("application.evaluate_signal.load_book", return_value=records_mock):

        from application.evaluate_signal import evaluate_signal
        result = evaluate_signal(packet, snap, cash_available=5000.0)

    assert result.verdict == "BLOCKED"
    assert result.effective_entry == 102.0
    assert result.effective_stop == 98.0


# ---------------------------------------------------------------------------
# _sessions_since_earnings (WO-P400-E2.023)
# ---------------------------------------------------------------------------

def test_sessions_since_earnings_none_when_unknown():
    from application.evaluate_signal import _sessions_since_earnings
    assert _sessions_since_earnings(None) is None

def test_sessions_since_earnings_none_when_future_date():
    from application.evaluate_signal import _sessions_since_earnings
    from datetime import date, timedelta
    future = (date.today() + timedelta(days=5)).isoformat()
    assert _sessions_since_earnings(future) is None

def test_sessions_since_earnings_zero_same_day():
    from application.evaluate_signal import _sessions_since_earnings
    from datetime import date
    assert _sessions_since_earnings(date.today().isoformat()) == 0

def test_sessions_since_earnings_weekday_count():
    """Walk back exactly 5 real weekdays from today and confirm the count matches
    -- avoids hardcoding a specific date so this doesn't rot as 'today' changes."""
    from application.evaluate_signal import _sessions_since_earnings
    from datetime import date, timedelta
    d = date.today()
    weekdays_back = 0
    target = 5
    while weekdays_back < target:
        d = d - timedelta(days=1)
        if d.weekday() < 5:
            weekdays_back += 1
    assert _sessions_since_earnings(d.isoformat()) == target

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
