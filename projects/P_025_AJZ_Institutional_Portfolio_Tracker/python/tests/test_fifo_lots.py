"""Permanent tests for domain/fifo_lots.py."""

from __future__ import annotations

from datetime import date

from domain.fifo_lots import process_fifo_lots, summarize_fifo_cost
from schemas import TradeRecord


def _t(
    trade_id: int,
    account: str,
    symbol: str,
    qty: float,
    px: float,
    d: date,
    direction: str = "long",
    status: str = "open",
) -> TradeRecord:
    return TradeRecord(
        trade_id=trade_id,
        account_id=account,
        underlying_symbol=symbol,
        qty=qty,
        entry_price=px,
        open_date=d,
        direction=direction,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        asset_type="stock",
    )


def test_partial_sell_consumes_oldest_lot():
    trades = [
        _t(1, "AJZ6348", "AAPL", 10, 100.0, date(2025, 1, 2)),
        _t(2, "AJZ6348", "AAPL", 10, 120.0, date(2025, 1, 3)),
        _t(3, "AJZ6348", "AAPL", 6, 130.0, date(2025, 1, 4), direction="short"),
    ]
    lots = process_fifo_lots(trades)
    assert len(lots) == 2
    assert lots[0].remaining_qty == 4.0
    assert lots[0].lot_price == 100.0
    assert lots[1].remaining_qty == 10.0
    assert lots[1].lot_price == 120.0
    summary = summarize_fifo_cost(lots)
    assert summary[0].remaining_shares == 14.0
    assert summary[0].remaining_cost == 4 * 100 + 10 * 120


def test_closed_long_self_consumes():
    trades = [
        _t(1, "AJZ6348", "MSFT", 5, 200.0, date(2025, 1, 2), status="closed"),
    ]
    lots = process_fifo_lots(trades)
    assert lots == []


def test_short_does_not_open_lot():
    trades = [
        _t(1, "AJZ6348", "TSLA", 8, 250.0, date(2025, 1, 2), direction="short"),
    ]
    assert process_fifo_lots(trades) == []


def test_two_accounts_same_ticker_isolated():
    trades = [
        _t(1, "AJZ6348", "SPY", 10, 400.0, date(2025, 1, 2)),
        _t(2, "5232-9885", "SPY", 3, 410.0, date(2025, 1, 2)),
        _t(3, "AJZ6348", "SPY", 4, 420.0, date(2025, 1, 3), direction="short"),
    ]
    lots = process_fifo_lots(trades)
    by_acct = {(lot.account_id, lot.ticker): lot.remaining_qty for lot in lots}
    assert by_acct[("AJZ6348", "SPY")] == 6.0
    assert by_acct[("5232-9885", "SPY")] == 3.0
    summary = summarize_fifo_cost(lots)
    assert len(summary) == 2
