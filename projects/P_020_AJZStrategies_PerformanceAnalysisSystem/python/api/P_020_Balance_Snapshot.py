"""
P_020 Balance Snapshot
Pulls current account balances for AJZ Strategies (...6348) and
Inherited Roth IRA (...9885) and appends a dated row to the
running balance history CSV.
"""

import csv
import json
import sys
from datetime import datetime, date
from pathlib import Path

import schwab

BASE_DIR       = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH    = BASE_DIR / "config" / "P_020_schwab_config.json"
TOKEN_PATH     = BASE_DIR / "config" / "P_020_schwab_token.json"
SNAPSHOT_DIR   = BASE_DIR / "data" / "balance_snapshots"
HISTORY_FILE   = SNAPSHOT_DIR / "P_020_Balance_History.csv"

HISTORY_HEADERS = [
    "snapshot_date", "account_label", "account_last4", "account_type",
    "liquidation_value", "cash_available", "buying_power",
    "long_market_value", "short_market_value",
]

TARGET_ACCOUNTS = ["AJZ", "IRA"]


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_client(config):
    return schwab.auth.client_from_token_file(
        token_path=str(TOKEN_PATH),
        api_key=config["app_key"],
        app_secret=config["app_secret"],
    )


def get_account_numbers(client):
    resp = client.get_account_numbers()
    if resp.status_code != 200:
        raise RuntimeError(f"get_account_numbers failed: {resp.status_code}")
    return {a["accountNumber"][-4:]: a["hashValue"] for a in resp.json()}


def pull_balance(client, hash_value):
    resp = client.get_account(hash_value, fields=[client.Account.Fields.POSITIONS])
    if resp.status_code != 200:
        raise RuntimeError(f"get_account failed: {resp.status_code} {resp.text[:200]}")
    data = resp.json()
    balances = data.get("securitiesAccount", {}).get("currentBalances", {})
    agg      = data.get("securitiesAccount", {}).get("aggregatedBalance", {})
    return {
        "liquidation_value" : round(balances.get("liquidationValue", agg.get("currentLiquidationValue", 0.0)), 2),
        "cash_available"    : round(balances.get("cashAvailableForWithdrawal", balances.get("availableFunds", 0.0)), 2),
        "buying_power"      : round(balances.get("buyingPower", balances.get("availableFundsNonMarginableTrade", 0.0)), 2),
        "long_market_value" : round(balances.get("longMarketValue", 0.0), 2),
        "short_market_value": round(balances.get("shortMarketValue", 0.0), 2),
    }


def ensure_history_file():
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=HISTORY_HEADERS).writeheader()
        print(f"  Created: {HISTORY_FILE.name}")


def run():
    today_str = date.today().strftime("%Y%m%d")
    now_str   = datetime.now().strftime("%Y-%m-%d")
    print("=" * 55)
    print(f"  P_020 Balance Snapshot  |  {now_str}")
    print("=" * 55)
    config   = load_config()
    client   = get_client(config)
    acct_map = get_account_numbers(client)
    accts    = config.get("accounts", {})
    ensure_history_file()
    rows = []
    for key in TARGET_ACCOUNTS:
        if key not in accts:
            print(f"  SKIP {key} -- not in config"); continue
        last4    = accts[key]["last4"]
        label    = accts[key]["label"]
        if last4 not in acct_map:
            print(f"  SKIP {label} (...{last4}) -- not found via API"); continue
        try:
            b = pull_balance(client, acct_map[last4])
            rows.append({"snapshot_date": now_str, "account_label": label,
                         "account_last4": last4, "account_type": "live", **b})
            print(f"  {label} (...{last4})")
            print(f"    Liquidation value : ${b['liquidation_value']:>12,.2f}")
            print(f"    Cash available    : ${b['cash_available']:>12,.2f}")
            print(f"    Buying power      : ${b['buying_power']:>12,.2f}")
            print(f"    Long market value : ${b['long_market_value']:>12,.2f}")
            print()
        except Exception as e:
            print(f"  ERROR {label}: {e}")
    if rows:
        with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=HISTORY_HEADERS).writerows(rows)
        snap = SNAPSHOT_DIR / f"P_020_Balance_{today_str}.csv"
        with open(snap, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HISTORY_HEADERS)
            w.writeheader(); w.writerows(rows)
        print(f"  Saved: {snap.name}")
        print(f"  Appended {len(rows)} row(s) to history.")
    print("=" * 55)


if __name__ == "__main__":
    run()