# auth_workflow.py
# AI-Agent-Learning-Hub — Schwab API Integration
# Orchestrates authentication and token validation workflows

import logging

from wrappers.schwab_auth import run_oauth_flow, get_authenticated_client
from wrappers.schwab_token_manager import ensure_valid_token, load_token_config

logger = logging.getLogger(__name__)


def run_initial_auth() -> bool:
    """Run the one-time OAuth flow to get initial tokens.

    Returns:
        True if authentication succeeded.
    """
    print("\n-- Schwab Initial Authentication --")
    print("This only needs to run once (or when refresh token expires).\n")
    config = run_oauth_flow()
    if config is None:
        logger.error("Initial auth workflow failed.")
        return False
    logger.info("Initial auth workflow completed.")
    return True


def run_token_check() -> bool:
    """Verify token status and refresh if needed.

    Returns:
        True if valid token is ready for API calls.
    """
    print("\n-- Schwab Token Status Check --")
    config = load_token_config()
    if config is None:
        print("[FAIL] No saved credentials. Run: python cli.py auth")
        return False
    valid = ensure_valid_token()
    print("[OK] Token valid. Ready for API calls." if valid else "[FAIL] Token issue - see messages above.")
    return valid


def run_connection_test() -> bool:
    """Test live Schwab API connection by fetching account list.

    Returns:
        True if connection and auth are working.
    """
    print("\n-- Schwab Connection Test --")
    if not ensure_valid_token():
        return False
    try:
        client = get_authenticated_client()
        if client is None:
            print("[FAIL] Could not create authenticated client.")
            return False
        response = client.get_accounts()
        accounts = response.json()
        print(f"[OK] Connection successful. Accounts found: {len(accounts)}")
        for acct in accounts:
            acct_num  = acct.get("securitiesAccount", {}).get("accountNumber", "Unknown")
            acct_type = acct.get("securitiesAccount", {}).get("type", "Unknown")
            print(f"   Account: ...{acct_num[-4:]}  Type: {acct_type}")
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        print(f"[FAIL] Connection test failed: {e}")
        return False
