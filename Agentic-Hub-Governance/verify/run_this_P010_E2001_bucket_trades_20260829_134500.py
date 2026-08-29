"""
FILE: run_this_P010_E2001_bucket_trades_20260829_134500.py
VERSION: 1.0
DATE: 2026-08-29
AUTHOR: Anthony Zoppi + Claude
LAYER: verify (PEH handoff, read-only, self-contained)
DESCRIPTION:
    WO-P010-E2.001 Question 2 groundwork. Buckets the real P_020 trades
    tagged system='P_300' by market regime (OFF/HALF/FULL) at each
    trade's open_date, using the SAME VP-reconstruction method as
    WO-P300-E5.006 (P_010 keeps no posture history, so this reuses
    P_300's SPY/QQQ 10-year grids and parser rather than re-deriving
    anything new). Read-only against both databases. Writes one CSV
    to this folder. Does not touch sizing, does not touch P_300's
    matcher/schema, does not decide anything -- produces the real
    per-bucket n's this WO's Acceptance Criteria need before Tony's
    keep/carve-out/defer decision.
"""
from __future__ import annotations

import csv
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

P300_PROJECT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_300_Vantage_Point_Pattern_Recognition"
)
sys.path.insert(0, str(P300_PROJECT / "python"))
from infrastructure.bulk_grid_reader import parse_bulk_file  # noqa: E402

GRIDS = {
    "SPY": P300_PROJECT / "data" / "reference" / "10_Pattern_SPY.xlsx",
    "QQQ": P300_PROJECT / "data" / "reference" / "10_Pattern_QQQ.xlsx",
}

TRADES_DB = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem"
    r"\data\database\P_020_trades.db"
)

OUT_CSV = Path(__file__).with_name(
    "p300_trades_bucketed_20260829_134500.csv")
MIN_N = 10  # WO-P010-E2.001 reuses P_115 Workstream E's per-bucket bar
BUCKET_ORDER = ["OFF", "HALF", "FULL"]


def load_avg_posture() -> dict[date, float]:
    """avg_posture per date, P_010 formula, exact-date join of SPY+QQQ.
    Identical method to WO-P300-E5.006's run_this_P300_20260829_101500.py
    -- not re-derived, reused on purpose so both measurements agree."""
    per_sym: dict[str, dict[date, float]] = {}
    for sym, path in GRIDS.items():
        parsed = parse_bulk_file(path)
        per_sym[sym] = {b.bar_date: (b.mtdiff + b.ltdiff) / 2.0
                        for b in parsed.bars}
        print(f"{sym}: {len(parsed.bars)} bars "
              f"{parsed.bars[0].bar_date} -> {parsed.bars[-1].bar_date}")
    common = set(per_sym["SPY"]) & set(per_sym["QQQ"])
    return {d: (per_sym["SPY"][d] + per_sym["QQQ"][d]) / 2.0 for d in common}


def bucket_of(avg_posture: float) -> str:
    """P_010 determine_risk_mode cuts -- same as production, do not edit."""
    if avg_posture >= 1.0:
        return "FULL"
    if avg_posture >= 0.0:
        return "HALF"
    return "OFF"


def load_p300_trades() -> list[dict]:
    """Real trades from P_020's ledger, system='P_300'. Read-only."""
    conn = sqlite3.connect(TRADES_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT trade_id, underlying_symbol, open_date, status "
        "FROM trades WHERE system = 'P_300' ORDER BY open_date"
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    print(f"P_020 trades.db: {len(rows)} rows with system='P_300'")
    return rows


def main() -> int:
    posture = load_avg_posture()
    print(f"posture dates (SPY&QQQ common): {len(posture)}")

    trades = load_p300_trades()
    tagged: list[dict] = []
    unmatched: list[dict] = []
    for t in trades:
        od = t["open_date"]
        try:
            d = datetime.strptime(od[:10], "%Y-%m-%d").date()
        except (TypeError, ValueError):
            unmatched.append(t)
            continue
        p = posture.get(d)
        if p is None:
            unmatched.append(t)
            continue
        tagged.append({**t, "open_date_parsed": d,
                       "avg_posture": p, "bucket": bucket_of(p)})

    print(f"matched: {len(tagged)}  unmatched (no grid date for "
          f"open_date): {len(unmatched)}")
    if unmatched:
        for u in unmatched:
            print(f"  UNMATCHED trade_id={u['trade_id']} "
                  f"symbol={u['underlying_symbol']} "
                  f"open_date={u['open_date']}")

    counts: dict[str, int] = {b: 0 for b in BUCKET_ORDER}
    for t in tagged:
        counts[t["bucket"]] += 1

    print("\nP_300-sourced trades by regime bucket (bar = n>=%d):" % MIN_N)
    for b in BUCKET_ORDER:
        n = counts[b]
        flag = "OK" if n >= MIN_N else f"BELOW BAR (need {MIN_N - n} more)"
        print(f"  {b:5s} n={n:3d}  {flag}")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["trade_id", "underlying_symbol", "open_date",
                    "status", "avg_posture", "bucket"])
        for t in tagged:
            w.writerow([t["trade_id"], t["underlying_symbol"],
                        t["open_date_parsed"].isoformat(), t["status"],
                        f"{t['avg_posture']:.4f}", t["bucket"]])
        for u in unmatched:
            w.writerow([u["trade_id"], u["underlying_symbol"],
                        u["open_date"], u["status"], "", "UNMATCHED"])

    print(f"\ncsv: {OUT_CSV}")
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
