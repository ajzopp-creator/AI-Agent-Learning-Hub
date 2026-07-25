"""Ingest pipeline — orchestrates the full flow from raw trade data to SQLite."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config import AUDIT_LOGS_DIR, LAST_RUN_FILE, load_params
from domain.trade_logic import (
    calculate_risk_amount,
    consolidate_fills,
    detect_orphaned_exits,
    get_asset_multiplier,
)
from infrastructure.db_client import get_connection
from infrastructure.tracker_reader import load_tracker_lookup
from infrastructure.vault_system_reader import load_vault_lookup
from application.system_attribution import apply_system_names
from domain.matcher import match_system
from infrastructure.tracker_reader import match_stop_price
from application.trade_writer import write_trade
from schemas import Trade

logger = logging.getLogger(__name__)


# ── Audit log ────────────────────────────────────────────────────────────

def _write_audit_log(lines: List[str]) -> Path:
    """Write audit log to audit_logs/ with today's date in filename."""
    AUDIT_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d_%H%M%S")
    path  = AUDIT_LOGS_DIR / f"P_020_Weekly_Audit_{today}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info(f"Audit log written: {path.name}")
    return path


# ── Last run date ────────────────────────────────────────────────────────

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
    """Save successful run date + full timestamp to P_020_last_run.json."""
    try:
        from schemas import LastRunFile
        record = LastRunFile(
            last_run_date=run_date,
            last_run_datetime=datetime.now().isoformat(timespec="seconds"),
        )
        LAST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
        LAST_RUN_FILE.write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )
        logger.info(f"Last run saved: {record.last_run_datetime}")
    except Exception as e:
        logger.warning(f"Could not save last run date: {e}")


# ── System name matching ─────────────────────────────────────────────────


# ── Trade building ───────────────────────────────────────────────────────

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
        logger.warning(f"Skipping malformed trade record: {e} — {raw}")
        return None


# ── Stop price population (paper trades only) ───────────────────────────

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


# ── Main pipeline ────────────────────────────────────────────────────────

def run_ingest(
    raw_trades: List[Dict],
    account_id: str,
    save_run_date: bool = True,
) -> Tuple[int, int, int, int]:
    """Full ingest pipeline: match → validate → write to DB.

    Args:
        raw_trades: List of raw trade dicts from schwab_mapper (already
                    qty-aware exit-matched — see domain.exit_allocator).
        account_id: Target account ID (e.g. 'AJZ6348').
        save_run_date: Whether to update P_020_last_run.json on success.

    Returns:
        Tuple of (inserted_count, updated_count, skipped_count, orphan_count).
    """
    audit: List[str] = [
        f"P_020 Weekly Audit — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Account: {account_id}",
        f"Input records: {len(raw_trades)}",
        "=" * 50,
    ]

    params = load_params()
    conn   = get_connection()
    lookup = load_tracker_lookup()
    vault_lookup = load_vault_lookup()

    if lookup:
        audit.append(f"Tracker Dashboard: loaded ({len(lookup.entries)} entries)")
    else:
        audit.append("Tracker Dashboard: unavailable — using TOS_Import default")

    if vault_lookup:
        audit.append(f"P_400 vault: {vault_lookup.summary()}")
    else:
        audit.append("P_400 vault: unavailable — tracker-only matching")

    # NOTE: raw_trades arriving from schwab_mapper.map_pull_file() are already
    # entry dicts with exit_1/2/3 attached (direction == 'long' for all of
    # them) -- exit matching happens upstream via domain.exit_allocator.
    # The split/consolidate/orphan-detect below is retained for any caller
    # that still passes unmatched raw fills; it is a no-op for the Schwab
    # API import path (exits_raw is always empty there).
    entries   = [t for t in raw_trades if t.get("direction") == "long"]
    exits_raw = [t for t in raw_trades if t.get("direction") == "short"]

    consolidated = consolidate_fills(entries, params["consolidation_window_minutes"])
    audit.append(
        f"Consolidation: {len(entries)} entries → {len(consolidated)} "
        f"(merged {len(entries) - len(consolidated)} fills)"
    )

    orphans = detect_orphaned_exits(exits_raw, consolidated)
    for o in orphans:
        audit.append(
            f"ORPHAN: {o.get('underlying_symbol')} exit on "
            f"{o.get('open_date')} — no matching entry in this batch"
        )

    all_trades = consolidated + [t for t in exits_raw if t not in orphans]
    apply_system_names(
        all_trades,
        lookup,
        params["default_system_name"],
        vault_lookup=vault_lookup,
    )
    _apply_stop_prices(all_trades, lookup, account_id)

    inserted = updated = skipped = 0

    for raw in all_trades:
        trade = _build_trade(raw, params, account_id)
        if trade is None:
            skipped += 1
            continue

        outcome, trade_id, new_exits = write_trade(conn, raw, trade, params)

        if outcome == "inserted":
            inserted += 1
            audit.append(
                f"OK: {raw.get('underlying_symbol')} {raw.get('open_date')} "
                f"system={raw.get('system')} exits={new_exits} (new trade)"
            )
        elif outcome == "updated":
            updated += 1
            audit.append(
                f"UPDATED: {raw.get('underlying_symbol')} {raw.get('open_date')} "
                f"system={raw.get('system')} new_exits={new_exits} "
                f"(existing entry, exits attached)"
            )
        elif outcome == "unchanged":
            skipped += 1
            audit.append(
                f"UNCHANGED (duplicate, no new exits): "
                f"{raw.get('underlying_symbol')} {raw.get('open_date')}"
            )
        else:  # error
            skipped += 1
            audit.append(
                f"ERROR: {raw.get('underlying_symbol')} {raw.get('open_date')} "
                f"duplicate txn_id but existing trade_id not found "
                f"txn_id={raw.get('schwab_transaction_id')}"
            )

    audit.append("=" * 50)
    audit.append(
        f"Inserted: {inserted}  Updated: {updated}  Skipped: {skipped}  "
        f"Orphans: {len(orphans)}"
    )

    _write_audit_log(audit)
    conn.close()

    if save_run_date and (inserted > 0 or updated > 0):
        save_last_run_date(datetime.now().strftime("%Y-%m-%d"))

    logger.info(
        f"Ingest complete — inserted: {inserted}, updated: {updated}, "
        f"skipped: {skipped}, orphans: {len(orphans)}"
    )
    return inserted, updated, skipped, len(orphans)
