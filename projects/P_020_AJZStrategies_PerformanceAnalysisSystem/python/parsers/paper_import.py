"""
paper_import.py
Reads TOS parser output CSVs (OPTIONS_IMPORT + STOCKS_IMPORT) for the
PaperMoney account and loads them into the P_020 SQLite DB under
account_id = 'PAPER'.

Runs the same Tracker Dashboard matching as the live pipeline — 90% of
paper trades are logged in the Tracker, so most will get proper system
names (P_115, P_118, etc.) rather than the TOS_Import fallback.

Usage:
    python paper_import.py --options <path> --stocks <path>
    python paper_import.py  # auto-finds latest files in tos_exports/paper/
"""

import argparse
import csv
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH      = PROJECT_ROOT / "data" / "database" / "P_020_trades.db"
PAPER_DIR    = PROJECT_ROOT / "data" / "tos_exports" / "paper"
DB_SRC       = PROJECT_ROOT / "python" / "database"

# Add database layer to path so we can reuse tracker_reader + matcher
if str(DB_SRC) not in sys.path:
    sys.path.insert(0, str(DB_SRC))

from infrastructure.tracker_reader import load_tracker_lookup
from domain.matcher import match_system

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

ACCOUNT_ID = "PAPER"

# ── Date parsing ───────────────────────────────────────────────────────────

def parse_date(val: str) -> str:
    """Convert M/D/YY or M/D/YYYY to YYYY-MM-DD. Returns '' if blank."""
    val = (val or "").strip()
    if not val:
        return ""
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(val, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    log.warning(f"Could not parse date: {val}")
    return val


def safe_float(val: str) -> float:
    try:
        return float((val or "").strip())
    except (ValueError, TypeError):
        return 0.0


def synthetic_id(symbol: str, open_date: str, entry_price: float,
                 qty: float, suffix: str = "") -> str:
    """Generate a dedup key for paper trades (no Schwab transaction ID)."""
    return f"PAPER_{symbol}_{open_date}_{entry_price}_{qty}{suffix}"


# ── DB helpers ─────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    if not DB_PATH.exists():
        log.error(f"Database not found: {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_paper_account(conn: sqlite3.Connection) -> None:
    """Insert PAPER account row if it doesn't exist."""
    exists = conn.execute(
        "SELECT 1 FROM accounts WHERE account_id = ?", (ACCOUNT_ID,)
    ).fetchone()
    if not exists:
        conn.execute(
            "INSERT INTO accounts (account_id, account_name, account_type, broker) "
            "VALUES (?, ?, ?, ?)",
            (ACCOUNT_ID, "TOS PaperMoney D-68748525", "paper", "thinkorswim"),
        )
        conn.commit()
        log.info("PAPER account row created in accounts table.")


def already_imported(conn: sqlite3.Connection, txn_id: str) -> bool:
    return bool(
        conn.execute(
            "SELECT 1 FROM trades WHERE schwab_transaction_id = ?", (txn_id,)
        ).fetchone()
    )


def insert_trade_row(conn: sqlite3.Connection, t: dict) -> int:
    cur = conn.execute(
        """INSERT INTO trades
           (account_id, system, underlying_symbol, asset_type, direction,
            open_date, qty, entry_price, total_commissions, status,
            source, schwab_transaction_id, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            t["account_id"], t["system"], t["underlying_symbol"],
            t["asset_type"], t["direction"], t["open_date"],
            t["qty"], t["entry_price"], t["total_commissions"],
            t["status"], t["source"], t["schwab_transaction_id"],
            t.get("notes", ""),
        ),
    )
    return cur.lastrowid


def insert_exit_row(conn: sqlite3.Connection, trade_id: int, e: dict) -> None:
    conn.execute(
        """INSERT INTO exits
           (trade_id, exit_number, exit_date, qty_exited,
            exit_price, exit_commissions, exit_pnl, hold_days)
           VALUES (?,?,?,?,?,?,?,?)""",
        (
            trade_id, e["exit_number"], e["exit_date"],
            e["qty_exited"], e["exit_price"], 0.0,
            e["exit_pnl"], e["hold_days"],
        ),
    )


# ── Status / P&L helpers ───────────────────────────────────────────────────

def determine_status(qty_total: float, qty_exited: float) -> str:
    if qty_exited <= 0:
        return "open"
    if qty_exited >= qty_total:
        return "closed"
    return "partial"


def calc_pnl(direction: str, entry: float, exit_price: float,
             qty: float, multiplier: float) -> float:
    if direction == "long":
        return round((exit_price - entry) * qty * multiplier, 2)
    else:
        return round((entry - exit_price) * qty * multiplier, 2)


# ── Exit parser ────────────────────────────────────────────────────────────

def parse_exits(row: dict, entry_price: float, direction: str,
                multiplier: float) -> list:
    """Extract up to 3 exits from a CSV row dict. Handles both option and
    stock column layouts automatically."""
    if "Exit #1 $" in row:
        # Options layout
        slots = [
            ("Exit #1 $",  "# Exited",  "Exit Date",  "# of Days"),
            ("Exit #2 $",  "# Exited2", "Exit Date3", "# of Days4"),
            ("Exit #3 $",  "# Exited5", "Exit Date6", "# of Days7"),
        ]
    else:
        # Stocks layout
        slots = [
            ("Exit #1",    "# Exited",  "Exit Date",  "# of Days"),
            ("Exit #2",    "# Exited2", "Exit Date3", "# of Days4"),
        ]

    exits = []
    for i, (ep_col, qty_col, dt_col, days_col) in enumerate(slots, start=1):
        ep_raw  = (row.get(ep_col)  or "").strip()
        qty_raw = (row.get(qty_col) or "").strip()
        dt_raw  = (row.get(dt_col)  or "").strip()
        if not ep_raw or not qty_raw or not dt_raw:
            continue
        ep   = safe_float(ep_raw)
        qty  = safe_float(qty_raw)
        dt   = parse_date(dt_raw)
        days = int(safe_float(row.get(days_col, "0")))
        if ep <= 0 or qty <= 0:
            continue
        exits.append({
            "exit_number": i,
            "exit_date":   dt,
            "exit_price":  ep,
            "qty_exited":  qty,
            "hold_days":   days,
            "exit_pnl":    calc_pnl(direction, entry_price, ep, qty, multiplier),
        })
    return exits


# ── Import options ─────────────────────────────────────────────────────────

def import_options(conn: sqlite3.Connection, csv_path: Path,
                   lookup) -> tuple:
    inserted = skipped = matched = unmatched = 0

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol     = (row.get("Symbol") or "").strip().upper()
            asset_type = (row.get("Trade Type") or "call").strip().lower()
            direction  = (row.get("Long/Short") or "long").strip().lower()
            open_date  = parse_date(row.get("Trade Date", ""))
            entry      = safe_float(row.get("Entry $$", "0"))
            qty        = safe_float(row.get("Contracts", "0"))
            comm       = safe_float(row.get("Comm.", "0"))
            strike     = safe_float(row.get("Strike", "0"))

            if not symbol or not open_date or qty <= 0:
                continue

            txn_id = synthetic_id(symbol, open_date, entry, qty,
                                  f"_{asset_type}")
            if already_imported(conn, txn_id):
                skipped += 1
                continue

            # Tracker Dashboard matching — same logic as live pipeline
            system = match_system(symbol=symbol, open_date=open_date, lookup=lookup)
            if system != "TOS_Import":
                matched += 1
            else:
                unmatched += 1

            exits      = parse_exits(row, entry, direction, multiplier=100.0)
            qty_exited = sum(e["qty_exited"] for e in exits)
            status     = determine_status(qty, qty_exited)

            trade = {
                "account_id":            ACCOUNT_ID,
                "system":                system,
                "underlying_symbol":     symbol,
                "asset_type":            asset_type,
                "direction":             direction,
                "open_date":             open_date,
                "qty":                   qty,
                "entry_price":           entry,
                "total_commissions":     comm,
                "status":                status,
                "source":                "tos_import",
                "schwab_transaction_id": txn_id,
                "notes":                 f"Strike: {strike}" if strike else "",
            }

            trade_id = insert_trade_row(conn, trade)
            for e in exits:
                insert_exit_row(conn, trade_id, e)
            inserted += 1

    return inserted, skipped, matched, unmatched


# ── Import stocks ──────────────────────────────────────────────────────────

def import_stocks(conn: sqlite3.Connection, csv_path: Path,
                  lookup) -> tuple:
    inserted = skipped = matched = unmatched = 0

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            symbol    = (row.get("Symbol") or "").strip().upper()
            direction = (row.get("Long/Short") or "long").strip().lower()
            open_date = parse_date(row.get("Trade Date", ""))
            entry     = safe_float(row.get("Entry Price", "0"))
            qty       = safe_float(row.get("Shares", "0"))
            comm      = safe_float(row.get("Comm.", "0"))

            if not symbol or not open_date or qty <= 0:
                continue

            txn_id = synthetic_id(symbol, open_date, entry, qty, "_stock")
            if already_imported(conn, txn_id):
                skipped += 1
                continue

            # Tracker Dashboard matching — same logic as live pipeline
            system = match_system(symbol=symbol, open_date=open_date, lookup=lookup)
            if system != "TOS_Import":
                matched += 1
            else:
                unmatched += 1

            exits      = parse_exits(row, entry, direction, multiplier=1.0)
            qty_exited = sum(e["qty_exited"] for e in exits)
            status     = determine_status(qty, qty_exited)

            trade = {
                "account_id":            ACCOUNT_ID,
                "system":                system,
                "underlying_symbol":     symbol,
                "asset_type":            "stock",
                "direction":             direction,
                "open_date":             open_date,
                "qty":                   qty,
                "entry_price":           entry,
                "total_commissions":     comm,
                "status":                status,
                "source":                "tos_import",
                "schwab_transaction_id": txn_id,
                "notes":                 "",
            }

            trade_id = insert_trade_row(conn, trade)
            for e in exits:
                insert_exit_row(conn, trade_id, e)
            inserted += 1

    return inserted, skipped, matched, unmatched


# ── Auto-find latest files ─────────────────────────────────────────────────

def find_latest(suffix: str) -> Path | None:
    files = sorted(PAPER_DIR.glob(f"*{suffix}"),
                   key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Import TOS paper trades into P_020 SQLite DB")
    parser.add_argument("--options", default=None,
                        help="Path to OPTIONS_IMPORT.csv")
    parser.add_argument("--stocks",  default=None,
                        help="Path to STOCKS_IMPORT.csv")
    args = parser.parse_args()

    options_path = (Path(args.options) if args.options
                    else find_latest("_OPTIONS_IMPORT.csv"))
    stocks_path  = (Path(args.stocks)  if args.stocks
                    else find_latest("_STOCKS_IMPORT.csv"))

    if not options_path or not options_path.exists():
        log.error(f"OPTIONS_IMPORT file not found: {options_path}")
        sys.exit(1)
    if not stocks_path or not stocks_path.exists():
        log.error(f"STOCKS_IMPORT file not found: {stocks_path}")
        sys.exit(1)

    log.info(f"Options file : {options_path.name}")
    log.info(f"Stocks file  : {stocks_path.name}")
    log.info(f"Database     : {DB_PATH}")

    # Load Tracker Dashboard once — reused for both options and stocks
    log.info("Loading Tracker Dashboard for system name matching...")
    lookup = load_tracker_lookup()
    if lookup:
        log.info(f"Tracker loaded — {lookup.traded_rows} traded entries available for matching.")
    else:
        log.warning("Tracker Dashboard unavailable — all trades will default to TOS_Import.")

    conn = get_conn()
    ensure_paper_account(conn)

    print("\nImporting options trades...")
    o_ins, o_skip, o_match, o_unmatch = import_options(conn, options_path, lookup)
    print(f"  Inserted : {o_ins}  |  Skipped (already in DB): {o_skip}")
    print(f"  Matched  : {o_match} system names from Tracker  |  TOS_Import fallback: {o_unmatch}")

    print("\nImporting stock trades...")
    s_ins, s_skip, s_match, s_unmatch = import_stocks(conn, stocks_path, lookup)
    print(f"  Inserted : {s_ins}  |  Skipped (already in DB): {s_skip}")
    print(f"  Matched  : {s_match} system names from Tracker  |  TOS_Import fallback: {s_unmatch}")

    conn.commit()
    conn.close()

    total     = o_ins + s_ins
    total_match = o_match + s_match
    total_unmatch = o_unmatch + s_unmatch

    print(f"\n{'='*55}")
    print(f"PAPER import complete — {total} trades added to DB")
    print(f"  Options  : {o_ins} inserted, {o_skip} skipped")
    print(f"  Stocks   : {s_ins} inserted, {s_skip} skipped")
    print(f"  System match rate: {total_match}/{total} "
          f"({round(100*total_match/total if total else 0, 1)}%) from Tracker")
    print(f"  TOS_Import fallback: {total_unmatch} trades")
    print(f"{'='*55}")
    print("\nNext: run stats_export.py --account PAPER for paper analysis CSVs.")


if __name__ == "__main__":
    main()

