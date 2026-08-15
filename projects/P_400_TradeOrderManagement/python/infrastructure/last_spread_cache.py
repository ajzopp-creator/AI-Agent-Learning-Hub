"""last_spread_cache.py -- Local JSON cache of each symbol's last observed
live regular-session half-spread.

Infrastructure layer: I/O only, no business logic. WO-P400-E5.005.

Written every time fetch_snapshot.py gets a live (market-open) quote;
read when fetch_snapshot.py prices a closed-market snapshot off the day's
close, so that path uses a real observed spread instead of a synthetic
zero. No pulled_date staleness gate like earnings_calendar_cache.py --
each symbol's entry updates independently on its own next live fetch, so
"stale" is meaningless at the cache level; a caller wanting per-entry
freshness should compare observed_at to now itself.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import ValidationError

from config import LAST_SPREAD_CACHE_PATH
from schemas import LastSpreadCache, SymbolSpreadEntry

logger = logging.getLogger("p400.last_spread_cache")


def load_cache() -> LastSpreadCache:
    """Load the cache from disk.

    Returns:
        An empty LastSpreadCache if the file doesn't exist yet (first run,
        before any live fetch) -- a real startup state, not an error.

    Raises:
        ValueError: file exists but is malformed or fails schema validation.
    """
    path = LAST_SPREAD_CACHE_PATH
    if not path.exists():
        return LastSpreadCache()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Last-spread cache {path} is not valid JSON: {exc}") from exc
    try:
        cache = LastSpreadCache(**raw)
    except ValidationError as exc:
        raise ValueError(f"Last-spread cache {path} failed validation: {exc}") from exc
    return cache


def save_cache(cache: LastSpreadCache) -> None:
    """Write the cache to disk, UTF-8, overwriting any existing file."""
    path = LAST_SPREAD_CACHE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache.model_dump(), indent=2), encoding="utf-8")
    logger.info("Wrote last-spread cache: %d symbols", len(cache.entries))


def record_live_spread(symbol: str, half_spread: float, price: float, observed_at: str) -> None:
    """Load, update one symbol's entry, save. Read-modify-write -- callers
    don't need to hold the cache object across the live-quote call."""
    cache = load_cache()
    cache.entries[symbol] = SymbolSpreadEntry(
        half_spread=half_spread, price=price, observed_at=observed_at,
    )
    save_cache(cache)


def get_last_spread(symbol: str) -> Optional[SymbolSpreadEntry]:
    """Look up one symbol's last observed live half-spread.

    Returns:
        None if this symbol has never had a live quote fetched -- caller's
        job to decide what "no real data" means for them (fetch_snapshot.py
        fails loud rather than fabricating a spread).
    """
    cache = load_cache()
    return cache.entries.get(symbol)