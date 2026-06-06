"""P_020 Trade Manager — command-line entry point for all database operations."""

import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Optional

from config import API_PULLS_DIR, DATABASE_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Database setup commands ────────────────────────────────────────────────

def cmd_init_db(args: argparse.Namespace) -> None:
    """Create database, all tables, view, and load seed data."""
    from infrastructure.db_client import initialize_database
    from infrastructure.db_seeder import seed_all
    logger.info("Initializing P_020 database...")
    conn = initialize_database()
    seed_all(conn)
    conn.close()
    logger.info(f"Done. Database ready at: {DATABASE_FILE}")


def cmd_verify(args: argparse.Namespace) -> None:
    """Verify database exists and print row counts for all tables."""
    if not DATABASE_FILE.exists():
        logger.error(f"Database not found: {DATABASE_FILE}")
        logger.error("Fix: run  python P_020_Trade_Manager.py init-db")
        sys.exit(1)

    conn = sqlite3.connect(str(DATABASE_FILE))
    tables = ["accounts", "systems", "trades", "exits"]

    print("\nP_020 Database Verification")
    print("=" * 45)
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<25} {count:>5} rows")

    view = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='view' AND name='v_trade_summary'"
    ).fetchone()
    status = "exists" if view else "MISSING — re-run init-db"
    print(f"  {'v_trade_summary (view)':<25} {status}")
    print("=" * 45)
    conn.close()


# ── Import command — pull latest Schwab data into database ─────────────────

def cmd_import(args: argparse.Namespace) -> None:
    """Map latest Schwab pull file and import into database.

    Reads the most recent pull JSON for the account, maps Schwab
    transactions to trade dicts, matches system names via Tracker
    Dashboard, writes to SQLite, and exports Power Query CSVs.
    """
    from application.ingest_pipeline import run_ingest
    from infrastructure.csv_exporter import export_all
    from infrastructure.db_client import get_connection
    from infrastructure.schwab_mapper import map_pull_file


    # Handle date override: --start and --end wipe DB and re-import full range
    if args.start or args.end:
        if not (args.start and args.end):
            logger.error("Both --start and --end are required for date override.")
            sys.exit(1)
        logger.info(f"Date override: {args.start} to {args.end} -- wiping existing trades.")
        wipe_conn = get_connection()
        wipe_conn.execute("DELETE FROM exits")
        wipe_conn.execute("DELETE FROM trades")
        wipe_conn.commit()
        wipe_conn.close()
        logger.info("Database wiped. Re-importing...")

        # Find pull file covering that range
        if not args.file:
            pull_path = _find_latest_pull(args.account)
            logger.info(f"Using latest pull file (ensure it covers {args.start} to {args.end})")

    # Determine pull file — use --file arg or find latest in api_pulls
    if args.file:
        pull_path = Path(args.file)
    else:
        pull_path = _find_latest_pull(args.account)

    if not pull_path or not pull_path.exists():
        logger.error(
            f"No pull file found for account '{args.account}'. "
            f"Run P_020_Schwab_Trade_Pull.py first."
        )
        sys.exit(1)

    logger.info(f"Using pull file: {pull_path.name}")

    # Map Schwab JSON → trade dicts
    account_label, trade_dicts = map_pull_file(pull_path)

    if not trade_dicts:
        logger.info("No trades to import from this pull file.")
        print("\nNothing to import — no OPENING transactions found in pull file.")
        return

    account_id = _resolve_account_id(args.account, account_label)
    logger.info(f"Importing {len(trade_dicts)} trades for account: {account_id}")

    inserted, skipped, orphans = run_ingest(
        raw_trades=trade_dicts,
        account_id=account_id,
        save_run_date=not args.dry_run,
    )

    print(f"\nImport complete — inserted: {inserted}  skipped: {skipped}  orphans: {orphans}")

    # Auto-export CSVs after successful import
    if inserted > 0 and not args.no_export:
        logger.info("Running CSV export...")
        conn = get_connection()
        export_all(conn)
        conn.close()
        print("Export complete — Power Query files updated.")

    print(f"\nAudit log: audit_logs\\")


# ── Export command — Power Query CSV files ─────────────────────────────────


def cmd_balance(args) -> None:
    """Pull current Schwab account balance and store as weekly snapshot."""
    from infrastructure.db_client import get_connection
    from infrastructure.schwab_balance_pull import get_account_hash, pull_balance, store_balance

    account_map = {"AJZ": ("AJZ6348", "6348"), "IRA": ("IRA9885", "9885")}
    account_id, last4 = account_map.get(args.account.upper(), ("AJZ6348", "6348"))

    logger.info(f"Pulling balance for account: {account_id}")

    # Look up encrypted hash required by Schwab API
    account_hash = get_account_hash(last4)
    if not account_hash:
        logger.error("Could not retrieve account hash -- check token and connection.")
        sys.exit(1)

    balance = pull_balance(account_hash)

    if not balance:
        logger.error("Balance pull failed -- check token and connection.")
        sys.exit(1)

    conn = get_connection()
    ok = store_balance(conn, account_id, balance)
    conn.close()

    if ok:
        print(f"Balance snapshot saved: {account_id}")
        print(f"  Total value   : ${balance['total_value']:>12,.2f}")
        if balance.get('cash_available') is not None:
            print(f"  Cash available: ${balance['cash_available']:>12,.2f}")
        if balance.get('buying_power') is not None:
            print(f"  Buying power  : ${balance['buying_power']:>12,.2f}")
        if balance.get('day_pnl') is not None:
            print(f"  Day P&L       : ${balance['day_pnl']:>12,.2f}")
    else:
        sys.exit(1)


def cmd_positions(args: argparse.Namespace) -> None:
    """Pull and display current open positions from Schwab."""
    from infrastructure.schwab_positions import get_account_hash, print_positions_report, pull_positions

    account_map = {"AJZ": ("AJZ6348", "6348"), "IRA": ("IRA9885", "9885")}
    account_id, last4 = account_map.get(args.account.upper(), ("AJZ6348", "6348"))

    logger.info(f"Pulling positions for account: {account_id}")

    account_hash = get_account_hash(last4)
    if not account_hash:
        logger.error("Could not retrieve account hash -- check token and connection.")
        sys.exit(1)

    positions = pull_positions(account_hash)
    if positions is None:
        logger.error("Positions pull failed -- check token and connection.")
        sys.exit(1)

    print_positions_report(positions)


def cmd_export(args: argparse.Namespace) -> None:
    """Export v_trade_summary to Power Query CSV files for Excel."""
    from infrastructure.csv_exporter import export_all
    from infrastructure.db_client import get_connection

    conn = get_connection()
    export_all(conn, account_id=args.account if args.account else None)
    conn.close()
    print("Export complete — check data\\exports\\ for CSV files.")


# ── Analyze command — AI review stats CSVs ────────────────────────────────

def cmd_analyze(args: argparse.Namespace) -> None:
    """Generate analysis CSV files — equity curve, R-distribution, monthly summary, etc."""
    from application.stats_export import export_all_stats

    export_all_stats(account_id=args.account if args.account else None)
    print("Analysis complete — check data\\exports\\ai_review\\ for CSV files.")


# ── Helpers ────────────────────────────────────────────────────────────────

def _find_latest_pull(account_arg: str) -> Optional[Path]:
    """Find the most recently modified pull JSON file for the given account.

    Args:
        account_arg: Account key — 'AJZ', 'IRA', or 'PAPER'.

    Returns:
        Path to the latest pull file, or None if not found.
    """
    folder_map = {
        "AJZ"  : API_PULLS_DIR / "ajz_strategies",
        "IRA"  : API_PULLS_DIR / "inherited_roth",
        "PAPER": API_PULLS_DIR / "paper",
    }
    folder = folder_map.get(account_arg.upper(), API_PULLS_DIR / "ajz_strategies")

    if not folder.exists():
        return None

    json_files = sorted(folder.glob("*.json"), key=lambda p: p.stat().st_mtime)
    return json_files[-1] if json_files else None


def _resolve_account_id(account_arg: str, account_label: str) -> str:
    """Map account arg or pull file label to a database account_id.

    Args:
        account_arg: CLI --account value (e.g. 'AJZ', 'IRA').
        account_label: account_label from the pull JSON file.

    Returns:
        Database account_id string (e.g. 'AJZ6348', 'IRA9885', 'PAPER').
    """
    mapping = {
        "AJZ"           : "AJZ6348",
        "AJZ_STRATEGIES": "AJZ6348",
        "IRA"           : "IRA9885",
        "INHERITED_ROTH": "IRA9885",
        "PAPER"         : "PAPER",
    }
    key = account_arg.upper() if account_arg else account_label.upper()
    return mapping.get(key, "AJZ6348")


# ── Parser ─────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="P_020_Trade_Manager",
        description="AJZ Strategies Performance Analysis System",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Database setup
    sub.add_parser("init-db", help="Create database, tables, view, and seed data")
    sub.add_parser("verify",  help="Verify database and show table row counts")

    # Import — main weekly command
    p_import = sub.add_parser(
        "import",
        help="Import latest Schwab pull file into database"
    )
    p_import.add_argument("--account",   default="AJZ",
                          help="Account: AJZ, IRA, or PAPER (default: AJZ)")
    p_import.add_argument("--file",      default=None,
                          help="Specific pull file path (default: latest for account)")
    p_import.add_argument("--dry-run",   action="store_true",
                          help="Run pipeline but do not update last_run.json")
    p_import.add_argument("--start",      default=None,
                          help="Start date YYYY-MM-DD for full re-import (requires --end)")
    p_import.add_argument("--end",        default=None,
                          help="End date YYYY-MM-DD for full re-import (requires --start)")
    p_import.add_argument("--no-export", action="store_true",
                          help="Skip CSV export after import")

    # Balance snapshot
    p_balance = sub.add_parser("balance", help="Pull and store Schwab account balance snapshot")
    p_balance.add_argument("--account", default="AJZ", help="Account: AJZ or IRA (default: AJZ)")

    # Export — Power Query CSVs
    p_export = sub.add_parser("export", help="Export Power Query CSV files for Excel")
    p_export.add_argument("--account", default=None, help="Filter by account ID")

    # Analyze — AI review CSVs
    p_analyze = sub.add_parser("analyze", help="Generate analysis CSV files for AI review")
    p_analyze.add_argument("--account", default=None, help="Filter by account ID")

    # Positions snapshot
    p_positions = sub.add_parser("positions", help="Display current open positions from Schwab")
    p_positions.add_argument("--account", default="AJZ", help="Account: AJZ or IRA (default: AJZ)")

    return parser


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    """Main entry point."""
    parser = _build_parser()
    args   = parser.parse_args()
    dispatch = {
        "init-db": cmd_init_db,
        "verify" : cmd_verify,
        "import" : cmd_import,
        "export" : cmd_export,
        "analyze": cmd_analyze,
        "balance"   : cmd_balance,
        "positions" : cmd_positions,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
