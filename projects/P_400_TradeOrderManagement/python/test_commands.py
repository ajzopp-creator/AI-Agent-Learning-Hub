"""test_commands.py -- WO-P400-E2.021: BLOCKED stock write includes drop_reason.

Self-contained fixtures (not imported from test_evaluate_signal.py) to
match this project's convention of per-test-file helpers, matching
test_options_council.py / test_spread_sizer.py style.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from config import TradeMode
from shared_resources.python_utils.signal_schemas import SignalV2


def _make_packet(entry: float, stop: float, target: float, symbol: str) -> SignalV2:
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


def _make_snapshot(price: float, entry: float, stop: float, symbol: str) -> dict:
    return {
        "symbol": symbol, "price": price, "bid": price - 0.01, "ask": price + 0.01,
        "price_timestamp": datetime.now(timezone.utc).isoformat(), "price_delay_seconds": 5,
        "atr_14": abs(entry - stop), "avg_volume_20d": 1000000, "data_source": "web",
        "today_volume": None, "next_earnings_date": None, "binary_events": [],
        "sector": None, "iv_rank": None, "option_chain_ref": None,
        "market_open": True, "guideline_stop_override": None,
    }


def _mock_infra():
    posture_mock = MagicMock(risk_mode="STANDARD", avg_posture=0.0)
    params_mock = MagicMock(account_balance=32669.72, risk_per_trade=490.04, max_position=1633.47)
    return posture_mock, params_mock, []


def test_blocked_stock_evaluate_writes_council_block_drop_reason(tmp_path):
    """cmd_evaluate's plain-stock BLOCKED write must pass drop_reason=
    'COUNCIL_BLOCK', matching the convention already used by the options
    and spread paths (record_writer._build_options_fields /
    _build_spread_fields). Previously missing entirely -- always wrote
    drop_reason=None on a stock BLOCKED verdict.
    """
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0, symbol="ZZZBLOCK")
    snap = _make_snapshot(price=102.0, entry=100.0, stop=98.0, symbol="ZZZBLOCK")

    snapshot_path = tmp_path / "snapshot_ZZZBLOCK.json"
    snapshot_path.write_text(json.dumps(snap), encoding="utf-8")

    posture_mock, params_mock, records_mock = _mock_infra()
    captured = {}

    def fake_write_p400_record(**kwargs):
        captured.update(kwargs)
        return True

    with patch("application.evaluate_signal.read_posture", return_value=posture_mock), \
         patch("application.evaluate_signal.read_params", return_value=params_mock), \
         patch("application.evaluate_signal.load_book", return_value=records_mock), \
         patch("application.commands._find_packet", return_value=packet), \
         patch("infrastructure.record_writer.write_p400_record", side_effect=fake_write_p400_record), \
         patch("infrastructure.signal_archiver.archive_packet", return_value=True), \
         patch("infrastructure.eval_cache.write_eval_cache", return_value=True):

        from application import commands
        rc = commands.cmd_evaluate("ZZZBLOCK", str(snapshot_path), cash=5000.0, trade_mode=TradeMode.REAL)

    assert rc == 0
    assert captured.get("verdict") == "BLOCKED"
    assert captured.get("drop_reason") == "COUNCIL_BLOCK"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# ---------------------------------------------------------------------------
# WO-P400-E2.022 -- options/spread BLOCKED runs must never double-write
# ---------------------------------------------------------------------------

def test_options_blocked_run_writes_record_exactly_once(tmp_path):
    """Regression for the WMT live incident: the trailing blanket
    `if result.verdict == "BLOCKED": write_p400_record(...)` in
    cmd_evaluate used to fire unconditionally, AFTER the options branch
    had already written its own full record via write_options_eval_record
    -- silently clobbering every option_* field on every options run
    where the stock-level Council blocked. write_p400_record is the one
    low-level function both paths funnel through, so counting its calls
    proves there's no second write, not just that the fields look right."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0, symbol="ZZZOPTBLOCK")
    snap = _make_snapshot(price=102.0, entry=100.0, stop=98.0, symbol="ZZZOPTBLOCK")

    snapshot_path = tmp_path / "snapshot_ZZZOPTBLOCK.json"
    snapshot_path.write_text(json.dumps(snap), encoding="utf-8")
    chain_path = tmp_path / "chain_ZZZOPTBLOCK.json"
    chain_path.write_text("{}", encoding="utf-8")  # never read -- evaluate_options is mocked

    posture_mock, params_mock, records_mock = _mock_infra()
    write_p400_record_calls = []

    def fake_write_p400_record(**kwargs):
        write_p400_record_calls.append(kwargs)
        return True

    fake_opt_result = MagicMock(
        symbol="ZZZOPTBLOCK", verdict="PASS",  # options council itself is clean
        council=MagicMock(blocks=[], cautions=[]),
        spec_text="[spec]",
        sizing=MagicMock(method="chart_based", contracts=1, option_entry=5.0,
                         option_stop=2.5, option_target=10.0, override_required=False),
        chain=MagicMock(expiration="2026-08-21", option_type="call", strike=100.0, iv=0.29),
    )

    with patch("application.evaluate_signal.read_posture", return_value=posture_mock), \
         patch("application.evaluate_signal.read_params", return_value=params_mock), \
         patch("application.evaluate_signal.load_book", return_value=records_mock), \
         patch("application.commands._find_packet", return_value=packet), \
         patch("application.evaluate_options.evaluate_options", return_value=fake_opt_result), \
         patch("infrastructure.record_writer.write_p400_record", side_effect=fake_write_p400_record), \
         patch("infrastructure.signal_archiver.archive_packet", return_value=True), \
         patch("infrastructure.eval_cache.write_eval_cache", return_value=True):

        from application import commands
        rc = commands.cmd_evaluate(
            "ZZZOPTBLOCK", str(snapshot_path), cash=5000.0, trade_mode=TradeMode.REAL,
            options=True, chain_path=str(chain_path),
        )

    assert rc == 0
    assert len(write_p400_record_calls) == 1, (
        f"Expected exactly one write_p400_record call, got {len(write_p400_record_calls)}: "
        f"{write_p400_record_calls}"
    )
    # The single write must reflect the stock-level BLOCK, not the clean options PASS.
    assert write_p400_record_calls[0]["verdict"] == "BLOCKED"
    assert write_p400_record_calls[0]["drop_reason"] == "COUNCIL_BLOCK"