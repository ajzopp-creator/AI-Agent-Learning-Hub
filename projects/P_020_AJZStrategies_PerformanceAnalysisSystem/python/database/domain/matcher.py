"""Pure matching logic for system name assignment - no I/O."""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Type alias - matches tracker_reader.TrackerLookup
TrackerLookup = Dict[Tuple[str, str], str]


def normalize_symbol(raw: str) -> str:
    """Strip option suffixes, spaces, special chars. Return uppercase."""
    cleaned = raw.strip().upper()
    cleaned = cleaned.split()[0]
    cleaned = re.split(r"[_\-]", cleaned)[0]
    return cleaned


def normalize_date(raw) -> Optional[str]:
    """Convert various date formats to YYYY-MM-DD string."""
    if raw is None:
        return None
    try:
        if hasattr(raw, "strftime"):
            return raw.strftime("%Y-%m-%d")
        for fmt in ("%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(str(raw).strip(), fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    except Exception:
        pass
    logger.debug(f"Could not normalize date: {raw!r}")
    return None


def match_system(
    symbol: str,
    open_date: str,
    lookup,
    default: str = "TOS_Import",
    window_days: int = 3,
) -> str:
    """Match a trade to its system name using the Tracker Dashboard lookup.

    Tries exact date first, then collects ALL matches within +-window_days
    and returns the one with the closest date. This handles cases where the
    same symbol appears in the Tracker from multiple systems on different dates
    (e.g., IBM from P_117 on one date and IBM from SNT on another date).
    """
    if lookup is None:
        return default

    norm_sym = normalize_symbol(symbol)

    # Exact match first
    result = lookup.get(norm_sym, open_date, None)
    if result is not None and result != default:
        logger.debug(f"Tracker exact match: ({norm_sym}, {open_date}) -> '{result}'")
        return result

    # Window search: collect ALL matches and pick closest date
    try:
        trade_date = datetime.strptime(open_date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        logger.debug(f"Could not parse open_date: {open_date!r} -- using '{default}'.")
        return default

    best_result = None
    best_delta = window_days + 1

    for delta in range(1, window_days + 1):
        for offset in (delta, -delta):
            candidate = (trade_date + timedelta(days=offset)).strftime("%Y-%m-%d")
            result = lookup.get(norm_sym, candidate, None)
            if result is not None and result != default and abs(offset) < best_delta:
                best_result = result
                best_delta = abs(offset)

    if best_result is not None:
        logger.debug(
            f"Tracker window match: ({norm_sym}, {open_date}) "
            f"closest={best_delta}d -> '{best_result}'"
        )
        return best_result

    logger.debug(
        f"No Tracker match for ({norm_sym}, {open_date}) +/-{window_days}d "
        f"-- using '{default}'."
    )
    return default


def match_all_trades(
    trades: List[Dict],
    lookup,
    default: str = "TOS_Import",
) -> List[Dict]:
    """Apply system name matching to a list of trade dicts in place."""
    matched = 0
    for trade in trades:
        system = match_system(
            symbol=trade.get("underlying_symbol", ""),
            open_date=str(trade.get("open_date", "")),
            lookup=lookup,
            default=default,
        )
        trade["system"] = system
        if system != default:
            matched += 1

    total = len(trades)
    logger.info(
        f"System matching complete: {matched}/{total} matched, "
        f"{total - matched} defaulted to '{default}'."
    )
    return trades
