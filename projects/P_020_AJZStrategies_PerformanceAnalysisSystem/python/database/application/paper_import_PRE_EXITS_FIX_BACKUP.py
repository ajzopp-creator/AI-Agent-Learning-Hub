"""
paper_import.py - Application layer.

Imports paper trades into SQLite, joining each trade to a ThinkLog entry
on (Symbol, Date). Tag string [WHY] [SIG] is parsed from the ThinkLog body
and stored in trades.reason / trades.signal_strength columns.

Inputs:
    --account-statement   TOS Account Statement CSV (raw export)
    --thinklog            TOS ThinkLog CSV (raw export, optional)

The Account Statement CSV is run through the archived TOS parser (or
already-produced _STOCKS_IMPORT.csv / _OPTIONS_IMPORT.csv files) to get
clean trade rows. ThinkLog is joined onto those rows by Symbol + Date.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application

Tag format expected in ThinkLog body's first line:
    MMDD: [WHY] [SIG] free text
    e.g. "0427: [SNT] [A] clean breakout"

Body without brackets parses safely with reason=None, signal_strength=None,
and the full body preserved in notes.

Usage:
    python paper_import.py \\
        --options OPTIONS_CSV --stocks STOCKS_CSV \\
        --thinklog THINKLOG_CSV [--commit]

Run without --commit for a preview. Add --commit to actually write to DB.
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from domain.thinklog_parser import parse_thinklog_note  # noqa: E402
from infrastructure.thinklog_reader import (  # noqa: E402
    read_thinklog_csv, build_lookup, get_body_for_trade,
)

DB_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)
PAPER_ACCOUNT_ID = "PAPER"
SOURCE_TAG = "tos_paper_csv"
DEFAULT_SYSTEM = "TOS_Import"


# ---------- CSV reading ----------

def _parse_trade_date(s: str) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _to_float(s) -> Optional[float]:
    if s is None or s == "":
        return None
    try:
        return float(str(s).replace(",", "").replace("$", "").strip())
    except ValueError:
        return None


def _clean_system(s: Optional[str]) -> str:
    if not s or not s.strip():
        return DEFAULT_SYSTEM
    return s.strip()


def read_options_csv(path: Path) -> List[Dict]:
    trades = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = (row.get("Symbol") or "").strip().upper()
            if not symbol:
                continue
            trade_type = (row.get("Trade Type") or "").strip().lower()
            asset_type = trade_type if trade_type in ("call", "put") else "call"
            direction = "long" if (row.get("Long/Short") or "").strip().lower() == "long" else "short"
            trades.append({
                "account_id": PAPER_ACCOUNT_ID,
                "system": _clean_system(row.get("System")),
                "underlying_symbol": symbol,
                "asset_type": asset_type,
                "direction": direction,
                "open_date": _parse_trade_date(row.get("Trade Date", "")),
                "qty": _to_float(row.get("Contracts")),
                "entry_price": _to_float(row.get("Entry $$")),
                "total_commissions": _to_float(row.get("Comm.")),
                "status": "closed",
                "notes": (row.get("Trade Comments") or "").strip() or None,
                "source": SOURCE_TAG,
                "reason": None,
                "signal_strength": None,
            })
    return trades


def read_stocks_csv(path: Path) -> List[Dict]:
    trades = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol = (row.get("Symbol") or "").strip().upper()
            if not symbol:
                continue
            ls = (row.get("Long/Short") or "").strip().lower()
            direction = "long" if ls == "long" else "short"
            trades.append({
                "account_id": PAPER_ACCOUNT_ID,
                "system": _clean_system(row.get("System")),
                "underlying_symbol": symbol,
                "asset_type": "stock",
                "direction": direction,
                "open_date": _parse_trade_date(row.get("Trade Date", "")),
                "qty": _to_float(row.get("Shares")),
                "entry_price": _to_float(row.get("Entry Price")),
                "total_commissions": _to_float(row.get("Comm.")),
                "status": "closed",
                "notes": (row.get("Trade Comments") or "").strip() or None,
                "source": SOURCE_TAG,
                "reason": None,
                "signal_strength": None,
            })
    return trades


# ---------- ThinkLog join + tag parsing ----------

def join_thinklog(trades: List[Dict], thinklog_path: Optional[Path]) -> Dict:
    """
    For each trade, look up ThinkLog body by (symbol, open_date) and parse
    [WHY] [SIG] tags out of it. Returns stats dict: {matched, unmatched,
    tagged, thinklog_total, thinklog_in_range}.

    Auto-filters ThinkLog to entries within +/- 3 days of the trade date
    range to keep the lookup tight as the ThinkLog file grows over time.
    """
    stats = {
        "matched": 0, "unmatched": 0, "tagged": 0,
        "thinklog_total": 0, "thinklog_in_range": 0,
    }
    if not thinklog_path or not thinklog_path.exists():
        stats["unmatched"] = len(trades)
        return stats

    all_records = read_thinklog_csv(thinklog_path)
    stats["thinklog_total"] = len(all_records)

    # Determine trade date range and filter ThinkLog records to within +/- 3 days
    trade_dates = [
        date.fromisoformat(t["open_date"])
        for t in trades if t.get("open_date")
    ]
    if trade_dates:
        from datetime import timedelta
        min_d = min(trade_dates) - timedelta(days=3)
        max_d = max(trade_dates) + timedelta(days=3)
        records = [r for r in all_records if min_d <= r["date"] <= max_d]
    else:
        records = all_records
    stats["thinklog_in_range"] = len(records)

    lookup = build_lookup(records)

    for t in trades:
        body = get_body_for_trade(lookup, t["underlying_symbol"], t["open_date"])
        if body is None:
            stats["unmatched"] += 1
            continue
        stats["matched"] += 1

        parsed = parse_thinklog_note(body)
        if parsed["reason"]:
            t["reason"] = parsed["reason"]
            stats["tagged"] += 1
        if parsed["signal_strength"]:
            t["signal_strength"] = parsed["signal_strength"]

        thinklog_notes = parsed["notes"] or body
        existing = (t.get("notes") or "").strip()
        if existing:
            t["notes"] = f"{existing} | {thinklog_notes}"
        else:
            t["notes"] = thinklog_notes

    return stats


# ---------- DB write ----------

def _trades_schema(conn: sqlite3.Connection) -> List[str]:
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(trades)")
    return [row[1] for row in cur.fetchall()]


def _is_duplicate(conn: sqlite3.Connection, t: Dict) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM trades WHERE account_id=? AND underlying_symbol=? "
        "AND open_date=? AND entry_price=? AND source=? LIMIT 1",
        (t["account_id"], t["underlying_symbol"], t["open_date"],
         t["entry_price"], t["source"]),
    )
    return cur.fetchone() is not None


def write_trades(trades: List[Dict], db_path: Path = DB_PATH) -> Dict:
    stats = {"inserted": 0, "skipped_dup": 0, "errors": 0}
    if not trades:
        return stats

    conn = sqlite3.connect(db_path)
    try:
        schema_cols = set(_trades_schema(conn))
        for t in trades:
            try:
                if _is_duplicate(conn, t):
                    stats["skipped_dup"] += 1
                    continue
                cols = [k for k in t.keys() if k in schema_cols]
                if not cols:
                    stats["errors"] += 1
                    continue
                placeholders = ",".join("?" for _ in cols)
                col_list = ",".join(cols)
                values = [t[k] for k in cols]
                conn.execute(
                    f"INSERT INTO trades ({col_list}) VALUES ({placeholders})",
                    values,
                )
                stats["inserted"] += 1
            except sqlite3.Error:
                stats["errors"] += 1
        conn.commit()
    finally:
        conn.close()
    return stats


# ---------- Preview & CLI ----------

def print_preview(trades: List[Dict], join_stats: Dict) -> None:
    print(f"\n{'Date':<11} {'Symbol':<8} {'Sys':<11} {'Reason':<10} "
          f"{'Sig':<4} {'Qty':>6} {'Entry':>8}")
    print("-" * 70)
    for t in trades:
        print(f"{(t.get('open_date') or '-'):<11} "
              f"{(t.get('underlying_symbol') or '-'):<8} "
              f"{(t.get('system') or '-'):<11} "
              f"{(t.get('reason') or '-'):<10} "
              f"{(t.get('signal_strength') or '-'):<4} "
              f"{(t.get('qty') or 0):>6} "
              f"{(t.get('entry_price') or 0):>8}")
    print(f"\nTotal trades: {len(trades)}")
    if join_stats.get("thinklog_total", 0) > 0:
        print(f"ThinkLog entries: {join_stats['thinklog_total']} total, "
              f"{join_stats['thinklog_in_range']} in trade date range")
    print(f"ThinkLog matched:   {join_stats['matched']}")
    print(f"ThinkLog unmatched: {join_stats['unmatched']}")
    print(f"Tags extracted:     {join_stats['tagged']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Import paper trades with ThinkLog enrichment")
    ap.add_argument("--options", type=Path, help="Path to _OPTIONS_IMPORT.csv")
    ap.add_argument("--stocks", type=Path, help="Path to _STOCKS_IMPORT.csv")
    ap.add_argument("--thinklog", type=Path, help="Path to TOS ThinkLog CSV export")
    ap.add_argument("--commit", action="store_true", help="Write to DB (default = dry run)")
    ap.add_argument("--dry-run", action="store_true", help="Preview only, do not write")
    args = ap.parse_args()

    if not args.options and not args.stocks:
        ap.error("Provide --options and/or --stocks")

    trades: List[Dict] = []
    if args.options:
        if not args.options.exists():
            print(f"ERROR: {args.options} not found"); return 1
        trades.extend(read_options_csv(args.options))
    if args.stocks:
        if not args.stocks.exists():
            print(f"ERROR: {args.stocks} not found"); return 1
        trades.extend(read_stocks_csv(args.stocks))

    join_stats = join_thinklog(trades, args.thinklog)
    print_preview(trades, join_stats)

    if args.commit and not args.dry_run:
        stats = write_trades(trades)
        print(f"\nDB write: inserted={stats['inserted']} "
              f"skipped_dup={stats['skipped_dup']} errors={stats['errors']}")
    else:
        print("\nDry run - no DB writes. Add --commit to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
