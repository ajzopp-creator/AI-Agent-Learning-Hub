"""
Read-only diagnostic for WO-P010-E2.001 Question 2.
Purpose: check P_020_trades.db for any existing attribution of trades to
P_300-sourced signals, and count what's there. No writes to the DB.
"""
import sqlite3
import json

db_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

result = {}

# Schema of trades table
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='trades'")
row = cur.fetchone()
result["schema"] = row[0] if row else None

# Column list (safety check before referencing columns below)
cur.execute("PRAGMA table_info(trades)")
cols = [r[1] for r in cur.fetchall()]
result["columns"] = cols

# Counts by system
cur.execute("SELECT system, COUNT(*) FROM trades GROUP BY system")
result["counts_by_system"] = cur.fetchall()

# Total trade count
cur.execute("SELECT COUNT(*) FROM trades")
result["total_trades"] = cur.fetchone()[0]

# Search text columns for any P_300 reference, only if columns exist
text_cols = [c for c in ["reason", "notes", "signal_strength"] if c in cols]
p300_hits = {}
for c in text_cols:
    cur.execute(f"SELECT COUNT(*) FROM trades WHERE {c} LIKE '%P_300%' OR {c} LIKE '%P300%'")
    p300_hits[c] = cur.fetchone()[0]
result["p300_text_hits"] = p300_hits

conn.close()

out_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P010_20260829_133224_output.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=str)

print("DONE")
