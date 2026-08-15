"""Tests for domain/sizing.py — WO-P400-E2.001 verify.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_sizing.py -v

All tests use p140 conda env. No network, no file I/O.
"""

import sys
import os

import pytest
from domain.sizing import three_gate_size, options_size, posture_multiplier, realistic_fill_rr


# ---------------------------------------------------------------------------
# posture_multiplier
# ---------------------------------------------------------------------------

def test_posture_off():
    assert posture_multiplier("OFF") == 0.50

def test_posture_correction():
    assert posture_multiplier("CORRECTION") == 0.50

def test_posture_half():
    assert posture_multiplier("HALF") == 0.75

def test_posture_standard():
    assert posture_multiplier("STANDARD") == 1.00

def test_posture_full():
    assert posture_multiplier("FULL") == 1.00

def test_posture_hot():
    assert posture_multiplier("HOT") == 1.00

def test_posture_unknown_defaults_to_1():
    assert posture_multiplier("UNKNOWN_MODE") == 1.00


# ---------------------------------------------------------------------------
# realistic_fill_rr
# ---------------------------------------------------------------------------

def test_rr_basic():
    # entry=50, stop=48, target=54 -> risk=2, reward=4, rr=2.0
    rr = realistic_fill_rr(50.0, 48.0, 54.0)
    assert rr == 2.0

def test_rr_with_spread():
    # entry=50 + 0.05 spread = 50.05; target=54 - 0.05 = 53.95; risk=50.05-48=2.05; reward=3.90
    rr = realistic_fill_rr(50.0, 48.0, 54.0, half_spread=0.05)
    assert rr < 2.0  # spread reduces R:R

def test_rr_invalid_stop():
    assert realistic_fill_rr(50.0, 51.0, 55.0) == 0.0  # stop >= entry


# ---------------------------------------------------------------------------
# three_gate_size — STANDARD risk_mode
# ---------------------------------------------------------------------------

def test_standard_risk_gate_wins():
    # base_risk=490, entry=50, stop=48, cash=50000, max_pos=1633
    # Gate1 = 490/2 = 245 shares
    # Gate2 = 50000/50 = 1000
    # Gate3 = 1633/50 = 32
    # smallest = 32 (Gate3)
    result = three_gate_size(
        entry=50.0, stop=48.0, target=54.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="STANDARD",
    )
    assert result.shares == 32
    assert result.winning_gate == "CONCENTRATION"

def test_risk_gate_wins_when_cash_large():
    # Gate1 = 490/2 = 245, Gate2 = 500/50 = 10, Gate3 = 1633/50 = 32
    # smallest = 10 (Cash)
    result = three_gate_size(
        entry=50.0, stop=48.0, target=54.0,
        base_risk_dollars=490.04, cash_available=500.0,
        max_position_dollars=1633.47, risk_mode="STANDARD",
    )
    assert result.shares == 10
    assert result.winning_gate == "CASH"

def test_risk_gate_itself_wins():
    # entry=100, stop=99 -> risk_per_share=1 -> gate1=490 shares
    # Gate2=50000/100=500, Gate3=1633/100=16
    # smallest=16
    result = three_gate_size(
        entry=100.0, stop=99.0, target=102.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="STANDARD",
    )
    assert result.shares == 16

def test_off_mode_50pct():
    # OFF mode -> adj_risk = 490 * 0.50 = 245
    # Same setup as standard test, Gate1 = 245/2 = 122
    result_std = three_gate_size(
        entry=50.0, stop=48.0, target=54.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="STANDARD",
    )
    result_off = three_gate_size(
        entry=50.0, stop=48.0, target=54.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="OFF",
    )
    assert result_off.adjusted_risk_dollars == pytest.approx(245.02, rel=0.01)
    assert result_off.posture_multiplier == 0.50

def test_invalid_stop_returns_zero():
    result = three_gate_size(
        entry=50.0, stop=51.0, target=54.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="STANDARD",
    )
    assert result.shares == 0
    assert result.winning_gate == "INVALID"

def test_rr_valid_flag():
    # target=54, entry=50, stop=48 -> rr=2.0 -> valid
    result = three_gate_size(
        entry=50.0, stop=48.0, target=54.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="STANDARD",
    )
    assert result.rr_valid is True

def test_rr_invalid_flag():
    # target=51, entry=50, stop=48 -> rr=0.5 -> invalid
    result = three_gate_size(
        entry=50.0, stop=48.0, target=51.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="STANDARD",
    )
    assert result.rr_valid is False


# ---------------------------------------------------------------------------
# options_size
# ---------------------------------------------------------------------------

def test_options_basic():
    # adj_risk = 490 * 1.0 = 490; haircut=0.20 -> budget=392
    # premium = 200/contract -> contracts = 1
    result = options_size(
        base_risk_dollars=490.04, risk_mode="STANDARD",
        premium_per_contract=200.0, option_delta=0.50,
    )
    assert result.contracts == 1
    assert result.haircut_applied_dollars == pytest.approx(98.0, rel=0.01)

def test_options_off_mode():
    # adj_risk = 490 * 0.50 = 245; haircut=0.20 -> budget=196
    # premium=200 -> 0 contracts
    result = options_size(
        base_risk_dollars=490.04, risk_mode="OFF",
        premium_per_contract=200.0, option_delta=0.50,
    )
    assert result.contracts == 0
    assert result.warning is not None

def test_options_invalid_premium():
    result = options_size(
        base_risk_dollars=490.04, risk_mode="STANDARD",
        premium_per_contract=0.0, option_delta=0.50,
    )
    assert result.contracts == 0
    assert "invalid" in result.warning.lower()

# ---------------------------------------------------------------------------
# three_gate_size -- Gate 3 posture scaling (WO-P400-E2.014)
# ---------------------------------------------------------------------------

def test_gate3_standard_unreduced():
    # entry=50, stop=40, huge cash -> Gate 3 binds. STANDARD cap $1,633.47.
    # Gate3 = 1633.47/50 = 32; Gate1 = 490/10 = 49 -> smallest 32 (CONCENTRATION)
    result = three_gate_size(
        entry=50.0, stop=40.0, target=70.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="STANDARD",
    )
    assert result.gate3_shares == 32
    assert result.shares == 32
    assert result.winning_gate == "CONCENTRATION"

def test_gate3_scales_half():
    # HALF cap = 1633.47 * 0.75 = 1225.10 -> 1225.10/50 = 24 shares
    result = three_gate_size(
        entry=50.0, stop=40.0, target=70.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="HALF",
    )
    assert result.gate3_shares == 24
    assert result.shares == 24
    assert result.winning_gate == "CONCENTRATION"

def test_gate3_scales_off():
    # OFF cap = 1633.47 * 0.50 = 816.74 -> 816.74/50 = 16 shares
    result = three_gate_size(
        entry=50.0, stop=40.0, target=70.0,
        base_risk_dollars=490.04, cash_available=50000.0,
        max_position_dollars=1633.47, risk_mode="OFF",
    )
    assert result.gate3_shares == 16
    assert result.shares == 16
    assert result.winning_gate == "CONCENTRATION"
