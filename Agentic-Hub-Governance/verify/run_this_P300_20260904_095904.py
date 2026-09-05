"""
P_300 -- Independent-review DB spot-check for WO-P300-E5.010
Read-only against buy_ledger.db. No writes. No project imports.
"""
import sqlite3
import sys
import statistics

DB_PATH = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\ledger\buy_ledger.db"

HORIZONS = [5, 7, 10, 15, 20]

EXPECTED_COMPLETE_CASE = {
    5:  (53.1, -0.52),
    7:  (56.8, 0.63),
    10: (57.4, 1.25),
    15: (56.5, 0.98),
    20: (59.0, 1.92),
}
WIN_TOL_PP = 2.0
RET_TOL_PP = 0.15


def fail(reason):
    print("FAIL:", reason)
    with open(__file__.replace(".py", ".done"), "w") as f:
        f.write("FAIL\n1\n")
    sys.exit(1)


def main():
    try:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    except Exception as e:
        fail(f"could not open DB read-only: {e}")
    cur = con.cursor()

    # Schema check first -- confirm expected columns exist before trusting any query.
    cols = [r[1] for r in cur.execute("PRAGMA table_info(fired_signals)").fetchall()]
    required = ["ticker", "signal_date", "chosen_horizon"] + [f"h{h}_return_pct" for h in HORIZONS]
    missing = [c for c in required if c not in cols]
    if missing:
        fail(f"fired_signals missing expected columns: {missing}. Live columns: {cols}")

    ret_cols = ", ".join(f"h{h}_return_pct" for h in HORIZONS)
    where_notnull = " AND ".join(f"h{h}_return_pct IS NOT NULL" for h in HORIZONS)

    rows = cur.execute(
        f"SELECT ticker, signal_date, {ret_cols} FROM fired_signals "
        f"WHERE chosen_horizon = 5 AND {where_notnull}"
    ).fetchall()

    n = len(rows)
    if n < 300:
        fail(f"complete-case population n={n}, expected ~324 (population 300-350 tolerance) -- filter or data drifted")

    # Recompute the complete-case panel independently (win% = return_pct > 0, avg = mean(*100)).
    print(f"Complete-case population: n={n}")
    panel_ok = True
    for idx, h in enumerate(HORIZONS):
        vals = [r[2 + idx] for r in rows]
        win_pct = 100.0 * sum(1 for v in vals if v > 0) / n
        avg_ret_pct = 100.0 * statistics.mean(vals)
        exp_win, exp_ret = EXPECTED_COMPLETE_CASE[h]
        win_diff = abs(win_pct - exp_win)
        ret_diff = abs(avg_ret_pct - exp_ret)
        status = "OK" if (win_diff <= WIN_TOL_PP and ret_diff <= RET_TOL_PP) else "MISMATCH"
        if status == "MISMATCH":
            panel_ok = False
        print(f"h{h}: win={win_pct:.1f}% (WO claimed {exp_win}%, diff {win_diff:.2f}pp) "
              f"avg_ret={avg_ret_pct:.2f}% (WO claimed {exp_ret}%, diff {ret_diff:.2f}pp) -> {status}")

    if not panel_ok:
        fail("one or more complete-case panel horizons did not match the WO's claimed table within tolerance")

    # Single-row spot-check -- first row by (signal_date, ticker), raw DB value vs x100-scaled.
    spot = sorted(rows, key=lambda r: (r[1], r[0]))[0]
    ticker, signal_date = spot[0], spot[1]
    print(f"\nSpot-check row: ticker={ticker} signal_date={signal_date}")
    for idx, h in enumerate(HORIZONS):
        raw = spot[2 + idx]
        print(f"  h{h}_return_pct raw={raw!r}  x100_scaled={raw * 100:.4f}%")

    con.close()
    print("PASS")
    with open(__file__.replace(".py", ".done"), "w") as f:
        f.write("PASS\n0\n")


if __name__ == "__main__":
    main()
