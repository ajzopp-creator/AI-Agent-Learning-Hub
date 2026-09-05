# FILE: run_this_P020_20260827_3.py
# PURPOSE: Closed trades since 2026-05-01, joined to exits for realized P&L.
#          Full row dump (system, symbol, date, pnl) for SNT bucketing and
#          manual oil-sector symbol classification, plus SNT summary stats.
# AUTHOR: Claude (P_115 project session, at Tony's request)
# DATE: 2026-08-27

import sqlite3

DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

query = """
SELECT
    t.trade_id,
    t.system,
    t.underlying_symbol,
    t.asset_type,
    t.direction,
    t.open_date,
    t.entry_price,
    t.qty,
    t.total_commissions AS entry_commissions,
    COALESCE(SUM(e.exit_pnl), 0) AS gross_exit_pnl,
    COALESCE(SUM(e.exit_commissions), 0) AS exit_commissions,
    MAX(e.exit_date) AS last_exit_date
FROM trades t
JOIN exits e ON e.trade_id = t.trade_id
WHERE t.status = 'closed'
  AND t.open_date >= '2026-05-01'
GROUP BY t.trade_id
ORDER BY t.open_date
"""

cur.execute(query)
rows = [dict(r) for r in cur.fetchall()]

print(f"---ROW_COUNT:{len(rows)}---")
print("---ALL-ROWS---")
for r in rows:
    net = r["gross_exit_pnl"] - r["entry_commissions"] - r["exit_commissions"]
    r["net_pnl"] = round(net, 2)
    print(r)

def bucket_stats(label, subset):
    n = len(subset)
    wins = [r for r in subset if r["net_pnl"] > 0]
    losses = [r for r in subset if r["net_pnl"] <= 0]
    total_pnl = sum(r["net_pnl"] for r in subset)
    win_rate = (len(wins) / n * 100) if n else 0
    avg_win = (sum(r["net_pnl"] for r in wins) / len(wins)) if wins else 0
    avg_loss = (sum(r["net_pnl"] for r in losses) / len(losses)) if losses else 0
    expectancy = (total_pnl / n) if n else 0
    print(f"---BUCKET:{label}---")
    print(f"n={n} wins={len(wins)} losses={len(losses)} win_rate={win_rate:.1f}%")
    print(f"total_pnl={total_pnl:.2f} expectancy_per_trade={expectancy:.2f}")
    print(f"avg_win={avg_win:.2f} avg_loss={avg_loss:.2f}")

snt = [r for r in rows if r["system"] == "SNT"]
bucket_stats("SNT", snt)

all_closed = rows
bucket_stats("ALL_CLOSED_SINCE_2026-05-01", all_closed)

for sysname in sorted(set(r["system"] for r in rows)):
    bucket_stats(sysname, [r for r in rows if r["system"] == sysname])

print("---DONE---")
conn.close()
