"""Schwab orders pull -- I/O only, no order-tree parsing (see domain/order_linkage.py)."""

import logging
import sys
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

_API_DIR = Path(__file__).resolve().parents[2] / "api"


def get_orders_for_account(
    account_hash: str,
    from_entered_datetime: Optional[str] = None,
    to_entered_datetime: Optional[str] = None,
    status: Optional[str] = None,
    max_results: Optional[int] = None,
) -> Optional[List[dict]]:
    """Pull raw orders for one account from Schwab.

    Returns the raw order dicts exactly as Schwab sends them -- including
    any nested childOrderStrategies -- for domain/order_linkage.py to walk.
    This function does no tree parsing itself.

    Args:
        account_hash: Encrypted hash from schwab_positions.get_account_hash().
        from_entered_datetime: ISO datetime string, inclusive lower bound.
            Schwab requires this if to_entered_datetime is given.
        to_entered_datetime: ISO datetime string, inclusive upper bound.
        status: Optional Schwab status filter (e.g. "FILLED", "WORKING").
        max_results: Optional cap on number of orders returned.

    Returns:
        List of raw order dicts, or None on failure.
    """
    try:
        if str(_API_DIR) not in sys.path:
            sys.path.insert(0, str(_API_DIR))
        from P_020_Schwab_Token_Manager import get_client
        client = get_client()
    except Exception as e:
        logger.error(f"Could not get Schwab client: {e}")
        return None
    try:
        resp = client.get_orders_for_account(
            account_hash,
            from_entered_datetime=from_entered_datetime,
            to_entered_datetime=to_entered_datetime,
            status=status,
            max_results=max_results,
        )
        if resp.status_code != 200:
            logger.error(f"Schwab API error {resp.status_code}: {resp.text[:200]}")
            return None
        orders = resp.json()
        logger.info(f"Pulled {len(orders)} orders.")
        return orders
    except Exception as e:
        logger.error(f"Orders pull failed: {e}")
        return None
