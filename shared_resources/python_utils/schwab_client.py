r"""schwab_client.py -- Hub-shared Schwab client factory (WO-P400-E4.001).

Generalized from P_020_Schwab_Token_Manager.py (projects\P_020_AJZStrategies_
PerformanceAnalysisSystem\python\api\). config_path/token_path are parameters
instead of hardcoded to P_020's own files -- same working token-refresh
behavior, callable by any project with its own config/token paths.
"""

from __future__ import annotations

import json
from pathlib import Path

import schwab


def _load_credentials(config_path: Path) -> tuple[str, str]:
    with open(config_path) as f:
        cfg = json.load(f)
    return cfg["app_key"], cfg["app_secret"]


def get_client(config_path: Path, token_path: Path):
    """Return authenticated Schwab client. Auto-refreshes token as needed."""
    if not token_path.exists():
        raise FileNotFoundError(
            f"Token not found: {token_path}\n"
            "Run: python cli.py schwab-auth"
        )
    app_key, app_secret = _load_credentials(config_path)
    try:
        client = schwab.auth.client_from_token_file(
            token_path=str(token_path),
            api_key=app_key,
            app_secret=app_secret,
        )
        return client
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Schwab client: {e}\n"
            "If token is expired, re-run: python cli.py schwab-auth"
        ) from e


def test_connection(config_path: Path, token_path: Path):
    """Quick connectivity check -- prints account numbers."""
    print("Testing Schwab API connection...", flush=True)
    try:
        client = get_client(config_path, token_path)
        resp = client.get_account_numbers()
        if resp.status_code == 200:
            accounts = resp.json()
            print(f"[OK] Connected -- {len(accounts)} account(s) found", flush=True)
            for acct in accounts:
                print(f"   Account: ...{acct['accountNumber'][-4:]}", flush=True)
            return client, accounts
        else:
            print(f"[FAIL] API returned status: {resp.status_code}", flush=True)
            return None, None
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}", flush=True)
        return None, None