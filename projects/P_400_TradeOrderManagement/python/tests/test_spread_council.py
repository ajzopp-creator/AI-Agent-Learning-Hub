r"""Tests for domain/spread_council.py -- WO-P400-E3.005 verify.

Run: C:\Users\Trader\.conda\envs\p140\python.exe -m pytest test_spread_council.py -v

Covers: both-legs-pass, long-leg-fails, short-leg-fails, both-fail, and
the ADBE 215C/225C regression case (short leg spread_pct_of_mid=11.9%,
which sized cleanly and rendered a full spec before this WO -- must
BLOCK now).
"""

import sys
import os

from schemas import OptionChainInput
from domain.spread_council import run_spread_council


def _chain(symbol="TEST", strike=100.0, option_type="call", oi=500,
           spread_pct=5.0, bid=2.00, ask=2.10):
    mid = round((bid + ask) / 2, 2)
    return OptionChainInput(
        symbol=symbol, underlying_price=100.0, expiration="2026-08-21",
        strike=strike, option_type=option_type, bid=bid, ask=ask, mid=mid,
        delta=0.5, iv=0.30, open_interest=oi, spread_pct_of_mid=spread_pct,
        data_source="tos", chain_timestamp="2026-07-04T10:00:00Z",
    )


# ---------------------------------------------------------------------------
# Both legs pass
# ---------------------------------------------------------------------------

def test_both_legs_pass():
    long_chain = _chain(strike=215.0, oi=500, spread_pct=4.0)
    short_chain = _chain(strike=225.0, oi=400, spread_pct=6.0)
    result = run_spread_council(long_chain, short_chain)
    assert result.verdict == "PASS"
    assert result.blocks == []


# ---------------------------------------------------------------------------
# Long leg fails
# ---------------------------------------------------------------------------

def test_long_leg_fails_oi():
    long_chain = _chain(strike=215.0, oi=50, spread_pct=4.0)
    short_chain = _chain(strike=225.0, oi=400, spread_pct=6.0)
    result = run_spread_council(long_chain, short_chain)
    assert result.verdict == "BLOCK"
    assert any("LONG_LEG_OI_TOO_LOW" in b for b in result.blocks)


def test_long_leg_fails_spread():
    long_chain = _chain(strike=215.0, oi=500, spread_pct=15.0)
    short_chain = _chain(strike=225.0, oi=400, spread_pct=6.0)
    result = run_spread_council(long_chain, short_chain)
    assert result.verdict == "BLOCK"
    assert any("LONG_LEG_SPREAD_TOO_WIDE" in b for b in result.blocks)


# ---------------------------------------------------------------------------
# Short leg fails
# ---------------------------------------------------------------------------

def test_short_leg_fails_oi():
    long_chain = _chain(strike=215.0, oi=500, spread_pct=4.0)
    short_chain = _chain(strike=225.0, oi=80, spread_pct=6.0)
    result = run_spread_council(long_chain, short_chain)
    assert result.verdict == "BLOCK"
    assert any("SHORT_LEG_OI_TOO_LOW" in b for b in result.blocks)


def test_short_leg_fails_spread():
    long_chain = _chain(strike=215.0, oi=500, spread_pct=4.0)
    short_chain = _chain(strike=225.0, oi=400, spread_pct=11.9)
    result = run_spread_council(long_chain, short_chain)
    assert result.verdict == "BLOCK"
    assert any("SHORT_LEG_SPREAD_TOO_WIDE" in b for b in result.blocks)


# ---------------------------------------------------------------------------
# Both legs fail
# ---------------------------------------------------------------------------

def test_both_legs_fail():
    long_chain = _chain(strike=215.0, oi=50, spread_pct=15.0)
    short_chain = _chain(strike=225.0, oi=80, spread_pct=12.0)
    result = run_spread_council(long_chain, short_chain)
    assert result.verdict == "BLOCK"
    assert len(result.blocks) == 4
    assert any("LONG_LEG_OI_TOO_LOW" in b for b in result.blocks)
    assert any("LONG_LEG_SPREAD_TOO_WIDE" in b for b in result.blocks)
    assert any("SHORT_LEG_OI_TOO_LOW" in b for b in result.blocks)
    assert any("SHORT_LEG_SPREAD_TOO_WIDE" in b for b in result.blocks)


# ---------------------------------------------------------------------------
# ADBE regression -- WO-P400-E3.005 canonical case
# ---------------------------------------------------------------------------

def test_adbe_215c_225c_regression_blocks():
    """Real case found live 2026-06-30: short leg (225C) spread_pct_of_mid
    =11.9% sized cleanly and rendered a full Pattern C spec before this
    WO. Must BLOCK now -- same leg would BLOCK outright on single-leg path.
    """
    long_chain = _chain(symbol="ADBE", strike=215.0, option_type="call",
                         oi=800, spread_pct=3.5, bid=18.50, ask=18.90)
    short_chain = _chain(symbol="ADBE", strike=225.0, option_type="call",
                          oi=300, spread_pct=11.9, bid=9.20, ask=10.45)
    result = run_spread_council(long_chain, short_chain)
    assert result.verdict == "BLOCK"
    assert any("SHORT_LEG_SPREAD_TOO_WIDE" in b for b in result.blocks)
    assert not any("LONG_LEG" in b for b in result.blocks)