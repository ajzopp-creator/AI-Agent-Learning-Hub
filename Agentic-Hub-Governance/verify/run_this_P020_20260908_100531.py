r"""
PEH validation script -- WO-P400-E6.001, Remaining Gate 1.

Runs the already-built migration_add_orders_table.py for real against the
live P_020_trades.db production database. Idempotent (CREATE TABLE IF NOT
EXISTS / CREATE INDEX IF NOT EXISTS) -- safe to run, but this is the first
time it has ever executed outside :memory:.

DB backed up before this script was staged:
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db.backup_2026-09-08

Expected output: table + 4 indexes created (or confirmed existing), then
"Migration complete." followed by the verified column list.
"""
import sys
sys.path.insert(
    0,
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database\infrastructure",
)

from migration_add_orders_table import migrate

migrate()

import sqlite3

conn = sqlite3.connect(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)
cur = conn.cursor()
cur.execute("PRAGMA table_info(orders)")
cols = [row[1] for row in cur.fetchall()]
print(f"orders table columns ({len(cols)}): {cols}")
conn.close()