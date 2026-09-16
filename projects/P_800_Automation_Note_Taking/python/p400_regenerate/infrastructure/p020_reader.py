"""p400_regenerate/infrastructure/p020_reader.py -- read P_020's closed
P_400-sourced orders, for syncing back into P_400's vault notes.

Lazy cross-project read, same sys.path-insert pattern as
shared_resources/python_utils/p020_order_writer.py -- P_020's python\\
database\\ folder isn't part of the Hub's installed package. This
direction (P_800 reading FROM P_020) has no sys.modules collision risk:
p400_regenerate's own modules are namespaced ("p400_regenerate.x", see
this sub-project's __init__.py), so nothing here ever populates bare
sys.modules['infrastructure']/['domain'] the way P_400's flat top-level
packages do -- the collision found and fixed in
shared_resources/python_utils/p020_order_writer.py doesn't apply here.

No "synced" flag exists on P_020's orders table, by design -- idempotency
is checked downstream in application/regenerate_command.py by reading
each order's own vault note's CURRENT lifecycle_status (already CLOSED =
already synced, skip). Adding a redundant tracking column here would be
duplicate state.

Part of: P_800 Automation Note-Taking -- p400_regenerate sub-project
Layer:   infrastructure (I/O)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

_P_020_DATABASE_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)


def get_closed_p400_orders() -> List[dict]:
    """Return every closed, P_400-sourced order from P_020's orders table.

    Returns:
        List of plain dicts (one per closed order), each with at least
        order_id, schwab_order_id, entry_date, close_date, realized_pnl.
        Empty list if P_020's database can't be reached.
    """
    if str(_P_020_DATABASE_DIR) not in sys.path:
        sys.path.insert(0, str(_P_020_DATABASE_DIR))

    try:
        from infrastructure.db_client import get_connection
    except Exception:
        return []

    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT order_id, schwab_order_id, entry_date, close_date, "
            "realized_pnl FROM orders "
            "WHERE status = 'closed' AND source_project = 'P400' "
            "AND schwab_order_id IS NOT NULL"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
