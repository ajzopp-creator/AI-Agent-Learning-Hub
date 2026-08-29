"""
P_025 Domain — Trade Processor

Pure business logic for converting a list of TradeRecord objects into
DailyUnits and DailyCash series. No I/O, no logging of side-effects,
no external dependencies beyond the standard library and schemas.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Iterable

from schemas import (
    CostBasisRow,
    DailyCashRow,
    DailyInvestedRow,
    DailyUnitsRow,
    MarketDataRow,
    TradeRecord,
)


def filter_primary_accounts(
    trades: Iterable[TradeRecord],
    primary_accounts: tuple[str, ...],
) -> list[TradeRecord]:
    """Return only trades that belong to the primary reporting accounts."""
    allowed = {a.upper() for a in primary_accounts}
    return [t for t in trades if t.account_id.upper() in allowed]


def _trading_date_range(start: date, end: date) -> list[date]:
    """Generate every calendar day from start to end inclusive.
    (Weekends are kept; the caller may later filter to trading days if desired.)
    """
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def calculate_daily_units(
    trades: list[TradeRecord],
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[DailyUnitsRow]:
    """
    Convert trade history into end-of-day share positions.

    Algorithm
    ---------
    1. Sort trades by open_date.
    2. Maintain a running position dict[ticker] = net shares.
    3. On each day that has activity, emit the position snapshot.
    4. Forward-fill the position for days with no activity so the series
       is continuous (required for Excel Equity_Curve formulas).

    Notes
    -----
    - Direction "long" adds qty; "short" subtracts qty.
    - Closed trades are still processed (their qty effect is already reflected
      by the corresponding opening trade + any later closing trade).
    - This is a simplified model that does not yet handle partial fills or
      complex multi-leg option structures. It is sufficient for the current
      equity / simple options book.
    """
    if not trades:
        return []

    sorted_trades = sorted(trades, key=lambda t: (t.open_date, t.trade_id))

    first_date = start_date or sorted_trades[0].open_date
    last_date = end_date or max(t.open_date for t in sorted_trades)

    # Group trades by date for efficient lookup
    trades_by_date: dict[date, list[TradeRecord]] = defaultdict(list)
    for t in sorted_trades:
        trades_by_date[t.open_date].append(t)

    position: dict[str, float] = defaultdict(float)
    result: list[DailyUnitsRow] = []

    for d in _trading_date_range(first_date, last_date):
        for t in trades_by_date.get(d, []):
            signed_qty = t.qty if t.direction == "long" else -t.qty
            position[t.underlying_symbol] += signed_qty

        # Snapshot only non-zero positions to keep the series compact
        snapshot = {sym: qty for sym, qty in position.items() if abs(qty) > 1e-9}
        result.append(DailyUnitsRow(date=d, units=snapshot))

    return result


def calculate_daily_cash(
    trades: list[TradeRecord],
    starting_cash: dict[str, float] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[DailyCashRow]:
    """
    Produce a daily cash balance series per account.

    Very simplified model:
    - Starting cash is taken from the supplied dict (or 0.0).
    - Each trade reduces cash by (qty * entry_price + commissions) for longs
      and increases cash for shorts (premium received).
    - Realized P&L is added back when a trade is marked closed.

    This is intentionally conservative and will be refined once the full
    P_020 cash ledger is available.
    """
    if not trades:
        return []

    cash: dict[str, float] = defaultdict(float)
    if starting_cash:
        for acct, bal in starting_cash.items():
            cash[acct.upper()] = bal

    sorted_trades = sorted(trades, key=lambda t: (t.open_date, t.trade_id))
    first_date = start_date or sorted_trades[0].open_date
    last_date = end_date or max(t.open_date for t in sorted_trades)

    trades_by_date: dict[date, list[TradeRecord]] = defaultdict(list)
    for t in sorted_trades:
        trades_by_date[t.open_date].append(t)

    result: list[DailyCashRow] = []
    accounts_seen: set[str] = set()

    for d in _trading_date_range(first_date, last_date):
        for t in trades_by_date.get(d, []):
            acct = t.account_id.upper()
            accounts_seen.add(acct)
            notional = t.qty * t.entry_price
            if t.direction == "long":
                cash[acct] -= notional + t.total_commissions
            else:
                cash[acct] += notional - t.total_commissions

            if t.status == "closed" and t.realized_pnl is not None:
                cash[acct] += t.realized_pnl

        for acct in accounts_seen:
            result.append(
                DailyCashRow(
                    date=d,
                    account_id=acct,
                    cash_balance=round(cash[acct], 2),
                )
            )

    return result


def calculate_daily_invested(
    daily_units: list[DailyUnitsRow],
    market_data: list[MarketDataRow],
) -> list[DailyInvestedRow]:
    """
    For each date, compute total invested market value =
    sum over tickers of (shares held × closing price).

    Missing prices are treated as 0 for that ticker/date.
    """
    price_by_date: dict[date, dict[str, float]] = {
        row.date: row.prices for row in market_data
    }
    result: list[DailyInvestedRow] = []
    for units_row in daily_units:
        prices = price_by_date.get(units_row.date, {})
        total = 0.0
        for ticker, shares in units_row.units.items():
            px = prices.get(ticker)
            if px is not None and shares:
                total += shares * px
        result.append(
            DailyInvestedRow(date=units_row.date, invested_value=round(total, 2))
        )
    return result


def average_cost_by_ticker(
    trades: list[TradeRecord],
    account_id: str | None = None,
) -> dict[str, float]:
    """
    Volume-weighted average entry price per ticker (long buys only).

    avg = sum(qty * entry_price) / sum(qty) for direction == long.
    Optional account_id filter (e.g. AJZ6348 only).
    Shorts are excluded from the average in this v1 policy.
    """
    notional: dict[str, float] = defaultdict(float)
    quantity: dict[str, float] = defaultdict(float)
    acct = account_id.upper() if account_id else None
    for t in trades:
        if t.direction != "long" or t.qty <= 0:
            continue
        if acct and t.account_id.upper() != acct:
            continue
        notional[t.underlying_symbol] += t.qty * t.entry_price
        quantity[t.underlying_symbol] += t.qty
    return {
        sym: (notional[sym] / quantity[sym]) if quantity[sym] else 0.0
        for sym in quantity
    }


def build_cost_basis_rows(
    trades: list[TradeRecord],
    daily_units: list[DailyUnitsRow],
    account_id: str = "AJZ6348",
) -> list[CostBasisRow]:
    """
    For each ticker with a current long position, compute:
      avg_cost, current_shares, total_cost_basis = avg_cost * shares.

    Current shares taken from the last DailyUnitsRow that has that ticker.
    """
    avg = average_cost_by_ticker(trades, account_id=account_id)
    if not daily_units:
        return []

    # Latest shares per ticker (scan from end)
    current: dict[str, float] = {}
    for row in reversed(daily_units):
        for sym, qty in row.units.items():
            if sym not in current:
                current[sym] = qty

    rows: list[CostBasisRow] = []
    for sym, shares in sorted(current.items()):
        if shares <= 0:
            continue  # skip flat / short for cost-basis column
        a = avg.get(sym, 0.0)
        rows.append(
            CostBasisRow(
                ticker=sym,
                avg_cost=round(a, 6),
                current_shares=shares,
                total_cost_basis=round(a * shares, 2),
                account_id=account_id,
            )
        )
    return rows
