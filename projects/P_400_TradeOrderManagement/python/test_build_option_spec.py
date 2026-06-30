"""test_build_option_spec.py -- Unit tests for application\build_option_spec.py.

Covers: chart-based PASS full grid, override-required 1-contract note,
zero-contract no-override [NO SPEC], paper banner, OCC call/put format,
leverage multiple, dual stock->option price block.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from schemas import OptionChainInput
from domain.options_sizer import OptionSizingResult
from application.build_option_spec import build_option_spec


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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
        method="chart_based", contracts=2,
        option_entry=5.00, option_stop=2.50, option_target=10.00,
        risk_per_contract=250.0, total_risk_dollars=500.0,
        adjusted_risk_budget=245.02, rr_option=2.0, rr_valid=True,
        override_required=False, spread_recommended=False,
        gate1_contracts=2, gate2_contracts=10, gate3_contracts=5,
        winning_gate="RISK", warning=None, notes=[],
    )
    defaults.update(kwargs)
    return OptionSizingResult(**defaults)


def render(**kwargs) -> str:
    args = dict(
        underlying_symbol="TEST", chain=make_chain(), sizing=make_sizing(),
        stock_entry=100.0, stock_stop=95.0, stock_target=110.0, is_paper=False,
    )
    args.update(kwargs)
    return build_option_spec(**args)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_chart_based_pass_renders_full_grid():
    out = render()
    assert "PATTERN B" in out
    assert "Contracts:    2" in out
    assert "LEG 1 -- Entry" in out
    assert "LEG 2 -- Stop Loss" in out
    assert "LEG 3 -- Take Profit" in out
    assert "[NO SPEC" not in out
    assert "[OVERRIDE" not in out


def test_dual_price_block_shows_both():
    out = render()
    assert "TEST 100.00  ->  option $5.00" in out
    assert "TEST 95.00  ->  option ~$2.50" in out
    assert "TEST 110.00  ->  option ~$10.00" in out


def test_leverage_multiple_rendered():
    # |0.50| * 100.0 / 5.00 = 10.0x
    out = render()
    assert "10.0x" in out


def test_underlying_stop_trigger_not_option_mark():
    out = render()
    assert "TEST stock at or below 95.00" in out


# ---------------------------------------------------------------------------
# OCC symbol format
# ---------------------------------------------------------------------------

def test_occ_call_format():
    out = render(underlying_symbol="ADBE",
                 chain=make_chain(symbol="ADBE", strike=215.0,
                                  expiration="2026-07-17", option_type="call"))
    assert "ADBE  260717C00215000" in out


def test_occ_put_format():
    out = render(underlying_symbol="MCHP",
                 chain=make_chain(symbol="MCHP", strike=80.0,
                                  expiration="2026-03-20", option_type="put",
                                  delta=-0.45))
    assert "MCHP  260320P00080000" in out


# ---------------------------------------------------------------------------
# Override / zero-contract / paper
# ---------------------------------------------------------------------------

def test_override_required_renders_one_contract_with_note():
    out = render(sizing=make_sizing(contracts=0, override_required=True,
                                    total_risk_dollars=0.0))
    assert out.startswith("[OVERRIDE")
    assert "Contracts:    1" in out
    assert "Qty:     1" in out


def test_zero_contracts_no_override_returns_no_spec():
    out = render(sizing=make_sizing(contracts=0, override_required=False))
    assert out.startswith("[NO SPEC")
    assert "PATTERN B" not in out


def test_paper_banner_prepended():
    out = render(is_paper=True)
    assert "*** PAPER TRADE -- NOT FOR SUBMISSION TO SCHWAB ***" in out