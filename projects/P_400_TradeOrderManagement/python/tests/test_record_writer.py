"""test_record_writer.py -- Unit tests for infrastructure/record_writer.py.

Covers: base write_p400_record() field passthrough, write_options_eval_record()
verdict mapping + OCC symbol construction, write_spread_eval_record() field
mapping, and (WO-P400-E3.006) order_id/SUBMITTED/MANUAL_DECLINE dispositions.
write_to_vault() is monkeypatched -- no real Obsidian I/O.
"""

import sys
from types import SimpleNamespace
from pathlib import Path


from schemas import OptionChainInput
from domain.options_council import OptionsCouncilResult
from domain.options_sizer import OptionSizingResult
from domain.spread_sizer import SpreadSizingResult
from shared_resources.python_utils.signal_schemas import (
    AssetClass, SignalContext, SignalMetadata, SignalV2,
)
from application.evaluate_options import OptionsEvalResult
from application.evaluate_spread import SpreadCouncilResult, SpreadEvalResult
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


def make_stock_result(verdict="APPROVED"):
    # verdict default "APPROVED" preserves every pre-existing call site
    # (make_stock_result() with no args) -- WO-P400-E2.022 adds the
    # stock-level verdict so options/spread field-builders can check it.
    return SimpleNamespace(
        posture=SimpleNamespace(risk_mode="OFF"),
        effective_entry=100.0, effective_stop=95.0,
        verdict=verdict,
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
# WO-P400-E3.006 -- order_id / SUBMITTED / MANUAL_DECLINE
# ---------------------------------------------------------------------------

def test_order_id_present_resolves_submitted(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=7, signal_source="P_300", trade_mode_value="REAL",
        order_id="5365031365",
    )
    assert captured["data"]["order_id"] == "5365031365"
    assert captured["data"]["lifecycle_status"] == "SUBMITTED"


def test_no_order_id_stays_pending(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=7, signal_source="P_300", trade_mode_value="REAL",
    )
    assert captured["data"]["order_id"] is None
    assert captured["data"]["lifecycle_status"] == "PENDING"


def test_manual_decline_resolves_dropped(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=7, signal_source="P_300", trade_mode_value="REAL",
        drop_reason="MANUAL_DECLINE",
    )
    assert captured["data"]["drop_reason"] == "MANUAL_DECLINE"
    assert captured["data"]["lifecycle_status"] == "DROPPED"


def test_order_id_ignored_on_blocked_verdict(monkeypatch):
    # order_id should never coexist with BLOCKED in practice, but the
    # resolver must not mis-mark it SUBMITTED if it somehow does.
    captured = _capture_vault_write(monkeypatch)
    write_p400_record(
        symbol="TEST", verdict="BLOCKED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=0, signal_source="P_300", trade_mode_value="REAL",
        order_id="999",
    )
    assert captured["data"]["lifecycle_status"] == "DROPPED"


# ---------------------------------------------------------------------------
# WO-P400-E2.019 -- paper/real book routing
# ---------------------------------------------------------------------------

def test_real_trade_routes_to_p400_schema(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=3, signal_source="P_300", trade_mode_value="REAL",
    )
    assert captured["schema_name"] == "P400"


def test_paper_trade_routes_to_p400_paper_schema(monkeypatch):
    captured = _capture_vault_write(monkeypatch)
    write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=3, signal_source="P_300", trade_mode_value="PAPER",
    )
    assert captured["schema_name"] == "P400_PAPER"


# ---------------------------------------------------------------------------
# WO-P020-E1.007 Part 2 / WO-P400-E6.001 -- why_code persisted from signal_source
# ---------------------------------------------------------------------------

def test_why_code_persisted_from_signal_source(monkeypatch):
    # Root cause: signal_source was received on every call, used only to
    # derive p115_linked/p300_linked, then discarded -- why_code stayed
    # null on all 419 real vault records. This locks in the fix.
    captured = _capture_vault_write(monkeypatch)
    write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=3, signal_source="P_300", trade_mode_value="REAL",
    )
    assert captured["data"]["why_code"] == "P_300"


def test_why_code_not_limited_to_p115_p300(monkeypatch):
    # The linked booleans only ever recognized two sources; why_code must
    # carry whatever signal_source actually is, so P_020's reader (which
    # checks why_code first) works for every system, not just those two.
    captured = _capture_vault_write(monkeypatch)
    write_p400_record(
        symbol="TEST", verdict="APPROVED", risk_mode="OFF",
        entry_price=100.0, stop_price=95.0, target_1=115.0,
        position_size=3, signal_source="P_116", trade_mode_value="REAL",
    )
    assert captured["data"]["why_code"] == "P_116"
    assert captured["data"]["p115_linked"] is False
    assert captured["data"]["p300_linked"] is False
