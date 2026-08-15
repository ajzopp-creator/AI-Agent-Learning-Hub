"""test_options_council.py -- Unit tests for domain\options_council.py.

Covers: OI block, spread block, R:R minimum block, R:R parity block,
IV-rank caution, zero-contracts caution, clean PASS path.
"""

import sys
from pathlib import Path


from schemas import OptionChainInput
from domain.options_sizer import size_option_chart_based, OptionSizingResult
from domain.options_council import run_options_council


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_chain(**kwargs) -> OptionChainInput:
    defaults = dict(
        symbol="TEST", underlying_price=100.0, expiration="2026-07-18",
        strike=100.0, option_type="call",
        bid=4.80, ask=5.20, mid=5.00,
        delta=0.50, iv=0.30,
        open_interest=300, spread_pct_of_mid=8.0,
        data_source="tos", chain_timestamp="2026-06-16T10:00:00Z",
    )
    defaults.update(kwargs)
    return OptionChainInput(**defaults)


def make_sizing(**kwargs) -> OptionSizingResult:
    """Build a minimal passing OptionSizingResult for council tests."""
    from dataclasses import asdict
    defaults = dict(
        method="chart_based", contracts=2,
        option_entry=5.00, option_stop=2.50, option_target=10.00,
        risk_per_contract=250.0, total_risk_dollars=500.0,
        adjusted_risk_budget=490.04, rr_option=2.0, rr_valid=True,
        override_required=False, spread_recommended=False,
        gate1_contracts=2, gate2_contracts=10, gate3_contracts=5,
        winning_gate="RISK", warning=None, notes=[],
    )
    defaults.update(kwargs)
    return OptionSizingResult(**defaults)


# ---------------------------------------------------------------------------
# Block tests
# ---------------------------------------------------------------------------

def test_oi_too_low_blocks():
    chain = make_chain(open_interest=50)
    sizing = make_sizing()
    r = run_options_council(chain, sizing, stock_rr=2.5)
    assert r.verdict == "BLOCK"
    assert any("OI_TOO_LOW" in b for b in r.blocks)


def test_spread_too_wide_blocks():
    chain = make_chain(spread_pct_of_mid=15.0)
    sizing = make_sizing()
    r = run_options_council(chain, sizing, stock_rr=2.5)
    assert r.verdict == "BLOCK"
    assert any("SPREAD_TOO_WIDE" in b for b in r.blocks)


def test_rr_below_minimum_blocks():
    chain = make_chain()
    sizing = make_sizing(rr_option=1.5, rr_valid=False)
    r = run_options_council(chain, sizing, stock_rr=2.5)
    assert r.verdict == "BLOCK"
    assert any("RR_BELOW_MIN" in b for b in r.blocks)


def test_rr_parity_fail_blocks():
    chain = make_chain()
    # stock_rr=3.0, option_rr=1.8 -> parity threshold=3.0, fails
    sizing = make_sizing(rr_option=1.8, rr_valid=False)
    r = run_options_council(chain, sizing, stock_rr=3.0)
    assert r.verdict == "BLOCK"
    assert any("RR_PARITY" in b for b in r.blocks)


# ---------------------------------------------------------------------------
# Caution tests
# ---------------------------------------------------------------------------

def test_iv_high_caution():
    chain = make_chain(iv=0.55)  # 55% > 50 threshold
    sizing = make_sizing(rr_option=2.5, rr_valid=True)
    r = run_options_council(chain, sizing, stock_rr=2.0)
    assert r.verdict == "CAUTION"
    assert r.spread_recommended is True
    assert any("IV_HIGH" in c for c in r.cautions)


def test_zero_contracts_caution():
    chain = make_chain()
    sizing = make_sizing(contracts=0, override_required=True, rr_option=2.5, rr_valid=True)
    r = run_options_council(chain, sizing, stock_rr=2.0)
    assert r.verdict == "CAUTION"
    assert any("ZERO_CONTRACTS" in c for c in r.cautions)


# ---------------------------------------------------------------------------
# Clean PASS
# ---------------------------------------------------------------------------

def test_clean_pass():
    chain = make_chain(open_interest=500, spread_pct_of_mid=3.0, iv=0.20)
    sizing = make_sizing(rr_option=2.5, rr_valid=True, contracts=2)
    r = run_options_council(chain, sizing, stock_rr=2.3)
    assert r.verdict == "PASS"
    assert r.blocks == []
    assert r.cautions == []