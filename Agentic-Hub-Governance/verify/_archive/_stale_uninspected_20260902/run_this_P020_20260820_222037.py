"""WO-P020-E1.014 follow-up -- diagnostic ONLY, read-only. Dumps every
field in Schwab's raw currentBalances/initialBalances response for the
AJZ account so Tony's TOS screenshot numbers (Option Buying Power, Net
Liq, Intraday Buying Power, Cash & Sweep Vehicle, Available Funds For
Trading, Cash Balance) can be matched against real API field names.

Does NOT write to the DB, the P_000 params file, or any production file.
Read-only against the live Schwab API only.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DONE_MARKER = SCRIPT_DIR / (Path(__file__).name + ".done")

PROJECT_ROOT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)
sys.path.insert(0, str(PROJECT_ROOT))


def write_done(status: str, exit_code: int) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    DONE_MARKER.write_text(
        f"status={status}\nexit_code={exit_code}\ntimestamp={ts}\n",
        encoding="utf-8",
    )


def main() -> None:
    from infrastructure.schwab_balance_pull import _get_client, get_account_hash

    account_hash = get_account_hash("6348")
    if not account_hash:
        print("FAIL: could not get account hash")
        write_done("FAIL", 1)
        sys.exit(1)

    client = _get_client()
    resp = client.get_account(account_hash, fields=client.Account.Fields.POSITIONS)
    if resp.status_code != 200:
        print(f"FAIL: Schwab API error {resp.status_code}: {resp.text[:300]}")
        write_done("FAIL", 1)
        sys.exit(1)

    data = resp.json()
    acct = data.get("securitiesAccount", {})
    curr = acct.get("currentBalances", {})
    init = acct.get("initialBalances", {})

    print("=" * 70)
    print("RAW currentBalances (all fields, sorted)")
    print("=" * 70)
    for key in sorted(curr.keys()):
        print(f"  {key:35s} = {curr[key]}")

    print()
    print("=" * 70)
    print("RAW initialBalances (all fields, sorted) -- for comparison only")
    print("=" * 70)
    for key in sorted(init.keys()):
        print(f"  {key:35s} = {init[key]}")

    print()
    print("=" * 70)
    print("Currently parsed by pull_balance():")
    print(f"  cashAvailableForTrading = {curr.get('cashAvailableForTrading')}")
    print(f"  buyingPower             = {curr.get('buyingPower')}")
    print("=" * 70)

    # Full raw JSON dump too, in case a field lives outside currentBalances/initialBalances
    print()
    print("Full raw account JSON (for reference, do not parse by hand):")
    print(json.dumps(data, indent=2, default=str))

    print()
    print("PASS")
    write_done("PASS", 0)


if __name__ == "__main__":
    main()
