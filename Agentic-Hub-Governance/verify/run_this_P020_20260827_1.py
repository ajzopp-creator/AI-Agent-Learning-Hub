# FILE: run_this_P020_20260827_1.py
# PURPOSE: Read-only pull of P_020_trades.db -- schema check + closed trades
#          since 2026-05-01, for SNT-system and oil-sector loss review.
# AUTHOR: Claude (P_115 project session, at Tony's request)
# DATE: 2026-08-27

import sqlite3

DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("---SCHEMA---")
cur.execute("PRAGMA table_info(trades)")
cols = [dict(r) for r in cur.fetchall()]
for c in cols:
    print(c["cid"], c["name"], c["type"])

col_names = [c["name"] for c in cols]
print("---COLUMN-NAMES---")
print(",".join(col_names))

print("---ALL-CLOSED-TRADES-SINCE-2026-05-01---")
try:
    cur.execute("SELECT * FROM trades WHERE close_date >= '2026-05-01' ORDER BY close_date")
    rows = cur.fetchall()
    print(f"ROW_COUNT:{len(rows)}")
    for r in rows:
        print(dict(r))
except Exception as e:
    print(f"QUERY_ERROR: {e}")

print("---DONE---")
conn.close()
