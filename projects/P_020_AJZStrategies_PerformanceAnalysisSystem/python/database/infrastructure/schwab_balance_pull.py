"""Schwab balance snapshot - pulls current and start-of-day balance using schwab-py client."""

import logging
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Path to the Phase 2 Token Manager
_API_DIR = Path(__file__).resolve().parents[2] / "api"


def _get_client():
    """Get authenticated schwab-py client via existing Token Manager."""
    if str(_API_DIR) not in sys.path:
        sys.path.insert(0, str(_API_DIR))
    from P_020_Schwab_Token_Manager import get_client
    return get_client()


def pull_balance(account_hash: str) -> Optional[dict]:
    """Pull current and start-of-day balance using schwab-py client.

    Uses GET /accounts/{accountHash} which returns both
    initialBalances (start of day) and currentBalances (real-time).

    Args:
        account_hash: Encrypted account hash from get_account_numbers().

    Returns:
        Dict with total_value, start_of_day_value, cash_available,
        buying_power, day_pnl or None on failure.
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

        data = resp.json()
        acct = data.get("securitiesAccount", {})

        curr = acct.get("currentBalances", {})
        init = acct.get("initialBalances", {})

        total_value = (
            curr.get("liquidationValue")
            or curr.get("totalValue")
            or 0.0
        )
        start_of_day = (
            init.get("liquidationValue")
            or init.get("totalValue")
            or init.get("accountValue")
            or None
        )

        return {
            "total_value"       : total_value,
            "start_of_day_value": start_of_day,
            "cash_available"    : curr.get("cashAvailableForTrading"),
            "buying_power"      : curr.get("buyingPower"),
            "day_pnl"           : curr.get("dayProfitLoss"),
        }

    except Exception as e:
        logger.error(f"Balance pull failed: {e}")
        return None


def get_account_hash(last4: str) -> Optional[str]:
    """Look up the encrypted account hash for an account by last 4 digits.

    Args:
        last4: Last 4 digits of account number (e.g. '6348').

    Returns:
        Encrypted account hash string, or None if not found.
    """
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


def store_balance(
    conn: sqlite3.Connection,
    account_id: str,
    balance: dict,
    snapshot_date: Optional[date] = None,
) -> bool:
    """Insert or replace a balance snapshot row.

    Args:
        conn: Active SQLite connection.
        account_id: DB account_id (e.g. 'AJZ6348').
        balance: Dict from pull_balance().
        snapshot_date: Date for snapshot - defaults to today.

    Returns:
        True on success, False on failure.
    """
    snap_date = (snapshot_date or date.today()).isoformat()
    try:
        conn.execute("""
            INSERT INTO account_balances
                (account_id, snapshot_date, total_value, start_of_day_value,
                 cash_available, buying_power, day_pnl, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'schwab_api')
            ON CONFLICT(account_id, snapshot_date) DO UPDATE SET
                total_value        = excluded.total_value,
                start_of_day_value = excluded.start_of_day_value,
                cash_available     = excluded.cash_available,
                buying_power       = excluded.buying_power,
                day_pnl            = excluded.day_pnl,
                created_at         = CURRENT_TIMESTAMP
        """, (
            account_id,
            snap_date,
            balance["total_value"],
            balance.get("start_of_day_value"),
            balance.get("cash_available"),
            balance.get("buying_power"),
            balance.get("day_pnl"),
        ))
        conn.commit()
        logger.info(
            f"Balance snapshot saved: {account_id} {snap_date} "
            f"current=${balance['total_value']:,.2f}"
            + (f"  start-of-day=${balance['start_of_day_value']:,.2f}"
               if balance.get("start_of_day_value") else "")
        )
        return True
    except Exception as e:
        logger.error(f"Failed to store balance: {e}")
        return False