"""
Read-only check: does P_020_trades.db have a 'systems' table (referenced
by trades.system FK), and if so, is it the authoritative list vs the
hardcoded 'Valid Trading Systems' list in p020-project-context SKILL.md?
No writes.
"""
import sqlite3
import json

db_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

result = {}

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
result["all_tables"] = [r[0] for r in cur.fetchall()]

cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='systems'")
row = cur.fetchone()
result["systems_schema"] = row[0] if row else None

if row:
    cur.execute("SELECT * FROM systems")
    cols = [d[0] for d in cur.description]
    result["systems_columns"] = cols
    result["systems_rows"] = cur.fetchall()

conn.close()

out_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_P020_20260829_check_systems_table_output.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, default=str)

print("DONE")
