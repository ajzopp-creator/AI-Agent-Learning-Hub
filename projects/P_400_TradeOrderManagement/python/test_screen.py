"""Tests for domain/screen.py — WO-P400-E2.001 verify.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_screen.py -v

Covers PASS/FAIL/WARN reason codes against fixture packets.
"""

import sys
import os
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
            signal_date_str="2026-06-12T10:00:00", **ctx_overrides):
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
# FAIL: heat breach
# ---------------------------------------------------------------------------

def test_fail_heat_breach():
    # current_heat=3800, gate1*risk=245*2=490, projected=4290 > 3920 cap
    r = _screen(current_heat_dollars=3800.0)
    assert r.outcome == SCREEN_FAIL
    assert RC_HEAT_BREACH in r.reason_codes


# ---------------------------------------------------------------------------
# FAIL: position count
# ---------------------------------------------------------------------------

def test_fail_position_count():
    r = _screen(open_position_count=8)
    assert r.outcome == SCREEN_FAIL
    assert RC_POSITION_COUNT in r.reason_codes


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
        signal_date_str="2026-06-12T10:00:00",
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
    # 2026-01-01 is ~100+ trading days ago
    r = _screen(signal_date_str="2026-01-01T10:00:00")
    assert r.outcome == SCREEN_WARN
    assert RC_SIGNAL_STALE in r.reason_codes

def test_fresh_signal_no_stale_warn():
    r = _screen(signal_date_str="2026-06-12T09:00:00")
    assert RC_SIGNAL_STALE not in r.reason_codes


# ---------------------------------------------------------------------------
# screen_all ranking
# ---------------------------------------------------------------------------

def test_screen_all_pass_first():
    signals = [
        {"symbol": "BAD", "signal_file": "bad.json", "entry": 50.0, "stop": 48.0,
         "target": 52.0, "signal_date_str": "2026-06-12T10:00:00"},   # rr=1.0 FAIL
        {"symbol": "GOOD", "signal_file": "good.json", "entry": 50.0, "stop": 48.0,
         "target": 54.0, "signal_date_str": "2026-06-12T10:00:00"},   # rr=2.0 PASS
    ]
    ctx = _base_context()
    results = screen_all(signals, ctx)
    assert results[0].symbol == "GOOD"
    assert results[0].outcome == SCREEN_PASS
    assert results[1].outcome == SCREEN_FAIL

def test_screen_all_ranked_by_rr_within_pass():
    signals = [
        {"symbol": "A", "signal_file": "a.json", "entry": 50.0, "stop": 48.0,
         "target": 54.0, "signal_date_str": "2026-06-12T10:00:00"},   # rr=2.0
        {"symbol": "B", "signal_file": "b.json", "entry": 50.0, "stop": 48.0,
         "target": 56.0, "signal_date_str": "2026-06-12T10:00:00"},   # rr=3.0
    ]
    ctx = _base_context()
    results = screen_all(signals, ctx)
    # B has higher RR and should come first
    assert results[0].symbol == "B"
