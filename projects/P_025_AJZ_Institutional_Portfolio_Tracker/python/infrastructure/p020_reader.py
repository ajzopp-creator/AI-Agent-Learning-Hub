"""
P_025 Infrastructure — P_020 Reader

Responsible solely for reading trade data from the P_020 SQLite database
(or CSV fallback). Contains no business logic.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from schemas import TradeRecord

logger = logging.getLogger(__name__)


def _parse_date(value: str | date | datetime | None) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return datetime.fromisoformat(str(value)[:10]).date()
    except (ValueError, TypeError):
        return None


def _row_to_trade(row: sqlite3.Row) -> Optional[TradeRecord]:
    """Convert a database row into a TradeRecord. Returns None on failure."""
    try:
        open_dt = row["open_datetime"] if "open_datetime" in row.keys() else None
        return TradeRecord(
            trade_id=int(row["trade_id"]),
            account_id=str(row["account_id"]),
            system=row["system"] if "system" in row.keys() else None,
            underlying_symbol=str(row["underlying_symbol"]),
            asset_type=str(row["asset_type"] or "stock").lower(),
            direction=str(row["direction"] or "long").lower(),
            open_date=_parse_date(row["open_date"]),
            open_datetime=_parse_date(open_dt) and datetime.fromisoformat(str(open_dt)) or None,
            qty=float(row["qty"] or 0),
            entry_price=float(row["entry_price"] or 0),
            stop_price=float(row["stop_price"]) if row["stop_price"] is not None else None,
            risk_amount=float(row["risk_amount"]) if row["risk_amount"] is not None else None,
            total_commissions=float(row["total_commissions"] or 0),
            status=str(row["status"] or "open").lower(),
            realized_pnl=float(row["realized_pnl"]) if row["realized_pnl"] is not None else None,
            realized_R=float(row["realized_R"]) if row["realized_R"] is not None else None,
            schwab_transaction_id=row["schwab_transaction_id"] if "schwab_transaction_id" in row.keys() else None,
            notes=row["notes"] if "notes" in row.keys() else None,
        )
    except Exception as exc:
        logger.warning("Skipping malformed trade row: %s", exc)
        return None


def read_trades(
    db_path: Path,
    account_ids: tuple[str, ...] | None = None,
    ira_feed_ready: bool = False,
) -> list[TradeRecord]:
    """
    Read trades from P_020 SQLite database.

    Parameters
    ----------
    db_path:
        Path to P_020_trades.db
    account_ids:
        Optional filter. If None, all primary accounts are requested.
    ira_feed_ready:
        When False (current state until ~2026-08-24), the Inherited Roth
        account (5232-9885) is silently excluded from the query so that a
        missing table / empty result does not raise.

    Returns
    -------
    List of validated TradeRecord objects. Empty list if the database is
    missing or no matching rows exist.
    """
    if not db_path.exists():
        logger.warning("P_020 database not found at %s — returning empty trade list", db_path)
        return []

    # Build the account filter, respecting the temporary IRA feed status
    if account_ids is None:
        from config import ACCOUNT_AJZ6348, ACCOUNT_IRA9885, PRIMARY_ACCOUNTS
        requested = list(PRIMARY_ACCOUNTS)
    else:
        requested = list(account_ids)

    if not ira_feed_ready:
        requested = [a for a in requested if a != "5232-9885"]
        logger.info(
            "Inherited Roth (5232-9885) feed not yet ready — excluding from this pull. "
            "Expected availability: Monday 2026-08-24."
        )

    if not requested:
        logger.warning("No accounts left to query after IRA filter")
        return []

    placeholders = ",".join("?" for _ in requested)
    sql = f"""
        SELECT *
        FROM v_trade_summary
        WHERE UPPER(account_id) IN ({placeholders})
        ORDER BY open_date, trade_id
    """

    trades: list[TradeRecord] = []
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, [a.upper() for a in requested])
            for row in cursor:
                trade = _row_to_trade(row)
                if trade is not None:
                    trades.append(trade)
    except sqlite3.Error as exc:
        logger.error("SQLite error while reading P_020: %s", exc)
        # Fallback attempt on the raw trades table if the view is missing
        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    f"""
                    SELECT * FROM trades
                    WHERE UPPER(account_id) IN ({placeholders})
                    ORDER BY open_date, trade_id
                    """,
                    [a.upper() for a in requested],
                )
                for row in cursor:
                    trade = _row_to_trade(row)
                    if trade is not None:
                        trades.append(trade)
        except sqlite3.Error as exc2:
            logger.error("Fallback query also failed: %s", exc2)
            return []

    logger.info("Loaded %d trades from P_020 for accounts %s", len(trades), requested)
    return trades
