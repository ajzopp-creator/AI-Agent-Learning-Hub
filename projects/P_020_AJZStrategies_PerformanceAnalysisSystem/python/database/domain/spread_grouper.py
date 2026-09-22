"""spread_grouper.py -- tags live Schwab entry fills that belong to the same
multi-leg combo order with a shared spread_group_id (WO-P020-E1.021).

Pure logic: no I/O, no DB access. Operates on the fill-dict shape
schwab_mapper.py already builds (order_id, full_symbol, etc.) after
_aggregate_by_order() has run -- each dict here is already one correctly
identified leg (WO-P020-E1.017's (order_id, full_symbol) key made that
correct); this module's only job is deciding which of those already-correct
legs belong to the same spread.

Why order_id alone is the right signal: Schwab's transaction history API
returns one row per leg for a multi-leg order, linked only by a shared
orderId -- there is no separate "combo" transaction type to detect. Any
order_id shared by 2+ DISTINCT full_symbols on the OPENING side is, by
construction, one multi-leg order (Schwab does not bundle unrelated
symbols under one order_id). No named-strategy text parsing is needed
here the way paper's TOS-CSV-based spread_leg_parser.py needs it --
that parser exists to handle a text DESCRIPTION field the live JSON
pull format doesn't have.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\domain\\spread_grouper.py
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List


def assign_spread_groups(entry_fills: List[Dict]) -> None:
    """Mutate entry_fills in place, adding a "spread_group_id" key.

    Fills sharing the same order_id AND covering 2+ distinct full_symbols
    get spread_group_id = f"SG_{order_id}". Every other fill gets
    spread_group_id = None (single-leg order, unchanged behavior).

    Args:
        entry_fills: OPENING fill dicts from schwab_mapper._aggregate_by_order(),
            each already keyed uniquely by (order_id, full_symbol).
    """
    by_order: Dict[str, List[Dict]] = defaultdict(list)
    for fill in entry_fills:
        order_id = fill.get("order_id")
        if order_id:
            by_order[order_id].append(fill)

    for fill in entry_fills:
        fill["spread_group_id"] = None

    for order_id, group in by_order.items():
        symbols = {g["full_symbol"] for g in group}
        if len(symbols) < 2:
            continue
        group_id = f"SG_{order_id}"
        for fill in group:
            fill["spread_group_id"] = group_id
