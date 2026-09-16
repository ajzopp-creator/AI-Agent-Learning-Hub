"""test_build_option_spec_scaleout.py -- Unit tests for
application\\build_option_spec_scaleout.py (WO-P400-E8.003).

Covers: contracts split (even/odd/single), T2 premium delta-translation,
shared stop across both brackets, single-contract edge case (bracket 2
omitted rather than a 0-qty leg).
"""

from schemas import OptionChainInput
from domain.options_sizer import OptionSizingResult
from application.build_option_spec_scaleout import build_option_spec_scaleout


def make_chain(**kwargs) -> OptionChainInput:
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


def make_sizing(**kwargs) -> OptionSizingResult:
    defaults = dict(
        method="chart_based", contracts=4,
        option_entry=5.00, option_stop=2.50, option_target=10.00,
        risk_per_contract=250.0, total_risk_dollars=1000.0,
        adjusted_risk_budget=1000.0, rr_option=2.0, rr_valid=True,
        override_required=False, spread_recommended=False,
        gate1_contracts=4, gate2_contracts=10, gate3_contracts=5,
        winning_gate="RISK", warning=None, notes=[],
    )
    defaults.update(kwargs)
    return OptionSizingResult(**defaults)


def render(contracts=4, **kwargs) -> str:
    args = dict(
        underlying_symbol="TEST", option_sym="TEST  260717C00100000",
        chain=make_chain(), sizing=make_sizing(), contracts=contracts,
        leverage=10.0, stock_entry=100.0, stock_stop=95.0,
        stock_target_1=110.0, stock_target_2=120.0,
    )
    args.update(kwargs)
    return build_option_spec_scaleout(**args)


# ---------------------------------------------------------------------------
# Contracts split
# ---------------------------------------------------------------------------

def test_even_split_two_and_two():
    out = render(contracts=4)
    assert "4  (2 @ T1, 2 @ T2)" in out


def test_odd_split_extra_goes_to_t2():
    out = render(contracts=5)
    assert "5  (2 @ T1, 3 @ T2)" in out


def test_single_contract_bracket_1_omitted():
    # Remainder rides to T2 (documented design, matches the odd-split
    # case above) -- at n=1 that means ALL of it goes to T2, not T1.
    out = render(contracts=1)
    assert "1  (0 @ T1, 1 @ T2)" in out
    assert "BRACKET 1 (T1)" not in out
    assert "BRACKET 2 (T2)" in out


# ---------------------------------------------------------------------------
# Both brackets present on a real split
# ---------------------------------------------------------------------------

def test_both_brackets_rendered():
    out = render()
    assert "BRACKET 1 (T1)" in out
    assert "BRACKET 2 (T2)" in out
    assert out.count("Stop Loss") == 2
    assert out.count("Take Profit") == 2


def test_shared_stop_in_both_brackets():
    out = render()
    assert out.count("TEST stock at or below 95.00") == 2


def test_single_shared_entry_leg():
    out = render(contracts=4)
    assert out.count("LEG 1 -- Entry") == 1
    assert "Qty:     4" in out  # full quantity on the one entry leg


# ---------------------------------------------------------------------------
# T2 premium delta-translation
# ---------------------------------------------------------------------------

def test_t2_premium_delta_translated():
    # entry=5.00, delta=0.50, stock_reward=(120-100)=20 -> target = 5 + 0.5*20 = 15.00
    out = render()
    assert "TEST 120.00  ->  option ~$15.00" in out


def test_t1_premium_unchanged_from_sizing():
    # T1 still comes straight from sizing.option_target (10.00), not re-derived
    out = render()
    assert "TEST 110.00  ->  option ~$10.00" in out


def test_rr_at_t2_computed():
    # option_entry=5.00, option_stop=2.50 -> risk=2.50; T2 premium=15.00
    # rr = (15.00 - 5.00) / 2.50 = 4.00
    out = render()
    assert "R:R at T2:     4.00" in out
