import sqlite3

db = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
conn = sqlite3.connect(db)
cur = conn.cursor()

print("--- systems table ---")
for row in cur.execute("SELECT system_id, system_name, active FROM systems ORDER BY system_id"):
    print(row)

print()
print("--- trades.system value counts (top 20) ---")
for row in cur.execute("SELECT system, COUNT(*) FROM trades GROUP BY system ORDER BY COUNT(*) DESC LIMIT 20"):
    print(row)

print()
print("--- trades where system = 'OIL' ---")
for row in cur.execute("SELECT trade_id, symbol, open_date, system, account_id FROM trades WHERE system = 'OIL'"):
    print(row)

conn.close()
