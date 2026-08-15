"""test_options_sizer.py -- Unit tests for domain\options_sizer.py.

Covers: Chart-Based delta translation, Risk-Budget-First 2xATR floor,
Gate 3 premium cap, 0-contract override path, posture multiplier.
"""

import sys
from pathlib import Path


import pytest
from schemas import OptionChainInput
from domain.options_sizer import (
    size_option_chart_based,
    size_option_risk_budget,
    _translate_stop,
    _translate_target,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_chain(**kwargs) -> OptionChainInput:
    defaults = dict(
        symbol="MU", underlying_price=1087.99, expiration="2026-07-18",
        strike=1090.0, option_type="call",
        bid=28.40, ask=29.10, mid=28.75,
        delta=0.49, iv=0.31,
        open_interest=412, spread_pct_of_mid=2.43,
        data_source="tos", chain_timestamp="2026-06-16T10:00:00Z",
    )
    defaults.update(kwargs)
    return OptionChainInput(**defaults)


STANDARD_PARAMS = dict(
    stock_entry=1087.99, stock_stop=1006.22, stock_target=1250.00,
    base_risk_dollars=490.04, cash_available=10000.0,
    max_position_dollars=1633.47, risk_mode="STANDARD",
)

OFF_PARAMS = {**STANDARD_PARAMS, "risk_mode": "OFF",
              "base_risk_dollars": 490.04}


# ---------------------------------------------------------------------------
# Delta translation helpers
# ---------------------------------------------------------------------------

def test_translate_stop_basic():
    # entry=10.00, delta=0.50, stock_risk=5.00 -> stop = 10 - (0.5*5) = 7.50
    assert _translate_stop(10.00, 0.50, 5.00) == 7.50


def test_translate_stop_floors_at_penny():
    # extreme scenario: stop would go negative
    result = _translate_stop(1.00, 0.99, 5.00)
    assert result == 0.01


def test_translate_target_basic():
    # entry=10.00, delta=0.50, stock_reward=20.00 -> target = 10 + (0.5*20) = 20.00
    assert _translate_target(10.00, 0.50, 20.00) == 20.00


# ---------------------------------------------------------------------------
# Chart-Based sizing
# ---------------------------------------------------------------------------

def test_chart_based_standard_mode():
    chain = make_chain()
    r = size_option_chart_based(chain, **STANDARD_PARAMS)
    assert r.method == "chart_based"
    assert r.option_stop < r.option_entry < r.option_target
    assert r.risk_per_contract > 0


def test_chart_based_off_mode_50pct():
    chain = make_chain()
    r_std = size_option_chart_based(chain, **STANDARD_PARAMS)
    r_off = size_option_chart_based(chain, **OFF_PARAMS)
    # OFF budget is 50% -- gate1 contracts should be <= standard
    assert r_off.gate1_contracts <= r_std.gate1_contracts
    assert r_off.adjusted_risk_budget == pytest.approx(490.04 * 0.50, rel=0.01)


def test_chart_based_gate3_premium_cap():
    # max_position_dollars=500 with premium ~$28.75*100=$2875 -> gate3=0
    chain = make_chain()
    params = {**STANDARD_PARAMS, "max_position_dollars": 500.0}
    r = size_option_chart_based(chain, **params)
    assert r.gate3_contracts == 0
    assert r.contracts == 0
    assert r.override_required is True


def test_chart_based_zero_contracts_sets_override():
    chain = make_chain()
    params = {**STANDARD_PARAMS, "cash_available": 100.0}
    r = size_option_chart_based(chain, **params)
    assert r.contracts == 0
    assert r.override_required is True
    assert r.warning is not None


def test_chart_based_rr_valid_flag():
    chain = make_chain()
    r = size_option_chart_based(chain, **STANDARD_PARAMS)
    # rr_valid should match whether rr_option >= 2.0
    assert r.rr_valid == (r.rr_option >= 2.0)


def test_chart_based_spread_recommended_when_iv_high():
    # iv=0.55 -> 55% > 50 threshold -> spread_recommended
    chain = make_chain(iv=0.55)
    r = size_option_chart_based(chain, **STANDARD_PARAMS)
    assert r.spread_recommended is True


def test_chart_based_no_spread_when_iv_low():
    chain = make_chain(iv=0.25)
    r = size_option_chart_based(chain, **STANDARD_PARAMS)
    assert r.spread_recommended is False


# ---------------------------------------------------------------------------
# Risk-Budget-First sizing
# ---------------------------------------------------------------------------

RB_PARAMS = dict(
    atr_14=25.0, base_risk_dollars=490.04,
    cash_available=10000.0, max_position_dollars=1633.47,
    risk_mode="STANDARD",
)


def test_risk_budget_method_label():
    chain = make_chain()
    r = size_option_risk_budget(chain, **RB_PARAMS)
    assert r.method == "risk_budget_first"


def test_risk_budget_stop_is_tighter():
    # stop must be between entry and zero
    chain = make_chain()
    r = size_option_risk_budget(chain, **RB_PARAMS)
    assert 0 < r.option_stop < r.option_entry


def test_risk_budget_atr_floor_applied():
    # with large ATR, 2xATR floor should dominate over budget stop
    chain = make_chain(mid=5.00, bid=4.80, ask=5.20, delta=0.50)
    r = size_option_risk_budget(chain, atr_14=8.0, base_risk_dollars=490.04,
                                cash_available=10000.0, max_position_dollars=1633.47,
                                risk_mode="STANDARD")
    # 2xATR stop = 5.00 - (0.50 * 2 * 8.0) = 5.00 - 8.0 = capped at 0.01
    assert r.option_stop == pytest.approx(0.01, abs=0.02)


def test_risk_budget_off_mode():
    chain = make_chain()
    r = size_option_risk_budget(chain, atr_14=25.0, base_risk_dollars=490.04,
                                cash_available=10000.0, max_position_dollars=1633.47,
                                risk_mode="OFF")
    assert r.adjusted_risk_budget == pytest.approx(490.04 * 0.50, rel=0.01)