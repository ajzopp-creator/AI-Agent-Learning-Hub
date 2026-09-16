import sqlite3
conn = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM orders")
n = cur.fetchone()[0]
conn.close()
with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_status_check.txt", "w") as f:
    f.write(f"orders rows: {n}")