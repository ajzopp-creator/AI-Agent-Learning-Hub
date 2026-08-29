"""
paper_import.py -- Application layer (orchestration only).

Reads options/stocks CSVs via infrastructure/paper_csv_reader.py, joins
ThinkLog tags, previews, and writes via application/paper_writer.py.
Optionally also detects and imports multi-leg spread trades from the raw
AccountStatement.csv in the same run (--raw-csv, WO-P020-E1.002) -- the
options/stocks IMPORT CSVs never contain spread data since the old TOS
parser drops CUSTOM/multi-leg lines before that stage, so spreads must
be read from the raw statement directly.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\paper_import.py

Usage:
    python paper_import.py --options OPTIONS_CSV --stocks STOCKS_CSV \\
        --thinklog THINKLOG_CSV --raw-csv RAW_ACCOUNTSTATEMENT_CSV [--commit]

Run without --commit for a preview. Add --commit to actually write to DB.
--raw-csv is optional -- omit it to import single-leg trades only, exactly
as before this option existed.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from domain.thinklog_parser import parse_thinklog_note  # noqa: E402
from infrastructure.thinklog_reader import (  # noqa: E402
    read_thinklog_csv, build_lookup, get_body_for_trade,
)
from infrastructure.paper_csv_reader import read_options_csv, read_stocks_csv  # noqa: E402
from paper_writer import write_trades  # noqa: E402


def join_thinklog(trades: List[Dict], thinklog_path: Optional[Path]) -> Dict:
    """Look up ThinkLog body by (symbol, open_date), parse [WHY] [SIG]
    tags into each trade dict. Returns join stats."""
    stats = {"matched": 0, "unmatched": 0, "tagged": 0,
              "thinklog_total": 0, "thinklog_in_range": 0}
    if not thinklog_path or not thinklog_path.exists():
        stats["unmatched"] = len(trades)
        return stats

    all_records = read_thinklog_csv(thinklog_path)
    stats["thinklog_total"] = len(all_records)

    trade_dates = [date.fromisoformat(t["open_date"]) for t in trades if t.get("open_date")]
    if trade_dates:
        min_d, max_d = min(trade_dates) - timedelta(days=3), max(trade_dates) + timedelta(days=3)
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
        t["notes"] = f"{existing} | {thinklog_notes}" if existing else thinklog_notes
    return stats


def print_preview(trades: List[Dict], join_stats: Dict) -> None:
    print(f"\n{'Date':<11} {'Symbol':<8} {'Sys':<11} {'Status':<8} {'Reason':<10} "
          f"{'Sig':<4} {'Qty':>6} {'Entry':>8} {'Exits':>6}")
    print("-" * 80)
    for t in trades:
        print(f"{(t.get('open_date') or '-'):<11} "
              f"{(t.get('underlying_symbol') or '-'):<8} "
              f"{(t.get('system') or '-'):<11} "
              f"{(t.get('status') or '-'):<8} "
              f"{(t.get('reason') or '-'):<10} "
              f"{(t.get('signal_strength') or '-'):<4} "
              f"{(t.get('qty') or 0):>6} "
              f"{(t.get('entry_price') or 0):>8} "
              f"{len(t.get('_exits', [])):>6}")
    print(f"\nTotal trades: {len(trades)}")
    if join_stats.get("thinklog_total", 0) > 0:
        print(f"ThinkLog entries: {join_stats['thinklog_total']} total, "
              f"{join_stats['thinklog_in_range']} in trade date range")
    print(f"ThinkLog matched:   {join_stats['matched']}")
    print(f"ThinkLog unmatched: {join_stats['unmatched']}")
    print(f"Tags extracted:     {join_stats['tagged']}")


def run_spread_import(raw_csv: Path, commit: bool) -> Dict:
    """Detect and import multi-leg spread trades from the raw
    AccountStatement.csv (WO-P020-E1.002). Separate DB connection from
    write_trades()'s internal one -- same pattern paper_spread_import.py's
    own CLI already uses.

    Args:
        raw_csv: Path to the raw (unparsed) AccountStatement.csv.
        commit: Write to DB if True, dry-run preview only if False.

    Returns:
        {"found": int, "imported": int} from import_spreads().
    """
    from infrastructure.db_client import get_connection
    from paper_spread_import import import_spreads

    if not raw_csv.exists():
        print(f"ERROR: {raw_csv} not found -- skipping spread detection")
        return {"found": 0, "imported": 0}

    conn = get_connection()
    try:
        return import_spreads(conn, raw_csv, commit=commit, verbose=True)
    finally:
        conn.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Import paper trades with ThinkLog enrichment")
    ap.add_argument("--options", type=Path, help="Path to _OPTIONS_IMPORT.csv")
    ap.add_argument("--stocks", type=Path, help="Path to _STOCKS_IMPORT.csv")
    ap.add_argument("--thinklog", type=Path, help="Path to TOS ThinkLog CSV export")
    ap.add_argument("--raw-csv", type=Path, default=None,
                     help="Path to the raw AccountStatement.csv -- catches multi-leg "
                          "spread trades the options/stocks IMPORT CSVs never contain "
                          "(WO-P020-E1.002). Omit to import single-leg trades only.")
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

    do_commit = args.commit and not args.dry_run

    if do_commit:
        stats = write_trades(trades)
        print(f"\nDB write: inserted={stats['inserted']} skipped_dup={stats['skipped_dup']} "
              f"errors={stats['errors']} exits_inserted={stats['exits_inserted']}")
    else:
        print("\nDry run - no DB writes. Add --commit to write.")

    if args.raw_csv:
        spread_stats = run_spread_import(args.raw_csv, commit=do_commit)
        print(f"\nSpread detection: {spread_stats['found']} found, "
              f"{spread_stats['imported']} imported")

    return 0


if __name__ == "__main__":
    sys.exit(main())
