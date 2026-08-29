"""Import command orchestration — Schwab pull -> map -> ingest -> export.

Moved out of P_020_Trade_Manager.py (WO-P020-E1.006) to keep the CLI
entry point thin. No behavior change from the original cmd_import.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config import API_PULLS_DIR, load_params

logger = logging.getLogger(__name__)


def find_latest_pull(account_arg: str) -> Optional[Path]:
    """Find the most recently modified pull JSON file for the given account.

    Args:
        account_arg: Account key -- 'AJZ', 'IRA', or 'PAPER'.

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


def resolve_account_id(account_arg: str, account_label: str) -> str:
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


def _resolve_orphans_against_db(orphans: List[Dict], account_id: str, dry_run: bool = False) -> int:
    """Attempt to attach orphaned exits to already-open trades in the DB.

    Orphans have no matching entry within the current pull batch -- this
    happens when the entry was opened in a prior week's pull. Looks up
    the oldest open/partial trade for each orphan's symbol and attaches
    the exit if found; otherwise leaves it as a genuine unresolved orphan.

    Args:
        orphans: Orphaned exit dicts from schwab_mapper.map_pull_file.
        account_id: Database account_id to search within.

    Returns:
        Count of orphans successfully resolved.
    """
    from application.trade_writer import attach_orphan_exit
    from infrastructure.db_client import get_connection
    from infrastructure.db_reader import get_open_trade_for_symbol

    params = load_params()
    conn = get_connection()
    resolved = 0

    for orphan in orphans:
        symbol = orphan.get("underlying_symbol", "")
        open_trade = get_open_trade_for_symbol(conn, account_id, symbol)
        if open_trade is None:
            logger.warning(
                f"ORPHAN EXIT unresolved: {symbol} {orphan.get('open_date')} "
                f"qty={orphan.get('qty')} -- no open position in DB either."
            )
            continue

        outcome, trade_id, new_exits = attach_orphan_exit(conn, orphan, open_trade, params, dry_run=dry_run)
        if outcome == "updated" and new_exits > 0:
            resolved += 1
            print(f"  Resolved orphan: {symbol} exit {orphan.get('open_date')} -> trade_id={trade_id}")

    conn.close()
    return resolved


def run_import_command(
    account: str,
    file: Optional[str],
    dry_run: bool,
    start: Optional[str],
    end: Optional[str],
    no_export: bool,
    thinklog: Optional[str] = None,
) -> None:
    """Run the full import pipeline: pull file -> map -> ingest -> export.

    Args:
        account: CLI --account value.
        file: Specific pull file path, or None to use latest.
        dry_run: If True, do not update last_run.json.
        start: Start date for full re-import date override.
        end: End date for full re-import date override.
        no_export: If True, skip CSV export after import.
        thinklog: Optional path to a live-account ThinkLog CSV export --
                see application.ingest_pipeline.run_ingest() for override
                semantics. None = no-op, identical to today's behavior.

    Prints results and exits(1) on unrecoverable errors -- matches the
    original cmd_import behavior.
    """
    from application.ingest_pipeline import run_ingest
    from infrastructure.csv_exporter import export_all
    from infrastructure.db_client import get_connection
    from infrastructure.schwab_mapper import map_pull_file

    if start or end:
        if not (start and end):
            logger.error("Both --start and --end are required for date override.")
            sys.exit(1)
        logger.info(f"Date override: {start} to {end} -- wiping existing trades.")
        wipe_conn = get_connection()
        wipe_conn.execute("DELETE FROM exits")
        wipe_conn.execute("DELETE FROM trades")
        wipe_conn.commit()
        wipe_conn.close()
        logger.info("Database wiped. Re-importing...")
        if not file:
            pull_path = find_latest_pull(account)
            logger.info(f"Using latest pull file (ensure it covers {start} to {end})")

    if file:
        pull_path = Path(file)
    else:
        pull_path = find_latest_pull(account)

    if not pull_path or not pull_path.exists():
        logger.error(
            f"No pull file found for account '{account}'. "
            f"Run P_020_Schwab_Trade_Pull.py first."
        )
        sys.exit(1)

    logger.info(f"Using pull file: {pull_path.name}")

    account_label, trade_dicts, orphans = map_pull_file(pull_path)
    account_id = resolve_account_id(account, account_label)

    resolved = _resolve_orphans_against_db(orphans, account_id, dry_run=dry_run) if orphans else 0
    if orphans:
        print(
            f"\nOrphaned exits: {len(orphans)} found, "
            f"{resolved} resolved against open DB trades."
        )

    if not trade_dicts:
        logger.info("No trades to import from this pull file.")
        print("\nNothing to import — no OPENING transactions found in pull file.")
        if resolved and not no_export:
            conn = get_connection()
            export_all(conn)
            conn.close()
            print("Export complete — Power Query files updated.")
        return

    logger.info(f"Importing {len(trade_dicts)} trades for account: {account_id}")

    inserted, updated, skipped, db_orphans = run_ingest(
        raw_trades=trade_dicts,
        account_id=account_id,
        save_run_date=not dry_run,
        thinklog_path=thinklog,
    )

    dry_run_tag = "[DRY RUN -- nothing written] " if dry_run else ""
    print(
        f"\n{dry_run_tag}Import complete — inserted: {inserted}  updated: {updated}  "
        f"skipped: {skipped}  orphans: {db_orphans}"
    )

    if (inserted > 0 or updated > 0 or resolved > 0) and not no_export:
        logger.info("Running CSV export...")
        conn = get_connection()
        export_all(conn)
        conn.close()
        print("Export complete — Power Query files updated.")

    print(f"\nAudit log: audit_logs\\")
