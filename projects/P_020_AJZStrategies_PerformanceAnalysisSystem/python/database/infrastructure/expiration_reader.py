"""Read helper for open option trades with an expiration_date set.

Split out as its own file rather than appended to db_writer.py or
db_reader.py -- both are already at/near the 300-line hard cap
(WO-P020-E1.018 discovery, 2026-09-15). Single reason to change: the
expiration-close feature's one query.
"""

import logging
import sqlite3
from datetime import date as date_type
from typing import Dict, List

logger = logging.getLogger(__name__)


def get_expired_open_option_trades(conn: sqlite3.Connection) -> List[Dict]:
    """Read open option trades with an expiration_date set -- candidates
    for domain.expiration_closer to evaluate.

    Deliberately broad here (asset_type + expiration_date IS NOT NULL
    only) -- the cash-settled allowlist and buffer-days guard are domain
    logic, not a SQL filter, so they stay testable without a DB.

    Args:
        conn: Active SQLite connection.

    Returns:
        List of dicts, one per candidate trade: trade_id, underlying_symbol,
        asset_type, direction, qty, entry_price, open_date, status,
        expiration_date, settlement_price.
    """
    rows = conn.execute("""
        SELECT trade_id, underlying_symbol, asset_type, direction, qty,
               entry_price, open_date, status, expiration_date, settlement_price
          FROM trades
         WHERE status = 'open'
           AND asset_type IN ('call', 'put')
           AND expiration_date IS NOT NULL
           AND settlement_price IS NOT NULL
    """).fetchall()

    candidates = []
    for row in rows:
        candidates.append({
            "trade_id": row[0],
            "underlying_symbol": row[1],
            "asset_type": row[2],
            "direction": row[3],
            "qty": row[4],
            "entry_price": row[5],
            "open_date": date_type.fromisoformat(row[6]),
            "status": row[7],
            "expiration_date": date_type.fromisoformat(row[8]),
            "settlement_price": row[9],
        })

    logger.debug(f"get_expired_open_option_trades → {len(candidates)} candidate(s)")
    return candidates
