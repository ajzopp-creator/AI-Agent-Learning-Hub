r"""Tests for domain/risk_vote.py -- RISK role, extracted from council.py 2026-07-20.

Run: C:\Users\Trader\.conda\envs\p140\python.exe -m pytest test_risk_vote.py -v

RISK never blocks (Tony directive 2026-07-20). Every threshold that used to
BLOCK now returns SEVERE_WARNING with can_block=False. Covers all 5 checks
(4 original + new cash-vs-risk) hit and missed, plus the open-positions
note and the never-BLOCK guarantee.
"""

import sys
import os

import pytest
from domain.council import Decision
from domain.risk_vote import risk_vote
from domain.council_codes import (
    RC_ALL_CLEAR,
    RC_CASH_BELOW_RISK,
    RC_DAILY_LOSS,
    RC_HEAT_BREACH,
    RC_POSITION_COUNT,
    RC_SECTOR_CONCENTRATION,
)


def test_risk_pass_all_clear():
    v = risk_vote(
        new_trade_risk_dollars=490.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=2,
        realized_day_loss_dollars=0.0, new_sector="Tech",
        open_sector_counts={"Tech": 1},
        cash_available=1000.0, adjusted_risk_dollars=490.0,
    )
    assert v.decision == Decision.PASS
    assert v.reason_code == RC_ALL_CLEAR


def test_risk_severe_warning_heat_breach():
    # heat_cap = 32669 * 0.12 = 3920; current=3800, new=500 -> 4300 > cap
    v = risk_vote(
        new_trade_risk_dollars=500.0, current_heat_dollars=3800.0,
        account_balance=32669.72, open_position_count=2,
        realized_day_loss_dollars=0.0, new_sector=None,
        open_sector_counts={},
        cash_available=1000.0, adjusted_risk_dollars=500.0,
    )
    assert v.decision == Decision.SEVERE_WARNING
    assert v.reason_code == RC_HEAT_BREACH
    assert v.can_block is False


def test_risk_severe_warning_position_count():
    v = risk_vote(
        new_trade_risk_dollars=100.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=8,
        realized_day_loss_dollars=0.0, new_sector=None,
        open_sector_counts={},
        cash_available=1000.0, adjusted_risk_dollars=100.0,
        open_symbols=["AMX", "ATKR", "EME"],
    )
    assert v.decision == Decision.SEVERE_WARNING
    assert v.reason_code == RC_POSITION_COUNT
    assert v.can_block is False
    assert "AMX" in v.reason_detail  # open-positions note attached


def test_risk_severe_warning_daily_loss():
    # circuit breaker = 32669 * 0.03 = 980; loss=1000 >= 980
    v = risk_vote(
        new_trade_risk_dollars=100.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=0,
        realized_day_loss_dollars=1000.0, new_sector=None,
        open_sector_counts={},
        cash_available=1000.0, adjusted_risk_dollars=100.0,
    )
    assert v.decision == Decision.SEVERE_WARNING
    assert v.reason_code == RC_DAILY_LOSS
    assert v.can_block is False


def test_risk_severe_warning_sector_concentration():
    v = risk_vote(
        new_trade_risk_dollars=100.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=2,
        realized_day_loss_dollars=0.0, new_sector="Tech",
        open_sector_counts={"Tech": 2},
        cash_available=1000.0, adjusted_risk_dollars=100.0,
    )
    assert v.decision == Decision.SEVERE_WARNING
    assert v.reason_code == RC_SECTOR_CONCENTRATION
    assert v.can_block is False


def test_risk_severe_warning_cash_below_risk():
    # New check 2026-07-20: cash < posture-adjusted risk$ for this trade.
    v = risk_vote(
        new_trade_risk_dollars=100.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=0,
        realized_day_loss_dollars=0.0, new_sector=None,
        open_sector_counts={},
        cash_available=150.0, adjusted_risk_dollars=240.54,
    )
    assert v.decision == Decision.SEVERE_WARNING
    assert v.reason_code == RC_CASH_BELOW_RISK
    assert v.can_block is False


def test_risk_cash_exactly_equal_to_risk_passes():
    # Boundary: cash == adjusted_risk_dollars should PASS, not warn.
    v = risk_vote(
        new_trade_risk_dollars=100.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=0,
        realized_day_loss_dollars=0.0, new_sector=None,
        open_sector_counts={},
        cash_available=240.54, adjusted_risk_dollars=240.54,
    )
    assert v.decision == Decision.PASS
    assert v.reason_code == RC_ALL_CLEAR


def test_risk_never_returns_block():
    # Exhaustive worst-case: no combination of inputs should ever produce
    # Decision.BLOCK. This is the core guarantee of the 2026-07-20 change.
    v = risk_vote(
        new_trade_risk_dollars=99999.0, current_heat_dollars=99999.0,
        account_balance=32669.72, open_position_count=99,
        realized_day_loss_dollars=99999.0, new_sector="Tech",
        open_sector_counts={"Tech": 99},
        cash_available=0.0, adjusted_risk_dollars=99999.0,
    )
    assert v.decision != Decision.BLOCK
    assert v.can_block is False