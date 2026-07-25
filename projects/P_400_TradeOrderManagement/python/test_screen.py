r"""Tests for domain/screen.py -- WO-P400-E2.001 verify.

Run: C:\Users\Trader\.conda\envs\p140\python.exe -m pytest test_screen.py -v

Covers PASS/FAIL/WARN reason codes against fixture packets.
HEAT_BREACH/POSITION_COUNT downgraded FAIL -> WARN 2026-07-20 -- see
domain/screen.py docstring. WARN-never-disposed is covered separately in
test_dispose_failed.py::test_warn_never_disposed (outcome-based, already
covers these two reason codes with no changes needed there).
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from domain.screen import (
    SCREEN_FAIL,
    SCREEN_PASS,
    SCREEN_WARN,
    RC_DUPLICATE,
    RC_HEAT_BREACH,
    RC_POSITION_COUNT,
    RC_SIGNAL_STALE,
    RC_ZERO_SHARES,
    screen_all,
    screen_signal,
)
from domain.council_codes import RC_RR_BELOW_MIN


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _fresh_signal_date_str(days_ago: int = 1) -> str:
    """Return an ISO date string `days_ago` calendar days before now.

    Test fixtures use this instead of a hardcoded absolute date so
    "fresh, not stale" cases stay fresh no matter what day the suite
    runs (WO-P400-E3.008 -- a hardcoded 2026-07-02 date drifted past
    the 3-trading-day staleness window within a few calendar days and
    started failing tests that had nothing to do with the code change
    under review).
    """
    return (datetime.now() - timedelta(days=days_ago)).isoformat()

def _base_context(**overrides):
    ctx = {
        "risk_mode": "STANDARD",
        "base_risk_dollars": 490.04,
        "current_heat_dollars": 0.0,
        "heat_cap_dollars": 3920.37,
        "open_position_count": 0,
        "max_positions": 8,
        "open_symbols": [],
    }
    ctx.update(overrides)
    return ctx


def _screen(symbol="AAPL", entry=50.0, stop=48.0, target=54.0,
            signal_date_str=None, **ctx_overrides):
    if signal_date_str is None:
        signal_date_str = _fresh_signal_date_str()
    ctx = _base_context(**ctx_overrides)
    return screen_signal(
        symbol=symbol,
        signal_file=f"{symbol}_test_v2.0.json",
        entry=entry, stop=stop, target=target,
        signal_date_str=signal_date_str,
        risk_mode=ctx["risk_mode"],
        base_risk_dollars=ctx["base_risk_dollars"],
        current_heat_dollars=ctx["current_heat_dollars"],
        heat_cap_dollars=ctx["heat_cap_dollars"],
        open_position_count=ctx["open_position_count"],
        max_positions=ctx["max_positions"],
        open_symbols=ctx["open_symbols"],
    )


# ---------------------------------------------------------------------------
# PASS cases
# ---------------------------------------------------------------------------

def test_clean_signal_passes():
    r = _screen()
    assert r.outcome == SCREEN_PASS
    assert r.reason_codes == []

def test_pass_includes_rr():
    r = _screen(entry=50.0, stop=48.0, target=54.0)
    assert r.packet_rr == pytest.approx(2.0)

def test_pass_includes_gate1_shares():
    # adj_risk=490, risk_per_share=2 -> gate1=245
    r = _screen()
    assert r.posture_gate_shares == 245


# ---------------------------------------------------------------------------
# FAIL: R:R below minimum
# ---------------------------------------------------------------------------

def test_fail_rr_too_low():
    r = _screen(entry=50.0, stop=48.0, target=52.0)  # rr=1.0
    assert r.outcome == SCREEN_FAIL
    assert RC_RR_BELOW_MIN in r.reason_codes

def test_fail_rr_just_below():
    # rr = (53.9 - 50) / (50 - 48) = 3.9/2 = 1.95 < 2.0
    r = _screen(entry=50.0, stop=48.0, target=53.9)
    assert r.outcome == SCREEN_FAIL

def test_pass_rr_exactly_at_minimum():
    r = _screen(entry=50.0, stop=48.0, target=54.0)  # rr=2.0
    assert r.outcome == SCREEN_PASS


# ---------------------------------------------------------------------------
# FAIL: duplicate symbol
# ---------------------------------------------------------------------------

def test_fail_duplicate():
    r = _screen(symbol="AAPL", open_symbols=["AAPL", "MSFT"])
    assert r.outcome == SCREEN_FAIL
    assert RC_DUPLICATE in r.reason_codes

def test_fail_duplicate_case_insensitive():
    r = _screen(symbol="aapl", open_symbols=["AAPL"])
    assert RC_DUPLICATE in r.reason_codes


# ---------------------------------------------------------------------------
# WARN: heat breach (downgraded from FAIL 2026-07-20)
# ---------------------------------------------------------------------------

def test_warn_heat_breach():
    # current_heat=3800, gate1*risk=245*2=490, projected=4290 > 3920 cap
    r = _screen(current_heat_dollars=3800.0)
    assert r.outcome == SCREEN_WARN
    assert RC_HEAT_BREACH in r.reason_codes


# ---------------------------------------------------------------------------
# WARN: position count (downgraded from FAIL 2026-07-20)
# ---------------------------------------------------------------------------

def test_warn_position_count():
    r = _screen(open_position_count=8)
    assert r.outcome == SCREEN_WARN
    assert RC_POSITION_COUNT in r.reason_codes

def test_position_count_never_fails():
    # Exhaustive: no position count, however extreme, should produce FAIL.
    r = _screen(open_position_count=999)
    assert r.outcome != SCREEN_FAIL


# ---------------------------------------------------------------------------
# FAIL: OFF mode produces 0 shares
# ---------------------------------------------------------------------------

def test_fail_zero_shares_off_mode():
    # OFF mode: adj_risk=245; entry=500, stop=498, risk_per_share=2
    # gate1 = int(245/2) = 122 — still > 0; need very tight stop
    # Use entry=500, stop=499.98 -> risk=0.02 -> gate1=int(245/0.02)=12250 — passes
    # To force 0: very high entry relative to risk budget
    # entry=5000, stop=4999, risk_per_share=1; OFF adj=245 -> gate1=245 — still fine
    # Use tiny risk budget: base_risk=5, off=2.5, entry=100, stop=99 -> gate1=int(2.5/1)=2 -- still >0
    # Force 0: base_risk=1, off=0.5, entry=100, stop=99 -> gate1=0
    r = screen_signal(
        symbol="TEST", signal_file="test.json",
        entry=100.0, stop=99.0, target=102.0,
        signal_date_str=_fresh_signal_date_str(),
        risk_mode="OFF",
        base_risk_dollars=1.0,
        current_heat_dollars=0.0,
        heat_cap_dollars=3920.0,
        open_position_count=0,
        max_positions=8,
        open_symbols=[],
    )
    assert r.outcome == SCREEN_FAIL
    assert RC_ZERO_SHARES in r.reason_codes


# ---------------------------------------------------------------------------
# WARN: stale signal
# ---------------------------------------------------------------------------

def test_warn_stale_signal():
    # ~200 calendar days ago -- always far past the 3-trading-day limit,
    # regardless of what day this suite runs (WO-P400-E3.008).
    r = _screen(signal_date_str=_fresh_signal_date_str(200))
    assert r.outcome == SCREEN_WARN
    assert RC_SIGNAL_STALE in r.reason_codes

def test_fresh_signal_no_stale_warn():
    r = _screen(signal_date_str=_fresh_signal_date_str())
    assert RC_SIGNAL_STALE not in r.reason_codes


# ---------------------------------------------------------------------------
# screen_all ranking
# ---------------------------------------------------------------------------

def test_screen_all_pass_first():
    fresh = _fresh_signal_date_str()
    signals = [
        {"symbol": "BAD", "signal_file": "bad.json", "entry": 50.0, "stop": 48.0,
         "target": 52.0, "signal_date_str": fresh},   # rr=1.0 FAIL
        {"symbol": "GOOD", "signal_file": "good.json", "entry": 50.0, "stop": 48.0,
         "target": 54.0, "signal_date_str": fresh},   # rr=2.0 PASS
    ]
    ctx = _base_context()
    results = screen_all(signals, ctx)
    assert results[0].symbol == "GOOD"
    assert results[0].outcome == SCREEN_PASS
    assert results[1].outcome == SCREEN_FAIL

def test_screen_all_ranked_by_rr_within_pass():
    fresh = _fresh_signal_date_str()
    signals = [
        {"symbol": "A", "signal_file": "a.json", "entry": 50.0, "stop": 48.0,
         "target": 54.0, "signal_date_str": fresh},   # rr=2.0
        {"symbol": "B", "signal_file": "b.json", "entry": 50.0, "stop": 48.0,
         "target": 56.0, "signal_date_str": fresh},   # rr=3.0
    ]
    ctx = _base_context()
    results = screen_all(signals, ctx)
    # B has higher RR and should come first
    assert results[0].symbol == "B"

def test_screen_all_warn_ranks_between_pass_and_fail():
    # All packets share open_position_count=8 in context, so any packet
    # that would otherwise PASS gets downgraded to WARN (position count),
    # while a genuine RR FAIL stays FAIL. WARN must rank below PASS-tier
    # RR ordering but above FAIL regardless of its own RR.
    fresh = _fresh_signal_date_str()
    signals = [
        {"symbol": "ATMAX", "signal_file": "atmax.json", "entry": 50.0, "stop": 48.0,
         "target": 54.0, "signal_date_str": fresh},   # rr=2.0 -> WARN (position count)
        {"symbol": "BADRR", "signal_file": "badrr.json", "entry": 50.0, "stop": 48.0,
         "target": 52.0, "signal_date_str": fresh},   # rr=1.0 -> FAIL (RR, stays FAIL)
        {"symbol": "CLEAN", "signal_file": "clean.json", "entry": 50.0, "stop": 48.0,
         "target": 60.0, "signal_date_str": fresh},   # rr=5.0 -> WARN (position count)
    ]
    ctx = _base_context(open_position_count=8)
    results = screen_all(signals, ctx)
    assert [r.symbol for r in results] == ["CLEAN", "ATMAX", "BADRR"]
    assert [r.outcome for r in results] == [SCREEN_WARN, SCREEN_WARN, SCREEN_FAIL]