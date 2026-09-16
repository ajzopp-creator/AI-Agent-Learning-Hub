"""Single source of truth for valid P_020 trading-system codes.

Reads the `systems` table in P_020_trades.db at call time, replacing
three hand-maintained hardcoded lists that had drifted out of sync
with the table and with each other (generate_dashboard.py SYSTEM_ORDER,
resolve_tos_imports.py VALID_SYSTEMS, tracker_reader.py _VALID_SYSTEMS
-- found 2026-09-13, none of the three matched the table).
"""

import sqlite3
from typing import List, Set

from config import DATABASE_FILE


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(str(DATABASE_FILE))


def get_valid_system_ids() -> Set[str]:
    """Return every registered system_id as a set, for `in` membership checks.

    Includes both 'Day' and 'DAY' -- the systems table's row is 'Day' but
    7 live trades already use 'DAY' (case mismatch flagged 2026-08-29 in
    p020-project-context skill, not corrected here). Every other code
    passes through with the exact casing stored in the table.
    """
    conn = _connect()
    try:
        rows = conn.execute("SELECT system_id FROM systems").fetchall()
    finally:
        conn.close()
    ids: Set[str] = {r[0] for r in rows}
    if "Day" in ids:
        ids.add("DAY")
    return ids


def get_system_display_order() -> List[str]:
    """Return active system_ids ordered by the systems.display_order column.

    Requires migration_add_display_order.py to have been run once --
    that migration adds and backfills the column.
    """
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT system_id FROM systems "
            "WHERE active = 1 ORDER BY display_order, system_id"
        ).fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows]
