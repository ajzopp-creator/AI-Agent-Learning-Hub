import sqlite3

db = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='exits'")
print(cur.fetchone()[0])
print('---')
cur.execute("SELECT COUNT(*) FROM exits")
print("exit rows:", cur.fetchone()[0])
