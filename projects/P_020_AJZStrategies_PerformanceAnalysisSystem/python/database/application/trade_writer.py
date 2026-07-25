"""Per-trade write logic for the ingest pipeline -- insert a new trade, or
attach new exits to an existing duplicate entry.

Extracted from ingest_pipeline.run_ingest() so that file stays
orchestration-only. This is the fix for the skip-bug in WO-P020-E1.001:
previously, when insert_trade() returned None because the entry already
existed, the pipeline skipped the whole record -- exits never got written,
even after the position closed. Here, a duplicate entry triggers a lookup
of the existing trade_id, and exits are built/inserted against it.
insert_exit() already dedupes safely per (trade_id, exit_number), so this
is idempotent across repeated runs.
"""

import logging
from datetime import date
from typing import Dict, List, Optional, Tuple

from domain.trade_logic import (
    calculate_exit_pnl,
    calculate_hold_days,
    determine_trade_status,
    get_asset_multiplier,
)
from infrastructure.db_reader import get_exits_for_trade
from infrastructure.db_writer import (
    get_trade_id_by_schwab_id,
    insert_exit,
    insert_trade,
    update_trade_status,
)
from schemas import Exit

logger = logging.getLogger(__name__)


def build_exits(raw: Dict, trade_id: int, params: Dict) -> List[Exit]:
    """Build Exit objects from raw exit_1/2/3 keys attached to a trade dict."""
    exits = []
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


def write_trade(conn, raw: Dict, trade, params: Dict) -> Tuple[str, Optional[int], int]:
    """Insert a new trade, or attach new exits to an existing duplicate entry.

    Args:
        conn: Active SQLite connection.
        raw: Raw trade dict carrying exit_1/2/3 keys (from exit_allocator).
        trade: Validated Trade schema object built from raw.
        params: Loaded business parameters.

    Returns:
        Tuple of (outcome, trade_id, new_exit_count). outcome is one of
        'inserted' (brand-new trade), 'updated' (existing entry, new exits
        attached), 'unchanged' (existing entry, nothing new to add), or
        'error' (duplicate detected but existing trade_id not found --
        should not happen, logged for investigation if it does).
    """
    trade_id = insert_trade(conn, trade)
    outcome = "inserted"

    if trade_id is None:
        trade_id = get_trade_id_by_schwab_id(conn, trade.schwab_transaction_id)
        if trade_id is None:
            logger.warning(
                f"Duplicate detected for {trade.underlying_symbol} {trade.open_date} "
                f"but existing trade_id not found -- skipping "
                f"(txn_id={trade.schwab_transaction_id})."
            )
            return "error", None, 0
        outcome = "updated"

    exits = build_exits(raw, trade_id, params)
    new_exit_count = sum(1 for e in exits if insert_exit(conn, e) is not None)

    if new_exit_count == 0 and outcome == "updated":
        outcome = "unchanged"

    qty_closed = sum(e.qty_exited for e in exits)
    new_status = determine_trade_status(trade.qty, qty_closed)
    update_trade_status(conn, trade_id, new_status, trade.total_commissions)

    return outcome, trade_id, new_exit_count


def attach_orphan_exit(conn, orphan: Dict, open_trade, params: Dict) -> Tuple[str, Optional[int], int]:
    """Attach an orphaned exit to an already-open trade found in the DB.

    Orphans occur when exit_allocator finds no matching entry within the
    current pull batch -- typically because the entry was opened in a
    prior week's pull. This looks up the oldest open/partial DB trade for
    the symbol and attaches the exit there instead of dropping it.

    Args:
        conn: Active SQLite connection.
        orphan: Orphaned exit dict from domain.exit_allocator (underlying_
                symbol, price, qty, open_date, open_datetime, fees).
        open_trade: sqlite3.Row for the matched open/partial trade.
        params: Loaded business parameters.

    Returns:
        Tuple of (outcome, trade_id, new_exit_count). outcome is 'updated'
        (exit attached), or 'unchanged' (all 3 exit slots already used).
    """
    trade_id = open_trade["trade_id"]
    existing = get_exits_for_trade(conn, trade_id)
    next_slot = len(existing) + 1

    if next_slot > 3:
        logger.warning(
            f"Cannot attach orphan exit to trade_id={trade_id} -- "
            f"all 3 exit slots already used."
        )
        return "unchanged", trade_id, 0

    exit_leg = {
        "exit_price": orphan.get("price"),
        "qty_exited": orphan.get("qty"),
        "exit_date": orphan.get("open_date"),
        "exit_datetime": orphan.get("open_datetime"),
        "exit_commissions": orphan.get("fees", 0.0),
    }
    raw = {
        "entry_price": open_trade["entry_price"],
        "asset_type": open_trade["asset_type"],
        "direction": open_trade["direction"],
        "open_date": date.fromisoformat(open_trade["open_date"]),
        f"exit_{next_slot}": exit_leg,
    }

    exits = build_exits(raw, trade_id, params)
    new_exit_count = sum(1 for e in exits if insert_exit(conn, e) is not None)
    if new_exit_count == 0:
        return "unchanged", trade_id, 0

    qty_closed = sum(e["qty_exited"] for e in get_exits_for_trade(conn, trade_id))
    new_status = determine_trade_status(open_trade["qty"], qty_closed)
    new_commissions = open_trade["total_commissions"] + exit_leg["exit_commissions"]
    update_trade_status(conn, trade_id, new_status, new_commissions)

    logger.info(
        f"Attached orphan exit to trade_id={trade_id} "
        f"({open_trade['underlying_symbol']}) -- status={new_status}"
    )
    return "updated", trade_id, new_exit_count
