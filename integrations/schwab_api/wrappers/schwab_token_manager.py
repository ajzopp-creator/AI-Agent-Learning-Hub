# wrappers/schwab_token_manager.py
# AI-Agent-Learning-Hub — Schwab API Integration
# Token validation — checks if token file exists and is readable

import json
import logging
from typing import Optional

from config import SCHWAB_CONFIG_FILE
from wrappers.schwab_auth import get_authenticated_client, load_credentials

logger = logging.getLogger(__name__)


def load_token_config() -> Optional[dict]:
    """Load raw token config written by schwab-py.

    Returns:
        Dict of token data if file exists, None otherwise.
    """
    if not SCHWAB_CONFIG_FILE.exists():
        logger.warning("Token config file not found.")
        return None
    try:
        with open(SCHWAB_CONFIG_FILE, "r") as f:
            data = json.load(f)
        logger.info("Token config loaded successfully.")
        return data
    except Exception as e:
        logger.error(f"Failed to load token config: {e}")
        return None


def ensure_valid_token() -> bool:
    """Check token file exists and client can be created.

    schwab-py manages token refresh internally via client_from_token_file.

    Returns:
        True if valid token is ready, False if action required.
    """
    config = load_token_config()

    if config is None:
        print("[FAIL] No credentials found. Run: P_020_Schwab_Auth.bat auth")
        return False

    # Try creating a client — schwab-py will auto-refresh if needed
    client = get_authenticated_client()
    if client is None:
        print("[FAIL] Could not create authenticated client. Run: P_020_Schwab_Auth.bat auth")
        return False

    logger.info("Token valid - client created successfully.")
    return True
