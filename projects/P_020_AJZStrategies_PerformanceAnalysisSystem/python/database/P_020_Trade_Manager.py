"""P_020 Trade Manager — command-line entry point for all database operations."""

import argparse
import logging
import sqlite3
import sys

from config import DATABASE_FILE

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


# ── Import — main weekly command (logic in application/import_command.py) ──

def cmd_import(args: argparse.Namespace) -> None:
    """Map latest Schwab pull file and import into database."""
    from application.import_command import run_import_command
    run_import_command(
        account=args.account,
        file=args.file,
        dry_run=args.dry_run,
        start=args.start,
        end=args.end,
        no_export=args.no_export,
        thinklog=args.thinklog,
    )


# ── ThinkLog backfill (logic in application/thinklog_backfill.py) ─────────

def cmd_thinklog(args: argparse.Namespace) -> None:
    """Retroactively apply ThinkLog tag overrides to trades already in the DB."""
    from application.thinklog_backfill import run_backfill
    symbols = args.symbols.split(",") if args.symbols else None
    run_backfill(
        thinklog_path=args.thinklog,
        date_from=args.start,
        date_to=args.end,
        account_id=args.account,
        symbols=symbols,
        commit=args.commit,
    )


# ── Account snapshots (logic in application/account_commands.py) ──────────

def cmd_balance(args: argparse.Namespace) -> None:
    """Pull current Schwab account balance and store as weekly snapshot."""
    from application.account_commands import run_balance_command
    run_balance_command(args.account)


def cmd_positions(args: argparse.Namespace) -> None:
    """Pull and display current open positions from Schwab."""
    from application.account_commands import run_positions_command
    run_positions_command(args.account)


# ── Export / Analyze ────────────────────────────────────────────────────────

def cmd_export(args: argparse.Namespace) -> None:
    """Export v_trade_summary to Power Query CSV files for Excel."""
    from infrastructure.csv_exporter import export_all
    from infrastructure.db_client import get_connection

    conn = get_connection()
    export_all(conn, account_id=args.account if args.account else None)
    conn.close()
    print("Export complete — check data\\exports\\ for CSV files.")


def cmd_analyze(args: argparse.Namespace) -> None:
    """Generate analysis CSV files — equity curve, R-distribution, monthly summary, etc."""
    from application.stats_export import export_all_stats

    export_all_stats(account_id=args.account if args.account else None)
    print("Analysis complete — check data\\exports\\ai_review\\ for CSV files.")


# ── Parser ─────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="P_020_Trade_Manager",
        description="AJZ Strategies Performance Analysis System",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="Create database, tables, view, and seed data")
    sub.add_parser("verify",  help="Verify database and show table row counts")

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
    p_import.add_argument("--thinklog",  default=None,
                          help="Path to live-account ThinkLog CSV export -- "
                               "a matching tag always overrides the resolved system")

    p_thinklog = sub.add_parser(
        "thinklog",
        help="Backfill ThinkLog tag overrides onto trades already in the DB"
    )
    p_thinklog.add_argument("--thinklog", required=True,
                            help="Path to a ThinkLog CSV export")
    p_thinklog.add_argument("--start", required=True,
                            help="Start date YYYY-MM-DD (inclusive)")
    p_thinklog.add_argument("--end", required=True,
                            help="End date YYYY-MM-DD (inclusive)")
    p_thinklog.add_argument("--symbols", default=None,
                            help="Comma-separated symbol allow-list (default: all)")
    p_thinklog.add_argument("--account", default=None,
                            help="Filter by account ID, e.g. AJZ6348 (default: all)")
    p_thinklog.add_argument("--commit", action="store_true",
                            help="Write the updates (default: dry-run preview only)")

    p_balance = sub.add_parser("balance", help="Pull and store Schwab account balance snapshot")
    p_balance.add_argument("--account", default="AJZ", help="Account: AJZ or IRA (default: AJZ)")

    p_export = sub.add_parser("export", help="Export Power Query CSV files for Excel")
    p_export.add_argument("--account", default=None, help="Filter by account ID")

    p_analyze = sub.add_parser("analyze", help="Generate analysis CSV files for AI review")
    p_analyze.add_argument("--account", default=None, help="Filter by account ID")

    p_positions = sub.add_parser("positions", help="Display current open positions from Schwab")
    p_positions.add_argument("--account", default="AJZ", help="Account: AJZ or IRA (default: AJZ)")

    return parser


# ── Entry point ────────────────────────────────────────────────────────────

def main() -> None:
    """Main entry point."""
    parser = _build_parser()
    args   = parser.parse_args()
    dispatch = {
        "init-db"  : cmd_init_db,
        "verify"   : cmd_verify,
        "import"   : cmd_import,
        "thinklog" : cmd_thinklog,
        "export"   : cmd_export,
        "analyze"  : cmd_analyze,
        "balance"  : cmd_balance,
        "positions": cmd_positions,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
