# FILE: run_this_P020_20260827_2.py
# PURPOSE: Discover full table list + schemas in P_020_trades.db, then pull
#          closed SNT + oil-sector trades since 2026-05-01 using correct
#          column names once known.
# AUTHOR: Claude (P_115 project session, at Tony's request)
# DATE: 2026-08-27

import sqlite3

DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("---TABLES---")
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r["name"] for r in cur.fetchall()]
for t in tables:
    print(t)

for t in tables:
    print(f"---SCHEMA:{t}---")
    cur.execute(f"PRAGMA table_info({t})")
    for c in cur.fetchall():
        print(dict(c))

print("---TRADES-STATUS-VALUES---")
cur.execute("SELECT DISTINCT status FROM trades")
for r in cur.fetchall():
    print(dict(r))

print("---TRADES-OPEN-DATE-RANGE---")
cur.execute("SELECT MIN(open_date), MAX(open_date), COUNT(*) FROM trades")
print(cur.fetchone()[:])

print("---TRADES-SNT-COUNT---")
cur.execute("SELECT COUNT(*) FROM trades WHERE system='SNT'")
print(cur.fetchone()[0])

print("---SAMPLE-TRADES-ROWS---")
cur.execute("SELECT * FROM trades ORDER BY open_date DESC LIMIT 5")
for r in cur.fetchall():
    print(dict(r))

print("---DONE---")
conn.close()
