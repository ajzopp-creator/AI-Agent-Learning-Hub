"""
FILE: run_this_P010_E2001_win_loss_20260829_140000.py
VERSION: 1.0
DATE: 2026-08-29
AUTHOR: Anthony Zoppi + Claude
LAYER: verify (PEH handoff, read-only, self-contained)
DESCRIPTION:
    WO-P010-E2.001 Question 2, next layer (Tony approved 2026-08-29,
    "yes"). Joins the already-bucketed 28 P_300 trades
    (p300_trades_bucketed_20260829_134500.csv) against P_020's `exits`
    table to get REAL realized P&L (stops, actual sizing already baked
    in via exit_pnl) per bucket, so this can be compared against the
    raw-forward-return numbers in WO-P300-E5.006 that had no stop and
    no sizing. Read-only. No writes to trades.db. Does not decide
    keep/carve-out/defer -- that stays Tony's call per the WO.
"""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

BUCKETED_CSV = Path(__file__).with_name(
    "p300_trades_bucketed_20260829_134500.csv")
TRADES_DB = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem"
    r"\data\database\P_020_trades.db"
)
OUT_CSV = Path(__file__).with_name(
    "p300_trades_winloss_20260829_140000.csv")
BUCKET_ORDER = ["OFF", "HALF", "FULL"]


def load_bucketed_trades() -> list[dict]:
    rows = []
    with BUCKETED_CSV.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    print(f"bucketed input: {len(rows)} rows")
    return rows


def load_realized_pnl(trade_ids: list[int]) -> dict[int, float]:
    """Sum exit_pnl per trade_id -- covers partial exits correctly."""
    conn = sqlite3.connect(TRADES_DB)
    cur = conn.cursor()
    placeholders = ",".join("?" for _ in trade_ids)
    cur.execute(
        f"SELECT trade_id, SUM(exit_pnl) FROM exits "
        f"WHERE trade_id IN ({placeholders}) GROUP BY trade_id",
        trade_ids,
    )
    result = {tid: pnl for tid, pnl in cur.fetchall()}
    conn.close()
    return result


def main() -> int:
    rows = load_bucketed_trades()
    bucketed_only = [r for r in rows if r["bucket"] != "UNMATCHED"]
    trade_ids = [int(r["trade_id"]) for r in bucketed_only]
    pnl_by_trade = load_realized_pnl(trade_ids)

    open_count = 0
    stats: dict[str, dict[str, float | int]] = {
        b: {"n_closed": 0, "wins": 0, "losses": 0, "total_pnl": 0.0}
        for b in BUCKET_ORDER
    }

    out_rows = []
    for r in bucketed_only:
        tid = int(r["trade_id"])
        bucket = r["bucket"]
        pnl = pnl_by_trade.get(tid)
        if pnl is None:
            # no exits recorded -- trade is still open (or unclosed
            # partial with zero exits so far); exclude from win/loss
            open_count += 1
            out_rows.append({**r, "realized_pnl": "", "outcome": "OPEN"})
            continue
        outcome = "WIN" if pnl > 0 else ("LOSS" if pnl < 0 else "SCRATCH")
        stats[bucket]["n_closed"] += 1
        if pnl > 0:
            stats[bucket]["wins"] += 1
        elif pnl < 0:
            stats[bucket]["losses"] += 1
        stats[bucket]["total_pnl"] += pnl
        out_rows.append({**r, "realized_pnl": f"{pnl:.2f}",
                          "outcome": outcome})

    print(f"open (no exits yet, excluded from win/loss): {open_count}")
    print("\nP_300-sourced trades, REAL closed-trade outcomes by bucket:")
    for b in BUCKET_ORDER:
        s = stats[b]
        n = s["n_closed"]
        wr = (s["wins"] / n * 100.0) if n else 0.0
        avg = (s["total_pnl"] / n) if n else 0.0
        print(f"  {b:5s} closed_n={n:2d}  wins={s['wins']:2d}  "
              f"losses={s['losses']:2d}  win%={wr:5.1f}  "
              f"total_pnl=${s['total_pnl']:8.2f}  avg_pnl=${avg:7.2f}")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["trade_id", "underlying_symbol", "open_date",
                      "status", "avg_posture", "bucket", "realized_pnl",
                      "outcome"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    print(f"\ncsv: {OUT_CSV}")
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
