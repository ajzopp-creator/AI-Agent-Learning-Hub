"""
order_linkage.py

Pure logic: recursively walks a raw Schwab order's childOrderStrategies
tree and returns an OrderChain -- the root order plus a flat list of every
descendant order, each tagged with its orderStrategyType, nesting depth,
quantity, asset type, put/call, average fill price, and enter/close
timestamps.

Built for WO-P400-E6.001 Scope item 2's Tier-1 reconciliation matching.
Confirmed live against 29 real orders (2026-08-21 diagnostic, see WO):
childOrderStrategies is a real, populated key; linkage nests (observed
TRIGGER -> OCO -> two SINGLEs), not a flat sibling-ID field like TOS's
TRG BY#/RE#.

Fields extended 2026-09-07 (same WO, file 5 sizing): the original
version only carried linkage/identity fields (order_id, status, symbol,
depth). order_reconciler.py needs quantity/fill price/timestamps (Tier 1)
and asset_type (Tier 2's exit_allocator.py fill-dict conversion requires
it as a pass-through field) too, so those are pulled here rather than
re-walking the tree a second time downstream. asset_type is Schwab's raw
"EQUITY"/"OPTION" string, not remapped to the stock/etf/call/put/spread
vocabulary schwab_mapper.py uses elsewhere -- exit_allocator.py only
passes this field through, it never branches on it, so the raw value is
sufficient here.

put_call added 2026-09-07 (same day, file 6 sizing): db_order_writer.py's
promote_order_to_trade() needs asset_type + put_call together to call
schwab_mapper.py's existing _map_asset_type() and get a real
Trade.asset_type value (stock/etf/call/put/spread) -- asset_type alone
("OPTION") isn't enough to know call vs put.

No I/O. Input is a raw order dict already fetched by
infrastructure/schwab_order_puller.py -- this module never calls the
Schwab API itself.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   domain (pure logic)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class LinkedOrder:
    """One node in an order's parent/child linkage tree."""

    order_id: int
    parent_order_id: Optional[int]
    order_strategy_type: str
    status: Optional[str]
    symbol: Optional[str]
    depth: int
    quantity: Optional[float]
    asset_type: Optional[str]
    put_call: Optional[str]
    avg_fill_price: Optional[float]
    entered_time: Optional[str]
    close_time: Optional[str]


@dataclass
class OrderChain:
    """A root order plus every descendant found under childOrderStrategies."""

    root: LinkedOrder
    descendants: List[LinkedOrder] = field(default_factory=list)

    @property
    def all_order_ids(self) -> List[int]:
        """Return every order_id in this chain, root first."""
        return [self.root.order_id] + [d.order_id for d in self.descendants]

    def find(self, order_id: int) -> Optional[LinkedOrder]:
        """Return the node matching order_id, or None if not in this chain."""
        if self.root.order_id == order_id:
            return self.root
        for node in self.descendants:
            if node.order_id == order_id:
                return node
        return None


def build_order_chain(raw_order: dict) -> OrderChain:
    """Build an OrderChain from one raw Schwab order response.

    Args:
        raw_order: A single order dict as returned by Schwab's orders
            endpoint, containing at minimum orderId and optionally
            childOrderStrategies (nested, same shape).

    Returns:
        OrderChain with root = raw_order itself, descendants = every
        order found by recursively walking childOrderStrategies.

    Raises:
        ValueError: raw_order has no orderId -- not a valid order object.
    """
    root = _parse_node(raw_order, parent_order_id=None, depth=0)
    descendants = _walk_children(
        raw_order, parent_order_id=root.order_id, depth=1
    )
    return OrderChain(root=root, descendants=descendants)


def _walk_children(
    order_dict: dict, parent_order_id: int, depth: int
) -> List[LinkedOrder]:
    """Recursively parse childOrderStrategies into a flat node list."""
    results: List[LinkedOrder] = []
    for child in order_dict.get("childOrderStrategies") or []:
        node = _parse_node(child, parent_order_id=parent_order_id, depth=depth)
        results.append(node)
        results.extend(
            _walk_children(child, parent_order_id=node.order_id, depth=depth + 1)
        )
    return results


def _extract_avg_fill_price(order_dict: dict) -> Optional[float]:
    """Return the quantity-weighted average fill price for this order.

    Reads orderActivityCollection's executionLegs (Schwab's actual fill
    records). Falls back to the order-level 'price' field (limit/stop
    price, not a real fill) only when no executions are present -- e.g.
    a WORKING or CANCELED order that never filled.
    """
    total_qty = 0.0
    total_value = 0.0
    for activity in order_dict.get("orderActivityCollection") or []:
        for leg in activity.get("executionLegs") or []:
            qty = leg.get("quantity")
            price = leg.get("price")
            if qty is None or price is None:
                continue
            total_qty += qty
            total_value += qty * price
    if total_qty:
        return round(total_value / total_qty, 4)
    return order_dict.get("price")


def _parse_node(
    order_dict: dict, parent_order_id: Optional[int], depth: int
) -> LinkedOrder:
    """Extract one LinkedOrder from a raw Schwab order dict."""
    order_id = order_dict.get("orderId")
    if order_id is None:
        raise ValueError(
            f"order dict at depth {depth} has no orderId: {order_dict!r}"
        )

    symbol = None
    quantity = None
    asset_type = None
    put_call = None
    legs = order_dict.get("orderLegCollection") or []
    if legs:
        instrument = legs[0].get("instrument", {})
        symbol = instrument.get("symbol")
        asset_type = instrument.get("assetType")
        put_call = instrument.get("putCall")
        quantity = legs[0].get("quantity")

    return LinkedOrder(
        order_id=order_id,
        parent_order_id=parent_order_id,
        order_strategy_type=order_dict.get("orderStrategyType", "SINGLE"),
        status=order_dict.get("status"),
        symbol=symbol,
        depth=depth,
        quantity=quantity,
        asset_type=asset_type,
        put_call=put_call,
        avg_fill_price=_extract_avg_fill_price(order_dict),
        entered_time=order_dict.get("enteredTime"),
        close_time=order_dict.get("closeTime"),
    )
