import sqlite3
conn = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM orders")
o = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM trades WHERE trade_id = 3156")
t = cur.fetchone()[0]
cur.execute("SELECT MAX(order_id) FROM orders")
maxo = cur.fetchone()[0]
conn.close()
with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_live_check.txt","w") as f:
    f.write(f"orders rows: {o}\nmax order_id: {maxo}\ntrade 3156 exists: {t}")