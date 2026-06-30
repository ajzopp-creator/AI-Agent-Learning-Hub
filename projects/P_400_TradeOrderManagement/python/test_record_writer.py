"""test_record_writer.py -- Unit tests for infrastructure/record_writer.py.

Covers: base write_p400_record() field passthrough, write_options_eval_record()
verdict mapping + OCC symbol construction, write_spread_eval_record() field
mapping. write_to_vault() is monkeypatched -- no real Obsidian I/O.
"""

import sys
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from schemas import OptionChainInput
from domain.options_council import OptionsCouncilResult
from domain.options_sizer import OptionSizingResult
from domain.spread_sizer import SpreadSizingResult
from shared_resources.python_utils.signal_schemas import (
    AssetClass, SignalContext, SignalMetadata, SignalV2,
)
from application.evaluate_options import OptionsEvalResult
from application.evaluate_spread import SpreadEvalResult
import infrastructure.record_writer as rw_module
from infrastructure.record_writer import (
    write_p400_record, write_options_eval_record, write_spread_eval_record,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def make_packet(**kwargs) -> SignalV2:
    defaults = dict(
        signal_id="TEST-2026-06-30-001", signal_timestamp="2026-06-30T09:00:00Z",
        signal_source="P_300", strategy="dip_buy", symbol="TEST",
        asset_class=AssetClass.STOCK,
        guideline_entry=100.0, guideline_stop=95.0, guideline_target=115.0,
        signal_horizon="3-5 days", confidence_level="MEDIUM", position_size=1,
        context=SignalContext(close_at_signal=100.0, trailing_volume_30d=1000000.0,
                              signal_rationale="test fixture"),
        signal_metadata=SignalMetadata(session_date="2026-06-30", chart_timeframe="1D",
                                       signal_source_link="test\\path.md"),
    )
    defaults.update(kwargs)
    return SignalV2(**defaults)


def make_stock_result():
    return SimpleNamespace(
        posture=SimpleNamespace(risk_mode="OFF"),
        effective_entry=100.0, effective_stop=95.0,
    )


def _capture_vault_write(monkeypatch):
    captured = {}
    def fake_write(schema_name, data):
        captured["schema_name"] = schema_name
        captured["data"] = data
        return True
    monkeypatch.setattr(rw_module, "write_to_vault", fake_write)
    return captured


# ---------------------------------------------------------------------------
# write_p400_record -- base passthrough
# ---------------------------------------------------------------------------

def test_base_write_passes_required_fields(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    result = write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=3, signal_source="P_300", trade_mode_value="REAL",
    )
    assert result is True
    assert captured["schema_name"] == "P400"
    assert captured["data"]["ticker"] == "TEST"
    assert captured["data"]["council_verdict"] == "APPROVED"
    assert captured["data"]["p300_linked"] is True


def test_vault_write_failure_returns_false(monkeypatch):
    def fake_write(schema_name, data):
        raise OSError("disk full")
    monkeypatch.setattr(rw_module, "write_to_vault", fake_write)
    result = write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=3, signal_source="P_300", trade_mode_value="REAL",
    )
    assert result is False


# ---------------------------------------------------------------------------
# write_options_eval_record -- verdict mapping + OCC construction
# ---------------------------------------------------------------------------

def _make_opt_result(verdict, override_required=False, contracts=2):
    chain = OptionChainInput(
        symbol="TEST", underlying_price=100.0, expiration="2026-07-17",
        strike=100.0, option_type="call", bid=4.8, ask=5.2, mid=5.0,
        delta=0.5, iv=0.30, open_interest=300, spread_pct_of_mid=8.0,
        data_source="tos", chain_timestamp="2026-06-30T10:00:00Z",
    )
    sizing = OptionSizingResult(
        method="chart_based", contracts=contracts,
        option_entry=5.0, option_stop=2.5, option_target=10.0,
        risk_per_contract=250.0, total_risk_dollars=250.0 * contracts,
        adjusted_risk_budget=245.02, rr_option=2.0, rr_valid=True,
        override_required=override_required, spread_recommended=False,
        gate1_contracts=contracts, gate2_contracts=10, gate3_contracts=5,
        winning_gate="RISK", warning=None, notes=[],
    )
    council = OptionsCouncilResult(verdict=verdict, blocks=[], cautions=[])
    return OptionsEvalResult(symbol="TEST", verdict=verdict, sizing=sizing,
                             council=council, chain=chain, spec_text="[ignored]")


def test_options_pass_maps_to_approved(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    opt_result = _make_opt_result("PASS")
    written, verdict = write_options_eval_record(
        opt_result, make_stock_result(), make_packet(), "REAL", "TEST",
    )
    assert written is True
    assert verdict == "APPROVED"
    assert captured["data"]["option_contract"] == "TEST260717C100"


def test_options_block_maps_to_blocked_with_drop_reason(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    opt_result = _make_opt_result("BLOCK")
    written, verdict = write_options_eval_record(
        opt_result, make_stock_result(), make_packet(), "REAL", "TEST",
    )
    assert verdict == "BLOCKED"
    assert captured["data"]["drop_reason"] == "COUNCIL_BLOCK"


def test_options_override_records_one_contract(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    opt_result = _make_opt_result("CAUTION", override_required=True, contracts=0)
    written, verdict = write_options_eval_record(
        opt_result, make_stock_result(), make_packet(), "REAL", "TEST",
    )
    assert verdict == "APPROVED_WITH_CAUTION"
    assert captured["data"]["option_contracts"] == 1
    assert captured["data"]["option_override"] is True


# ---------------------------------------------------------------------------
# write_spread_eval_record -- spread field mapping
# ---------------------------------------------------------------------------

def _make_spread_result(override_required=False, contracts=1):
    long_chain = OptionChainInput(
        symbol="TEST", underlying_price=100.0, expiration="2026-07-17",
        strike=100.0, option_type="call", bid=4.8, ask=5.2, mid=5.0,
        delta=0.5, iv=0.30, open_interest=300, spread_pct_of_mid=8.0,
        data_source="tos", chain_timestamp="2026-06-30T10:00:00Z",
    )
    short_chain = OptionChainInput(
        symbol="TEST", underlying_price=100.0, expiration="2026-07-17",
        strike=110.0, option_type="call", bid=1.8, ask=2.1, mid=1.95,
        delta=0.25, iv=0.28, open_interest=200, spread_pct_of_mid=15.4,
        data_source="tos", chain_timestamp="2026-06-30T10:00:00Z",
    )
    sizing = SpreadSizingResult(
        long_strike=100.0, short_strike=110.0, spread_width=10.0,
        debit_per_spread=3.05, max_profit_per_spread=695.0, max_loss_per_spread=305.0,
        breakeven=103.05, contracts=contracts, total_max_loss=305.0 * contracts,
        adjusted_risk_budget=245.02, rr_spread=2.28, rr_valid=True,
        override_required=override_required, gate1_contracts=contracts,
        gate2_contracts=19, gate3_contracts=5, winning_gate="RISK",
        warning=None, notes=[],
    )
    return SpreadEvalResult(symbol="TEST", sizing=sizing, long_chain=long_chain,
                            short_chain=short_chain, spec_text="[ignored]")


def test_spread_viable_maps_to_approved(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    spread_result = _make_spread_result()
    written, verdict = write_spread_eval_record(
        spread_result, make_stock_result(), make_packet(), "REAL",
    )
    assert written is True
    assert verdict == "APPROVED"
    assert captured["data"]["spread_long_strike"] == 100.0
    assert captured["data"]["spread_short_strike"] == 110.0
    assert captured["data"]["spread_debit"] == 3.05
    assert captured["data"]["spread_max_loss"] == 305.0
    assert captured["data"]["spread_breakeven"] == 103.05


def test_spread_override_maps_to_caution(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    spread_result = _make_spread_result(override_required=True, contracts=0)
    written, verdict = write_spread_eval_record(
        spread_result, make_stock_result(), make_packet(), "REAL",
    )
    assert verdict == "APPROVED_WITH_CAUTION"
    assert captured["data"]["option_contracts"] == 1
    assert captured["data"]["option_override"] is True