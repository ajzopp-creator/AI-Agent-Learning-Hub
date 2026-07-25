r"""schwab_auth.py -- Hub-shared Schwab OAuth re-authentication (WO-P400-E4.001).

Generalized from P_020_Schwab_Auth.py (projects\P_020_AJZStrategies_
PerformanceAnalysisSystem\python\api\). Opens the browser automatically,
captures the OAuth callback via UIAutomation (no copy-paste), same working
flow -- only change is config_path/token_path are parameters instead of
hardcoded to P_020's files, so any project (P_400, P_020, future) can call
this with its own paths.

Flow: schwab.auth.client_from_manual_flow() -- never build the callback URL
separately (CSRF mismatch, per p020-project-context skill). Callback is
https://127.0.0.1 with no port. Auth codes expire ~30s.
"""

from __future__ import annotations

import builtins
import json
import re
import subprocess
import time
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import schwab

POLL_PS = r"""
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$wins = $root.FindAll([System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition)
foreach ($w in $wins) {
    $editCond = New-Object System.Windows.Automation.PropertyCondition(
        [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
        [System.Windows.Automation.ControlType]::Edit)
    $edits = $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, $editCond)
    foreach ($e in $edits) {
        try {
            $vp = $e.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern)
            $val = $vp.Current.Value
            if ($val -like "*127.0.0.1*code=*") { Write-Host $val; exit }
        } catch {}
    }
}
"""


def _poll_browser() -> str | None:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", POLL_PS],
            capture_output=True, text=True, timeout=8,
        )
        url = result.stdout.strip()
        if url and "code=" in url:
            return url
    except Exception:
        pass
    return None


def _extract_state(url: str) -> str | None:
    try:
        params = parse_qs(urlparse(url).query)
        return params.get("state", [None])[0]
    except Exception:
        return None


def _load_credentials(config_path: Path) -> tuple[str, str]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path) as f:
        cfg = json.load(f)
    return cfg["app_key"], cfg["app_secret"]


def run_auth(config_path: Path, token_path: Path) -> None:
    """Run the full browser-callback OAuth flow, writing token_path on success."""
    print("Schwab OAuth -- Re-authentication", flush=True)
    print("=" * 50, flush=True)

    app_key, app_secret = _load_credentials(config_path)

    captured_state = [None]
    original_print = builtins.print

    def intercept_print(*args, **kwargs):
        original_print(*args, **kwargs)
        text = " ".join(str(a) for a in args)
        if "schwabapi.com" in text and "state=" in text:
            match = re.search(r'https://api\.schwabapi\.com\S+', text)
            if match:
                state = _extract_state(match.group(0))
                if state:
                    captured_state[0] = state
                    original_print("\n[Auth] Browser opening automatically...", flush=True)
                    webbrowser.open(match.group(0))

    def patched_input(prompt: str = "") -> str:
        for _ in range(10):
            if captured_state[0]:
                break
            time.sleep(1)

        expected_state = captured_state[0]
        original_print("\nLog in and approve access in the browser.", flush=True)
        original_print("Callback will be captured automatically.\n", flush=True)

        for i in range(120):
            url = _poll_browser()
            if url:
                url_state = _extract_state(url)
                if expected_state is None or url_state == expected_state:
                    original_print("\n[Auth] Callback captured!", flush=True)
                    return url
            if i > 0 and i % 20 == 0:
                original_print(f"  Still waiting... ({i}s elapsed)", flush=True)
            time.sleep(1)

        raise TimeoutError("Timed out waiting for Schwab callback.")

    builtins.print = intercept_print
    builtins.input = patched_input

    try:
        client = schwab.auth.client_from_manual_flow(
            api_key=app_key,
            app_secret=app_secret,
            callback_url="https://127.0.0.1",
            token_path=str(token_path),
        )
        builtins.print = original_print
        print("\nAuthentication successful!", flush=True)
        print(f"Token saved to: {token_path}", flush=True)
        resp = client.get_account_numbers()
        if resp.status_code == 200:
            accounts = resp.json()
            print(f"API test passed -- {len(accounts)} account(s):", flush=True)
            for acct in accounts:
                print(f"   ...{acct['accountNumber'][-4:]}", flush=True)
        else:
            print(f"API test status: {resp.status_code}", flush=True)

    except Exception as e:
        builtins.print = original_print
        print(f"\nAuthentication failed: {e}", flush=True)

    finally:
        builtins.print = original_print
        builtins.input = input