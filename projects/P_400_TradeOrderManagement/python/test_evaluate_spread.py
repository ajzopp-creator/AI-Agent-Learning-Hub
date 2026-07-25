"""test_evaluate_spread.py -- Unit tests for application/evaluate_spread.py.

Pure orchestration test -- infrastructure readers monkeypatched so no real
filesystem state (P_010, P_000, chain files) is required.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from schemas import AccountParams, OptionChainInput, PostureSnapshot
from shared_resources.python_utils.signal_schemas import (
    AssetClass, SignalContext, SignalMetadata, SignalV2,
)
from application import evaluate_spread as es_module
from application.evaluate_spread import evaluate_spread


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_packet(**kwargs) -> SignalV2:
    defaults = dict(
        signal_id="TEST-2026-06-30-001",
        signal_timestamp="2026-06-30T09:00:00Z",
        signal_source="P_300",
        strategy="dip_buy",
        symbol="TEST",
        asset_class=AssetClass.STOCK,
        guideline_entry=100.0, guideline_stop=95.0, guideline_target=115.0,
        signal_horizon="3-5 days",
        confidence_level="MEDIUM",
        position_size=1,
        context=SignalContext(
            close_at_signal=100.0, trailing_volume_30d=1000000.0,
            signal_rationale="test fixture",
        ),
        signal_metadata=SignalMetadata(
            session_date="2026-06-30", chart_timeframe="1D",
            signal_source_link="test\\path.md",
        ),
    )
    defaults.update(kwargs)
    return SignalV2(**defaults)


def make_long_chain(**kwargs) -> OptionChainInput:
    defaults = dict(
        symbol="TEST", underlying_price=100.0, expiration="2026-07-17",
        strike=100.0, option_type="call",
        bid=4.80, ask=5.20, mid=5.00,
        delta=0.50, iv=0.30,
        open_interest=300, spread_pct_of_mid=8.0,
        data_source="tos", chain_timestamp="2026-06-30T10:00:00Z",
    )
    defaults.update(kwargs)
    return OptionChainInput(**defaults)


def make_short_chain(**kwargs) -> OptionChainInput:
    defaults = dict(
        symbol="TEST", underlying_price=100.0, expiration="2026-07-17",
        strike=110.0, option_type="call",
        bid=1.80, ask=2.10, mid=1.95,
        delta=0.25, iv=0.28,
        open_interest=200, spread_pct_of_mid=6.0,
        data_source="tos", chain_timestamp="2026-06-30T10:00:00Z",
    )
    defaults.update(kwargs)
    return OptionChainInput(**defaults)


def _patch_readers(monkeypatch, long_chain, short_chain):
    chains = {"long.json": long_chain, "short.json": short_chain}
    monkeypatch.setattr(es_module, "load_chain", lambda path: chains[path])
    monkeypatch.setattr(es_module, "read_posture", lambda: PostureSnapshot(
        risk_mode="OFF", avg_posture=-5.99, timestamp="2026-06-30T10:00:00Z",
    ))
    monkeypatch.setattr(es_module, "read_params", lambda: AccountParams(
        account_balance=32669.72, risk_per_trade=490.04, max_position=1633.47,
    ))


# ---------------------------------------------------------------------------
# Happy path -- viable spread renders Pattern C
# ---------------------------------------------------------------------------

def test_viable_spread_renders_spec(monkeypatch):
    long_c = make_long_chain()
    short_c = make_short_chain()
    _patch_readers(monkeypatch, long_c, short_c)
    result = evaluate_spread(
        packet=make_packet(), long_chain_path="long.json",
        short_chain_path="short.json", cash_available=6000.0,
    )
    assert result.sizing.contracts >= 0
    assert "PATTERN C" in result.spec_text


# ---------------------------------------------------------------------------
# 0 contracts -- size_vertical_debit_spread() sets override_required=True
# whenever final==0 (mirrors options_sizer.py semantics; there is no real
# 0-contract/non-override state). Spec renders 1 contract with a loud
# override note rather than a blank/[NO SPEC] result.
# ---------------------------------------------------------------------------

def test_zero_contracts_renders_override_note(monkeypatch):
    # Tiny risk budget forces Gate 1 to 0 -- patch params to near-zero risk
    long_c = make_long_chain()
    short_c = make_short_chain()
    monkeypatch.setattr(es_module, "load_chain",
                        lambda path: {"long.json": long_c, "short.json": short_c}[path])
    monkeypatch.setattr(es_module, "read_posture", lambda: PostureSnapshot(
        risk_mode="OFF", avg_posture=-5.99, timestamp="2026-06-30T10:00:00Z",
    ))
    monkeypatch.setattr(es_module, "read_params", lambda: AccountParams(
        account_balance=32669.72, risk_per_trade=0.50, max_position=1633.47,
    ))
    result = evaluate_spread(
        packet=make_packet(), long_chain_path="long.json",
        short_chain_path="short.json", cash_available=6000.0,
    )
    assert result.sizing.contracts == 0
    assert result.sizing.override_required is True
    assert result.spec_text.startswith("[OVERRIDE")
    assert "Qty:     1" in result.spec_text


# ---------------------------------------------------------------------------
# Mismatched option types -- invalid spread notice
# ---------------------------------------------------------------------------

def test_mismatched_option_types_invalid_spread(monkeypatch):
    long_c = make_long_chain(option_type="call")
    short_c = make_short_chain(option_type="put", strike=90.0, delta=-0.25)
    _patch_readers(monkeypatch, long_c, short_c)
    result = evaluate_spread(
        packet=make_packet(), long_chain_path="long.json",
        short_chain_path="short.json", cash_available=6000.0,
    )
    assert result.sizing.contracts == 0
    assert result.sizing.warning is not None
    assert "mismatch" in result.sizing.warning