"""Ingest pipeline â€” orchestrates the full flow from raw trade data to SQLite."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config import AUDIT_LOGS_DIR, LAST_RUN_FILE, load_params
from domain.trade_logic import (
    calculate_exit_pnl,
    calculate_hold_days,
    calculate_risk_amount,
    consolidate_fills,
    detect_orphaned_exits,
    determine_trade_status,
    get_asset_multiplier,
)
from infrastructure.db_client import get_connection
from infrastructure.db_writer import insert_exit, insert_trade, update_trade_status
from infrastructure.tracker_reader import load_tracker_lookup
from domain.matcher import match_system
from infrastructure.tracker_reader import match_stop_price
from schemas import Exit, Trade

logger = logging.getLogger(__name__)


# â”€â”€ Audit log â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _write_audit_log(lines: List[str]) -> Path:
    """Write audit log to audit_logs/ with today's date in filename."""
    AUDIT_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d_%H%M%S")
    path  = AUDIT_LOGS_DIR / f"P_020_Weekly_Audit_{today}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"Audit log written: {path.name}")
    return path


# â”€â”€ Last run date â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def get_last_run_date() -> Optional[str]:
    """Read last successful run date from P_020_last_run.json."""
    try:
        if LAST_RUN_FILE.exists():
            data = json.loads(LAST_RUN_FILE.read_text(encoding="utf-8"))
            return data.get("last_run_date")
    except Exception as e:
        logger.warning(f"Could not read last run date: {e}")
    return None


def save_last_run_date(run_date: str) -> None:
    """Save successful run date to P_020_last_run.json."""
    try:
        LAST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_RUN_FILE.write_text(
            json.dumps({"last_run_date": run_date}, indent=2),
            encoding="utf-8",
        )
        logger.info(f"Last run date saved: {run_date}")
    except Exception as e:
        logger.warning(f"Could not save last run date: {e}")


# â”€â”€ System name matching â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _apply_system_names(trades: List[Dict], lookup, default: str) -> None:
    """Apply Tracker Dashboard system name matching to all trade dicts.

    Works with both TrackerLookup (Pydantic model) and plain dict lookups.
    Modifies trade dicts in place.

    Args:
        trades: List of trade dicts â€” must have 'underlying_symbol' and 'open_date'.
        lookup: TrackerLookup object or None.
        default: Fallback system name.
    """
    matched = 0
    for trade in trades:
        system = match_system(
            symbol=trade.get("underlying_symbol", ""),
            open_date=str(trade.get("open_date", "")),
            lookup=lookup,
            default=default,
        )
        trade["system"] = system
        if system != default:
            matched += 1

    logger.info(
        f"System matching: {matched}/{len(trades)} matched, "
        f"{len(trades) - matched} defaulted to '{default}'."
    )


# â”€â”€ Trade building â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _build_trade(raw: Dict, params: Dict, account_id: str) -> Optional[Trade]:
    """Convert a raw trade dict into a validated Trade schema object."""
    try:
        asset_type  = raw.get("asset_type", "stock")
        multiplier  = get_asset_multiplier(asset_type, params["options_multiplier"])
        entry_price = float(raw["entry_price"])
        qty         = float(raw["qty"])
        stop_price  = raw.get("stop_price")
        if stop_price is not None:
            stop_price = float(stop_price)

        risk_amount = calculate_risk_amount(
            entry_price=entry_price,
            qty=qty,
            multiplier=multiplier,
            stop_price=stop_price,
            default_risk_pct=params["default_risk_pct"],
        )

        return Trade(
            account_id=account_id,
            system=raw.get("system", params["default_system_name"]),
            underlying_symbol=raw["underlying_symbol"].upper(),
            asset_type=asset_type,
            direction=raw.get("direction", "long"),
            open_date=raw["open_date"],
            open_datetime=raw.get("open_datetime"),
            qty=qty,
            entry_price=entry_price,
            stop_price=stop_price,
            risk_amount=risk_amount,
            total_commissions=float(raw.get("total_commissions", 0)),
            status="open",
            tags=raw.get("tags"),
            notes=raw.get("notes"),
            source=raw.get("source", "schwab_api"),
            schwab_transaction_id=raw.get("schwab_transaction_id"),
        )
    except (KeyError, ValueError, TypeError) as e:
        logger.warning(f"Skipping malformed trade record: {e} â€” {raw}")
        return None


# â”€â”€ Exit building â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _build_exits(raw: Dict, trade_id: int, params: Dict) -> List[Exit]:
    """Build Exit objects from raw exit data attached to a trade dict."""
    exits       = []
    asset_type  = raw.get("asset_type", "stock")
    multiplier  = get_asset_multiplier(asset_type, params["options_multiplier"])
    entry_price = float(raw["entry_price"])
    direction   = raw.get("direction", "long")

    for n in (1, 2, 3):
        ex = raw.get(f"exit_{n}")
        if not ex:
            continue
        try:
            exit_price = float(ex["exit_price"])
            qty_exited = float(ex["qty_exited"])
            exit_date  = ex["exit_date"]
            open_date  = raw["open_date"]

            pnl  = calculate_exit_pnl(entry_price, exit_price, qty_exited, direction, multiplier)
            hold = calculate_hold_days(open_date, exit_date)

            exits.append(Exit(
                trade_id=trade_id,
                exit_number=n,
                exit_date=exit_date,
                exit_datetime=ex.get("exit_datetime"),
                qty_exited=qty_exited,
                exit_price=exit_price,
                exit_commissions=float(ex.get("exit_commissions", 0)),
                exit_pnl=pnl,
                hold_days=hold,
            ))
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Skipping malformed exit_{n} for trade_id={trade_id}: {e}")

    return exits


# -- Stop price population (paper trades only) --------------------------------

def _apply_stop_prices(trades, lookup, account_id: str) -> None:
    """Populate stop_price on each trade dict from the Tracker Dashboard.

    Only runs for PAPER account. Live trades do not use tracker stop prices.
    Sets raw["stop_price"] which _build_trade() picks up for risk_amount calc.
    """
    if "PAPER" not in account_id.upper():
        return
    if lookup is None:
        logger.debug("No Tracker lookup -- stop prices not applied.")
        return

    populated = 0
    missing = 0
    for trade in trades:
        symbol    = trade.get("underlying_symbol", "")
        open_date = str(trade.get("open_date", ""))
        stop      = match_stop_price(lookup, symbol, open_date)
        if stop is not None:
            trade["stop_price"] = stop
            populated += 1
        else:
            missing += 1

    logger.info(
        f"Stop prices (PAPER): {populated} populated, {missing} missing from Tracker."
    )


# â”€â”€ Main pipeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def run_ingest(
    raw_trades: List[Dict],
    account_id: str,
    save_run_date: bool = True,
) -> Tuple[int, int, int]:
    """Full ingest pipeline: consolidate â†’ match â†’ validate â†’ write to DB.

    Args:
        raw_trades: List of raw trade dicts from Schwab mapper or CSV.
        account_id: Target account ID (e.g. 'AJZ6348').
        save_run_date: Whether to update P_020_last_run.json on success.

    Returns:
        Tuple of (inserted_count, skipped_count, orphan_count).
    """
    audit: List[str] = [
        f"P_020 Weekly Audit â€” {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Account: {account_id}",
        f"Input records: {len(raw_trades)}",
        "=" * 50,
    ]

    params = load_params()
    conn   = get_connection()
    lookup = load_tracker_lookup()

    if lookup:
        audit.append(f"Tracker Dashboard: loaded ({len(lookup.entries)} entries)")
    else:
        audit.append("Tracker Dashboard: unavailable â€” using TOS_Import default")

    # Split entries and orphan-check exits
    entries   = [t for t in raw_trades if t.get("direction") == "long"]
    exits_raw = [t for t in raw_trades if t.get("direction") == "short"]

    consolidated = consolidate_fills(entries, params["consolidation_window_minutes"])
    audit.append(
        f"Consolidation: {len(entries)} entries â†’ {len(consolidated)} "
        f"(merged {len(entries) - len(consolidated)} fills)"
    )

    orphans = detect_orphaned_exits(exits_raw, consolidated)
    for o in orphans:
        audit.append(
            f"ORPHAN: {o.get('underlying_symbol')} exit on "
            f"{o.get('open_date')} â€” no matching entry in this batch"
        )

    # Apply system name matching using TrackerLookup
    all_trades = consolidated + [t for t in exits_raw if t not in orphans]
    _apply_system_names(all_trades, lookup, params["default_system_name"])

    # Apply stop prices from Tracker -- PAPER account only
    _apply_stop_prices(all_trades, lookup, account_id)

    inserted = skipped = 0

    for raw in all_trades:
        trade = _build_trade(raw, params, account_id)
        if trade is None:
            skipped += 1
            continue

        trade_id = insert_trade(conn, trade)
        if trade_id is None:
            skipped += 1
            audit.append(
                f"SKIPPED (duplicate): {raw.get('underlying_symbol')} "
                f"{raw.get('open_date')} txn_id={raw.get('schwab_transaction_id')}"
            )
            continue

        exits = _build_exits(raw, trade_id, params)
        qty_closed = 0.0
        for exit_ in exits:
            insert_exit(conn, exit_)
            qty_closed += exit_.qty_exited

        new_status = determine_trade_status(trade.qty, qty_closed)
        if new_status != "open":
            update_trade_status(conn, trade_id, new_status)

        inserted += 1
        audit.append(
            f"OK: {raw.get('underlying_symbol')} {raw.get('open_date')} "
            f"system={raw.get('system')} exits={len(exits)} status={new_status}"
        )

    audit.append("=" * 50)
    audit.append(f"Inserted: {inserted}  Skipped: {skipped}  Orphans: {len(orphans)}")

    _write_audit_log(audit)
    conn.close()

    if save_run_date and inserted > 0:
        save_last_run_date(datetime.now().strftime("%Y-%m-%d"))

    logger.info(
        f"Ingest complete â€” inserted: {inserted}, "
        f"skipped: {skipped}, orphans: {len(orphans)}"
    )
    return inserted, skipped, len(orphans)

