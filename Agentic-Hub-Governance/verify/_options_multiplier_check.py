import sqlite3
conn = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("""
    SELECT t.trade_id, t.underlying_symbol, t.asset_type, t.direction, t.entry_price, t.qty, t.source,
           e.exit_price, e.exit_pnl
    FROM trades t JOIN exits e ON e.trade_id = t.trade_id
    WHERE t.asset_type IN ('call','put') AND t.source != 'P400'
    ORDER BY t.trade_id DESC LIMIT 8
""")
rows = cur.fetchall()
out = ["Recent NON-P400 options trades (entry/exit price vs exit_pnl):"]
for r in rows:
    d = dict(r)
    implied_mult = None
    diff = (d["exit_price"] - d["entry_price"]) * (1 if d["direction"]=="long" else -1) * d["qty"]
    if diff != 0:
        implied_mult = round(d["exit_pnl"] / diff, 2)
    out.append(f"  trade {d['trade_id']} {d['underlying_symbol']} {d['direction']} qty={d['qty']} entry={d['entry_price']} exit={d['exit_price']} exit_pnl={d['exit_pnl']} implied_multiplier={implied_mult}")
conn.close()
with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_options_multiplier_check.txt","w") as f:
    f.write("\n".join(out))