"""Schwab positions snapshot - pulls current open positions using schwab-py client."""

import logging
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

_API_DIR = Path(__file__).resolve().parents[2] / "api"
_SKIP_SYMBOLS = {"SNVXX", "SNSXX", "SWVXX"}


def _get_client():
    if str(_API_DIR) not in sys.path:
        sys.path.insert(0, str(_API_DIR))
    from P_020_Schwab_Token_Manager import get_client
    return get_client()


def get_account_hash(last4: str) -> Optional[str]:
    """Look up encrypted account hash by last 4 digits of account number."""
    try:
        client = _get_client()
        resp = client.get_account_numbers()
        if resp.status_code != 200:
            logger.error(f"get_account_numbers failed: {resp.status_code}")
            return None
        for entry in resp.json():
            if str(entry.get("accountNumber", "")).endswith(last4):
                return entry.get("hashValue")
        logger.error(f"No account found ending in {last4}")
        return None
    except Exception as e:
        logger.error(f"get_account_hash failed: {e}")
        return None


def pull_positions(account_hash: str) -> Optional[List[dict]]:
    """Pull current open positions.

    Args:
        account_hash: Encrypted account hash from get_account_hash().

    Returns:
        List of position dicts (symbol, asset_type, qty, avg_price,
        market_value, unrealized_pnl, day_pnl), or None on failure.
    """
    try:
        client = _get_client()
    except Exception as e:
        logger.error(f"Could not get Schwab client: {e}")
        return None
    try:
        resp = client.get_account(account_hash, fields=client.Account.Fields.POSITIONS)
        if resp.status_code != 200:
            logger.error(f"Schwab API error {resp.status_code}: {resp.text[:200]}")
            return None
        acct = resp.json().get("securitiesAccount", {})
        raw_positions = acct.get("positions", [])
        positions = []
        for pos in raw_positions:
            instrument = pos.get("instrument", {})
            asset_type = instrument.get("assetType", "").upper()
            symbol = (instrument.get("symbol") or "").strip().upper()
            if symbol in _SKIP_SYMBOLS or asset_type == "CASH_EQUIVALENT":
                continue
            qty = pos.get("longQuantity", 0.0) or -pos.get("shortQuantity", 0.0)
            # Schwab API uses longOpenProfitLoss / shortOpenProfitLoss, not unrealizedProfitLoss
            unrealized_pnl = (
                pos.get("longOpenProfitLoss")
                or pos.get("shortOpenProfitLoss")
                or 0.0
            )
            positions.append({
                "symbol"        : symbol,
                "asset_type"    : asset_type,
                "qty"           : qty,
                "avg_price"     : pos.get("averagePrice", 0.0),
                "market_value"  : pos.get("marketValue", 0.0),
                "unrealized_pnl": unrealized_pnl,
                "day_pnl"       : pos.get("currentDayProfitLoss", 0.0),
            })
        logger.info(f"Pulled {len(positions)} open positions.")
        return positions
    except Exception as e:
        logger.error(f"Positions pull failed: {e}")
        return None


def print_positions_report(positions: List[dict]) -> None:
    """Print formatted positions report to console."""
    if not positions:
        print("No open positions.")
        return
    sep = "=" * 65
    div = "-" * 61
    sym_h, type_h, qty_h = "SYMBOL", "TYPE", "QTY"
    avg_h, mkt_h, pnl_h = "AVG PRICE", "MKT VALUE", "UNREAL P&L"
    print()
    print(sep)
    print(f"  OPEN POSITIONS  ({date.today().isoformat()})")
    print(sep)
    print(f"  {sym_h:<12} {type_h:<12} {qty_h:>8} {avg_h:>10} {mkt_h:>12} {pnl_h:>12}")
    print(f"  {div}")
    total_value = 0.0
    total_pnl   = 0.0
    for p in sorted(positions, key=lambda x: x["symbol"]):
        sym   = p["symbol"]
        atype = p["asset_type"]
        qty   = p["qty"]
        avg   = p["avg_price"]
        mval  = p["market_value"]
        upnl  = p["unrealized_pnl"]
        print(f"  {sym:<12} {atype:<12} {qty:>8.0f} {avg:>10.2f} {mval:>12,.2f} {upnl:>12,.2f}")
        total_value += mval
        total_pnl   += upnl
    print(f"  {div}")
    total_h = "TOTAL"
    print(f"  {total_h:<36} {total_value:>12,.2f} {total_pnl:>12,.2f}")
    print(sep)
    print()
