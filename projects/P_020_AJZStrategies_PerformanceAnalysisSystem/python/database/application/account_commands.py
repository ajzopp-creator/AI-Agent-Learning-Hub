"""Account snapshot commands — balance pull and open-positions pull.

Moved out of P_020_Trade_Manager.py (WO-P020-E1.006) to keep the CLI
entry point thin. No behavior change from the original cmd_balance /
cmd_positions.
"""

import logging
import sys

logger = logging.getLogger(__name__)

ACCOUNT_MAP = {"AJZ": ("AJZ6348", "6348"), "IRA": ("IRA9885", "9885")}


def run_balance_command(account: str) -> None:
    """Pull current Schwab account balance and store as weekly snapshot.

    Args:
        account: CLI --account value ('AJZ' or 'IRA').

    Exits(1) on failure -- matches original cmd_balance behavior.
    """
    from infrastructure.db_client import get_connection
    from infrastructure.schwab_balance_pull import get_account_hash, pull_balance, store_balance

    account_id, last4 = ACCOUNT_MAP.get(account.upper(), ("AJZ6348", "6348"))
    logger.info(f"Pulling balance for account: {account_id}")

    account_hash = get_account_hash(last4)
    if not account_hash:
        logger.error("Could not retrieve account hash -- check token and connection.")
        sys.exit(1)

    balance = pull_balance(account_hash)
    if not balance:
        logger.error("Balance pull failed -- check token and connection.")
        sys.exit(1)

    conn = get_connection()
    ok = store_balance(conn, account_id, balance)
    conn.close()

    if not ok:
        sys.exit(1)

    print(f"Balance snapshot saved: {account_id}")
    print(f"  Total value   : ${balance['total_value']:>12,.2f}")
    if balance.get('cash_available') is not None:
        print(f"  Cash available: ${balance['cash_available']:>12,.2f}")
    if balance.get('buying_power') is not None:
        print(f"  Buying power  : ${balance['buying_power']:>12,.2f}")
    if balance.get('day_pnl') is not None:
        print(f"  Day P&L       : ${balance['day_pnl']:>12,.2f}")


def run_positions_command(account: str) -> None:
    """Pull and display current open positions from Schwab.

    Args:
        account: CLI --account value ('AJZ' or 'IRA').

    Exits(1) on failure -- matches original cmd_positions behavior.
    """
    from infrastructure.schwab_positions import get_account_hash, print_positions_report, pull_positions

    account_id, last4 = ACCOUNT_MAP.get(account.upper(), ("AJZ6348", "6348"))
    logger.info(f"Pulling positions for account: {account_id}")

    account_hash = get_account_hash(last4)
    if not account_hash:
        logger.error("Could not retrieve account hash -- check token and connection.")
        sys.exit(1)

    positions = pull_positions(account_hash)
    if positions is None:
        logger.error("Positions pull failed -- check token and connection.")
        sys.exit(1)

    print_positions_report(positions)
