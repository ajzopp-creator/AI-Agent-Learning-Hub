"""
vault_reader.py -- Infrastructure layer (I/O only, no logic).

Reads rows from v_trade_summary for the Obsidian vault export
(WO-P020-E1.005). Returns plain dicts -- no business logic here, that
lives in domain/vault_mapper.py.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\infrastructure\\vault_reader.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure
"""
import logging
import sqlite3
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def get_closed_trades(
    conn: sqlite3.Connection,
    min_open_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch non-open trades from v_trade_summary.

    Includes both 'partial' and 'closed' status trades per WO-P020-E1.005
    (status != 'open' is the WO's own filter -- a partially-closed trade
    still has at least one exit worth recording, and overwrite=True on
    the vault write means a later exit just updates the same note).

    Args:
        conn: Active SQLite connection (row_factory must be sqlite3.Row --
            get_connection() in db_client.py already sets this).
        min_open_date: Optional 'YYYY-MM-DD' floor on open_date. None =
            no floor (all history included). Used to exclude the frozen
            pre-2026 backlog per Tony's standing rule.

    Returns:
        List of plain dicts, one per row, column name -> value.
    """
    sql = "SELECT * FROM v_trade_summary WHERE status != 'open'"
    params: List[str] = []
    if min_open_date:
        sql += " AND open_date >= ?"
        params.append(min_open_date)
    sql += " ORDER BY last_exit_date DESC"

    rows = conn.execute(sql, params).fetchall()
    result = [dict(row) for row in rows]
    logger.debug(f"get_closed_trades → {len(result)} rows (min_open_date={min_open_date})")
    return result
