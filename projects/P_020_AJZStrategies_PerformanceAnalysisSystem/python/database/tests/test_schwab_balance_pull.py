"""Tests for infrastructure.schwab_balance_pull -- pull_balance()'s
cash_available field-fallback guarantee. Ref WO-P020-E1.016.

Tests the response-parsing logic directly (constructs a fake response
object) rather than the full pull_balance() function, since that
function reaches out to a live authenticated Schwab client via
_get_client() -- not something a unit test should invoke. The parsing
logic under test is copied inline to mirror pull_balance()'s exact
extraction expression; if that expression changes, this test's copy
must change with it (see docstring on each test).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _extract_cash_available(curr: dict) -> float | None:
    """Mirrors the exact extraction expression in pull_balance() --
    infrastructure/schwab_balance_pull.py line ~76. Kept as a literal
    copy, not an import, because pull_balance() is not decomposed into
    a separately-callable parsing function (WO-P020-E1.016 scope was
    the one-line fix, not a refactor)."""
    return curr.get("cashAvailableForTrading") or curr.get("availableFunds")


def test_falls_back_to_available_funds_when_cash_available_absent():
    """Margin-account case (confirmed live 2026-08-20): currentBalances
    has no cashAvailableForTrading key at all. availableFunds must be
    used instead of silently returning None."""
    curr = {"availableFunds": 19630.17, "buyingPower": 39260.34}
    assert _extract_cash_available(curr) == 19630.17


def test_falls_back_to_available_funds_when_cash_available_is_none():
    """Same as above but the key IS present, just None -- both shapes
    seen in the wild must resolve to the same fallback."""
    curr = {"cashAvailableForTrading": None, "availableFunds": 19630.17}
    assert _extract_cash_available(curr) == 19630.17


def test_prefers_cash_available_when_present_and_nonzero():
    """Textbook cash-account case: cashAvailableForTrading is a real,
    non-None, non-zero value. That value wins, availableFunds is not
    used even if also present."""
    curr = {"cashAvailableForTrading": 5000.00, "availableFunds": 19630.17}
    assert _extract_cash_available(curr) == 5000.00


def test_both_absent_returns_none_not_fabricated_value():
    """Neither field present -- must stay None. No default/fabricated
    dollar amount is invented when Schwab gives us nothing usable."""
    curr = {"buyingPower": 39260.34}
    assert _extract_cash_available(curr) is None
