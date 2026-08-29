"""spread_leg_parser.py -- parses TOS multi-leg combo description strings
into structured leg data (WO-P020-E1.002, extended WO-P020-E1.002-followup
2026-08-22 for VERTICAL/IRON CONDOR).

Two distinct TOS description shapes, both handled here:

1. CUSTOM -- explicit per-leg ratio group, e.g.:
     BOT +1 1/-1/1/-1 CUSTOM SPY 100 20 FEB 26/20 FEB 26/20 FEB 26/20 FEB 26
     665/675/705/695 CALL/CALL/PUT/PUT @14.45
   The ratio group (1/-1/1/-1) gives each leg's direction directly,
   independent of the container BOT/SOLD.

2. Named strategies (VERTICAL, IRON CONDOR) -- no ratio group at all,
   single shared expiration, e.g.:
     SOLD -1 VERTICAL SPY 100 (Weeklys) 6 AUG 26 735/730 PUT @1.40
     SOLD -1 IRON CONDOR SPY 100 (Weeklys) 31 JUL 26 745/750/735/730 CALL/PUT @3.21
   Direction is inferred (Tony, confirmed 2026-08-22): for each right
   (CALL or PUT), strikes are listed short-then-long -- the first strike
   under a given right takes the container's action (short if SOLD, long
   if BOT), the second takes the opposite. Strikes divide evenly into
   pairs of 2 per right-type listed (VERTICAL: 1 type, 2 strikes, 1 pair;
   IRON CONDOR: 2 types, 4 strikes, 2 pairs) -- the same rule generalizes
   to both without special-casing either strategy name.

Both cases are only ever called on the opening line -- closing is a
normal exit at the combo level via spread_matcher.py.

Still NOT handled -- confirmed low/zero real-world volume, not silently
dangerous since both return None (graceful skip, logged/counted upstream,
never miscounted as a single-leg trade):
  - COMBO: one real fill ever seen (2026-01-30), predates the paper
    account reset (2026-06-13) -- out of scope for the backfill this
    extension exists to support. Revisit if it recurs post-reset.
  - STRANGLE: zero real fills found across every paper export checked
    2026-08-22 -- the only match anywhere was a CANCELED order, never
    filled. No implementation needed unless one actually executes.
"""

from __future__ import annotations

import re
from typing import Optional

CUSTOM_PATTERN = (
    r'(BOT|SOLD)\s+([+-])(\d+)\s+'
    r'([\d/+-]+)\s+CUSTOM\s+'
    r'([A-Z]+)\s+100\s+'
    r'((?:\d{1,2}\s+[A-Z]{3}\s+\d{2}/?)+)\s+'
    r'([\d./]+)\s+'
    r'((?:CALL|PUT)(?:/(?:CALL|PUT))*)\s+'
    r'@(-?[\d.]+)'
)

NAMED_SPREAD_PATTERN = (
    r'(BOT|SOLD)\s+([+-])(\d+)\s+'
    r'(VERTICAL|IRON CONDOR)\s+'
    r'([A-Z]+)\s+100\s+'
    r'(?:\(\w+\)\s+)?'
    r'(\d{1,2}\s+[A-Z]{3}\s+\d{2})\s+'
    r'([\d./]+)\s+'
    r'((?:CALL|PUT)(?:/(?:CALL|PUT))*)\s+'
    r'@(-?[\d.]+)'
)


def parse_multi_leg_description(desc: str) -> Optional[dict]:
    """Parse a TOS multi-leg combo DESCRIPTION string.

    Tries CUSTOM's explicit-ratio format first, then the named-strategy
    (VERTICAL/IRON CONDOR) inferred-direction format. Either shape
    returns the same dict structure -- callers don't need to know which
    one matched.

    Args:
        desc: Raw DESCRIPTION field from a TOS Account Statement TRD row.

    Returns:
        Dict with container_action, container_qty, symbol, net_price,
        leg_count, and legs (list of leg dicts), or None if the string
        doesn't match any recognized multi-leg format.
    """
    if not isinstance(desc, str):
        return None

    result = _parse_custom(desc)
    if result is not None:
        return result
    return _parse_named_spread(desc)


def _parse_custom(desc: str) -> Optional[dict]:
    """Parse the CUSTOM explicit-ratio-group format. See module docstring."""
    match = re.search(CUSTOM_PATTERN, desc)
    if not match:
        return None

    (action, sign, qty, ratio_group, symbol,
     exp_group, strike_group, type_group, price) = match.groups()

    ratios = [int(x) for x in ratio_group.split('/')]
    expirations = exp_group.split('/')
    strikes = [float(x) for x in strike_group.split('/')]
    types = type_group.split('/')

    n = len(ratios)
    if not (len(expirations) == n and len(strikes) == n and len(types) == n):
        return None  # leg-count mismatch -- unrecognized shape, skip

    legs = [
        {
            "leg_number": i + 1,
            "strike": strikes[i],
            "put_call": types[i],
            "expiration": expirations[i],
            "ratio": ratios[i],
            "direction": "long" if ratios[i] > 0 else "short",
        }
        for i in range(n)
    ]

    return {
        "container_action": action,
        "container_qty": f"{sign}{qty}",
        "symbol": symbol,
        "net_price": float(price),
        "leg_count": n,
        "legs": legs,
    }


def _parse_named_spread(desc: str) -> Optional[dict]:
    """Parse VERTICAL / IRON CONDOR's inferred-direction format.

    Strikes divide into pairs of 2 per right-type listed. Within each
    pair: first strike takes the container's action, second takes the
    opposite (Tony, confirmed 2026-08-22 -- see module docstring).
    """
    match = re.search(NAMED_SPREAD_PATTERN, desc)
    if not match:
        return None

    (action, sign, qty, strategy, symbol,
     expiration, strike_group, type_group, price) = match.groups()

    strikes = [float(x) for x in strike_group.split('/')]
    types = type_group.split('/')

    if len(strikes) != len(types) * 2:
        return None  # doesn't fit the paired-strikes shape -- unrecognized, skip

    container_direction = "long" if action == "BOT" else "short"
    opposite_direction = "short" if container_direction == "long" else "long"

    legs = []
    for type_idx, put_call in enumerate(types):
        first_strike = strikes[type_idx * 2]
        second_strike = strikes[type_idx * 2 + 1]
        legs.append({
            "leg_number": len(legs) + 1,
            "strike": first_strike,
            "put_call": put_call,
            "expiration": expiration,
            "ratio": 1 if container_direction == "long" else -1,
            "direction": container_direction,
        })
        legs.append({
            "leg_number": len(legs) + 1,
            "strike": second_strike,
            "put_call": put_call,
            "expiration": expiration,
            "ratio": 1 if opposite_direction == "long" else -1,
            "direction": opposite_direction,
        })

    return {
        "container_action": action,
        "container_qty": f"{sign}{qty}",
        "symbol": symbol,
        "net_price": float(price),
        "leg_count": len(legs),
        "legs": legs,
        "strategy": strategy,
    }
