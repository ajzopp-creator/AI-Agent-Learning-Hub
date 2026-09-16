import sqlite3
DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
conn = sqlite3.connect(DB)
print("=== P_210 trades ===")
for r in conn.execute(
    "SELECT trade_id, underlying_symbol, asset_type, direction, open_date, "
    "status, qty, entry_price, schwab_transaction_id, source "
    "FROM trades WHERE system='P_210' ORDER BY open_date"
):
    print(r)
print()
print("=== any exits attached to P_210 trades ===")
for r in conn.execute(
    "SELECT e.trade_id, e.exit_number, e.exit_date, e.qty_exited, e.exit_price, e.exit_pnl "
    "FROM exits e JOIN trades t ON e.trade_id = t.trade_id WHERE t.system='P_210'"
):
    print(r)
print()
print("=== today's date per DB (max open_date across all trades) ===")
print(conn.execute("SELECT MAX(open_date) FROM trades").fetchone())
conn.close()
print("PASS")
