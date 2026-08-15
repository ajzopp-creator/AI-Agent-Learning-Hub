"""earnings_calendar_cache.py -- Local JSON cache for the earnings calendar
automation.

Infrastructure layer: I/O only, no business logic. WO-P400-E5.002.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Optional

from pydantic import ValidationError

from config import EARNINGS_CALENDAR_CACHE_PATH, EARNINGS_CALENDAR_MAX_STALENESS_DAYS
from schemas import EarningsCalendarCache

logger = logging.getLogger("p400.earnings_calendar_cache")


def load_cache() -> Optional[EarningsCalendarCache]:
    """Load the cache from disk.

    Returns:
        None if the file doesn't exist yet (first run, before any refresh)
        -- a real startup state, not an error.

    Raises:
        ValueError: file exists but is malformed or fails schema validation.
    """
    path = EARNINGS_CALENDAR_CACHE_PATH
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Earnings calendar cache {path} is not valid JSON: {exc}") from exc
    try:
        cache = EarningsCalendarCache(**raw)
    except ValidationError as exc:
        raise ValueError(f"Earnings calendar cache {path} failed validation: {exc}") from exc
    logger.info("Loaded earnings calendar cache: %d symbols, pulled %s",
                len(cache.entries), cache.pulled_date)
    return cache


def save_cache(cache: EarningsCalendarCache) -> None:
    """Write the cache to disk, UTF-8, overwriting any existing file."""
    path = EARNINGS_CALENDAR_CACHE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache.model_dump(), indent=2), encoding="utf-8")
    logger.info("Wrote earnings calendar cache: %d symbols, pulled %s",
                len(cache.entries), cache.pulled_date)


def cache_age_days(cache: EarningsCalendarCache, today: Optional[date] = None) -> int:
    """Days between cache.pulled_date and today.

    A negative result would mean a clock/timezone bug -- callers should treat
    that as suspicious, not silently clamp it to zero.
    """
    today = today or date.today()
    pulled = date.fromisoformat(cache.pulled_date)
    return (today - pulled).days


def is_stale(cache: EarningsCalendarCache, today: Optional[date] = None) -> bool:
    """True if the cache is older than EARNINGS_CALENDAR_MAX_STALENESS_DAYS.

    Fixed-monthly-schedule staleness check (Tony's call, 2026-08-08): trust
    the pull date, don't spot-check individual symbols against the live API.
    """
    return cache_age_days(cache, today) > EARNINGS_CALENDAR_MAX_STALENESS_DAYS