"""
run_this_P300_20260831_093649.py
P_300 -- h5 ledger gap diagnosis: is the 75.5% predicted / 51.1% realized
win-rate gap (n=472, -0.75% avg return) concentrated in time (a bad
regime/stretch) or in a handful of symbols, or spread broadly across
both? Read-only against buy_ledger.db -- no writes to the ledger itself.

Schema (infrastructure/ledger_db.py, verified by reading the source,
not assumed): fired_signals(ledger_id, ticker, signal_date TEXT
YYYYMMDD, signal_class, chosen_horizon, pattern_id, ..., win_rate_pct,
mean_return_pct, h5_return_pct, ..., filled_date, fired_at, ...).

M-060 guard: signal_date format has been misparsed before in this
exact codebase (YYYYMMDD vs YYYY-MM-DD confusion). Tries YYYYMMDD
first (current schemas_ledger.py docstring), falls back to YYYY-MM-DD,
logs which one actually worked instead of assuming.
"""
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\ledger\buy_ledger.db")
OUT_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\outputs\reports\ledger")


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def parse_signal_date(raw: str) -> datetime:
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValueError(f"signal_date {raw!r} matches neither YYYYMMDD nor YYYY-MM-DD")


def iso_week_label(dt: datetime) -> str:
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def main():
    if not DB_PATH.exists():
        fail(f"ledger DB not found at {DB_PATH}")

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT ticker, signal_date, win_rate_pct, mean_return_pct, h5_return_pct "
        "FROM fired_signals WHERE chosen_horizon = 5 AND h5_return_pct IS NOT NULL"
    ).fetchall()
    conn.close()

    if not rows:
        fail("0 rows returned for chosen_horizon=5 with h5_return_pct filled -- "
             "schema or filter assumption is wrong, re-check before trusting any report")

    date_fmt_used = set()
    records = []
    for r in rows:
        dt = parse_signal_date(r["signal_date"])
        date_fmt_used.add("YYYYMMDD" if len(r["signal_date"]) == 8 and "-" not in r["signal_date"] else "YYYY-MM-DD")
        records.append({
            "ticker": r["ticker"], "date": dt,
            "pred_wr": r["win_rate_pct"], "ret": r["h5_return_pct"],
        })

    n = len(records)
    total_ret = sum(x["ret"] for x in records)
    avg_ret = total_ret / n
    win_rate = 100.0 * sum(1 for x in records if x["ret"] > 0) / n

    print(f"=== h5 gap diagnosis: {n} rows, signal_date format seen: {sorted(date_fmt_used)} ===")
    print(f"Overall: avg_return={avg_ret:+.3f}% win_rate={win_rate:.1f}% "
          f"(matches calibration report's -0.75% / 51.1% -- sanity check)\n")

    # --- Time bucketing (ISO week) ---
    by_week = defaultdict(list)
    for x in records:
        by_week[iso_week_label(x["date"])].append(x)

    print(f"=== By week ({len(by_week)} weeks) ===")
    print(f"{'week':10} {'n':>4} {'win%':>6} {'avg_ret%':>9} {'pred_wr%':>9}")
    week_summary = []
    for wk in sorted(by_week):
        items = by_week[wk]
        wn = len(items)
        wwr = 100.0 * sum(1 for x in items if x["ret"] > 0) / wn
        wret = sum(x["ret"] for x in items) / wn
        wpred = sum(x["pred_wr"] for x in items) / wn
        week_summary.append((wk, wn, wwr, wret, wpred))
        print(f"{wk:10} {wn:>4} {wwr:>5.1f}% {wret:>+8.3f}% {wpred:>8.1f}%")

    total_negative = sum(x["ret"] for x in records if x["ret"] < 0)
    worst_week = min(week_summary, key=lambda w: w[3] * w[1])
    worst_week_total = sum(x["ret"] for x in by_week[worst_week[0]] if x["ret"] < 0)
    week_concentration = 100.0 * worst_week_total / total_negative if total_negative else 0.0
    print(f"\nWorst single week: {worst_week[0]} (n={worst_week[1]}, avg_ret={worst_week[3]:+.3f}%) "
          f"-- {week_concentration:.1f}% of total negative return\n")

    # --- Symbol bucketing ---
    by_symbol = defaultdict(list)
    for x in records:
        by_symbol[x["ticker"]].append(x)

    symbol_summary = []
    for sym, items in by_symbol.items():
        sn = len(items)
        sret_total = sum(x["ret"] for x in items)
        swr = 100.0 * sum(1 for x in items if x["ret"] > 0) / sn
        symbol_summary.append((sym, sn, swr, sret_total, sret_total / sn))
    symbol_summary.sort(key=lambda s: s[3])

    print(f"=== By symbol ({len(symbol_summary)} distinct tickers) -- worst 15 by total return contributed ===")
    print(f"{'ticker':8} {'n':>3} {'win%':>6} {'total_ret%':>11} {'avg_ret%':>9}")
    for sym, sn, swr, stot, savg in symbol_summary[:15]:
        print(f"{sym:8} {sn:>3} {swr:>5.1f}% {stot:>+10.3f}% {savg:>+8.3f}%")

    worst5_total = sum(s[3] for s in symbol_summary[:5] if s[3] < 0)
    symbol_concentration = 100.0 * worst5_total / total_negative if total_negative else 0.0
    single_ticker_symbols = sum(1 for s in symbol_summary if s[1] == 1)
    print(f"\nWorst 5 symbols alone: {symbol_concentration:.1f}% of total negative return")
    print(f"Symbols with only 1 fired signal: {single_ticker_symbols} / {len(symbol_summary)} "
          f"(a single bad trade looks identical to a real pattern in a tiny sample)")

    print(f"\n=== Read this as ===")
    print(f"If week_concentration is high (one/two weeks dominate): likely a regime/stretch effect.")
    print(f"If symbol_concentration is high but spread across many weeks: likely specific tickers/setups.")
    print(f"If neither concentrates: the -0.75% average is broad-based, not an outlier-driven artifact.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "h5_gap_diagnosis_20260831_093649.txt"
    out_path.write_text(
        f"h5 gap diagnosis -- {datetime.now().isoformat()}\n"
        f"n={n} avg_ret={avg_ret:+.3f}% win_rate={win_rate:.1f}%\n"
        f"Worst week: {worst_week[0]} ({week_concentration:.1f}% of negative return)\n"
        f"Worst 5 symbols: {symbol_concentration:.1f}% of negative return\n",
        encoding="utf-8",
    )
    print(f"\nSummary also written to {out_path}")

    done_path = Path(__file__).with_suffix(".done")
    done_path.write_text(f"PASS\n0\n{datetime.now().isoformat()}\n", encoding="utf-8")
    print("PASS")


if __name__ == "__main__":
    main()
