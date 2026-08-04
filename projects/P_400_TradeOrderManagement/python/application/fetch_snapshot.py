"""fetch_snapshot.py -- `fetch-snapshot` CLI command (WO-P400-E4.002).

Orchestrates schwab_market_data + optional --earnings-date/--sector flags
into a validated SnapshotDict, written to snapshot_SYMBOL.json. Live data
for price/bid/ask/ATR/volume; earnings/sector stay web-search-sourced
(Tony's explicit call, 2026-07-21) and are passed in, never fetched here.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH
from domain.market_hours import is_market_open_now
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

    quote = get_quote_data(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH, symbol)
    if quote is None:
        print(f"[ERROR] Could not fetch live quote for {symbol}. "
              f"No file written -- fall back to manual/TOS entry.")
        return 1

    bars_result = get_daily_bars(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH, symbol)
    if bars_result is None:
        print(f"[ERROR] Could not fetch price history for {symbol}. "
              f"No file written -- fall back to manual/TOS entry.")
        return 1
    bars, volumes = bars_result

    if quote["price"] is None or quote["bid"] is None or quote["ask"] is None:
        print(f"[ERROR] Quote for {symbol} missing required price/bid/ask. "
              f"No file written -- fall back to manual/TOS entry.")
        return 1

    atr_14 = compute_atr_wilder(bars, period=14)
    recent_volumes = volumes[-20:]
    avg_volume_20d = sum(recent_volumes) / len(recent_volumes) if recent_volumes else 0.0

    now = datetime.now(timezone.utc)
    try:
        snapshot = SnapshotDict(
            symbol=symbol,
            price=quote["price"],
            bid=quote["bid"],
            ask=quote["ask"],
            price_timestamp=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            price_delay_seconds=0,
            atr_14=atr_14,
            avg_volume_20d=avg_volume_20d,
            data_source="schwab_api",
            today_volume=quote.get("today_volume"),
            next_earnings_date=earnings_date,
            sector=sector,
            last_earnings_date=last_earnings_date,
            market_open=is_market_open_now(now),
        )
    except Exception as e:
        print(f"[ERROR] SnapshotDict validation failed for {symbol}: {e}. "
              f"No file written.")
        return 1

    safe_symbol = symbol.replace("/", "_")
    out_path = PYTHON_DIR / f"snapshot_{safe_symbol}.json"
    out_path.write_text(json.dumps(snapshot.model_dump(), indent=2), encoding="utf-8")
    print(f"[OK] snapshot_{safe_symbol}.json written (data_source=schwab_api): {out_path}")
    print(f"  price={snapshot.price}  atr_14={snapshot.atr_14:.2f}  "
          f"avg_volume_20d={snapshot.avg_volume_20d:.0f}")
    return 0