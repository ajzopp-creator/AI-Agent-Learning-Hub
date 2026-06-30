"""test_compare_vehicles.py -- WO-P400-E3.004 (item 2) integration verification.

Confirms run_comparison() actually invokes run_options_council() on the live
path (previously it was built, unit-tested, and called nowhere) and that an
OI-too-low BLOCK reaches the formatted output string.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from shared_resources.python_utils.signal_schemas import SignalV2


def _make_packet(entry=100.0, stop=95.0, target=120.0, symbol="TEST"):
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


def _write_snapshot(tmp_path, price=100.0):
    snap = {
        "symbol": "TEST", "price": price, "bid": price - 0.05, "ask": price + 0.05,
        "price_timestamp": "2026-06-29T17:00:00Z", "price_delay_seconds": 5,
        "atr_14": 5.0, "avg_volume_20d": 1000000, "today_volume": None,
        "next_earnings_date": None, "binary_events": [], "sector": None,
        "iv_rank": None, "option_chain_ref": None, "data_source": "manual",
        "market_open": True,
    }
    p = tmp_path / "snapshot_TEST.json"
    p.write_text(json.dumps(snap), encoding="utf-8")
    return str(p)


def _write_chain(tmp_path, open_interest=86, spread_pct=5.0):
    """open_interest=86 is intentionally below the 150 minimum -- triggers OI_TOO_LOW."""
    chain = {
        "symbol": "TEST", "underlying_price": 100.0, "expiration": "2026-07-17",
        "strike": 105.0, "option_type": "call", "bid": 4.80, "ask": 5.20, "mid": 5.0,
        "delta": 0.45, "iv": 0.40, "open_interest": open_interest,
        "spread_pct_of_mid": spread_pct, "data_source": "tos",
        "chain_timestamp": "2026-06-29T17:00:00Z",
    }
    p = tmp_path / "chain_TEST.json"
    p.write_text(json.dumps(chain), encoding="utf-8")
    return str(p)


def _mock_infra(posture="STANDARD", balance=32669.72, risk=490.04, max_pos=1633.47):
    posture_mock = MagicMock(risk_mode=posture, avg_posture=0.0)
    params_mock = MagicMock(account_balance=balance, risk_per_trade=risk, max_position=max_pos)
    return posture_mock, params_mock


def test_run_comparison_calls_options_council_and_surfaces_block(tmp_path):
    """The exact gap this WO fixes: options_council.py was never invoked on
    the live compare path. This confirms it now runs and an OI block reaches
    the printed output."""
    packet = _make_packet()
    snap_path = _write_snapshot(tmp_path)
    chain_path = _write_chain(tmp_path, open_interest=86)  # below 150 minimum

    posture_mock, params_mock = _mock_infra()

    with patch("application.compare_vehicles.read_posture", return_value=posture_mock), \
         patch("application.compare_vehicles.read_params", return_value=params_mock), \
         patch("application.compare_vehicles.run_options_council",
               wraps=__import__("domain.options_council", fromlist=["run_options_council"]).run_options_council) as spy:

        from application.compare_vehicles import run_comparison
        output = run_comparison(packet, snap_path, chain_path, cash_available=10000.0)

    assert spy.called, "run_options_council was never invoked -- the original WO-E3.004 gap"
    assert "OI_TOO_LOW" in output
    assert "BLOCK" in output
    assert "RECOMMENDATION: STOCK" in output  # option must lose despite any R:R


def test_run_comparison_clean_chain_passes_council(tmp_path):
    """A clean, liquid chain passes the council with no blocks -- confirms
    the wiring doesn't false-positive-block a healthy strike."""
    packet = _make_packet()
    snap_path = _write_snapshot(tmp_path)
    chain_path = _write_chain(tmp_path, open_interest=900, spread_pct=4.0)

    posture_mock, params_mock = _mock_infra()

    with patch("application.compare_vehicles.read_posture", return_value=posture_mock), \
         patch("application.compare_vehicles.read_params", return_value=params_mock):

        from application.compare_vehicles import run_comparison
        output = run_comparison(packet, snap_path, chain_path, cash_available=10000.0)

    assert "Options Council: PASS" in output
    assert "OI_TOO_LOW" not in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])