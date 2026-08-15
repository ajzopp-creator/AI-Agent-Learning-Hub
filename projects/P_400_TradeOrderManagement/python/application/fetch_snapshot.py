"""fetch_snapshot.py -- `fetch-snapshot` CLI command (WO-P400-E4.002).

Orchestrates schwab_market_data + optional --earnings-date/--sector flags
into a validated SnapshotDict, written to snapshot_SYMBOL.json. Live data
for price/bid/ask/ATR/volume; earnings/sector stay web-search-sourced
(Tony's explicit call, 2026-07-21) and are passed in, never fetched here.

WO-P400-E5.005: when the market is closed at fetch time, skip the live
quote entirely and price off the last completed daily bar's close instead
(already pulled below for ATR -- no extra API call). bid/ask are
reconstructed as close +/- the symbol's last observed LIVE half-spread
(infrastructure/last_spread_cache.py) -- a real friction number measured
earlier, not a synthetic zero. No cached spread for this symbol yet ->
fail loud, no file written (never fabricate); the fix is to fetch this
symbol live at least once during market hours first.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH
from domain.market_hours import is_market_open_now
from infrastructure.last_spread_cache import get_last_spread, record_live_spread
from schemas import SnapshotDict
from shared_resources.python_utils.atr import compute_atr_wilder

PYTHON_DIR = Path(__file__).resolve().parents[1]  # snapshot_SYMBOL.json lives here


def cmd_fetch_snapshot(
    symbol: str,
    earnings_date: Optional[str] = None,
    sector: Optional[str] = None,
    last_earnings_date: Optional[str] = None,
) -> int:
    from infrastructure.schwab_market_data import get_daily_bars, get_quote_data

    symbol = symbol.upper()
    now = datetime.now(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    market_open = is_market_open_now(now)

    bars_result = get_daily_bars(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH, symbol)
    if bars_result is None:
        print(f"[ERROR] Could not fetch price history for {symbol}. "
              f"No file written -- fall back to manual/TOS entry.")
        return 1
    bars, volumes = bars_result

    if market_open:
        quote = get_quote_data(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH, symbol)
        if quote is None:
            print(f"[ERROR] Could not fetch live quote for {symbol}. "
                  f"No file written -- fall back to manual/TOS entry.")
            return 1
        if quote["price"] is None or quote["bid"] is None or quote["ask"] is None:
            print(f"[ERROR] Quote for {symbol} missing required price/bid/ask. "
                  f"No file written -- fall back to manual/TOS entry.")
            return 1
        price, bid, ask = quote["price"], quote["bid"], quote["ask"]
        today_volume = quote.get("today_volume")
        data_source = "schwab_api"
        price_basis = "live"

        # Record this real spread for the next closed-market fetch to reuse.
        half_spread = (ask - bid) / 2.0
        record_live_spread(symbol, half_spread=half_spread, price=price, observed_at=now_iso)
    else:
        if not bars:
            print(f"[ERROR] No daily bars available for {symbol} to price the close. "
                  f"No file written -- fall back to manual/TOS entry.")
            return 1
        close_price = bars[-1][2]  # Bar = (high, low, close); most recent completed session

        cached = get_last_spread(symbol)
        if cached is None:
            print(f"[ERROR] No live spread on record for {symbol} -- can't price the close "
                  f"without fabricating a spread. Fetch this symbol live during market "
                  f"hours at least once first. No file written.")
            return 1
        half_spread = cached.half_spread
        price = close_price
        bid, ask = close_price - half_spread, close_price + half_spread
        today_volume = None
        data_source = "schwab_api_close"
        price_basis = "close"
        print(f"[INFO] Market closed -- pricing {symbol} off last regular-session "
              f"close ({close_price}), spread from last live observation "
              f"({cached.observed_at}, half_spread={half_spread:.4f}).")

    atr_14 = compute_atr_wilder(bars, period=14)
    recent_volumes = volumes[-20:]
    avg_volume_20d = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0.0

    try:
        snapshot = SnapshotDict(
            symbol=symbol,
            price=price,
            bid=bid,
            ask=ask,
            price_timestamp=now_iso,
            price_delay_seconds=0,
            atr_14=atr_14,
            avg_volume_20d=avg_volume_20d,
            data_source=data_source,
            today_volume=today_volume,
            next_earnings_date=earnings_date,
            sector=sector,
            last_earnings_date=last_earnings_date,
            market_open=market_open,
            price_basis=price_basis,
        )
    except Exception as e:
        print(f"[ERROR] SnapshotDict validation failed for {symbol}: {e}. "
              f"No file written.")
        return 1

    safe_symbol = symbol.replace("/", "_")
    out_path = PYTHON_DIR / f"snapshot_{safe_symbol}.json"
    out_path.write_text(json.dumps(snapshot.model_dump(), indent=2), encoding="utf-8")
    print(f"[OK] snapshot_{safe_symbol}.json written (data_source={data_source}): {out_path}")
    print(f"  price={snapshot.price}  atr_14={snapshot.atr_14:.2f}  "
          f"avg_volume_20d={snapshot.avg_volume_20d:.0f}")
    return 0