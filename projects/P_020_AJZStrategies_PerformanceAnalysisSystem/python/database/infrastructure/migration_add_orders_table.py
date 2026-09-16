"""
migration_add_orders_table.py

One-time migration: creates the `orders` table (WO-P400-E6.001 Scope item 2) --
the SQLite source of truth for P_400-submitted orders, replacing dead-ended
Obsidian vault notes as the primary record. Idempotent -- safe to run multiple
times (CREATE TABLE IF NOT EXISTS / CREATE INDEX IF NOT EXISTS).

Column design folds in the Attribution Integrity Standard (WO-P000-E22.001)
per WO-P400-E6.001's 2026-09-06 coordination note: why_code/sig_code/
source_project/confidence_tier use that Standard's vocabulary directly,
rather than a competing scheme reconciled later.

Columns extended 2026-09-07 (same WO, file 6 sizing, before this migration
was ever run for real -- edited in place rather than a follow-on ALTER):
entry_fill_price/asset_type/put_call added. Found while building
db_order_writer.py's promote_order_to_trade() -- Trade.entry_price needs
the actual fill price (planned_entry_price is only the planned number),
and Trade.asset_type needs a real EQUITY/OPTION + putCall pair to map
through schwab_mapper.py's existing _map_asset_type(), neither of which
the original column list captured.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure (migration)

Usage:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe migration_add_orders_table.py

Expected output on first run:
    Created table: orders
    Created index: idx_orders_symbol
    Created index: idx_orders_account_id
    Created index: idx_orders_status
    Created index: idx_orders_schwab_order_id
    Migration complete.

Expected output on subsequent runs:
    Table exists: orders
    Created index: idx_orders_symbol       (IF NOT EXISTS is cheap)
    Created index: idx_orders_account_id
    Created index: idx_orders_status
    Created index: idx_orders_schwab_order_id
    Migration complete.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)

ORDERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id            TEXT    NOT NULL,
    symbol                TEXT    NOT NULL,
    side                  TEXT    NOT NULL,
    qty                   REAL    NOT NULL,
    planned_entry_price   REAL,
    planned_stop_price    REAL,
    planned_target_price  REAL,
    trade_mode            TEXT    NOT NULL DEFAULT 'REAL',
    submitted_ts          TEXT    NOT NULL,
    schwab_order_id       TEXT,
    status                TEXT    NOT NULL DEFAULT 'pending',
    council_verdict       TEXT,
    why_code              TEXT,
    sig_code              TEXT,
    source_project        TEXT    NOT NULL DEFAULT 'P400',
    confidence_tier       TEXT    NOT NULL DEFAULT 'CONFIRMED',
    entry_date            TEXT,
    close_date            TEXT,
    realized_pnl          REAL,
    entry_fill_price      REAL,
    asset_type            TEXT,
    put_call              TEXT
)
"""


def _table_exists(cur: sqlite3.Cursor, table: str) -> bool:
    """Return True if a table with this name already exists."""
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    )
    return cur.fetchone() is not None


def migrate() -> None:
    """Create the orders table and its indexes if they don't already exist."""
    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        already_existed = _table_exists(cur, "orders")
        cur.execute(ORDERS_TABLE_SQL)
        if already_existed:
            print("Table exists: orders")
        else:
            print("Created table: orders")

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol)"
        )
        print("Created index: idx_orders_symbol")

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_account_id "
            "ON orders(account_id)"
        )
        print("Created index: idx_orders_account_id")

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)"
        )
        print("Created index: idx_orders_status")

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_schwab_order_id "
            "ON orders(schwab_order_id)"
        )
        print("Created index: idx_orders_schwab_order_id")

        conn.commit()
        print("Migration complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
