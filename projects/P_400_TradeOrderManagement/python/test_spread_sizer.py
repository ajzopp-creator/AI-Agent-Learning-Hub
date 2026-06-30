"""test_spread_sizer.py -- Unit tests for domain\spread_sizer.py.

Covers: max loss gate, R:R on spread, spread width selection,
Gate 3 cap on max loss, debit <= 0 guard, type mismatch guard,
posture multiplier at OFF mode.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pytest
from schemas import OptionChainInput
from domain.spread_sizer import (
    size_vertical_debit_spread,
    _spread_width,
    _breakeven,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_chain(strike: float, mid: float, iv: float = 0.30, **kwargs) -> OptionChainInput:
    defaults = dict(
        symbol="MU", underlying_price=1087.99,
        expiration="2026-07-18", option_type="call",
        bid=mid - 0.15, ask=mid + 0.15,
        delta=0.50, open_interest=300,
        spread_pct_of_mid=5.0, data_source="tos",
        chain_timestamp="2026-06-16T10:00:00Z",
    )
    defaults.update(kwargs)
    return OptionChainInput(strike=strike, mid=mid, iv=iv, **defaults)


STANDARD_PARAMS = dict(
    base_risk_dollars=490.04,
    cash_available=10000.0,
    max_position_dollars=1633.47,
    risk_mode="STANDARD",
)

OFF_PARAMS = {**STANDARD_PARAMS, "risk_mode": "OFF"}


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------

def test_spread_width_call():
    assert _spread_width(100.0, 110.0, "call") == 10.0


def test_spread_width_put():
    assert _spread_width(100.0, 90.0, "put") == 10.0


def test_breakeven_call():
    # long=100, debit=3.00 -> breakeven=103.00
    assert _breakeven(100.0, 3.00, "call") == 103.00


def test_breakeven_put():
    # long=100, debit=3.00 -> breakeven=97.00
    assert _breakeven(100.0, 3.00, "put") == 97.00


# ---------------------------------------------------------------------------
# Core sizing tests
# ---------------------------------------------------------------------------

def test_basic_call_spread():
    long_c = make_chain(strike=1090.0, mid=28.75)
    short_c = make_chain(strike=1110.0, mid=18.50)
    r = size_vertical_debit_spread(long_c, short_c, **STANDARD_PARAMS)
    assert r.contracts >= 0
    assert r.debit_per_spread == pytest.approx(10.25, abs=0.01)
    assert r.max_loss_per_spread == pytest.approx(1025.0, abs=0.01)
    assert r.spread_width == pytest.approx(20.0, abs=0.01)


def test_rr_calculation():
    # width=10, debit=3 -> max_profit=700, max_loss=300, rr=2.33
    long_c = make_chain(strike=100.0, mid=5.00)
    short_c = make_chain(strike=110.0, mid=2.00)
    r = size_vertical_debit_spread(long_c, short_c, **STANDARD_PARAMS)
    assert r.rr_spread == pytest.approx(700.0 / 300.0, rel=0.01)
    assert r.rr_valid == (r.rr_spread >= 2.0)


def test_gate3_uses_max_loss_not_notional():
    # max_position=500, max_loss per spread ~$1025 -> gate3=0
    long_c = make_chain(strike=1090.0, mid=28.75)
    short_c = make_chain(strike=1110.0, mid=18.50)
    params = {**STANDARD_PARAMS, "max_position_dollars": 500.0}
    r = size_vertical_debit_spread(long_c, short_c, **params)
    assert r.gate3_contracts == 0
    assert r.contracts == 0
    assert r.override_required is True


def test_off_mode_50pct_budget():
    long_c = make_chain(strike=100.0, mid=5.00)
    short_c = make_chain(strike=110.0, mid=2.00)
    r = size_vertical_debit_spread(long_c, short_c, **OFF_PARAMS)
    assert r.adjusted_risk_budget == pytest.approx(490.04 * 0.50, rel=0.01)


def test_debit_zero_or_negative_guard():
    # short leg premium >= long leg -> invalid
    long_c = make_chain(strike=100.0, mid=3.00)
    short_c = make_chain(strike=110.0, mid=5.00)  # short > long -- invalid
    r = size_vertical_debit_spread(long_c, short_c, **STANDARD_PARAMS)
    assert r.contracts == 0
    assert r.override_required is True
    assert r.warning is not None


def test_option_type_mismatch_guard():
    long_c = make_chain(strike=100.0, mid=5.00, option_type="call")
    short_c = make_chain(strike=110.0, mid=2.00, option_type="put")
    r = size_vertical_debit_spread(long_c, short_c, **STANDARD_PARAMS)
    assert r.contracts == 0
    assert "mismatch" in (r.warning or "")


def test_zero_contracts_sets_override():
    long_c = make_chain(strike=100.0, mid=5.00)
    short_c = make_chain(strike=110.0, mid=2.00)
    params = {**STANDARD_PARAMS, "cash_available": 50.0}
    r = size_vertical_debit_spread(long_c, short_c, **params)
    assert r.contracts == 0
    assert r.override_required is True