"""p820_override.py -- Domain layer.

Pure function: given a P_820 lookup and a (symbol, date) pair, resolve
the override for system/why_code/sig_code. No I/O -- the lookup is built
by infrastructure.p820_reader.load_p820_lookup() and passed in.

Highest-priority source in the resolver chain (Tony directive, 2026-08-16
P_020 session): P_820 > ThinkLog > Tracker > default. Dictated live at or
near order time, structured, no export-lag risk -- outranks even ThinkLog.

Same forward-window shape as thinklog_override.py (closest date wins,
forward-only), reused deliberately for consistency rather than inventing
a second matching design -- but no text parsing here, since P_820 entries
are already structured fields.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\domain\\p820_override.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   domain
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, NamedTuple, Optional, Tuple

from infrastructure.p820_reader import P820Entry

DEFAULT_FORWARD_DAYS = 3


class P820Override(NamedTuple):
    """Result of a P_820 match -- what to write, and what it replaces."""

    system:          str
    why_code:        str
    sig_code:        Optional[str]
    previous_system: str
    entry_date:      date
    gap_days:        int


def get_override(
    symbol: str,
    trade_date,
    lookup: Dict[Tuple[str, date], P820Entry],
    current_system: str,
    forward_days: int = DEFAULT_FORWARD_DAYS,
) -> Optional[P820Override]:
    """Resolve a P_820 override for one trade, if a dictated entry exists.

    Searches (symbol, trade_date), (symbol, trade_date - 1), ... down to
    (symbol, trade_date - forward_days). Returns on the first (closest)
    match. An entry can never match a LATER trade date than itself
    (forward-only, same reasoning as ThinkLog/vault windows).

    Args:
        symbol: Underlying symbol.
        trade_date: Trade's open_date -- str 'YYYY-MM-DD', date, or datetime.
        lookup: {(symbol, date): P820Entry} from
                infrastructure.p820_reader.load_p820_lookup().
        current_system: Whatever system the prior chain (ThinkLog/tracker/
                default) already resolved -- carried through as
                previous_system for audit-log reporting.
        forward_days: Max days the entry may precede the fill.

    Returns:
        P820Override if a matching entry with a non-empty why_code was
        found within the window, else None.
    """
    if not symbol or trade_date is None:
        return None

    if isinstance(trade_date, str):
        d = trade_date[:10]
    elif isinstance(trade_date, datetime):
        d = trade_date.date().isoformat()
    elif isinstance(trade_date, date):
        d = trade_date.isoformat()
    else:
        return None

    try:
        fill_date = date.fromisoformat(d)
    except ValueError:
        return None

    sym = symbol.strip().upper()
    for gap in range(0, forward_days + 1):
        candidate_date = fill_date - timedelta(days=gap)
        entry = lookup.get((sym, candidate_date))
        if entry is not None and entry["why_code"]:
            return P820Override(
                system=entry["why_code"],
                why_code=entry["why_code"],
                sig_code=entry["sig_code"],
                previous_system=current_system,
                entry_date=candidate_date,
                gap_days=gap,
            )

    return None
