"""_debug_raw_quote.py -- throwaway diagnostic (WO-P400-E7.001 support).

Dumps the FULL raw Schwab /quotes response for a symbol, unfiltered --
not just the price/bid/ask fields get_extended_quote_data() extracts.
Purpose: confirm whether a 0.0/0.0 extended bid/ask is a real empty
market or a data-feed quirk (stale quoteTime, missing size fields, etc.)
before trusting it as ground truth for E7.001's live-verification.

Usage:
    python _debug_raw_quote.py SYMBOL

Not a permanent file -- delete after diagnosis, not wired into cli.py.
"""

import json
import sys

from config import SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH
from shared_resources.python_utils.schwab_client import get_client


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python _debug_raw_quote.py SYMBOL")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    client = get_client(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH)
    resp = client.get_quotes([symbol])

    print(f"HTTP status: {resp.status_code}")
    if resp.status_code != 200:
        print(resp.text)
        sys.exit(1)

    data = resp.json()
    entry = data.get(symbol)
    if entry is None:
        print(f"No entry for {symbol} in response. Full response:")
        print(json.dumps(data, indent=2))
        sys.exit(1)

    print(f"\n=== FULL entry for {symbol} ===")
    print(json.dumps(entry, indent=2))

    ext = entry.get("extended")
    if ext:
        print("\n=== 'extended' node only ===")
        print(json.dumps(ext, indent=2))
    else:
        print("\nNo 'extended' key present in this response at all.")


if __name__ == "__main__":
    main()