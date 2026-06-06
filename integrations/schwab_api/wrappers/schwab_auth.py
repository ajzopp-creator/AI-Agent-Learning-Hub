# wrappers/schwab_auth.py
# AI-Agent-Learning-Hub — Schwab API Integration
# OAuth 2.0 — pure manual flow via schwab-py

import json
import logging
from datetime import datetime
from typing import Optional

import schwab

from config import SCHWAB_CALLBACK_URL, SCHWAB_CONFIG_FILE
from schemas import SchwabTokenConfig

logger = logging.getLogger(__name__)

CREDENTIALS_CACHE_FILE = SCHWAB_CONFIG_FILE.parent / "credentials_cache.json"


def load_credentials() -> tuple[str, str]:
    """Load app key and secret — prompt once, then read from cache.

    Returns:
        Tuple of (app_key, app_secret).
    """
    if CREDENTIALS_CACHE_FILE.exists():
        with open(CREDENTIALS_CACHE_FILE, "r") as f:
            data = json.load(f)
        app_key    = data.get("app_key", "")
        app_secret = data.get("app_secret", "")
        if app_key and app_secret:
            logger.info("Credentials loaded from cache.")
            return app_key, app_secret

    print("\n-- Schwab API Credentials (one-time setup) --")
    print("Find these at: developer.schwab.com -> Apps -> AJZ-Strategies-P020")
    app_key    = input("Enter App Key    : ").strip()
    app_secret = input("Enter App Secret : ").strip()

    with open(CREDENTIALS_CACHE_FILE, "w") as f:
        json.dump({"app_key": app_key, "app_secret": app_secret}, f, indent=2)
    logger.info("Credentials saved to cache.")

    return app_key, app_secret


def run_oauth_flow() -> Optional[bool]:
    """Run Schwab OAuth 2.0 manual flow via schwab-py.

    schwab-py prints the login URL — copy it, open in browser,
    log in, authorize, then paste the redirect URL back here.

    Returns:
        True on success, None on failure.
    """
    app_key, app_secret = load_credentials()

    try:
        logger.info("Starting OAuth flow.")
        print("\n-- Schwab Login --")
        print("schwab-py will print a URL below.")
        print("Copy it, paste into your browser, log in with BROKERAGE credentials.")
        print("After authorizing, copy the full redirect URL from the address bar.")
        print("It will start with: https://127.0.0.1?code=...")
        print("-" * 60)

        # schwab-py handles URL generation, state, and token exchange
        client = schwab.auth.client_from_manual_flow(
            api_key      = app_key,
            app_secret   = app_secret,
            callback_url = SCHWAB_CALLBACK_URL,
            token_path   = str(SCHWAB_CONFIG_FILE),
        )

        logger.info("OAuth flow completed successfully.")
        print("\n[OK] Authentication successful. Tokens saved.")
        return True

    except Exception as e:
        logger.error(f"OAuth flow failed: {e}")
        print(f"\n[FAIL] Authentication failed: {e}")
        return None


def get_authenticated_client() -> Optional[object]:
    """Return authenticated Schwab client from saved tokens.

    Returns:
        Authenticated schwab client, or None if tokens missing.
    """
    if not SCHWAB_CONFIG_FILE.exists():
        logger.warning("No token config found. Run auth flow first.")
        return None

    try:
        app_key, app_secret = load_credentials()
        client = schwab.auth.client_from_token_file(
            token_path = str(SCHWAB_CONFIG_FILE),
            api_key    = app_key,
            app_secret = app_secret,
        )
        logger.info("Authenticated client created from saved tokens.")
        return client

    except Exception as e:
        logger.error(f"Failed to create client from saved tokens: {e}")
        return None
