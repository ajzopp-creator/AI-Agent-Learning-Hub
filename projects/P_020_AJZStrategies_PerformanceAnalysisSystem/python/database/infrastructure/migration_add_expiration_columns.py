"""
migration_add_expiration_columns.py

One-time migration: adds expiration_date and settlement_price columns to
the trades table, for auto-closing 0DTE cash-settled options that expire
with no closing Schwab transaction. Idempotent -- safe to run multiple
times.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure (migration)
WO:      WO-P020-E1.018

Usage:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe migration_add_expiration_columns.py

Expected output on first run:
    Added column: expiration_date
    Added column: settlement_price
    Migration complete.

Expected output on subsequent runs:
    Skip (exists): expiration_date
    Skip (exists): settlement_price
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


def _column_exists(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())


def migrate() -> None:
    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()

        if _column_exists(cur, "trades", "expiration_date"):
            print("Skip (exists): expiration_date")
        else:
            cur.execute("ALTER TABLE trades ADD COLUMN expiration_date DATE")
            print("Added column: expiration_date")

        if _column_exists(cur, "trades", "settlement_price"):
            print("Skip (exists): settlement_price")
        else:
            cur.execute("ALTER TABLE trades ADD COLUMN settlement_price REAL")
            print("Added column: settlement_price")

        conn.commit()
        print("Migration complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
