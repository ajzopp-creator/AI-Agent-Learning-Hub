"""
migration_add_tag_columns.py

One-time migration: adds reason and signal_strength TEXT columns to the trades
table plus indexes for filtering. Idempotent — safe to run multiple times.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure (migration)

Usage:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe migration_add_tag_columns.py

Expected output on first run:
    Added column: reason
    Added column: signal_strength
    Created index: idx_trades_reason
    Created index: idx_trades_signal_strength
    Migration complete.

Expected output on subsequent runs:
    Skip (exists): reason
    Skip (exists): signal_strength
    Created index: idx_trades_reason       (IF NOT EXISTS is cheap)
    Created index: idx_trades_signal_strength
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

        if _column_exists(cur, "trades", "reason"):
            print("Skip (exists): reason")
        else:
            cur.execute("ALTER TABLE trades ADD COLUMN reason TEXT")
            print("Added column: reason")

        if _column_exists(cur, "trades", "signal_strength"):
            print("Skip (exists): signal_strength")
        else:
            cur.execute("ALTER TABLE trades ADD COLUMN signal_strength TEXT")
            print("Added column: signal_strength")

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_trades_reason "
            "ON trades(reason)"
        )
        print("Created index: idx_trades_reason")

        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_trades_signal_strength "
            "ON trades(signal_strength)"
        )
        print("Created index: idx_trades_signal_strength")

        conn.commit()
        print("Migration complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
