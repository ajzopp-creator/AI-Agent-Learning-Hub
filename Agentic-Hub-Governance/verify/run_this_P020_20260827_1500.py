import sqlite3, sys, os, datetime

TS = "20260827_1500"
PROJECT = "P_020"
BASE = r"C:\Users\Trader\AI-Agent-Learning-Hub"
DB = os.path.join(BASE, r"projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")
VERIFY = os.path.join(BASE, r"Agentic-Hub-Governance\verify")
DONE = os.path.join(VERIFY, "run_this_" + PROJECT + "_" + TS + ".py.done")

def log(*a):
    print(*a)

status_line = "FAIL: unknown error"
exit_code = 1

try:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(trades)")
    cols_info = cur.fetchall()
    colnames = [r["name"] for r in cols_info]
    log("---COLUMNS---")
    for r in cols_info:
        log(r["cid"], r["name"], r["type"])

    log("---TOTAL ROWS---")
    cur.execute("SELECT COUNT(*) AS n FROM trades")
    log(cur.fetchone()["n"])

    log("---SYSTEM COUNTS---")
    cur.execute("SELECT system, COUNT(*) as n FROM trades GROUP BY system")
    for r in cur.fetchall():
        log(dict(r))

    close_date_col = next((c for c in colnames if c.lower() in ("close_date", "exit_date", "closed_date")), None)
    status_col = next((c for c in colnames if c.lower() in ("status", "trade_status")), None)
    pnl_candidates = [c for c in colnames if any(k in c.lower() for k in ("pnl", "profit", "p_l", "gain_loss", "realized"))]

    log("---DETECTED---")
    log("close_date_col:", close_date_col)
    log("status_col:", status_col)
    log("pnl_candidates:", pnl_candidates)

    if close_date_col:
        q = "SELECT * FROM trades WHERE " + close_date_col + " >= '2026-05-01' ORDER BY " + close_date_col
        cur.execute(q)
        rows = cur.fetchall()
        log("---CLOSED SINCE 2026-05-01 (n=" + str(len(rows)) + ")---")
        for r in rows:
            log(dict(r))
    else:
        log("NO close_date-like column found -- dumping full table sample")
        cur.execute("SELECT * FROM trades LIMIT 5")
        for r in cur.fetchall():
            log(dict(r))

    conn.close()
    status_line = "PASS"
    exit_code = 0
    print("PASS")
except Exception as e:
    status_line = "FAIL: " + repr(e)
    exit_code = 1
    print("FAIL:", repr(e))

with open(DONE, "w", encoding="utf-8") as f:
    f.write(datetime.datetime.now().isoformat() + "\n" + status_line + "\nexit_code=" + str(exit_code) + "\n")

sys.exit(exit_code)
