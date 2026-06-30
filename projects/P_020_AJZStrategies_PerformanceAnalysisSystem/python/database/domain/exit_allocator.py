"""Domain logic -- quantity-aware allocation of exit fills to entry fills.

Pure logic, no I/O. Replaces the chronological grab-up-to-3 matching that
used to live in schwab_mapper.py. That version had no concept of an entry's
remaining quantity, so a contract with more than one separate entry could
have all its exits greedily consumed by whichever entry was processed
first, leaving sibling entries permanently open. See WO-P020-E1.001.
"""

import logging
from collections import defaultdict
from datetime import date as date_type
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

MAX_EXIT_SLOTS = 3


def allocate_exits(entries: List[Dict], exits: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Allocate exit fills to entry fills, qty-aware, grouped by full_symbol.

    Args:
        entries: Parsed entry (OPENING) fill dicts -- full_symbol,
                 underlying_symbol, open_date, qty, price, fees, etc.
        exits: Parsed exit (CLOSING) fill dicts -- same shape.

    Returns:
        Tuple of (trade dicts with exit_1/2/3 attached, orphaned exit dicts).
    """
    entries_by_symbol: Dict[str, List[Dict]] = defaultdict(list)
    exits_by_symbol: Dict[str, List[Dict]] = defaultdict(list)

    for e in entries:
        entries_by_symbol[e.get("full_symbol") or e["underlying_symbol"]].append(e)
    for x in exits:
        exits_by_symbol[x.get("full_symbol") or x["underlying_symbol"]].append(x)

    trade_dicts: List[Dict] = []
    orphans: List[Dict] = []

    for symbol in set(entries_by_symbol) | set(exits_by_symbol):
        built, leftover = _allocate_for_symbol_group(
            symbol, entries_by_symbol.get(symbol, []), exits_by_symbol.get(symbol, [])
        )
        trade_dicts.extend(built)
        orphans.extend(leftover)

    return trade_dicts, orphans


def _allocate_for_symbol_group(
    symbol: str, entries: List[Dict], exits: List[Dict]
) -> Tuple[List[Dict], List[Dict]]:
    """Allocate exits to entries within one full_symbol group, oldest entry first."""
    sorted_entries = sorted(entries, key=lambda e: e["open_date"] or date_type.min)
    queue = sorted(
        ({**x, "_remaining": x["qty"], "_orig_qty": x["qty"]} for x in exits),
        key=lambda x: x["open_date"] or date_type.min,
    )

    trade_dicts = []
    for entry in sorted_entries:
        remaining = entry["qty"]
        slots: List[Dict] = []

        for ex in queue:
            if remaining <= 0:
                break
            if ex["_remaining"] <= 0:
                continue
            if ex["open_date"] is None or ex["open_date"] < entry["open_date"]:
                continue

            consume_qty = min(remaining, ex["_remaining"])
            _add_exit_slot(slots, ex, consume_qty, symbol)
            ex["_remaining"] -= consume_qty
            remaining -= consume_qty

        trade_dicts.append(_build_trade_dict(entry, slots))

    leftover = [_strip_internal(ex) for ex in queue if ex["_remaining"] > 0.0001]
    _log_leftover(symbol, leftover, has_entries=bool(entries))

    return trade_dicts, leftover


def _add_exit_slot(slots: List[Dict], ex: Dict, consume_qty: float, symbol: str) -> None:
    """Append a new exit slot, or merge into the 3rd slot once the cap is hit."""
    share = round(ex["fees"] * (consume_qty / ex["_orig_qty"]), 2) if ex["_orig_qty"] else 0.0
    new_slot = {
        "exit_price": ex["price"],
        "qty_exited": consume_qty,
        "exit_date": ex["open_date"],
        "exit_datetime": ex["open_datetime"],
        "exit_commissions": share,
    }

    if len(slots) < MAX_EXIT_SLOTS:
        slots.append(new_slot)
        return

    last = slots[-1]
    total_qty = last["qty_exited"] + new_slot["qty_exited"]
    if total_qty:
        last["exit_price"] = round(
            (last["exit_price"] * last["qty_exited"] + new_slot["exit_price"] * new_slot["qty_exited"])
            / total_qty, 4,
        )
    last["qty_exited"] = total_qty
    last["exit_commissions"] = round(last["exit_commissions"] + new_slot["exit_commissions"], 2)
    if new_slot["exit_date"] and (not last["exit_date"] or new_slot["exit_date"] > last["exit_date"]):
        last["exit_date"] = new_slot["exit_date"]
        last["exit_datetime"] = new_slot["exit_datetime"]

    logger.warning(
        f"4th+ exit chunk for {symbol} merged into exit_3 (weighted avg) -- "
        f"schema limit is {MAX_EXIT_SLOTS} exit slots per entry."
    )


def _build_trade_dict(entry: Dict, slots: List[Dict]) -> Dict:
    """Build the trade dict shape ingest_pipeline expects, with exit_N attached."""
    trade = {
        "underlying_symbol": entry["underlying_symbol"],
        "asset_type": entry["asset_type"],
        "direction": entry["direction"],
        "open_date": entry["open_date"],
        "open_datetime": entry["open_datetime"],
        "qty": entry["qty"],
        "entry_price": entry["price"],
        "total_commissions": entry["fees"],
        "source": "schwab_api",
        "schwab_transaction_id": entry["schwab_transaction_id"],
    }
    for n, slot in enumerate(slots, start=1):
        trade[f"exit_{n}"] = slot
        trade["total_commissions"] = round(trade["total_commissions"] + slot["exit_commissions"], 2)
    return trade


def _strip_internal(ex: Dict) -> Dict:
    """Remove the internal _remaining/_orig_qty tracking keys before returning."""
    return {k: v for k, v in ex.items() if not k.startswith("_")}


def _log_leftover(symbol: str, leftover: List[Dict], has_entries: bool) -> None:
    """Log unresolved exits -- either no entry exists, or qty exceeds entries available."""
    if not leftover:
        return
    reason = (
        "exceeds total entry qty available in this batch" if has_entries
        else "no matching entry for this symbol in this batch"
    )
    for o in leftover:
        logger.warning(f"ORPHAN EXIT: {symbol} {o.get('open_date')} qty={o.get('qty')} -- {reason}.")
