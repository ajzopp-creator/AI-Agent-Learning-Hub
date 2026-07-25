"""Database reader — query helpers for trades and exits by common filters."""

import logging
import sqlite3
from typing import List, Optional

logger = logging.getLogger(__name__)


# ── Trade queries ──────────────────────────────────────────────────────────

def get_all_trades(
    conn: sqlite3.Connection,
    account_id: Optional[str] = None,
    system: Optional[str] = None,
    status: Optional[str] = None,
) -> List[sqlite3.Row]:
    """Fetch trades with optional filters.

    Args:
        conn: Active SQLite connection.
        account_id: Filter by account (e.g. 'AJZ6348'). None = all accounts.
        system: Filter by trading system (e.g. 'P_118'). None = all systems.
        status: Filter by status ('open', 'partial', 'closed'). None = all.

    Returns:
        List of sqlite3.Row objects matching the filters.
    """
    sql    = "SELECT * FROM trades WHERE 1=1"
    params = []

    if account_id:
        sql += " AND account_id = ?"
        params.append(account_id)
    if system:
        sql += " AND system = ?"
        params.append(system)
    if status:
        sql += " AND status = ?"
        params.append(status)

    sql += " ORDER BY open_date DESC"
    rows = conn.execute(sql, params).fetchall()
    logger.debug(f"get_all_trades → {len(rows)} rows")
    return rows


def get_trades_by_date_range(
    conn: sqlite3.Connection,
    date_from: str,
    date_to: str,
    account_id: Optional[str] = None,
) -> List[sqlite3.Row]:
    """Fetch trades opened within a date range.

    Args:
        conn: Active SQLite connection.
        date_from: Start date as 'YYYY-MM-DD' string (inclusive).
        date_to: End date as 'YYYY-MM-DD' string (inclusive).
        account_id: Optional account filter.

    Returns:
        List of sqlite3.Row objects in the date range.
    """
    sql    = "SELECT * FROM trades WHERE open_date BETWEEN ? AND ?"
    params = [date_from, date_to]

    if account_id:
        sql += " AND account_id = ?"
        params.append(account_id)

    sql += " ORDER BY open_date"
    rows = conn.execute(sql, params).fetchall()
    logger.debug(f"get_trades_by_date_range({date_from}→{date_to}) → {len(rows)} rows")
    return rows


def get_open_trades(
    conn: sqlite3.Connection,
    account_id: Optional[str] = None,
) -> List[sqlite3.Row]:
    """Fetch all open or partial trades.

    Args:
        conn: Active SQLite connection.
        account_id: Optional account filter.

    Returns:
        List of sqlite3.Row objects with status 'open' or 'partial'.
    """
    return get_all_trades(conn, account_id=account_id, status="open") + \
           get_all_trades(conn, account_id=account_id, status="partial")


def get_open_trade_for_symbol(
    conn: sqlite3.Connection,
    account_id: str,
    symbol: str,
) -> Optional[sqlite3.Row]:
    """Fetch the oldest open/partial trade for a symbol -- FIFO match target
    for orphaned exits whose entry fell outside the current pull window.

    Args:
        conn: Active SQLite connection.
        account_id: Account to search within.
        symbol: Underlying symbol (case-insensitive).

    Returns:
        Oldest matching open/partial trade row, or None if no open
        position exists for this symbol.
    """
    sql = """
        SELECT * FROM trades
         WHERE account_id = ? AND underlying_symbol = ?
           AND status IN ('open', 'partial')
         ORDER BY open_date ASC
         LIMIT 1
    """
    row = conn.execute(sql, (account_id, symbol.upper())).fetchone()
    if row:
        logger.debug(f"get_open_trade_for_symbol({symbol}) -> trade_id={row['trade_id']}")
    return row


def get_trade_by_symbol_and_date(
    conn: sqlite3.Connection,
    symbol: str,
    open_date: str,
    account_id: Optional[str] = None,
) -> Optional[sqlite3.Row]:
    """Fetch the most recent trade matching symbol and open date.

    Args:
        conn: Active SQLite connection.
        symbol: Underlying symbol (e.g. 'QBTS').
        open_date: Trade open date as 'YYYY-MM-DD' string.
        account_id: Optional account filter.

    Returns:
        Matching sqlite3.Row or None if not found.
    """
    sql    = """
        SELECT * FROM trades
         WHERE underlying_symbol = ? AND open_date = ?
    """
    params = [symbol.upper(), open_date]

    if account_id:
        sql += " AND account_id = ?"
        params.append(account_id)

    sql += " ORDER BY trade_id DESC LIMIT 1"
    return conn.execute(sql, params).fetchone()


# ── Exit queries ───────────────────────────────────────────────────────────

def get_exits_for_trade(
    conn: sqlite3.Connection,
    trade_id: int,
) -> List[sqlite3.Row]:
    """Fetch all exits for a given trade ordered by exit_number.

    Args:
        conn: Active SQLite connection.
        trade_id: Primary key of the parent trade.

    Returns:
        List of exit rows ordered by exit_number ascending.
    """
    rows = conn.execute(
        "SELECT * FROM exits WHERE trade_id = ? ORDER BY exit_number",
        (trade_id,),
    ).fetchall()
    logger.debug(f"get_exits_for_trade(trade_id={trade_id}) → {len(rows)} exits")
    return rows


# ── Summary view queries ───────────────────────────────────────────────────

def get_trade_summary(
    conn: sqlite3.Connection,
    account_id: Optional[str] = None,
    asset_type: Optional[str] = None,
) -> List[sqlite3.Row]:
    """Query v_trade_summary with optional filters.

    Args:
        conn: Active SQLite connection.
        account_id: Optional account filter (excludes invest accounts by default).
        asset_type: Optional asset type filter ('stock', 'etf', 'call', etc.).

    Returns:
        List of summary view rows.
    """
    sql    = "SELECT * FROM v_trade_summary WHERE 1=1"
    params = []

    if account_id:
        sql += " AND account_id = ?"
        params.append(account_id)
    if asset_type:
        sql += " AND asset_type = ?"
        params.append(asset_type)

    sql += " ORDER BY open_date DESC"
    rows = conn.execute(sql, params).fetchall()
    logger.debug(f"get_trade_summary → {len(rows)} rows")
    return rows
