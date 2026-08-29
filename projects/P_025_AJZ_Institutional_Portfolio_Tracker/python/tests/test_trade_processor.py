"""
Permanent regression tests for domain/trade_processor.py

One assertion per known invariant. Never delete — only grow.
"""

from __future__ import annotations

from datetime import date

from domain.trade_processor import (
    average_cost_by_ticker,
    build_cost_basis_rows,
    calculate_daily_invested,
    calculate_daily_units,
    filter_primary_accounts,
)
from schemas import DailyUnitsRow, MarketDataRow, TradeRecord


def _make_trade(
    trade_id: int,
    account: str,
    symbol: str,
    qty: float,
    open_date: date,
    direction: str = "long",
) -> TradeRecord:
    return TradeRecord(
        trade_id=trade_id,
        account_id=account,
        underlying_symbol=symbol,
        qty=qty,
        entry_price=100.0,
        open_date=open_date,
        direction=direction,  # type: ignore[arg-type]
        asset_type="stock",
        status="open",
    )


def test_filter_primary_accounts_excludes_paper():
    trades = [
        _make_trade(1, "AJZ6348", "AAPL", 10, date(2025, 1, 2)),
        _make_trade(2, "PAPER", "MSFT", 5, date(2025, 1, 3)),
        _make_trade(3, "5232-9885", "SPY", 20, date(2025, 1, 4)),
    ]
    result = filter_primary_accounts(trades, ("AJZ6348", "5232-9885"))
    assert len(result) == 2
    assert all(t.account_id != "PAPER" for t in result)


def test_daily_units_accumulates_long_position():
    trades = [
        _make_trade(1, "AJZ6348", "AAPL", 10, date(2025, 1, 2)),
        _make_trade(2, "AJZ6348", "AAPL", 5, date(2025, 1, 3)),
    ]
    rows = calculate_daily_units(trades, start_date=date(2025, 1, 2), end_date=date(2025, 1, 4))
    # Day 1: 10 shares
    assert rows[0].units.get("AAPL") == 10.0
    # Day 2: 15 shares
    assert rows[1].units.get("AAPL") == 15.0
    # Day 3: still 15 (forward filled)
    assert rows[2].units.get("AAPL") == 15.0


def test_daily_units_handles_short():
    trades = [
        _make_trade(1, "AJZ6348", "TSLA", 10, date(2025, 1, 2), direction="short"),
    ]
    rows = calculate_daily_units(trades, start_date=date(2025, 1, 2), end_date=date(2025, 1, 2))
    assert rows[0].units.get("TSLA") == -10.0


def test_daily_invested_sums_shares_times_price():
    units = [
        DailyUnitsRow(date=date(2025, 1, 2), units={"AAPL": 10, "MSFT": 5}),
    ]
    market = [
        MarketDataRow(date=date(2025, 1, 2), prices={"AAPL": 100.0, "MSFT": 200.0}),
    ]
    rows = calculate_daily_invested(units, market)
    assert len(rows) == 1
    assert rows[0].invested_value == 2000.0  # 10*100 + 5*200


def test_average_cost_by_ticker():
    trades = [
        _make_trade(1, "AJZ6348", "AAPL", 10, date(2025, 1, 2)),
        _make_trade(2, "AJZ6348", "AAPL", 10, date(2025, 1, 3)),
    ]
    # both at entry_price=100.0 from helper
    costs = average_cost_by_ticker(trades)
    assert costs["AAPL"] == 100.0


def test_build_cost_basis_rows_total():
    trades = [
        _make_trade(1, "AJZ6348", "AAPL", 10, date(2025, 1, 2)),
    ]
    units = [
        DailyUnitsRow(date=date(2025, 1, 2), units={"AAPL": 10}),
    ]
    rows = build_cost_basis_rows(trades, units, account_id="AJZ6348")
    assert len(rows) == 1
    assert rows[0].ticker == "AAPL"
    assert rows[0].avg_cost == 100.0
    assert rows[0].total_cost_basis == 1000.0


def test_resolve_start_date_modes():
    from config import LOOKBACK_DAYS_YEARLY, resolve_start_date

    end = date(2026, 8, 22)
    assert LOOKBACK_DAYS_YEARLY == 365
    assert resolve_start_date(end, "yearly") == date(2025, 8, 22)
    assert resolve_start_date(end, "ytd") == date(2026, 1, 1)
    assert resolve_start_date(end, "full") == date(2023, 8, 23)
