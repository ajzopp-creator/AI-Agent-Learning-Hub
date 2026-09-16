import sqlite3
conn = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
cur = conn.cursor()
cur.execute("SELECT * FROM orders")
rows = cur.fetchall()
conn.close()
with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_final_state_check.txt","w") as f:
    f.write(f"orders rows: {len(rows)}\n" + str(rows))