"""Database writer -- insert/update orders; promote a reconciled order into
the trades table.

Layer note: promote_order_to_trade() imports insert_trade()/insert_exit()
from infrastructure.db_writer and _map_asset_type from
infrastructure.schwab_mapper -- reused, not duplicated, so a P_400-
originated trade gets the exact same dedup protection and asset-type
mapping every schwab_mapper-sourced trade already gets.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure (I/O)
"""

import logging
import sqlite3
from datetime import date
from typing import Optional

from schemas import Exit, Order, Trade

logger = logging.getLogger(__name__)

_ORDER_COLUMNS = (
    "order_id", "account_id", "symbol", "side", "qty",
    "planned_entry_price", "planned_stop_price", "planned_target_price",
    "trade_mode", "submitted_ts", "schwab_order_id", "status",
    "council_verdict", "why_code", "sig_code", "source_project",
    "confidence_tier", "entry_date", "close_date", "realized_pnl",
    "entry_fill_price", "asset_type", "put_call",
)


def insert_order(conn: sqlite3.Connection, order: Order) -> Optional[int]:
    """Insert a new order row. Skips if schwab_order_id already exists.

    Args:
        conn: Active SQLite connection.
        order: Validated Order schema object (order_id left None -- the
            DB assigns it).

    Returns:
        Inserted order_id, or None if skipped due to dedup.
    """
    if order.schwab_order_id:
        existing = conn.execute(
            "SELECT 1 FROM orders WHERE schwab_order_id = ?",
            (order.schwab_order_id,),
        ).fetchone()
        if existing:
            logger.debug(
                f"Skipping duplicate order: schwab_order_id={order.schwab_order_id}"
            )
            return None

    cursor = conn.execute("""
        INSERT INTO orders (
            account_id, symbol, side, qty, planned_entry_price,
            planned_stop_price, planned_target_price, trade_mode,
            submitted_ts, schwab_order_id, status, council_verdict,
            why_code, sig_code, source_project, confidence_tier,
            entry_date, close_date, realized_pnl, entry_fill_price,
            asset_type, put_call
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order.account_id, order.symbol, order.side, order.qty,
        order.planned_entry_price, order.planned_stop_price,
        order.planned_target_price, order.trade_mode,
        str(order.submitted_ts), order.schwab_order_id, order.status,
        order.council_verdict, order.why_code, order.sig_code,
        order.source_project, order.confidence_tier,
        str(order.entry_date) if order.entry_date else None,
        str(order.close_date) if order.close_date else None,
        order.realized_pnl, order.entry_fill_price, order.asset_type,
        order.put_call,
    ))
    conn.commit()
    order_id = cursor.lastrowid
    logger.debug(f"Inserted order #{order_id}: {order.symbol} ({order.source_project})")
    return order_id


def update_order_status(
    conn: sqlite3.Connection,
    order_id: int,
    status: str,
    entry_date: Optional[str] = None,
    close_date: Optional[str] = None,
    realized_pnl: Optional[float] = None,
    entry_fill_price: Optional[float] = None,
    asset_type: Optional[str] = None,
    put_call: Optional[str] = None,
) -> None:
    """Update an order's status and, once reconciled, its fill/close data.

    Uses COALESCE so passing None for any reconciliation field leaves the
    existing DB value untouched -- a status-only transition (e.g.
    'pending' -> 'working') can call this with just order_id and status.

    Args:
        conn: Active SQLite connection.
        order_id: Primary key of the order to update.
        status: New status value.
        entry_date: ISO date string, set once the entry fills.
        close_date: ISO date string, set once the position closes.
        realized_pnl: Realized P&L, set once the position closes.
        entry_fill_price: Actual average entry fill price.
        asset_type: Raw Schwab 'EQUITY'/'OPTION'.
        put_call: 'CALL'/'PUT', options only.
    """
    conn.execute("""
        UPDATE orders
           SET status = ?,
               entry_date = COALESCE(?, entry_date),
               close_date = COALESCE(?, close_date),
               realized_pnl = COALESCE(?, realized_pnl),
               entry_fill_price = COALESCE(?, entry_fill_price),
               asset_type = COALESCE(?, asset_type),
               put_call = COALESCE(?, put_call)
         WHERE order_id = ?
    """, (
        status, entry_date, close_date, realized_pnl,
        entry_fill_price, asset_type, put_call, order_id,
    ))
    conn.commit()
    logger.debug(f"Updated order #{order_id} -> status={status}")


def promote_order_to_trade(conn: sqlite3.Connection, order_id: int) -> Optional[int]:
    """Promote a reconciled, closed order into the trades table.

    Reads the order row back from SQLite (not passed in -- always
    promotes the DB's current state, not a possibly-stale in-memory
    Order object).

    Args:
        conn: Active SQLite connection.
        order_id: Primary key of the order to promote. Must already have
            close_date and realized_pnl set (i.e. already reconciled).

    Returns:
        The new trade_id, or None if the order isn't found, isn't yet
        reconciled, or insert_trade() skipped it as a duplicate.
    """
    from infrastructure.db_writer import insert_exit, insert_trade
    from infrastructure.schwab_mapper import _map_asset_type

    data = _fetch_order_row(conn, order_id)
    if data is None:
        logger.error(f"promote_order_to_trade: order #{order_id} not found")
        return None
    if data["close_date"] is None or data["realized_pnl"] is None:
        logger.error(
            f"promote_order_to_trade: order #{order_id} not yet reconciled "
            f"(close_date/realized_pnl missing)"
        )
        return None

    trade = _build_trade(data, _map_asset_type)
    trade_id = insert_trade(conn, trade)
    if trade_id is None:
        logger.info(f"order #{order_id}: insert_trade skipped (duplicate)")
        return None

    exit_ = _build_exit(data, trade_id)
    if exit_ is not None:
        insert_exit(conn, exit_)
    else:
        logger.warning(
            f"order #{order_id}: could not back-calculate exit_price "
            f"(missing entry_fill_price) -- trade recorded without an exit leg"
        )

    return trade_id


def _fetch_order_row(conn: sqlite3.Connection, order_id: int) -> Optional[dict]:
    """Read one orders row as a column-name-keyed dict."""
    row = conn.execute(
        f"SELECT {', '.join(_ORDER_COLUMNS)} FROM orders WHERE order_id = ?",
        (order_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(zip(_ORDER_COLUMNS, row))


def _build_trade(data: dict, map_asset_type) -> Trade:
    """Build a Trade from a reconciled order row.

    system = why_code (Signal Source ID, same convention every other
    trade source uses) falling back to source_project. reason = sig_code
    (more specific signal detail). schwab_transaction_id = schwab_order_id
    -- not a literal transaction ID, but serves the same dedup/traceability
    purpose db_writer.py's transaction_exists() check relies on.
    """
    entry_date = (
        date.fromisoformat(data["entry_date"]) if data["entry_date"]
        else date.fromisoformat(data["close_date"])
    )
    return Trade(
        account_id=data["account_id"],
        system=data["why_code"] or data["source_project"],
        underlying_symbol=data["symbol"],
        asset_type=map_asset_type(data["asset_type"] or "EQUITY", data["put_call"]),
        direction=data["side"],
        open_date=entry_date,
        qty=data["qty"],
        entry_price=data["entry_fill_price"] or data["planned_entry_price"] or 0.0,
        stop_price=data["planned_stop_price"],
        status="closed",
        source=data["source_project"],
        schwab_transaction_id=data["schwab_order_id"],
        reason=data["sig_code"],
    )


def _build_exit(data: dict, trade_id: int) -> Optional[Exit]:
    """Back-calculate the exit leg's price from realized_pnl and build an
    Exit. Returns None if entry_fill_price is missing (can't solve for
    exit_price without it) -- caller logs and skips, doesn't fail the
    whole promotion.

    ref EC-010, WO-P400-E6.001 Gate 2 -- this used to divide realized_pnl
    by qty alone with no options multiplier, so an option's back-solved
    exit_price came out nowhere near the real fill (a $3.00 realized_pnl
    on a 1-lot short call with entry 3.16 back-solved to an exit_price of
    0.16 instead of the real 3.13). realized_pnl is already the correct
    dollar total (multiplier applied in domain/order_reconciler.py), so
    the multiplier has to come back OUT here before dividing by qty to
    get back to a per-share/per-contract price.
    """
    if data["entry_fill_price"] is None or not data["qty"]:
        return None

    multiplier = 100 if data["asset_type"] == "OPTION" else 1
    sign = 1 if data["side"] == "long" else -1
    exit_price = round(
        data["entry_fill_price"]
        + sign * (data["realized_pnl"] / (data["qty"] * multiplier)),
        4,
    )

    close_date = date.fromisoformat(data["close_date"])
    open_date = (
        date.fromisoformat(data["entry_date"]) if data["entry_date"] else close_date
    )

    return Exit(
        trade_id=trade_id,
        exit_number=1,
        exit_date=close_date,
        qty_exited=data["qty"],
        exit_price=exit_price,
        exit_pnl=data["realized_pnl"],
        hold_days=(close_date - open_date).days,
    )
