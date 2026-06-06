"""
Schwab JSON mapper — reads raw API pull files and converts to trade dicts
that ingest_pipeline.run_ingest() expects.

Flow:
  1. Load JSON pull file from data/api_pulls/
  2. Parse each transaction → extract instrument + fees
  3. Group fills by orderId → aggregate qty, weighted avg price, sum fees
  4. Separate OPENING (entries) from CLOSING (exits)
  5. Match exits to entries by underlying_symbol
  6. Return list of trade dicts with exit_1/exit_2/exit_3 attached
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Fee types Schwab includes in transferItems as CURRENCY instruments
_FEE_TYPES = {"COMMISSION", "SEC_FEE", "OPT_REG_FEE", "TAF_FEE", "EXCHANGE_FEE"}

# Money market / sweep fund symbols to exclude from trade ingestion
_EXCLUDED_SYMBOLS = {"SNVXX", "SNSXX", "SWVXX"}


# ── JSON loader ────────────────────────────────────────────────────────────

def load_pull_file(path: Path) -> Tuple[str, List[Dict]]:
    """Load a Schwab pull JSON file and return (account_label, transactions).

    Args:
        path: Path to the raw pull JSON file.

    Returns:
        Tuple of (account_label string, list of raw transaction dicts).

    Raises:
        FileNotFoundError: If the pull file does not exist.
        KeyError: If expected JSON keys are missing.
    """
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    account_label = payload.get("account_label", "UNKNOWN")
    transactions  = payload.get("transactions", [])
    logger.info(
        f"Loaded pull file: {path.name} "
        f"({len(transactions)} transactions, account={account_label})"
    )
    return account_label, transactions


# ── Transaction parser ─────────────────────────────────────────────────────

def _parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse Schwab datetime string to UTC datetime object."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("+0000", "+00:00")).replace(
            tzinfo=timezone.utc
        )
    except Exception:
        return None


def _extract_instrument(transfer_items: List[Dict]) -> Optional[Dict]:
    """Extract the non-CURRENCY instrument item from transferItems.

    Args:
        transfer_items: List of transferItem dicts from a Schwab transaction.

    Returns:
        The instrument transferItem dict, or None if not found.
    """
    for item in transfer_items:
        instrument = item.get("instrument", {})
        if instrument.get("assetType") not in ("CURRENCY", None):
            return item
    return None


def _sum_fees(transfer_items: List[Dict]) -> float:
    """Sum all fee amounts from CURRENCY transferItems.

    Args:
        transfer_items: List of transferItem dicts.

    Returns:
        Total fees as a positive float rounded to 2 decimal places.
    """
    total = 0.0
    for item in transfer_items:
        instrument = item.get("instrument", {})
        if instrument.get("assetType") == "CURRENCY":
            fee_type = item.get("feeType", "")
            if fee_type in _FEE_TYPES:
                total += abs(item.get("amount", 0.0))
    return round(total, 2)


def _map_asset_type(schwab_asset_type: str, put_call: Optional[str]) -> str:
    """Map Schwab assetType + putCall to our schema asset_type.

    Args:
        schwab_asset_type: 'OPTION' or 'EQUITY' from Schwab.
        put_call: 'CALL', 'PUT', or None.

    Returns:
        Schema asset_type: 'call', 'put', 'stock'.
    """
    if schwab_asset_type == "OPTION":
        if put_call == "PUT":
            return "put"
        return "call"
    return "stock"


def _parse_transaction(txn: Dict) -> Optional[Dict]:
    """Parse a single Schwab transaction into a normalized fill dict.

    Args:
        txn: Raw Schwab transaction dict.

    Returns:
        Normalized fill dict, or None if transaction should be skipped.
    """
    if txn.get("type") != "TRADE" or txn.get("status") != "VALID":
        return None

    items = txn.get("transferItems", [])
    instrument_item = _extract_instrument(items)
    if not instrument_item:
        return None

    instrument   = instrument_item.get("instrument", {})
    asset_type   = instrument.get("assetType", "")
    put_call     = instrument.get("putCall")
    position_eff = instrument_item.get("positionEffect", "")
    amount       = instrument_item.get("amount", 0.0)  # negative = sell
    price        = instrument_item.get("price", 0.0)

    # Underlying symbol — use underlyingSymbol for options, symbol for equity
    underlying = (
        instrument.get("underlyingSymbol")
        or instrument.get("symbol", "UNKNOWN")
    ).strip().upper()

    # Skip money market / sweep symbols
    if underlying in _EXCLUDED_SYMBOLS:
        logger.debug(f"Skipping excluded symbol: {underlying}")
        return None

    # Direction: OPENING = long (buying), CLOSING = short (selling to close)
    # For equity: positive amount = buy = long
    if position_eff == "OPENING":
        direction = "long"
    elif position_eff == "CLOSING":
        direction = "short"
    else:
        direction = "long" if amount > 0 else "short"

    qty      = abs(amount)
    fees     = _sum_fees(items)
    trade_dt = _parse_datetime(txn.get("tradeDate") or txn.get("time", ""))
    trade_dt_local = trade_dt.astimezone().replace(tzinfo=None) if trade_dt else None
    trade_date = trade_dt_local.date() if trade_dt_local else None

    return {
        "activity_id"          : str(txn.get("activityId", "")),
        "order_id"             : str(txn.get("orderId", "")),
        "underlying_symbol"    : underlying,
        "full_symbol"          : instrument.get("symbol", "").strip(),
        "asset_type"           : _map_asset_type(asset_type, put_call),
        "direction"            : direction,
        "position_effect"      : position_eff,
        "open_date"            : trade_date,
        "open_datetime"        : trade_dt_local,
        "qty"                  : qty,
        "price"                : price,
        "fees"                 : fees,
        "net_amount"           : txn.get("netAmount", 0.0),
        "schwab_transaction_id": str(txn.get("activityId", "")),
    }


# ── Fill aggregation ───────────────────────────────────────────────────────

def _aggregate_by_order(fills: List[Dict]) -> List[Dict]:
    """Aggregate multiple fills of the same orderId into one record.

    Same orderId = same order executed in multiple partial fills.
    Aggregates: qty (sum), price (weighted avg), fees (sum).
    Uses earliest datetime.

    Args:
        fills: List of parsed fill dicts.

    Returns:
        List of aggregated fill dicts — one per orderId.
    """
    orders: Dict[str, List[Dict]] = defaultdict(list)
    for fill in fills:
        orders[fill["order_id"]].append(fill)

    aggregated = []
    for order_id, group in orders.items():
        if len(group) == 1:
            aggregated.append(group[0])
            continue

        total_qty   = sum(g["qty"] for g in group)
        total_cost  = sum(g["qty"] * g["price"] for g in group)
        avg_price   = round(total_cost / total_qty, 4) if total_qty > 0 else 0.0
        total_fees  = round(sum(g["fees"] for g in group), 2)
        earliest_dt = min(
            (g["open_datetime"] for g in group if g.get("open_datetime")),
            default=None,
        )

        merged = dict(group[0])
        merged["qty"]           = total_qty
        merged["price"]         = avg_price
        merged["fees"]          = total_fees
        merged["open_datetime"] = earliest_dt
        merged["open_date"]     = earliest_dt.date() if earliest_dt else group[0]["open_date"]
        merged["activity_id"]   = group[0]["activity_id"]  # keep first
        merged["schwab_transaction_id"] = group[0]["schwab_transaction_id"]

        logger.debug(
            f"Aggregated {len(group)} fills for order {order_id}: "
            f"{merged['underlying_symbol']} {total_qty} @ {avg_price}"
        )
        aggregated.append(merged)

    return aggregated


# ── Entry / exit matching ──────────────────────────────────────────────────

def _match_exits_to_entries(
    entries: List[Dict],
    exits: List[Dict],
) -> List[Dict]:
    """Attach exit records to matching entry records.

    Rules:
    - Match on full_symbol (prevents AMD stock exits matching AMD options).
    - Exit date must be >= entry open_date (no backwards-in-time matching).
    - Exits consumed FIFO (chronologically earliest first).
    - Each exit consumed by only one entry.
    """
    from datetime import date as date_type

    # Sort exits chronologically so FIFO works correctly
    sorted_exits = sorted(exits, key=lambda x: x["open_date"] or date_type.min)

    # Build exit pool keyed by full_symbol
    exit_pool: Dict[str, List[Dict]] = defaultdict(list)
    for ex in sorted_exits:
        key = ex.get("full_symbol") or ex["underlying_symbol"]
        exit_pool[key].append(ex)

    consumed = set()

    trade_dicts = []
    for entry in entries:
        symbol     = entry["underlying_symbol"]
        full_sym   = entry.get("full_symbol") or symbol
        entry_date = entry["open_date"]

        candidate_exits = exit_pool.get(full_sym, [])

        # Only exits on or after entry date, not yet consumed
        valid_exits = [
            ex for ex in candidate_exits
            if id(ex) not in consumed
            and ex["open_date"] is not None
            and ex["open_date"] >= entry_date
        ]

        trade = {
            "underlying_symbol"    : symbol,
            "asset_type"           : entry["asset_type"],
            "direction"            : entry["direction"],
            "open_date"            : entry_date,
            "open_datetime"        : entry["open_datetime"],
            "qty"                  : entry["qty"],
            "entry_price"          : entry["price"],
            "total_commissions"    : entry["fees"],
            "source"               : "schwab_api",
            "schwab_transaction_id": entry["schwab_transaction_id"],
        }

        for n, ex in enumerate(valid_exits[:3], start=1):
            consumed.add(id(ex))
            trade[f"exit_{n}"] = {
                "exit_price"      : ex["price"],
                "qty_exited"      : ex["qty"],
                "exit_date"       : ex["open_date"],
                "exit_datetime"   : ex["open_datetime"],
                "exit_commissions": ex["fees"],
            }
            trade["total_commissions"] = round(
                trade["total_commissions"] + ex["fees"], 2
            )

        trade_dicts.append(trade)

    # Flag orphaned exits
    all_entry_syms = {e["underlying_symbol"] for e in entries}
    for ex in exits:
        if id(ex) not in consumed:
            sym = ex["underlying_symbol"]
            if sym not in all_entry_syms:
                logger.warning(
                    f"ORPHAN EXIT: {sym} {ex['open_date']} "
                    f"price={ex['price']} qty={ex['qty']} "
                    f"-- no matching entry in this batch."
                )
            else:
                logger.warning(
                    f"ORPHAN EXIT: {sym} {ex['open_date']} "
                    f"price={ex['price']} qty={ex['qty']} "
                    f"-- exit predates all entries (check prior week)."
                )

    return trade_dicts



# ── Main public function ───────────────────────────────────────────────────

def map_pull_file(path: Path) -> Tuple[str, List[Dict]]:
    """Load and map a Schwab pull JSON file to ingest-ready trade dicts.

    This is the main entry point called by the CLI and weekly runner.

    Args:
        path: Path to the raw Schwab pull JSON file.

    Returns:
        Tuple of (account_label, list of trade dicts ready for run_ingest()).
    """
    account_label, raw_transactions = load_pull_file(path)

    # Parse each transaction
    fills = []
    skipped = 0
    for txn in raw_transactions:
        parsed = _parse_transaction(txn)
        if parsed:
            fills.append(parsed)
        else:
            skipped += 1

    logger.info(
        f"Parsed {len(fills)} fills, skipped {skipped} non-trade transactions."
    )

    # Aggregate fills by orderId
    aggregated = _aggregate_by_order(fills)
    logger.info(f"Aggregated to {len(aggregated)} orders.")

    # Split entries and exits
    entries = [f for f in aggregated if f["direction"] == "long"]
    exits   = [f for f in aggregated if f["direction"] == "short"]
    logger.info(f"Entries (OPENING): {len(entries)}  Exits (CLOSING): {len(exits)}")

    # Match exits to entries
    trade_dicts = _match_exits_to_entries(entries, exits)
    logger.info(f"Trade dicts ready for ingest: {len(trade_dicts)}")

    return account_label, trade_dicts
