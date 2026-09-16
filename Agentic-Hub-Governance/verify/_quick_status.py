import sqlite3
conn = sqlite3.connect(r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db')
cur = conn.cursor()
cur.execute('SELECT status, realized_pnl FROM orders WHERE order_id = 4')
print(cur.fetchone())
conn.close()