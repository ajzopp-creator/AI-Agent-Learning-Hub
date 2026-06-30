"""test_vehicle_selector.py -- WO-P400-E3.004 (items 1, 2) fix verification.

Tests that option_viable is strict (real contracts only, never override),
that a council BLOCK disqualifies the option regardless of R:R, and that
override-only outcomes are distinct ("OPTION_OVERRIDE_ONLY"), never
silently relabeled "OPTION".
"""
import pytest

from domain.sizing import SizingResult
from domain.options_sizer import OptionSizingResult
from domain.options_council import OptionsCouncilResult
from domain.vehicle_selector import compare_vehicles


def _stock(shares=10, rr=3.0, rr_valid=True, dollar_risk=100.0):
    return SizingResult(
        shares=shares, gate1_shares=shares, gate2_shares=shares, gate3_shares=shares,
        winning_gate="RISK", dollar_risk=dollar_risk, posture_multiplier=1.0,
        adjusted_risk_dollars=dollar_risk, rr_at_t1=rr, rr_valid=rr_valid,
    )


def _option(contracts=1, rr=3.0, rr_valid=True, override_required=False,
            spread_recommended=False, risk_per_contract=200.0):
    return OptionSizingResult(
        method="chart_based", contracts=contracts, option_entry=5.0, option_stop=3.0,
        option_target=10.0, risk_per_contract=risk_per_contract,
        total_risk_dollars=risk_per_contract * contracts,
        adjusted_risk_budget=500.0, rr_option=rr, rr_valid=rr_valid,
        override_required=override_required, spread_recommended=spread_recommended,
    )


def _council(verdict="PASS", blocks=None, cautions=None):
    return OptionsCouncilResult(
        verdict=verdict, blocks=blocks or [], cautions=cautions or [],
    )


def test_both_viable_option_wins_on_rr():
    r = compare_vehicles("TEST", _stock(rr=3.0), _option(contracts=1, rr=4.0), _council())
    assert r.recommended == "OPTION"
    assert r.option_viable is True


def test_both_viable_stock_wins_on_rr():
    r = compare_vehicles("TEST", _stock(rr=5.0), _option(contracts=1, rr=2.5), _council())
    assert r.recommended == "STOCK"


def test_council_block_disqualifies_option_despite_high_rr():
    """The exact WO-E3.004 finding: option R:R 5.61 >= stock R:R 5.59 must NOT
    win if the council BLOCKED it (e.g. OI too low) -- block wins outright."""
    r = compare_vehicles(
        "TEST", _stock(rr=5.59), _option(contracts=1, rr=5.61),
        _council(verdict="BLOCK", blocks=["OI_TOO_LOW: open_interest=86 < 150 minimum"]),
    )
    assert r.recommended == "STOCK"
    assert r.option_viable is False
    assert "OI_TOO_LOW" in r.recommendation_reason


def test_override_only_with_stock_viable_recommends_stock():
    """0 contracts/override-required must NOT win against a fully-viable
    stock trade -- this was the live ADBE 205C finding."""
    r = compare_vehicles(
        "TEST", _stock(shares=3, rr=5.59),
        _option(contracts=0, rr=5.61, override_required=True), _council(),
    )
    assert r.recommended == "STOCK"
    assert r.option_viable is False
    assert r.option_override_available is True
    assert "OVERRIDE REQUIRED" in r.recommendation_reason


def test_override_only_with_stock_also_dead_is_distinct_outcome():
    """When stock is also not viable, the override-only option path gets its
    own explicit outcome -- never silently labeled plain 'OPTION'."""
    r = compare_vehicles(
        "TEST", _stock(shares=0, rr=1.0, rr_valid=False),
        _option(contracts=0, rr=5.61, override_required=True), _council(),
    )
    assert r.recommended == "OPTION_OVERRIDE_ONLY"
    assert r.option_override_available is True


def test_spread_flag_preserved_when_not_blocked():
    r = compare_vehicles(
        "TEST", _stock(rr=3.0), _option(contracts=1, rr=4.0, spread_recommended=True),
        _council(),
    )
    assert r.recommended == "SPREAD"
    assert r.spread_recommended is True


def test_spread_flag_suppressed_when_council_blocks():
    """A council BLOCK suppresses the spread suggestion too -- a blocked
    strike's IV-rank caution is moot."""
    r = compare_vehicles(
        "TEST", _stock(rr=3.0),
        _option(contracts=1, rr=4.0, spread_recommended=True),
        _council(verdict="BLOCK", blocks=["SPREAD_TOO_WIDE: spread=12.0% > 10% max"]),
    )
    assert r.spread_recommended is False
    assert r.recommended == "STOCK"


def test_neither_viable_no_override_path():
    r = compare_vehicles(
        "TEST", _stock(shares=0, rr=1.0, rr_valid=False),
        _option(contracts=0, rr=1.0, rr_valid=False, override_required=False),
        _council(),
    )
    assert r.recommended == "NEITHER"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])