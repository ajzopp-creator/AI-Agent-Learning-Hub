"""Database writer — insert and update trades and exits with dedup protection."""

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from schemas import Exit, SpreadLeg, Trade

logger = logging.getLogger(__name__)


# ── Deduplication ──────────────────────────────────────────────────────────

def transaction_exists(conn: sqlite3.Connection, schwab_transaction_id: str) -> bool:
    """Check if a Schwab transaction ID is already in the trades table.

    Args:
        conn: Active SQLite connection.
        schwab_transaction_id: Schwab's unique transaction identifier.

    Returns:
        True if the transaction already exists, False otherwise.
    """
    row = conn.execute(
        "SELECT 1 FROM trades WHERE schwab_transaction_id = ?",
        (schwab_transaction_id,),
    ).fetchone()
    return row is not None


def get_trade_id_by_schwab_id(conn: sqlite3.Connection, schwab_transaction_id: str) -> Optional[int]:
    """Look up the existing trade_id for a Schwab transaction ID.

    Used when insert_trade() returns None (duplicate entry) but the trade may
    have new exit data to attach -- see WO-P020-E1.001.

    Args:
        conn: Active SQLite connection.
        schwab_transaction_id: Schwab's unique transaction identifier.

    Returns:
        The existing trade_id, or None if not found.
    """
    row = conn.execute(
        "SELECT trade_id FROM trades WHERE schwab_transaction_id = ?",
        (schwab_transaction_id,),
    ).fetchone()
    return row[0] if row else None


# ── Trade writers ──────────────────────────────────────────────────────────

def insert_trade(conn: sqlite3.Connection, trade: Trade) -> Optional[int]:
    """Insert a single trade row. Skips if schwab_transaction_id already exists.

    Args:
        conn: Active SQLite connection.
        trade: Validated Trade schema object.

    Returns:
        Inserted trade_id, or None if skipped due to dedup.
    """
    if trade.schwab_transaction_id:
        if transaction_exists(conn, trade.schwab_transaction_id):
            logger.debug(
                f"Skipping duplicate: {trade.underlying_symbol} "
                f"{trade.open_date} (txn_id={trade.schwab_transaction_id})"
            )
            return None

    cursor = conn.execute("""
        INSERT INTO trades (
            account_id, system, underlying_symbol, asset_type, direction,
            open_date, open_datetime, qty, entry_price, stop_price,
            risk_amount, total_commissions, status, tags, notes,
            source, schwab_transaction_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade.account_id,
        trade.system,
        trade.underlying_symbol,
        trade.asset_type,
        trade.direction,
        str(trade.open_date),
        str(trade.open_datetime) if trade.open_datetime else None,
        trade.qty,
        trade.entry_price,
        trade.stop_price,
        trade.risk_amount,
        trade.total_commissions,
        trade.status,
        trade.tags,
        trade.notes,
        trade.source,
        trade.schwab_transaction_id,
    ))
    conn.commit()
    trade_id = cursor.lastrowid
    logger.debug(
        f"Inserted trade #{trade_id}: {trade.underlying_symbol} "
        f"{trade.open_date} ({trade.system})"
    )
    return trade_id


def update_trade_status(
    conn: sqlite3.Connection,
    trade_id: int,
    status: str,
    total_commissions: Optional[float] = None,
) -> None:
    """Update trade status and optionally total commissions.

    Args:
        conn: Active SQLite connection.
        trade_id: Primary key of the trade to update.
        status: New status value — 'open', 'partial', or 'closed'.
        total_commissions: Updated commission total if provided.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    if total_commissions is not None:
        conn.execute("""
            UPDATE trades
               SET status = ?, total_commissions = ?, updated_at = ?
             WHERE trade_id = ?
        """, (status, total_commissions, now, trade_id))
    else:
        conn.execute("""
            UPDATE trades
               SET status = ?, updated_at = ?
             WHERE trade_id = ?
        """, (status, now, trade_id))
    conn.commit()
    logger.debug(f"Updated trade #{trade_id} → status={status}")


# ── Exit writers ───────────────────────────────────────────────────────────

def insert_exit(conn: sqlite3.Connection, exit_: Exit) -> Optional[int]:
    """Insert a single exit row. Skips if trade_id + exit_number already exists.

    Args:
        conn: Active SQLite connection.
        exit_: Validated Exit schema object.

    Returns:
        Inserted exit_id, or None if skipped due to dedup.
    """
    existing = conn.execute(
        "SELECT 1 FROM exits WHERE trade_id = ? AND exit_number = ?",
        (exit_.trade_id, exit_.exit_number),
    ).fetchone()

    if existing:
        logger.debug(
            f"Skipping duplicate exit: trade_id={exit_.trade_id} "
            f"exit_number={exit_.exit_number}"
        )
        return None

    cursor = conn.execute("""
        INSERT INTO exits (
            trade_id, exit_number, exit_date, exit_datetime,
            qty_exited, exit_price, exit_commissions, exit_pnl, hold_days
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        exit_.trade_id,
        exit_.exit_number,
        str(exit_.exit_date),
        str(exit_.exit_datetime) if exit_.exit_datetime else None,
        exit_.qty_exited,
        exit_.exit_price,
        exit_.exit_commissions,
        exit_.exit_pnl,
        exit_.hold_days,
    ))
    conn.commit()
    exit_id = cursor.lastrowid
    logger.debug(
        f"Inserted exit #{exit_id}: trade_id={exit_.trade_id} "
        f"exit_number={exit_.exit_number} pnl={exit_.exit_pnl:.2f}"
    )
    return exit_id


def insert_spread_legs(
    conn: sqlite3.Connection, trade_id: int, legs: list[SpreadLeg]
) -> list[int]:
    """Insert spread leg rows for a trade. Skips legs that already exist
    (dedup on trade_id + leg_number, same pattern as insert_exit).

    Args:
        conn: Active SQLite connection.
        trade_id: The parent trade's ID.
        legs: List of validated SpreadLeg schema objects.

    Returns:
        List of inserted leg_ids (skipped duplicates omitted).
    """
    inserted_ids = []
    for leg in legs:
        existing = conn.execute(
            "SELECT 1 FROM spread_legs WHERE trade_id = ? AND leg_number = ?",
            (trade_id, leg.leg_number),
        ).fetchone()

        if existing:
            logger.debug(
                f"Skipping duplicate leg: trade_id={trade_id} "
                f"leg_number={leg.leg_number}"
            )
            continue

        cursor = conn.execute("""
            INSERT INTO spread_legs (
                trade_id, leg_number, full_symbol, put_call,
                position_effect, direction, qty, price
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_id,
            leg.leg_number,
            leg.full_symbol,
            leg.put_call,
            leg.position_effect,
            leg.direction,
            leg.qty,
            leg.price,
        ))
        inserted_ids.append(cursor.lastrowid)

    conn.commit()
    logger.debug(
        f"Inserted {len(inserted_ids)} spread leg(s) for trade_id={trade_id}"
    )
    return inserted_ids
