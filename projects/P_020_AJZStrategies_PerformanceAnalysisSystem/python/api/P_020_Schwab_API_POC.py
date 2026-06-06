#!/usr/bin/env python3
"""
P_020 Schwab API Proof-of-Concept v2
=====================================
Fixed: callback URL port + Windows multiprocessing guard
"""

import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta


def main():
    # ── Load credentials ──────────────────────────────────────────────────
    CREDS_PATH = Path(__file__).parent / "schwab_credentials.py"
    spec = importlib.util.spec_from_file_location("creds", CREDS_PATH)
    creds = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(creds)

    if "PASTE_YOUR" in creds.APP_KEY:
        print("ERROR: Fill in your credentials in schwab_credentials.py first.")
        sys.exit(1)

    print("=" * 70)
    print("P_020 SCHWAB API PROOF-OF-CONCEPT")
    print("=" * 70)

    # ── Authenticate ──────────────────────────────────────────────────────
    print("\nStep 1: Authenticating with Schwab...")
    print("  Your browser will open — log in and authorize the app.")
    print("  Then copy the redirect URL and paste it back here.\n")

    import schwab

    try:
        client = schwab.auth.easy_client(
            api_key=creds.APP_KEY,
            app_secret=creds.APP_SECRET,
            callback_url=creds.CALLBACK_URL,
            token_path=creds.TOKEN_PATH
        )
        print("  Authentication successful")
    except Exception as e:
        print(f"  Authentication failed: {e}")
        sys.exit(1)

    # ── Get Account Numbers ───────────────────────────────────────────────
    print("\nStep 2: Getting account numbers...")
    try:
        resp = client.get_account_numbers()
        accounts = resp.json()
        print(f"  Found {len(accounts)} account(s):")
        for acct in accounts:
            print(f"    Account: ...{acct['accountNumber'][-4:]}  Hash: {acct['hashValue'][:16]}...")
        account_hash = accounts[0]['hashValue']
        account_num  = accounts[0]['accountNumber']
        print(f"\n  Using account ending in: ...{account_num[-4:]}")
    except Exception as e:
        print(f"  Failed to get accounts: {e}")
        sys.exit(1)

    # ── Pull Transactions ─────────────────────────────────────────────────
    print("\nStep 3: Pulling transaction history (last 60 days)...")
    end_date   = datetime.now()
    start_date = end_date - timedelta(days=60)

    try:
        resp = client.get_transactions(
            account_hash=account_hash,
            start_date=start_date,
            end_date=end_date,
            types=client.Transaction.TransactionType.TRADE
        )
        transactions = resp.json()
        print(f"  Retrieved {len(transactions)} TRADE transactions")
    except Exception as e:
        print(f"  Failed to get transactions: {e}")
        sys.exit(1)

    # ── Show Raw Structure of First 2 records ─────────────────────────────
    print("\nStep 4: Raw API structure (first 2 transactions)...")
    print("-" * 70)
    for txn in transactions[:2]:
        print(json.dumps(txn, indent=2, default=str))
        print("-" * 70)

    # ── Extract Key Fields ────────────────────────────────────────────────
    print("\nStep 5: Key fields extracted...")
    print(f"{'Date':<12} {'Symbol':<22} {'Instruction':<18} {'Qty':>5} {'Price':>8} {'Comm':>7} {'Type':<8}")
    print("-" * 70)

    options_count = 0
    stocks_count  = 0

    for txn in transactions:
        try:
            txn_date = txn.get('tradeDate', txn.get('transactionDate', ''))[:10]
            for item in txn.get('transferItems', []):
                instrument  = item.get('instrument', {})
                asset_type  = instrument.get('assetType', '')
                symbol      = instrument.get('symbol', '')
                instruction = item.get('instruction', '')
                quantity    = item.get('amount', 0)
                price       = item.get('price', 0) or 0
                commission  = txn.get('fees', {}).get('commission', 0) or 0

                if asset_type == 'OPTION':
                    put_call    = instrument.get('putCall', '')
                    strike      = instrument.get('strikePrice', '')
                    display_sym = f"{symbol} {put_call} {strike}"
                    options_count += 1
                else:
                    display_sym = symbol
                    stocks_count += 1

                print(f"{txn_date:<12} {display_sym:<22} {instruction:<18} {quantity:>5} {float(price):>8.2f} {float(commission):>7.2f} {asset_type:<8}")
        except Exception:
            continue

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Options transactions: {options_count}")
    print(f"  Stock  transactions:  {stocks_count}")
    print(f"  Total:                {options_count + stocks_count}")
    print("\nAPI proof-of-concept complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
