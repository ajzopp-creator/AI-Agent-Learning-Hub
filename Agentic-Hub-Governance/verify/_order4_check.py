import sqlite3
conn = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM orders WHERE order_id = 4")
row = cur.fetchone()
lines = ["--- order #4 ---"]
if row:
    for k, v in dict(row).items():
        lines.append(f"  {k}: {v}")
else:
    lines.append("  NOT FOUND")

cur.execute("SELECT * FROM trades WHERE schwab_transaction_id = '5375345511' ORDER BY trade_id DESC LIMIT 1")
trow = cur.fetchone()
if trow:
    tdict = dict(trow)
    lines.append("--- matching trades row ---")
    for k, v in tdict.items():
        lines.append(f"  {k}: {v}")
    cur.execute("SELECT * FROM exits WHERE trade_id = ?", (tdict["trade_id"],))
    erow = cur.fetchone()
    if erow:
        lines.append("--- matching exits row ---")
        for k, v in dict(erow).items():
            lines.append(f"  {k}: {v}")
    else:
        lines.append("--- no exits row ---")
else:
    lines.append("--- no trades row found for this schwab_order_id ---")
conn.close()
with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_order4_check.txt","w") as f:
    f.write("\n".join(lines))