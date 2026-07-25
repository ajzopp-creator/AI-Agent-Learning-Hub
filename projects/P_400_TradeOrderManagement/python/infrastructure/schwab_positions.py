"""P_400 infrastructure: fetch real held positions from Schwab (audit-book).

Read-only. Uses the shared Schwab client (WO-P400-E4.001) and the
AJZ_Strategies account -- the account P_000's balance/params track
(Tony confirmed 2026-07-24; the IRA (...9885) on the same shared config
is a separate account, not P_400-managed).
"""

from __future__ import annotations

import json
from typing import Dict

from config import SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH
from shared_resources.python_utils.schwab_client import get_client

ACCOUNT_KEY = "AJZ"


def get_real_positions() -> Dict[str, float]:
    """Return {symbol: net_quantity} for every open position in the AJZ account.

    net_quantity = longQuantity - shortQuantity. Raises on auth/API
    failure -- an audit built on stale/missing data is worse than no
    audit at all.
    """
    with open(SCHWAB_CONFIG_PATH) as f:
        cfg = json.load(f)
    last4 = str(cfg["accounts"][ACCOUNT_KEY]["last4"])

    client = get_client(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH)
    resp = client.get_account_numbers()
    if resp.status_code != 200:
        raise RuntimeError(f"get_account_numbers failed: {resp.status_code}")
    acct_map = {a["accountNumber"][-4:]: a["hashValue"] for a in resp.json()}
    if last4 not in acct_map:
        raise RuntimeError(f"AJZ account (...{last4}) not found via API")

    resp = client.get_account(acct_map[last4], fields=[client.Account.Fields.POSITIONS])
    if resp.status_code != 200:
        raise RuntimeError(f"get_account failed: {resp.status_code} {resp.text[:200]}")
    data = resp.json()
    positions = data.get("securitiesAccount", {}).get("positions", [])

    out: Dict[str, float] = {}
    for p in positions:
        symbol = p.get("instrument", {}).get("symbol", "")
        if not symbol:
            continue
        qty = p.get("longQuantity", 0.0) - p.get("shortQuantity", 0.0)
        if qty:
            out[symbol.upper()] = qty
    return out