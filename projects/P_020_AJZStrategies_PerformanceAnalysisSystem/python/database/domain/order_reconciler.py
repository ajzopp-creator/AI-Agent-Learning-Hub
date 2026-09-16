"""
order_reconciler.py

Pure logic: resolves entry_date/close_date/realized_pnl (plus the fields
db_order_writer.py's promote_order_to_trade() needs -- entry_fill_price/
asset_type/put_call) for a P_400 order using two matching tiers.

Tier 1 (primary, deterministic): reads an OrderChain's own linkage -- for
a bracket (TRIGGER -> OCO -> target/stop), the entry is the chain's root
and the exit is whichever descendant actually filled. No heuristic
involved; both sides come from the same Schwab-confirmed tree.

Tier 2 (fallback, only when no chain exists): a naked entry closed later
by an unrelated standalone order has no linkage to follow. Converts each
side into the fill-dict shape exit_allocator.py already expects and calls
its existing FIFO/qty-aware allocate_exits() unmodified -- reuses the
same logic WO-P020-E1.001 built for trade-level reconciliation, applied
here at the order level.

No I/O. Callers supply already-pulled OrderChain objects (from
domain/order_linkage.py, fed by infrastructure/schwab_order_puller.py).

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   domain (pure logic)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import List, Literal, Optional

from domain.exit_allocator import allocate_exits
from domain.exit_builder import compute_exit_pnl
from domain.order_linkage import LinkedOrder, OrderChain

logger = logging.getLogger(__name__)


@dataclass
class ReconciledOrder:
    """Result of reconciling one order against its actual fill(s)."""

    order_id: int
    entry_date: Optional[date]
    close_date: Optional[date]
    realized_pnl: Optional[float]
    matched_tier: Optional[int]  # 1, 2, or None if unresolved
    entry_fill_price: Optional[float]
    asset_type: Optional[str]
    put_call: Optional[str]


def reconcile_order(
    side: Literal["long", "short"],
    entry_chain: OrderChain,
    candidate_exit_chains: Optional[List[OrderChain]] = None,
) -> Optional[ReconciledOrder]:
    """Reconcile one order, trying Tier 1 first, Tier 2 only as fallback.

    Args:
        side: "long" or "short" -- needed to get the P&L sign right.
        entry_chain: OrderChain for the order being reconciled. If it has
            descendants (a real bracket), Tier 1 applies directly.
        candidate_exit_chains: Other, unrelated OrderChains (each a
            standalone order with no children of its own) to consider as
            possible closes for a naked entry. Only used when entry_chain
            has no descendants. Caller is responsible for narrowing this
            list to the same symbol/account beforehand -- this function
            does not filter by symbol itself.

    Returns:
        ReconciledOrder if a close was found, or None if the position is
        still open (no matching exit yet).
    """
    if entry_chain.descendants:
        return _reconcile_tier1(side, entry_chain)

    if candidate_exit_chains:
        return _reconcile_tier2(side, entry_chain, candidate_exit_chains)

    return None


def _reconcile_tier1(side: str, chain: OrderChain) -> Optional[ReconciledOrder]:
    """Tier 1: resolve directly from the chain's own linkage."""
    entry = chain.root
    if entry.status != "FILLED":
        return None  # entry hasn't filled yet -- nothing to reconcile

    filled_exits = [n for n in chain.descendants if n.status == "FILLED"]
    if not filled_exits:
        return None  # position still open, no close yet

    if len(filled_exits) > 1:
        logger.warning(
            f"order {entry.order_id}: {len(filled_exits)} filled "
            f"descendants found, expected 1 (OCO bracket) -- using most "
            f"recent by close_time"
        )
        filled_exits.sort(key=lambda n: n.close_time or "")

    exit_node = filled_exits[-1]

    return ReconciledOrder(
        order_id=entry.order_id,
        entry_date=_to_date(entry.close_time),
        close_date=_to_date(exit_node.close_time),
        realized_pnl=_compute_pnl(side, entry, exit_node),
        matched_tier=1,
        entry_fill_price=entry.avg_fill_price,
        asset_type=entry.asset_type,
        put_call=entry.put_call,
    )


def _reconcile_tier2(
    side: str, entry_chain: OrderChain, candidate_exit_chains: List[OrderChain]
) -> Optional[ReconciledOrder]:
    """Tier 2: FIFO/qty-aware fallback via the existing exit_allocator."""
    entry_node = entry_chain.root
    if entry_node.status != "FILLED":
        return None

    filled_candidates = [
        c.root for c in candidate_exit_chains if c.root.status == "FILLED"
    ]
    if not filled_candidates:
        return None  # no closing order has filled yet

    entry_fill = _to_fill_dict(entry_node, "OPENING", side)
    exit_fills = [_to_fill_dict(c, "CLOSING", side) for c in filled_candidates]

    trade_dicts, _orphans = allocate_exits([entry_fill], exit_fills)
    if not trade_dicts or "exit_1" not in trade_dicts[0]:
        return None  # allocator found no matching exit for this entry

    exit_1 = trade_dicts[0]["exit_1"]
    realized_pnl = None
    if entry_node.avg_fill_price is not None and entry_node.quantity:
        # ref EC-010, WO-P400-E6.001 Gate 2 -- this used to do its own
        # inline (exit - entry) * qty math and silently dropped the
        # options 100x contract multiplier every other P&L calc in this
        # codebase already applies (see exit_builder.compute_exit_pnl,
        # spread_matcher.compute_realized_pnl). Confirmed live
        # 2026-09-08 against a real SPY option: this path returned a
        # P&L 100x too small for a short option closed for a credit.
        # put_call.lower() maps to "call"/"put" -- asset_type on
        # LinkedOrder is Schwab's raw "EQUITY"/"OPTION" string, which
        # compute_exit_pnl does not recognize, so put_call is the field
        # that must be passed here.
        realized_pnl = compute_exit_pnl(
            entry_price=entry_node.avg_fill_price,
            exit_price=exit_1["exit_price"],
            qty_exited=exit_1["qty_exited"],
            direction=side,
            asset_type=(entry_node.put_call.lower() if entry_node.put_call else None),
        )

    return ReconciledOrder(
        order_id=entry_node.order_id,
        entry_date=_to_date(entry_node.close_time),
        close_date=exit_1["exit_date"],
        realized_pnl=realized_pnl,
        matched_tier=2,
        entry_fill_price=entry_node.avg_fill_price,
        asset_type=entry_node.asset_type,
        put_call=entry_node.put_call,
    )


def _to_fill_dict(node: LinkedOrder, position_effect: str, side: str) -> dict:
    """Convert one LinkedOrder into the fill-dict shape exit_allocator.py
    expects.

    full_symbol/underlying_symbol are approximated as the same value
    (order-level symbol, not option-suffix-stripped) -- a known
    simplification versus schwab_mapper.py's fuller parsing, acceptable
    here since Tier 2 only needs qty/price/date matching, not display
    formatting. fees defaults to 0.0 -- Schwab's order object does not
    carry commission data at this level. asset_type is Schwab's raw
    "EQUITY"/"OPTION" string (see order_linkage.py) -- exit_allocator.py
    only passes this field through into its output trade dict, it never
    branches on it, so the raw value is sufficient; falls back to
    "EQUITY" if the node's asset_type wasn't captured.
    """
    return {
        "full_symbol": node.symbol,
        "underlying_symbol": node.symbol,
        "asset_type": node.asset_type or "EQUITY",
        "open_date": _to_date(node.close_time),
        "open_datetime": node.entered_time,
        "qty": node.quantity or 0.0,
        "price": node.avg_fill_price or 0.0,
        "fees": 0.0,
        "position_effect": position_effect,
        "direction": side,
        "schwab_transaction_id": str(node.order_id),
    }


def _compute_pnl(
    side: str, entry: LinkedOrder, exit_node: LinkedOrder
) -> Optional[float]:
    """Side-aware realized P&L for a Tier 1 (chain-matched) close.

    Delegates to exit_builder.compute_exit_pnl() (ref EC-010,
    WO-P400-E6.001 Gate 2) -- this function used to do the (exit -
    entry) * qty math inline and silently dropped the options 100x
    contract multiplier for every options trade reconciled through
    Tier 1. See the matching note on the Tier 2 path below for the full
    root cause; put_call (not asset_type) is what compute_exit_pnl needs
    to recognize an option.
    """
    if (
        entry.avg_fill_price is None
        or exit_node.avg_fill_price is None
        or not entry.quantity
    ):
        return None
    return compute_exit_pnl(
        entry_price=entry.avg_fill_price,
        exit_price=exit_node.avg_fill_price,
        qty_exited=entry.quantity,
        direction=side,
        asset_type=(entry.put_call.lower() if entry.put_call else None),
    )


def _to_date(iso_str: Optional[str]) -> Optional[date]:
    """Extract the calendar date from a Schwab ISO8601 timestamp string
    (e.g. '2026-09-05T14:32:10+0000' -> date(2026, 9, 5)). Returns None
    if iso_str is None or malformed.
    """
    if not iso_str:
        return None
    try:
        return date.fromisoformat(iso_str[:10])
    except ValueError:
        return None
