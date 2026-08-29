import sqlite3
DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("TABLES:", tables)
for t in tables:
    if t == "trades":
        continue
    cur.execute("PRAGMA table_info(" + t + ")")
    print("---", t, "---")
    for r in cur.fetchall():
        print(r)
conn.close()
print("DONE_OK")
