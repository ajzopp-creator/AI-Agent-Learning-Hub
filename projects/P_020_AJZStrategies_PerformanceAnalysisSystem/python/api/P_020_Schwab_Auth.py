"""
P_020 Schwab Auth -- Fully Automated Re-authentication
Opens browser automatically, captures callback via UIAutomation, no copy-paste needed.
Tony only needs to log in when the browser opens.
"""
import schwab
import json
import time
import builtins
import webbrowser
import subprocess
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BASE_DIR    = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "P_020_schwab_config.json"
TOKEN_PATH  = BASE_DIR / "config" / "P_020_schwab_token.json"

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

def poll_browser():
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", POLL_PS],
            capture_output=True, text=True, timeout=8
        )
        url = result.stdout.strip()
        if url and "code=" in url:
            return url
    except Exception:
        pass
    return None

def extract_state(url):
    try:
        params = parse_qs(urlparse(url).query)
        return params.get("state", [None])[0]
    except Exception:
        return None

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        return json.load(f)

def run_auth():
    print("P_020 Schwab OAuth -- Re-authentication", flush=True)
    print("=" * 50, flush=True)

    config     = load_config()
    app_key    = config["app_key"]
    app_secret = config["app_secret"]

    captured_state = [None]
    original_print = builtins.print

    def intercept_print(*args, **kwargs):
        original_print(*args, **kwargs)
        text = " ".join(str(a) for a in args)
        if "schwabapi.com" in text and "state=" in text:
            match = re.search(r'https://api\.schwabapi\.com\S+', text)
            if match:
                state = extract_state(match.group(0))
                if state:
                    captured_state[0] = state
                    original_print("\n[Auth] Browser opening automatically...", flush=True)
                    webbrowser.open(match.group(0))

    def patched_input(prompt=""):
        for _ in range(10):
            if captured_state[0]:
                break
            time.sleep(1)

        expected_state = captured_state[0]
        original_print("\nLog in and approve access in the browser.", flush=True)
        original_print("Callback will be captured automatically.\n", flush=True)

        for i in range(120):
            url = poll_browser()
            if url:
                url_state = extract_state(url)
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
            api_key      = app_key,
            app_secret   = app_secret,
            callback_url = "https://127.0.0.1",
            token_path   = str(TOKEN_PATH)
        )
        builtins.print = original_print
        print("\nAuthentication successful!", flush=True)
        print(f"Token saved to: {TOKEN_PATH}", flush=True)
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

if __name__ == "__main__":
    run_auth()
