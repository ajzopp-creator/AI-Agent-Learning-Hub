"""
PEH run_this.py -- Ledger fill-status check (read-only)
Date: 2026-06-30
Purpose: Count rows by horizon-fill status in buy_ledger.db to determine
whether sufficient h20-complete rows exist to begin lambda tuning (M-046).
Read-only -- no writes, no production code touched.
Success criteria: prints counts for total rows, rows with h20_return_pct
NOT NULL (fully h20-filled), and a class breakdown (BUY/WATCH) of the
h20-filled subset. No assertions to fix; this is a status report, not a test.
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\ledger\buy_ledger.db"
)

def main():
    if not DB_PATH.exists():
        print(f"FAIL: ledger db not found at {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS n FROM fired_signals")
    total = cur.fetchone()["n"]

    cur.execute(
        "SELECT COUNT(*) AS n FROM fired_signals WHERE h20_return_pct IS NOT NULL"
    )
    h20_filled = cur.fetchone()["n"]

    cur.execute(
        "SELECT signal_class, COUNT(*) AS n FROM fired_signals "
        "WHERE h20_return_pct IS NOT NULL GROUP BY signal_class"
    )
    by_class = {row["signal_class"]: row["n"] for row in cur.fetchall()}

    cur.execute(
        "SELECT h5_return_pct, h7_return_pct, h10_return_pct, h15_return_pct, h20_return_pct "
        "FROM fired_signals"
    )
    rows = cur.fetchall()
    h5 = sum(1 for r in rows if r["h5_return_pct"] is not None)
    h7 = sum(1 for r in rows if r["h7_return_pct"] is not None)
    h10 = sum(1 for r in rows if r["h10_return_pct"] is not None)
    h15 = sum(1 for r in rows if r["h15_return_pct"] is not None)
    h20 = sum(1 for r in rows if r["h20_return_pct"] is not None)

    conn.close()

    print(f"total_rows={total}")
    print(f"h5_filled={h5} h7_filled={h7} h10_filled={h10} h15_filled={h15} h20_filled={h20}")
    print(f"h20_filled_by_class={by_class}")
    print("PASS")

if __name__ == "__main__":
    main()
