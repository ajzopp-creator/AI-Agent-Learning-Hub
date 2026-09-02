"""Tests for _apply_stop_prices() in application.ingest_pipeline -- this
function used to be gated `if "PAPER" not in account_id: return`, meaning
live AJZ6348 trades never received a stop_price from the Tracker Dashboard
at all. Fixed to run for every account except IRA9885, which bypasses
Tracker/vault matching entirely per WO-P020-E1.015 Decision 1 (no
meaningful IRA coverage exists in the Tracker). No WO filed for this fix
yet -- root cause found during the 2026-09-02 monthly review session.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from application.ingest_pipeline import _apply_stop_prices
from schemas import TrackerLookup


def _lookup_with_stop(symbol: str, date: str, stop: float) -> TrackerLookup:
    """Build a minimal TrackerLookup with one stop_price entry."""
    return TrackerLookup(stop_prices={(symbol, date): stop})


def test_ajz_account_gets_stop_price_from_tracker():
    """Regression: this was the bug. AJZ6348 must now receive a matching
    stop_price from the Tracker, not silently skip it."""
    lookup = _lookup_with_stop("QQQ", "2026-08-24", 450.0)
    trades = [{"underlying_symbol": "QQQ", "open_date": "2026-08-24"}]

    _apply_stop_prices(trades, lookup, "AJZ6348")

    assert trades[0]["stop_price"] == 450.0


def test_ira_account_still_skips_stop_price_entirely():
    """IRA9885 must remain excluded even when the Tracker has a matching
    entry -- confirms the bypass wasn't accidentally widened away."""
    lookup = _lookup_with_stop("IDU", "2026-03-19", 60.0)
    trades = [{"underlying_symbol": "IDU", "open_date": "2026-03-19"}]

    _apply_stop_prices(trades, lookup, "IRA9885")

    assert "stop_price" not in trades[0]


def test_paper_account_still_gets_stop_price():
    """Regression: PAPER behavior must be unchanged from before this fix."""
    lookup = _lookup_with_stop("AAPL", "2026-01-15", 180.0)
    trades = [{"underlying_symbol": "AAPL", "open_date": "2026-01-15"}]

    _apply_stop_prices(trades, lookup, "PAPER")

    assert trades[0]["stop_price"] == 180.0


def test_no_tracker_lookup_is_safe_noop_for_non_ira_account():
    """lookup=None must not raise for any non-IRA account, and must leave
    the trade dict untouched."""
    trades = [{"underlying_symbol": "MSFT", "open_date": "2026-05-01"}]

    _apply_stop_prices(trades, None, "AJZ6348")

    assert "stop_price" not in trades[0]


def test_no_match_in_tracker_leaves_trade_untouched():
    """A non-IRA account with a Tracker loaded but no matching row must not
    set stop_price -- confirms missing-match still falls through cleanly."""
    lookup = _lookup_with_stop("QQQ", "2026-08-24", 450.0)
    trades = [{"underlying_symbol": "TSLA", "open_date": "2026-08-24"}]

    _apply_stop_prices(trades, lookup, "AJZ6348")

    assert "stop_price" not in trades[0]
