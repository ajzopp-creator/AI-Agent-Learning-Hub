"""Pure business logic for trade calculations — no I/O, no database access."""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Risk & P&L calculations ────────────────────────────────────────────────

def calculate_risk_amount(
    entry_price: float,
    qty: float,
    multiplier: int,
    stop_price: Optional[float],
    default_risk_pct: float,
) -> float:
    """Calculate dollar risk for a trade.

    Uses stop_price if provided, otherwise applies default_risk_pct to position.

    Args:
        entry_price: Per share or per contract entry price.
        qty: Number of shares or contracts.
        multiplier: Options multiplier (100) or 1 for stocks/ETFs.
        stop_price: Stop loss price — None triggers default calculation.
        default_risk_pct: Fractional default risk (e.g. 0.015 = 1.5%).

    Returns:
        Dollar risk amount, rounded to 2 decimal places.
    """
    if stop_price is not None and stop_price > 0:
        risk_per_unit = abs(entry_price - stop_price)
        return round(risk_per_unit * qty * multiplier, 2)
    return round(entry_price * qty * multiplier * default_risk_pct, 2)


def calculate_exit_pnl(
    entry_price: float,
    exit_price: float,
    qty_exited: float,
    direction: str,
    multiplier: int,
) -> float:
    """Calculate realized P&L for one exit leg.

    Args:
        entry_price: Original entry price per unit.
        exit_price: Exit price per unit.
        qty_exited: Quantity closed at this exit.
        direction: 'long' or 'short'.
        multiplier: Options multiplier (100) or 1 for stocks/ETFs.

    Returns:
        Realized P&L for this exit, rounded to 2 decimal places.
    """
    price_diff = exit_price - entry_price
    if direction == "short":
        price_diff = -price_diff
    return round(price_diff * qty_exited * multiplier, 2)


def calculate_hold_days(open_date: date, exit_date: date) -> int:
    """Calculate calendar days held between open and exit dates.

    Args:
        open_date: Trade open date.
        exit_date: Exit date.

    Returns:
        Number of calendar days held (minimum 0).
    """
    delta = (exit_date - open_date).days
    return max(0, delta)


def determine_trade_status(qty: float, qty_closed: float) -> str:
    """Determine trade status based on quantity remaining.

    Args:
        qty: Original position size.
        qty_closed: Total quantity closed across all exits.

    Returns:
        'open', 'partial', or 'closed'.
    """
    if qty_closed <= 0:
        return "open"
    if qty_closed < qty:
        return "partial"
    return "closed"


def get_asset_multiplier(asset_type: str, options_multiplier: int) -> int:
    """Return the correct multiplier for a given asset type.

    Args:
        asset_type: 'stock', 'etf', 'call', 'put', or 'spread'.
        options_multiplier: Multiplier for options contracts (from params).

    Returns:
        100 for options types, 1 for stocks and ETFs.
    """
    if asset_type in ("call", "put", "spread"):
        return options_multiplier
    return 1


# ── Trade consolidation ────────────────────────────────────────────────────

def consolidate_fills(
    raw_fills: List[Dict],
    window_minutes: int,
) -> List[Dict]:
    """Consolidate same-symbol buy fills within a time window into single entries.

    Groups fills where: same underlying_symbol + same direction (buy/long) +
    open_datetime within window_minutes of each other.
    Sums qty and commissions across grouped fills. Uses earliest datetime.

    Args:
        raw_fills: List of raw fill dicts with keys:
                   underlying_symbol, direction, open_datetime (datetime),
                   qty, entry_price (weighted avg applied), total_commissions.
        window_minutes: Maximum minutes between fills to consolidate.

    Returns:
        List of consolidated fill dicts — fewer or equal entries than input.
    """
    if not raw_fills:
        return []

    buys = [f for f in raw_fills if f.get("direction") == "long"]
    non_buys = [f for f in raw_fills if f.get("direction") != "long"]

    consolidated: List[Dict] = []
    used = set()

    for i, fill in enumerate(buys):
        if i in used:
            continue

        group = [fill]
        used.add(i)
        anchor_dt: datetime = fill.get("open_datetime") or datetime.min

        for j, other in enumerate(buys):
            if j in used:
                continue
            if other["underlying_symbol"] != fill["underlying_symbol"]:
                continue
            other_dt: datetime = other.get("open_datetime") or datetime.min
            diff_minutes = abs((other_dt - anchor_dt).total_seconds() / 60)
            if diff_minutes <= window_minutes:
                group.append(other)
                used.add(j)

        if len(group) == 1:
            consolidated.append(fill)
            continue

        total_qty = sum(g["qty"] for g in group)
        total_cost = sum(g["qty"] * g["entry_price"] for g in group)
        avg_price = round(total_cost / total_qty, 4) if total_qty > 0 else 0
        total_comm = round(sum(g.get("total_commissions", 0) for g in group), 2)
        earliest = min(
            g["open_datetime"] for g in group if g.get("open_datetime")
        )

        merged = dict(fill)
        merged["qty"] = total_qty
        merged["entry_price"] = avg_price
        merged["total_commissions"] = total_comm
        merged["open_datetime"] = earliest
        merged["open_date"] = earliest.date() if earliest else fill.get("open_date")
        logger.debug(
            f"Consolidated {len(group)} fills of "
            f"{fill['underlying_symbol']} → {total_qty} units @ {avg_price}"
        )
        consolidated.append(merged)

    return consolidated + non_buys


# ── Orphan detection ───────────────────────────────────────────────────────

def detect_orphaned_exits(
    exits: List[Dict],
    entries: List[Dict],
) -> List[Dict]:
    """Identify exit records with no matching entry in the current batch.

    Matches on underlying_symbol (case-insensitive).

    Args:
        exits: List of exit fill dicts (direction='short' or sell).
        entries: List of entry fill dicts (direction='long' or buy).

    Returns:
        List of orphaned exit dicts — sells with no matching buy in batch.
    """
    entry_symbols = {e["underlying_symbol"].upper() for e in entries}
    orphans = [
        ex for ex in exits
        if ex.get("underlying_symbol", "").upper() not in entry_symbols
    ]
    if orphans:
        symbols = [o["underlying_symbol"] for o in orphans]
        logger.warning(
            f"Orphaned exits detected ({len(orphans)}): {symbols} — "
            f"check prior week for matching entries."
        )
    return orphans
