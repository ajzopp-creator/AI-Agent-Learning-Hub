"""
P_025 Domain — FIFO remaining long lots.

No I/O. Shorts never open a long lot. PAPER is the caller's filter.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable

from schemas import FifoCostRow, FifoLotRow, TradeRecord


def _consume(lots: deque, qty: float) -> None:
    remaining = qty
    while remaining > 1e-12 and lots:
        lot = lots[0]
        take = min(lot.remaining_qty, remaining)
        lot.remaining_qty = round(lot.remaining_qty - take, 8)
        lot.remaining_cost = round(lot.remaining_qty * lot.lot_price, 6)
        remaining -= take
        if lot.remaining_qty <= 1e-12:
            lots.popleft()


def process_fifo_lots(trades: Iterable[TradeRecord]) -> list[FifoLotRow]:
    """
    Walk trades in (open_date, trade_id) order.

    long  → open a lot; if status is closed, consume that qty FIFO
    short → consume existing long lots only; leftover short is dropped
    """
    books: dict[tuple[str, str], deque] = defaultdict(deque)
    ordered = sorted(trades, key=lambda t: (t.open_date, t.trade_id))
    for t in ordered:
        key = (t.account_id.upper(), t.underlying_symbol)
        lots = books[key]
        if t.direction == "long":
            lot = FifoLotRow(
                account_id=key[0],
                ticker=key[1],
                open_date=t.open_date,
                remaining_qty=float(t.qty),
                lot_price=float(t.entry_price),
                remaining_cost=round(float(t.qty) * float(t.entry_price), 6),
                source_trade_id=t.trade_id,
            )
            lots.append(lot)
            if t.status == "closed":
                _consume(lots, float(t.qty))
        else:
            _consume(lots, float(t.qty))

    out: list[FifoLotRow] = []
    for key in sorted(books):
        for lot in books[key]:
            if lot.remaining_qty > 1e-12:
                out.append(lot)
    return out


def summarize_fifo_cost(lots: Iterable[FifoLotRow]) -> list[FifoCostRow]:
    shares: dict[tuple[str, str], float] = defaultdict(float)
    cost: dict[tuple[str, str], float] = defaultdict(float)
    for lot in lots:
        key = (lot.ticker, lot.account_id)
        shares[key] += lot.remaining_qty
        cost[key] += lot.remaining_cost
    rows: list[FifoCostRow] = []
    for ticker, account in sorted(shares):
        rows.append(
            FifoCostRow(
                ticker=ticker,
                account_id=account,
                remaining_shares=round(shares[(ticker, account)], 6),
                remaining_cost=round(cost[(ticker, account)], 2),
            )
        )
    return rows
