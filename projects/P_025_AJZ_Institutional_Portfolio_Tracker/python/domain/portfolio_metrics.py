"""
P_025 Domain — Portfolio Metrics Helpers

Pure calculation helpers that may be used before data is written to Excel.
All heavy analytics remain Excel formulas; this module only contains
lightweight pure functions needed by the application layer.
"""

from __future__ import annotations

from typing import Iterable

from schemas import TradeRecord


def unique_tickers(trades: Iterable[TradeRecord]) -> list[str]:
    """Return sorted list of unique underlying symbols."""
    return sorted({t.underlying_symbol for t in trades})


def account_trade_count(trades: Iterable[TradeRecord]) -> dict[str, int]:
    """Return a simple count of trades per account_id."""
    counts: dict[str, int] = {}
    for t in trades:
        counts[t.account_id] = counts.get(t.account_id, 0) + 1
    return counts
