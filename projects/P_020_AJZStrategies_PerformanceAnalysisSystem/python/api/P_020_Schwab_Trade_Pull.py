import json
import sys
import argparse
from datetime import datetime, timezone, date, timedelta
from pathlib import Path

# -- Paths --------------------------------------------------------------------
BASE_DIR      = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH   = BASE_DIR / "config" / "P_020_schwab_config.json"
TOKEN_PATH    = BASE_DIR / "config" / "P_020_schwab_token.json"
PULL_BASE_DIR = BASE_DIR / "data" / "api_pulls"
LAST_RUN_FILE = PULL_BASE_DIR / "P_020_last_run.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from P_020_Schwab_Token_Manager import get_client

# -- Config -------------------------------------------------------------------
def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def get_account_info(config, account_key):
    accts = config.get("accounts", {})
    if account_key == "BOTH":
        return list(accts.items())
    if account_key in accts:
        return [(account_key, accts[account_key])]
    print(f"ERROR: Unknown account '{account_key}'. Valid options: AJZ, IRA, BOTH", flush=True)
    sys.exit(1)

# -- Date helpers -------------------------------------------------------------
def get_start_date(from_arg, account_info, config):
    if from_arg is None:
        return f"{datetime.now().year}-01-01"
    if from_arg.upper() == "BOA":
        boa = account_info.get("boa")
        if not boa:
            print("ERROR: BOA date not set in config for this account.", flush=True)
            sys.exit(1)
        return boa
    try:
        datetime.strptime(from_arg, "%Y-%m-%d")
        return from_arg
    except ValueError:
        print(f"ERROR: Invalid date format '{from_arg}'. Use YYYY-MM-DD or BOA.", flush=True)
        sys.exit(1)

def get_end_date():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def split_date_range(start_str, end_str):
    """Split a date range into chunks of max 365 days (Schwab API limit)."""
    start = date.fromisoformat(start_str)
    end   = date.fromisoformat(end_str)
    chunks = []
    chunk_start = start
    while chunk_start < end:
        chunk_end = min(chunk_start + timedelta(days=364), end)
        chunks.append((chunk_start.isoformat(), chunk_end.isoformat()))
        chunk_start = chunk_end + timedelta(days=1)
    return chunks

# -- Last run tracking --------------------------------------------------------
def load_last_run(account_label):
    if LAST_RUN_FILE.exists():
        with open(LAST_RUN_FILE) as f:
            data = json.load(f)
        return data.get(account_label)
    return None

def save_last_run(account_label, end_date):
    LAST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if LAST_RUN_FILE.exists():
        with open(LAST_RUN_FILE) as f:
            data = json.load(f)
    data[account_label]    = end_date   # per-account key
    data["last_run_date"]  = end_date   # canonical key read by batch
    data["last_updated"]   = datetime.now().isoformat()
    with open(LAST_RUN_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -- Pull ---------------------------------------------------------------------
def pull_transactions(client, account_hash, account_label, start_date, end_date):
    print(f"\nPulling {account_label} ({account_hash[:8]}...)", flush=True)
    print(f"  Date range: {start_date} to {end_date}", flush=True)

    chunks = split_date_range(start_date, end_date)
    if len(chunks) > 1:
        print(f"  Range exceeds 1 year -- splitting into {len(chunks)} chunks", flush=True)

    all_transactions = []

    for chunk_start, chunk_end in chunks:
        if len(chunks) > 1:
            print(f"  Chunk: {chunk_start} to {chunk_end}", flush=True)
        try:
            resp = client.get_transactions(
                account_hash,
                start_date        = date.fromisoformat(chunk_start),
                end_date          = date.fromisoformat(chunk_end),
                transaction_types = client.Transactions.TransactionType.TRADE
            )
            if resp.status_code != 200:
                print(f"  ERROR: API status {resp.status_code}", flush=True)
                print(f"  {resp.text[:300]}", flush=True)
                return None

            chunk_transactions = resp.json()
            all_transactions.extend(chunk_transactions)
            if len(chunks) > 1:
                print(f"    Got {len(chunk_transactions)} transactions", flush=True)

        except Exception as e:
            print(f"  EXCEPTION: {e}", flush=True)
            return None

    print(f"  Raw transactions: {len(all_transactions)}", flush=True)
    trd_only = [t for t in all_transactions if t.get("type") == "TRADE"]
    print(f"  TRD transactions: {len(trd_only)}", flush=True)
    return trd_only

def save_pull(transactions, account_label, start_date, end_date):
    pull_dir = PULL_BASE_DIR / account_label.lower()
    pull_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"P_020_raw_{account_label}_{start_date}_to_{end_date}_{timestamp}.json"
    out_path  = pull_dir / filename

    payload = {
        "account_label"     : account_label,
        "start_date"        : start_date,
        "end_date"          : end_date,
        "pull_timestamp"    : datetime.now().isoformat(),
        "transaction_count" : len(transactions),
        "transactions"      : transactions
    }
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"  Saved: {out_path.name}", flush=True)
    return out_path

# -- Main ---------------------------------------------------------------------
def run():
    parser = argparse.ArgumentParser(description="P_020 Schwab Trade Pull")
    parser.add_argument("--account", default="AJZ",
                        help="Account to pull: AJZ, IRA, or BOTH (default: AJZ)")
    parser.add_argument("--from",    dest="from_date", default=None,
                        help="Start date YYYY-MM-DD or BOA (default: Jan 1 current year)")
    args = parser.parse_args()

    print("\nP_020 Schwab Trade Pull -- Phase 2B", flush=True)
    print("=" * 50, flush=True)
    print(f"Account : {args.account}", flush=True)
    print(f"From    : {args.from_date if args.from_date else 'Jan 1 ' + str(datetime.now().year)}", flush=True)

    config   = load_config()
    client   = get_client()
    end_date = get_end_date()

    account_list = get_account_info(config, args.account.upper())

    resp = client.get_account_numbers()
    if resp.status_code != 200:
        print(f"ERROR: Could not get account numbers -- {resp.status_code}", flush=True)
        sys.exit(1)

    api_accounts = {a["accountNumber"][-4:]: a["hashValue"] for a in resp.json()}

    results = []
    any_failed = False

    for acct_key, acct_info in account_list:
        last4         = acct_info["last4"]
        account_label = acct_info["label"]

        if last4 not in api_accounts:
            print(f"\nERROR: Account ...{last4} not found in API response", flush=True)
            results.append({"account": account_label, "count": 0, "file": None})
            any_failed = True
            continue

        account_hash = api_accounts[last4]
        start_date   = get_start_date(args.from_date, acct_info, config)

        transactions = pull_transactions(client, account_hash, account_label, start_date, end_date)

        if transactions is not None:
            out_path = save_pull(transactions, account_label, start_date, end_date)
            save_last_run(account_label, end_date)
            results.append({"account": account_label, "count": len(transactions), "file": out_path.name})
        else:
            results.append({"account": account_label, "count": 0, "file": None})
            any_failed = True

    print("\n" + "=" * 50, flush=True)
    print("SUMMARY", flush=True)
    print("=" * 50, flush=True)
    for r in results:
        if r["file"]:
            print(f"  {r['account']}: {r['count']} transactions -- {r['file']}", flush=True)
        else:
            print(f"  {r['account']}: FAILED", flush=True)
    print("\nPhase 2B complete.", flush=True)

    sys.exit(1 if any_failed else 0)

if __name__ == "__main__":
    run()
