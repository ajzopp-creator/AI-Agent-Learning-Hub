import schwab
import json
import sys
from pathlib import Path

# -- Paths -- project config is the single source of truth -------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR   = PROJECT_ROOT / "config"
TOKEN_PATH   = CONFIG_DIR / "P_020_schwab_token.json"   # written by P_020_Schwab_Auth.py
CONFIG_PATH  = CONFIG_DIR / "P_020_schwab_config.json"  # app_key + app_secret


def _load_credentials():
    """Load app_key and app_secret from project config."""
    with open(CONFIG_PATH) as f:
        cfg = json.load(f)
    return cfg["app_key"], cfg["app_secret"]


def get_client():
    """Return authenticated Schwab client. Auto-refreshes token as needed."""
    if not TOKEN_PATH.exists():
        raise FileNotFoundError(
            f"Token not found: {TOKEN_PATH}\n"
            "Run: python P_020_Schwab_Auth.py"
        )
    app_key, app_secret = _load_credentials()
    try:
        client = schwab.auth.client_from_token_file(
            token_path = str(TOKEN_PATH),
            api_key    = app_key,
            app_secret = app_secret,
        )
        return client
    except Exception as e:
        raise RuntimeError(
            f"Failed to load Schwab client: {e}\n"
            "If token is expired, re-run: python P_020_Schwab_Auth.py"
        ) from e


def test_connection():
    """Quick connectivity check -- prints account numbers."""
    print("Testing Schwab API connection...", flush=True)
    try:
        client = get_client()
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


def _main() -> None:
    """CLI entry point -- exits non-zero on failed token pre-flight check.

    WO-P020-E1.007: weekly update Step 0 calls this script directly and
    relies on the exit code -- fail loud, don't just print and return, or
    the calling .bat can't tell success from failure. Split into a plain
    function so the exit-code contract is unit-testable without spawning
    a subprocess.
    """
    _, accounts = test_connection()
    if accounts is None:
        print("[FAIL] Token pre-flight check failed -- reauth required.", flush=True)
        print("Run: P_020_Schwab_Auth.bat", flush=True)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    _main()