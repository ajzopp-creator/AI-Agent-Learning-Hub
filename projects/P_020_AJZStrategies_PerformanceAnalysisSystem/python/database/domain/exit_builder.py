"""
exit_builder.py -- Domain layer.

Pure functions: extract exit rows from a parsed options/stocks CSV row,
and compute exit P&L. No I/O, no DB, no file access.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\domain\\exit_builder.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   domain
"""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional


def compute_exit_pnl(
    entry_price: float,
    exit_price: float,
    qty_exited: float,
    direction: str,
    asset_type: str,
) -> float:
    """P&L for one exit leg.

    Options use a 100x multiplier (per-contract), stock uses 1x.
    Short direction reverses the sign (profit when price falls).
    """
    multiplier = 100 if asset_type in ("call", "put") else 1
    diff = exit_price - entry_price
    if direction == "short":
        diff = -diff
    return round(diff * qty_exited * multiplier, 2)


def _hold_days(open_date: Optional[str], exit_date: Optional[str]) -> Optional[int]:
    if not open_date or not exit_date:
        return None
    try:
        return (date.fromisoformat(exit_date) - date.fromisoformat(open_date)).days
    except ValueError:
        return None


def _build_one_exit(
    exit_number: int,
    exit_price: Optional[float],
    qty_exited: Optional[float],
    exit_date: Optional[str],
    entry_price: Optional[float],
    direction: str,
    asset_type: str,
    open_date: Optional[str],
) -> Optional[Dict]:
    """Returns None if this exit slot is empty (no price or no date)."""
    if exit_price is None or exit_date is None or qty_exited is None:
        return None
    if entry_price is None:
        return None
    return {
        "exit_number": exit_number,
        "exit_date": exit_date,
        "qty_exited": qty_exited,
        "exit_price": exit_price,
        "exit_commissions": 0.0,
        "exit_pnl": compute_exit_pnl(
            entry_price, exit_price, qty_exited, direction, asset_type
        ),
        "hold_days": _hold_days(open_date, exit_date),
    }


def build_exits(
    entry_price: Optional[float],
    direction: str,
    asset_type: str,
    open_date: Optional[str],
    exit_slots: List[Dict],
) -> List[Dict]:
    """Build a list of exit-row dicts (ready for the exits table) from a
    list of raw exit slots, each: {"price": .., "qty": .., "date": ..}.
    Empty slots (missing price/date/qty) are skipped. exit_number is
    1-indexed in the order slots are given.
    """
    exits = []
    for i, slot in enumerate(exit_slots, start=1):
        built = _build_one_exit(
            exit_number=i,
            exit_price=slot.get("price"),
            qty_exited=slot.get("qty"),
            exit_date=slot.get("date"),
            entry_price=entry_price,
            direction=direction,
            asset_type=asset_type,
            open_date=open_date,
        )
        if built is not None:
            exits.append(built)
    return exits
