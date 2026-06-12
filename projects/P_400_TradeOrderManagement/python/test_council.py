"""Tests for domain/council.py — WO-P400-E2.001 verify.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_council.py -v

Covers every block threshold hit and missed; full verdict table.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from domain.council import (
    Decision,
    Role,
    behavioral_vote,
    council_verdict,
    macro_vote,
    quant_vote,
    risk_vote,
    tape_vote,
)
from domain.council_codes import (
    RC_ADVERSE_DRIFT,
    RC_ALL_CLEAR,
    RC_DAILY_LOSS,
    RC_EARNINGS_IN_WINDOW,
    RC_HEAT_BREACH,
    RC_MARKET_CLOSED,
    RC_OVERTRADING,
    RC_POSITION_COUNT,
    RC_PRICE_STALE,
    RC_REVENGE_TRADE,
    RC_RR_BELOW_MIN,
    RC_SECTOR_CONCENTRATION,
    RC_STOP_TOO_TIGHT,
    RC_STREAK_CHASING,
)


# ---------------------------------------------------------------------------
# Quant role
# ---------------------------------------------------------------------------

def test_quant_pass():
    v = quant_vote(rr_at_t1=2.5, stop=48.0, entry=50.0, target=55.0, atr_14=1.5)
    assert v.decision == Decision.PASS

def test_quant_blocks_rr_below_min():
    v = quant_vote(rr_at_t1=1.8, stop=48.0, entry=50.0, target=53.6, atr_14=1.5)
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_RR_BELOW_MIN

def test_quant_blocks_stop_too_tight():
    # risk_per_share=0.30, ATR=1.5 -> 0.30 < 1.0 * 1.5
    v = quant_vote(rr_at_t1=2.5, stop=49.7, entry=50.0, target=55.0, atr_14=1.5)
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_STOP_TOO_TIGHT

def test_quant_passes_when_atr_zero():
    # atr=0 means we cannot apply ATR block — should pass ATR check
    v = quant_vote(rr_at_t1=2.5, stop=48.0, entry=50.0, target=55.0, atr_14=0.0)
    assert v.decision == Decision.PASS


# ---------------------------------------------------------------------------
# Risk role
# ---------------------------------------------------------------------------

def test_risk_pass():
    v = risk_vote(
        new_trade_risk_dollars=490.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=2,
        realized_day_loss_dollars=0.0, new_sector="Tech",
        open_sector_counts={"Tech": 1},
    )
    assert v.decision == Decision.PASS

def test_risk_blocks_heat_breach():
    # heat_cap = 32669 * 0.12 = 3920; current=3800, new=500 -> 4300 > cap
    v = risk_vote(
        new_trade_risk_dollars=500.0, current_heat_dollars=3800.0,
        account_balance=32669.72, open_position_count=2,
        realized_day_loss_dollars=0.0, new_sector=None,
        open_sector_counts={},
    )
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_HEAT_BREACH

def test_risk_blocks_position_count():
    v = risk_vote(
        new_trade_risk_dollars=100.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=8,
        realized_day_loss_dollars=0.0, new_sector=None,
        open_sector_counts={},
    )
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_POSITION_COUNT

def test_risk_blocks_daily_loss():
    # circuit breaker = 32669 * 0.03 = 980; loss=1000 >= 980
    v = risk_vote(
        new_trade_risk_dollars=100.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=0,
        realized_day_loss_dollars=1000.0, new_sector=None,
        open_sector_counts={},
    )
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_DAILY_LOSS

def test_risk_blocks_sector_concentration():
    v = risk_vote(
        new_trade_risk_dollars=100.0, current_heat_dollars=0.0,
        account_balance=32669.72, open_position_count=2,
        realized_day_loss_dollars=0.0, new_sector="Tech",
        open_sector_counts={"Tech": 2},
    )
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_SECTOR_CONCENTRATION


# ---------------------------------------------------------------------------
# Macro role
# ---------------------------------------------------------------------------

def test_macro_pass():
    v = macro_vote(earnings_in_window=False)
    assert v.decision == Decision.PASS

def test_macro_blocks_earnings():
    v = macro_vote(earnings_in_window=True, defined_risk_confirmed=False)
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_EARNINGS_IN_WINDOW

def test_macro_caution_when_defined_risk_confirmed():
    v = macro_vote(earnings_in_window=True, defined_risk_confirmed=True)
    assert v.decision == Decision.CAUTION
    assert v.reason_code == RC_EARNINGS_IN_WINDOW

def test_macro_blocks_binary_event():
    v = macro_vote(earnings_in_window=False, binary_events=["FDA decision 2026-06-20"])
    assert v.decision == Decision.BLOCK


# ---------------------------------------------------------------------------
# Tape role
# ---------------------------------------------------------------------------

def test_tape_pass():
    v = tape_vote(price_delay_seconds=30, market_open=True, pre_market_flag=False,
                  adverse_drift_pct=0.0, rr_after_drift=2.5)
    assert v.decision == Decision.PASS

def test_tape_blocks_stale_price():
    v = tape_vote(price_delay_seconds=200, market_open=True, pre_market_flag=False,
                  adverse_drift_pct=0.0, rr_after_drift=2.5)
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_PRICE_STALE

def test_tape_blocks_market_closed():
    v = tape_vote(price_delay_seconds=30, market_open=False, pre_market_flag=False,
                  adverse_drift_pct=0.0, rr_after_drift=2.5)
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_MARKET_CLOSED

def test_tape_passes_market_closed_with_premarket_flag():
    v = tape_vote(price_delay_seconds=30, market_open=False, pre_market_flag=True,
                  adverse_drift_pct=0.0, rr_after_drift=2.5)
    assert v.decision == Decision.PASS

def test_tape_blocks_adverse_drift():
    v = tape_vote(price_delay_seconds=30, market_open=True, pre_market_flag=False,
                  adverse_drift_pct=2.5, rr_after_drift=1.5)
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_ADVERSE_DRIFT


# ---------------------------------------------------------------------------
# Behavioral role (annotates, never blocks)
# ---------------------------------------------------------------------------

def test_behavioral_pass():
    v = behavioral_vote("AAPL")
    assert v.decision == Decision.PASS
    assert v.can_block is False

def test_behavioral_revenge_caution():
    v = behavioral_vote("AAPL", recently_stopped_out_symbols=["AAPL", "MSFT"])
    assert v.decision == Decision.CAUTION
    assert v.reason_code == RC_REVENGE_TRADE
    assert v.can_block is False

def test_behavioral_overtrading():
    v = behavioral_vote("AAPL", orders_today=10, daily_order_norm=3)
    assert v.decision == Decision.CAUTION
    assert v.reason_code == RC_OVERTRADING

def test_behavioral_streak_chasing():
    v = behavioral_vote("AAPL", consecutive_wins=4, win_streak_threshold=3)
    assert v.decision == Decision.CAUTION
    assert v.reason_code == RC_STREAK_CHASING


# ---------------------------------------------------------------------------
# Verdict assembly
# ---------------------------------------------------------------------------

def test_verdict_approved_all_pass():
    votes = [
        quant_vote(2.5, 48.0, 50.0, 55.0, 1.5),
        risk_vote(490.0, 0.0, 32669.72, 0, 0.0, None, {}),
        macro_vote(False),
        tape_vote(30, True, False, 0.0, 2.5),
        behavioral_vote("AAPL"),
    ]
    r = council_verdict(votes)
    assert r.verdict == "APPROVED"

def test_verdict_blocked_by_quant():
    votes = [
        quant_vote(1.5, 48.0, 50.0, 53.0, 1.5),  # RR too low -> BLOCK
        risk_vote(490.0, 0.0, 32669.72, 0, 0.0, None, {}),
        macro_vote(False),
        tape_vote(30, True, False, 0.0, 2.5),
        behavioral_vote("AAPL"),
    ]
    r = council_verdict(votes)
    assert r.verdict == "BLOCKED"
    assert RC_RR_BELOW_MIN in r.block_codes

def test_verdict_caution_behavioral_only():
    votes = [
        quant_vote(2.5, 48.0, 50.0, 55.0, 1.5),
        risk_vote(490.0, 0.0, 32669.72, 0, 0.0, None, {}),
        macro_vote(False),
        tape_vote(30, True, False, 0.0, 2.5),
        behavioral_vote("AAPL", recently_stopped_out_symbols=["AAPL"]),
    ]
    r = council_verdict(votes)
    # Behavioral CAUTION with can_block=False -> APPROVED_WITH_CAUTION (not BLOCKED)
    assert r.verdict == "APPROVED_WITH_CAUTION"

def test_behavioral_caution_cannot_block():
    # Even with behavioral CAUTION, if all real roles PASS, not BLOCKED
    votes = [
        quant_vote(2.5, 48.0, 50.0, 55.0, 1.5),
        risk_vote(490.0, 0.0, 32669.72, 0, 0.0, None, {}),
        macro_vote(False),
        tape_vote(30, True, False, 0.0, 2.5),
        behavioral_vote("AAPL", orders_today=20, daily_order_norm=3),
    ]
    r = council_verdict(votes)
    assert r.verdict == "APPROVED_WITH_CAUTION"
    assert "BLOCKED" not in r.verdict
