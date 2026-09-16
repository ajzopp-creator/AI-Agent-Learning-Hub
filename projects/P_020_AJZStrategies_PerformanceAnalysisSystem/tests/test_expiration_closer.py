"""Regression tests -- WO-P020-E1.018 (0DTE cash-settled option auto-close).

Locks in the invariants that make expiration auto-close safe:
  1. A worthless 0DTE expiry (settlement_price ~0) closes with the correct
     synthetic P&L.
  2. An ITM cash-settled expiry (nonzero settlement_price) closes correctly
     too -- this isn't a special "worthless" case, closingPrice covers both.
  3. An equity/ETF option is NEVER auto-closed by this path, even past
     expiration with a settlement_price set -- the core scope guard the WO
     exists to enforce (a naive close would misrepresent an assignment).
  4. Same-day expiration is NOT eligible -- the buffer_days guard against
     the "hasn't settled yet" false positive.
  5. An underlying not on the explicit cash-settled allowlist is never
     auto-closed, regardless of any other field.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\tests\\
           test_expiration_closer.py
"""

import sys
from datetime import date
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / "python" / "database"
sys.path.insert(0, str(DB_DIR))

from domain.expiration_closer import (  # noqa: E402
    build_expiration_exit,
    find_expiration_closes,
    is_eligible_for_expiration_close,
)

CASH_SETTLED_ROOTS = frozenset({"NDXP"})
BUFFER_DAYS = 1
MULTIPLIER = 100


def _trade(**overrides):
    """Base open NDXP call trade, overridden per test."""
    base = {
        "trade_id": 9001,
        "status": "open",
        "asset_type": "call",
        "underlying_symbol": "NDXP",
        "direction": "long",
        "qty": 1.0,
        "entry_price": 6.05,
        "open_date": date(2026, 9, 9),
        "expiration_date": date(2026, 9, 9),
        "settlement_price": 0.0001,
    }
    base.update(overrides)
    return base


def test_0dte_worthless_expiry_closes_correctly():
    trade = _trade()
    as_of = date(2026, 9, 11)  # 2 days past expiration
    assert is_eligible_for_expiration_close(trade, CASH_SETTLED_ROOTS, as_of, BUFFER_DAYS)

    exit_ = build_expiration_exit(trade, trade["expiration_date"], MULTIPLIER)
    assert exit_["exit_price"] == 0.0001
    assert exit_["exit_pnl"] == -604.99  # (0.0001 - 6.05) * 1 * 100
    assert exit_["hold_days"] == 0
    assert exit_["exit_commissions"] == 0.0


def test_itm_cash_settled_nonzero_close():
    trade = _trade(
        direction="short",
        entry_price=3.00,
        open_date=date(2026, 9, 10),
        expiration_date=date(2026, 9, 10),
        settlement_price=15.50,
    )
    as_of = date(2026, 9, 12)  # 2 days past expiration
    assert is_eligible_for_expiration_close(trade, CASH_SETTLED_ROOTS, as_of, BUFFER_DAYS)

    exit_ = build_expiration_exit(trade, trade["expiration_date"], MULTIPLIER)
    assert exit_["exit_price"] == 15.50
    assert exit_["exit_pnl"] == -1250.00  # short: -(15.50 - 3.00) * 1 * 100


def test_equity_option_not_auto_closed():
    """Regression guard against scope creep -- the WO's core risk."""
    trade = _trade(
        underlying_symbol="AAPL",
        expiration_date=date(2026, 9, 5),
        settlement_price=0.05,
    )
    as_of = date(2026, 9, 12)
    assert not is_eligible_for_expiration_close(trade, CASH_SETTLED_ROOTS, as_of, BUFFER_DAYS)


def test_spy_not_auto_closed_even_though_index_tracking():
    """SPY looks like an index option in Schwab's data (assetType='OPTION',
    type='VANILLA', same as NDXP) but is physically-settled and
    assignable -- must never be treated as cash-settled without an
    explicit allowlist entry."""
    trade = _trade(
        underlying_symbol="SPY",
        expiration_date=date(2026, 9, 5),
        settlement_price=0.02,
    )
    as_of = date(2026, 9, 12)
    assert not is_eligible_for_expiration_close(trade, CASH_SETTLED_ROOTS, as_of, BUFFER_DAYS)


def test_same_day_expiration_not_closed_yet():
    """Buffer guard -- never close on the expiration date itself, even if
    settlement_price already looks final."""
    trade = _trade()  # expiration_date == open_date == 2026-09-09
    as_of = date(2026, 9, 9)  # same day, 0 days past
    assert not is_eligible_for_expiration_close(trade, CASH_SETTLED_ROOTS, as_of, BUFFER_DAYS)


def test_one_day_past_expiration_is_eligible():
    """Exactly at the buffer boundary -- 1 full day past is eligible."""
    trade = _trade()
    as_of = date(2026, 9, 10)  # 1 day past expiration
    assert is_eligible_for_expiration_close(trade, CASH_SETTLED_ROOTS, as_of, BUFFER_DAYS)


def test_missing_settlement_price_not_eligible():
    """No settlement_price captured (e.g. same-day ad-hoc pull before
    settlement) -- nothing to close against, must not be eligible."""
    trade = _trade(settlement_price=None)
    as_of = date(2026, 9, 15)
    assert not is_eligible_for_expiration_close(trade, CASH_SETTLED_ROOTS, as_of, BUFFER_DAYS)


def test_find_expiration_closes_filters_mixed_batch():
    """End-to-end: a mixed batch of eligible and ineligible trades returns
    only the eligible one, with the correct exit attached."""
    eligible = _trade(trade_id=9001)
    equity_guard = _trade(trade_id=9002, underlying_symbol="AAPL")
    same_day = _trade(trade_id=9003, expiration_date=date(2026, 9, 11))
    as_of = date(2026, 9, 11)

    results = find_expiration_closes(
        [eligible, equity_guard, same_day], CASH_SETTLED_ROOTS, as_of, BUFFER_DAYS, MULTIPLIER,
    )

    assert len(results) == 1
    assert results[0]["trade_id"] == 9001
    assert results[0]["exit"]["exit_pnl"] == -604.99
