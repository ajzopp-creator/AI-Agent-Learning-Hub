import sqlite3
conn = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
cur = conn.cursor()
cur.execute("DELETE FROM exits WHERE trade_id = 3155")
cur.execute("DELETE FROM trades WHERE trade_id = 3155 AND schwab_transaction_id = '5375345511' AND source = 'P400'")
cur.execute("DELETE FROM orders WHERE order_id = 2 AND symbol = 'SPY' AND source_project = 'P400'")
conn.commit()
cur.execute("SELECT COUNT(*) FROM orders")
o = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM trades WHERE trade_id = 3155")
t = cur.fetchone()[0]
conn.close()
with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_cleanup_spy.txt","w") as f:
    f.write(f"orders rows: {o}\ntrade 3155 remaining: {t}")