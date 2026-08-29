import sqlite3
c = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
print("ACCOUNTS:", c.execute("SELECT account_id, account_name, account_type FROM accounts").fetchall())
print("SYSTEMS:", c.execute("SELECT system_id, active FROM systems").fetchall())
