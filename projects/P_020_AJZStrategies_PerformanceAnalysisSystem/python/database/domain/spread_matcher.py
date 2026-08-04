"""spread_matcher.py -- pairs multi-leg spread opens with their closes by
structure signature, and computes realized P&L (WO-P020-E1.002). REF#
differs between open and close (they're separate TOS orders), so matching
can't use REF# -- the set of (strike, put_call) pairs across all legs,
plus symbol, uniquely identifies "the same combo structure" regardless of
which order opened or closed it.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple


def _structure_signature(fill: Dict) -> Tuple[str, Tuple]:
    """Build a hashable signature identifying a combo's leg structure.

    Args:
        fill: A parsed multi-leg fill dict (has a "parsed" key from
            spread_leg_parser, plus ref/datetime/fees attached by
            paper_spread_reader).

    Returns:
        (symbol, sorted tuple of (strike, put_call) pairs).
    """
    legs = fill["parsed"]["legs"]
    strikes_types = tuple(sorted((leg["strike"], leg["put_call"]) for leg in legs))
    return (fill["parsed"]["symbol"], strikes_types)


def match_spread_opens_closes(fills: List[Dict]) -> List[Dict]:
    """Pair BOT (open) fills with their SOLD (close) fills, FIFO by signature.

    Args:
        fills: List of parsed multi-leg fill dicts.

    Returns:
        List of {"open": fill, "close": fill_or_None} dicts -- one per
        open; unclosed positions get close=None (still open).
    """
    opens_by_sig: Dict[Tuple, List[Dict]] = {}
    closes_by_sig: Dict[Tuple, List[Dict]] = {}

    for fill in fills:
        sig = _structure_signature(fill)
        action = fill["parsed"]["container_action"]
        bucket = opens_by_sig if action == "BOT" else closes_by_sig
        bucket.setdefault(sig, []).append(fill)

    for bucket in (opens_by_sig, closes_by_sig):
        for sig in bucket:
            bucket[sig].sort(key=lambda f: f["datetime"])

    matched = []
    for sig, opens in opens_by_sig.items():
        closes = list(closes_by_sig.get(sig, []))
        for open_fill in opens:
            close_fill = None
            for i, c in enumerate(closes):
                if c["datetime"] >= open_fill["datetime"]:
                    close_fill = closes.pop(i)
                    break
            matched.append({"open": open_fill, "close": close_fill})

    return matched


def compute_realized_pnl(
    open_fill: Dict, close_fill: Dict, multiplier: int = 100
) -> float:
    """Compute realized P&L for a closed spread combo.

    Args:
        open_fill: The opening fill dict.
        close_fill: The closing fill dict.
        multiplier: Options contract multiplier (default 100).

    Returns:
        Realized P&L in dollars. Sign follows the entry direction: a net
        debit (long the structure) profits when exit > entry; a net
        credit (short the structure) profits when exit < entry.
    """
    entry_price = open_fill["parsed"]["net_price"]
    exit_price = close_fill["parsed"]["net_price"]
    qty = abs(int(open_fill["parsed"]["container_qty"]))
    direction = "long" if open_fill["parsed"]["container_action"] == "BOT" else "short"

    if direction == "long":
        return round((exit_price - entry_price) * qty * multiplier, 2)
    return round((entry_price - exit_price) * qty * multiplier, 2)
