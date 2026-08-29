"""
P_025 Diagnostics — Read-only inspection of the live P_020 database.

Self-contained PEH-style verifier.
Run with:  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe diagnostics.py

Prints PASS only when every critical check succeeds.
Never writes to the database or to the portfolio workbook.
"""

from __future__ import annotations

import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Make the project importable when run from any working directory
# ---------------------------------------------------------------------------
PROJECT_PYTHON = Path(__file__).resolve().parent
if str(PROJECT_PYTHON) not in sys.path:
    sys.path.insert(0, str(PROJECT_PYTHON))

from config import (
    ACCOUNT_AJZ6348,
    ACCOUNT_IRA9885,
    IRA_FEED_READY,
    P020_DB_PATH,
    PRIMARY_ACCOUNTS,
)
from infrastructure.p020_reader import read_trades
from schemas import TradeRecord


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def _ok(msg: str) -> None:
    print(f"  OK  {msg}")


def check_db_exists() -> None:
    print("\n=== 1. Database presence ===")
    print(f"  Path : {P020_DB_PATH}")
    if not P020_DB_PATH.exists():
        _fail(f"Database file does not exist at {P020_DB_PATH}")
    size_kb = P020_DB_PATH.stat().st_size / 1024
    _ok(f"File exists ({size_kb:.1f} KB)")


def check_schema() -> dict[str, int]:
    print("\n=== 2. Schema / row counts ===")
    expected_tables = {
        "trades",
        "exits",
        "v_trade_summary",
        "account_balances",
        "accounts",
        "systems",
        "spread_legs",
    }
    counts: dict[str, int] = {}
    try:
        with sqlite3.connect(P020_DB_PATH) as conn:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"
            )
            found = {row[0] for row in cur.fetchall()}
            missing = expected_tables - found
            if missing:
                _fail(f"Missing expected tables/views: {sorted(missing)}")
            _ok(f"All expected tables/views present ({len(found)} total objects)")

            for name in sorted(expected_tables):
                try:
                    n = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
                    counts[name] = n
                    print(f"       {name:20s} {n:6d} rows")
                except sqlite3.Error as exc:
                    _fail(f"Could not count {name}: {exc}")
    except sqlite3.Error as exc:
        _fail(f"SQLite error opening database: {exc}")
    return counts


def check_reader() -> list[TradeRecord]:
    print("\n=== 3. p020_reader.read_trades() ===")
    print(f"  IRA_FEED_READY = {IRA_FEED_READY}")
    print(f"  PRIMARY_ACCOUNTS = {PRIMARY_ACCOUNTS}")

    trades = read_trades(
        db_path=P020_DB_PATH,
        account_ids=PRIMARY_ACCOUNTS,
        ira_feed_ready=IRA_FEED_READY,
    )
    if not isinstance(trades, list):
        _fail("read_trades did not return a list")
    _ok(f"Loaded {len(trades)} TradeRecord objects")

    if trades and not all(isinstance(t, TradeRecord) for t in trades):
        _fail("One or more items are not TradeRecord instances")
    _ok("All items are valid TradeRecord instances")
    return trades


def check_account_breakdown(trades: list[TradeRecord]) -> None:
    print("\n=== 4. Account breakdown ===")
    counts = Counter(t.account_id for t in trades)
    for acct, n in sorted(counts.items()):
        print(f"       {acct:15s} {n:5d} trades")

    if ACCOUNT_AJZ6348 not in counts:
        print("  WARN AJZ6348 has zero trades in this pull (unexpected)")
    else:
        _ok(f"{ACCOUNT_AJZ6348} present ({counts[ACCOUNT_AJZ6348]} trades)")

    if IRA_FEED_READY:
        if ACCOUNT_IRA9885 not in counts:
            _fail(f"{ACCOUNT_IRA9885} expected but missing while IRA_FEED_READY=True")
        _ok(f"{ACCOUNT_IRA9885} present ({counts[ACCOUNT_IRA9885]} trades)")
    else:
        if ACCOUNT_IRA9885 in counts:
            print(f"  WARN {ACCOUNT_IRA9885} appeared even though IRA_FEED_READY=False")
        else:
            _ok(f"{ACCOUNT_IRA9885} correctly excluded (IRA_FEED_READY=False)")


def check_date_range_and_symbols(trades: list[TradeRecord]) -> None:
    print("\n=== 5. Date range & symbols ===")
    if not trades:
        print("  (no trades — skipping)")
        return

    dates = [t.open_date for t in trades if t.open_date]
    if not dates:
        _fail("No open_date values found on any trade")
    print(f"       Earliest open_date : {min(dates)}")
    print(f"       Latest   open_date : {max(dates)}")
    _ok("Date range extracted")

    symbols = sorted({t.underlying_symbol for t in trades})
    print(f"       Unique symbols     : {len(symbols)}")
    print(f"       Sample             : {symbols[:12]}")
    _ok("Symbol list extracted")


def check_critical_fields(trades: list[TradeRecord]) -> None:
    print("\n=== 6. Critical field sanity ===")
    if not trades:
        print("  (no trades — skipping)")
        return

    missing_qty = sum(1 for t in trades if t.qty is None or t.qty == 0)
    missing_price = sum(1 for t in trades if t.entry_price is None or t.entry_price == 0)
    bad_status = sum(1 for t in trades if t.status not in {"open", "partial", "closed"})

    if missing_qty:
        print(f"  WARN {missing_qty} trades have qty == 0 or None")
    else:
        _ok("All trades have non-zero qty")

    if missing_price:
        print(f"  WARN {missing_price} trades have entry_price == 0 or None")
    else:
        _ok("All trades have non-zero entry_price")

    if bad_status:
        _fail(f"{bad_status} trades have invalid status values")
    else:
        _ok("All status values are valid")


def main() -> int:
    print("=" * 60)
    print("P_025 Diagnostics — P_020 live database inspection")
    print("=" * 60)

    try:
        check_db_exists()
        counts = check_schema()
        trades = check_reader()
        check_account_breakdown(trades)
        check_date_range_and_symbols(trades)
        check_critical_fields(trades)
    except Exception as exc:
        _fail(f"Unhandled exception: {type(exc).__name__}: {exc}")

    print("\n" + "=" * 60)
    print("PASS")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
