"""spread_leg_parser.py -- parses TOS multi-leg CUSTOM combo description
strings into structured leg data (WO-P020-E1.002).

TOS packs a multi-leg order into one DESCRIPTION line, e.g.:
    BOT +1 1/-1/1/-1 CUSTOM SPY 100 20 FEB 26/20 FEB 26/20 FEB 26/20 FEB 26
    665/675/705/695 CALL/CALL/PUT/PUT @14.45

The ratio group (1/-1/1/-1) gives each leg's direction on the OPENING
transaction, independent of the container BOT/SOLD (which just means
"open 1 unit" vs "close 1 unit" of the whole combo) -- only meaningful at
open; this module is only ever called on the opening line, per
WO-P020-E1.002 scope (closing is handled as a normal exit at the combo
level via spread_matcher.py).

Does not yet handle the "COMBO" or "(Weeklys)" description variants seen
in messier real orders -- out of scope for this WO's acceptance criteria,
returns None (graceful skip) for anything it doesn't recognize.
"""

from __future__ import annotations

import re
from typing import Optional

MULTI_LEG_PATTERN = (
    r'(BOT|SOLD)\s+([+-])(\d+)\s+'
    r'([\d/+-]+)\s+CUSTOM\s+'
    r'([A-Z]+)\s+100\s+'
    r'((?:\d{1,2}\s+[A-Z]{3}\s+\d{2}/?)+)\s+'
    r'([\d./]+)\s+'
    r'((?:CALL|PUT)(?:/(?:CALL|PUT))*)\s+'
    r'@(-?[\d.]+)'
)


def parse_multi_leg_description(desc: str) -> Optional[dict]:
    """Parse a TOS multi-leg CUSTOM combo DESCRIPTION string.

    Args:
        desc: Raw DESCRIPTION field from a TOS Account Statement TRD row.

    Returns:
        Dict with container_action, container_qty, symbol, net_price,
        leg_count, and legs (list of leg dicts), or None if the string
        doesn't match the recognized CUSTOM multi-leg format.
    """
    if not isinstance(desc, str):
        return None

    match = re.search(MULTI_LEG_PATTERN, desc)
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
