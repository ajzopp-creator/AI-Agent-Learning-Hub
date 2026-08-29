"""thinklog_override.py -- Domain layer.

Pure function: given a live ThinkLog lookup and a (symbol, date) pair,
resolve the tag-driven override for system/reason/signal_strength. No
I/O -- the lookup is built by
infrastructure.thinklog_reader.build_multi_entry_lookup() and passed in.
Lookup values are already fully parsed (ParsedThinkLog dicts) -- this
function does not parse text itself.

Design decision (Tony, live session 2026-08-16): a ThinkLog tag ALWAYS
wins over whatever the vault/tracker/default chain (system_resolver.py)
already resolved. Reasoning: the tag is written by Tony himself at order
time -- ground truth, first-person, real-time. It is not a gap-filler,
it is the highest-priority source when present.

Forward-window matching (same session, real data): Tony's tags are
usually written the evening before the fill, not the same day -- SHEL
tagged 07-07, filled 07-08; MRK tagged 07-12, filled 07-13. Exact-date
matching missed both. Searches backward from the trade date up to
THINKLOG_MATCH_FORWARD_DAYS, closest date wins (mirrors the vault's
forward-only window in domain/system_resolver.py, smaller default since
this gap is a same-person typing habit, not a multi-day signal lag).

Open vocabulary, same as thinklog_parser.py -- the WHY tag is used
verbatim (uppercased) as the system value. No validation against a
fixed list: subscription services (OIL, SNT, WSZ) and future Hub
projects (P_110, P_102, etc.) all flow through identically, no schema
change needed per new source.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\domain\\thinklog_override.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   domain
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, NamedTuple, Optional, Tuple

from domain.thinklog_parser import ParsedThinkLog

DEFAULT_FORWARD_DAYS = 3


class TagOverride(NamedTuple):
    """Result of a ThinkLog tag match -- what to write, and what it replaces."""

    system:          str
    reason:          Optional[str]
    signal_strength: Optional[str]
    previous_system: str
    tag_date:        date
    gap_days:        int


def get_override(
    symbol: str,
    trade_date,
    lookup: Dict[Tuple[str, date], ParsedThinkLog],
    current_system: str,
    forward_days: int = DEFAULT_FORWARD_DAYS,
) -> Optional[TagOverride]:
    """Resolve a ThinkLog tag override for one trade, if a tag exists.

    Searches (symbol, trade_date), (symbol, trade_date - 1), ... down to
    (symbol, trade_date - forward_days). Returns on the first (closest)
    match -- a tag dated exactly on the fill wins over one dated a day
    or two earlier, which wins over one further back. A tag can never
    match a LATER trade date than its own (forward-only, same reasoning
    as the vault window) -- only earlier-or-equal dates are searched.

    Args:
        symbol: Underlying symbol.
        trade_date: Trade's open_date -- str 'YYYY-MM-DD', date, or datetime.
        lookup: {(symbol, date): ParsedThinkLog} from
                infrastructure.thinklog_reader.build_multi_entry_lookup().
        current_system: Whatever system the vault/tracker/default chain
                already resolved -- carried through as previous_system for
                audit-log reporting.
        forward_days: Max days the tag may precede the fill. Default from
                config.THINKLOG_MATCH_FORWARD_DAYS via the caller.

    Returns:
        TagOverride if a dated entry with a non-empty WHY tag was found
        within the window, else None -- meaning current_system is left
        untouched by the caller.
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
        if entry is not None and entry["reason"]:
            return TagOverride(
                system=entry["reason"],
                reason=entry["reason"],
                signal_strength=entry["signal_strength"],
                previous_system=current_system,
                tag_date=candidate_date,
                gap_days=gap,
            )

    return None
