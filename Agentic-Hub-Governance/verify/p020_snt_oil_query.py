import sqlite3

DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

q = """
SELECT t.trade_id, t.system, t.underlying_symbol, t.asset_type, t.direction,
       t.open_date, t.total_commissions AS entry_comm,
       SUM(e.exit_pnl) AS total_exit_pnl,
       SUM(e.exit_commissions) AS total_exit_comm,
       MAX(e.exit_date) AS last_exit_date
FROM trades t
JOIN exits e ON e.trade_id = t.trade_id
WHERE e.exit_date >= '2026-05-01'
GROUP BY t.trade_id
ORDER BY last_exit_date
"""
cur.execute(q)
rows = [dict(r) for r in cur.fetchall()]

print("TOTAL CLOSED TRADES SINCE 2026-05-01:", len(rows))
print("---ALL ROWS---")
for r in rows:
    print(r)

def stats(label, subset):
    n = len(subset)
    if n == 0:
        print(label, "-- n=0")
        return
    wins = [r for r in subset if r["total_exit_pnl"] > 0]
    losses = [r for r in subset if r["total_exit_pnl"] <= 0]
    total_pnl = sum(r["total_exit_pnl"] for r in subset)
    win_rate = len(wins) / n * 100
    expectancy = total_pnl / n
    print(label, "-- n=%d, wins=%d, losses=%d, win_rate=%.1f%%, total_exit_pnl=%.2f, expectancy_per_trade=%.2f" % (
        n, len(wins), len(losses), win_rate, total_pnl, expectancy))

snt = [r for r in rows if r["system"] == "SNT"]
print("---SNT BUCKET---")
for r in snt:
    print(r)
stats("SNT", snt)

oil_tickers = {"XOM","CVX","OXY","COP","SLB","HAL","MRO","DVN","FANG","PXD","WMB","KMI",
               "USO","UNG","USL","BOIL","UCO","SCO","DBO","XLE","OIH","VLO","PSX","MPC",
               "BKR","APA","EQT","CTRA","TRGP","CL","WTI"}
oil = [r for r in rows if r["underlying_symbol"] in oil_tickers]
print("---OIL-CANDIDATE BUCKET (ticker-list match)---")
for r in oil:
    print(r)
stats("OIL(candidate list)", oil)

print("---ALL DISTINCT SYMBOLS IN WINDOW (for manual oil-sector check)---")
print(sorted(set(r["underlying_symbol"] for r in rows)))

conn.close()
print("DONE_OK")
