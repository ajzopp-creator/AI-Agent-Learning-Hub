"""refresh_earnings_calendar.py -- Monthly refresh of the earnings calendar
cache.

Application layer: orchestration only. Pulls Nasdaq's public earnings
calendar one day at a time across a ~90-day window (a short backward buffer
plus the forward lookahead) and merges into one cache. No sector here --
sector is a lazy per-symbol call at lookup time (application/earnings_lookup.py).

No scheduler -- Tony triggers this manually on a monthly cadence via
`cli.py refresh-earnings-calendar`. WO-P400-E5.002.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from config import (
    EARNINGS_CALENDAR_LOOKAHEAD_DAYS,
    EARNINGS_CALENDAR_LOOKBACK_BUFFER_DAYS,
)
from infrastructure.earnings_calendar_cache import save_cache
from infrastructure.earnings_calendar_client import NasdaqRequestError, fetch_earnings_for_date
from schemas import EarningsCalendarCache, EarningsEntry

logger = logging.getLogger("p400.refresh_earnings_calendar")


def _date_range(today: Optional[date] = None) -> List[date]:
    today = today or date.today()
    start = today - timedelta(days=EARNINGS_CALENDAR_LOOKBACK_BUFFER_DAYS)
    end = today + timedelta(days=EARNINGS_CALENDAR_LOOKAHEAD_DAYS)
    span = (end - start).days
    return [start + timedelta(days=n) for n in range(span + 1)]


def _pull_all_records(days: List[date]) -> List[dict]:
    """One Nasdaq call per day, merged. A single day's failure (e.g. a
    transient block) is logged and skipped, not fatal to the whole refresh
    -- weekends/holidays legitimately return zero rows, and a bad day
    shouldn't cost the other ~89."""
    all_records: List[dict] = []
    for day in days:
        try:
            rows = fetch_earnings_for_date(day.isoformat())
        except NasdaqRequestError as exc:
            logger.warning("Skipping %s: %s", day.isoformat(), exc)
            continue
        for row in rows:
            row.setdefault("date", day.isoformat())
        all_records.extend(rows)
    return all_records


def _collapse_to_entries(records: List[dict], today: date) -> Dict[str, EarningsEntry]:
    """Collapse Nasdaq's date-indexed rows into one EarningsEntry per symbol.

    A symbol can appear more than once in the window (a past report and an
    upcoming one). Keeps the nearest future date as next_earnings_date and
    the nearest past-or-today date as last_earnings_date.
    """
    nearest_next: Dict[str, date] = {}
    nearest_last: Dict[str, date] = {}
    for row in records:
        symbol = row.get("symbol")
        row_date_str = row.get("date")
        if not symbol or not row_date_str:
            continue
        symbol = symbol.upper()
        try:
            row_date = date.fromisoformat(row_date_str)
        except ValueError:
            continue
        if row_date >= today:
            if symbol not in nearest_next or row_date < nearest_next[symbol]:
                nearest_next[symbol] = row_date
        else:
            if symbol not in nearest_last or row_date > nearest_last[symbol]:
                nearest_last[symbol] = row_date

    symbols = set(nearest_next) | set(nearest_last)
    entries: Dict[str, EarningsEntry] = {}
    for symbol in symbols:
        entries[symbol] = EarningsEntry(
            symbol=symbol,
            next_earnings_date=nearest_next.get(symbol).isoformat() if symbol in nearest_next else None,
            last_earnings_date=nearest_last.get(symbol).isoformat() if symbol in nearest_last else None,
            sector=None,   # lazy, per-symbol at lookup time -- not here
            source="nasdaq_calendar",
            date_confirmed=True,   # Nasdaq-reported, not cadence-estimated
        )
    return entries


def refresh_earnings_calendar() -> EarningsCalendarCache:
    """Pull the window, build the cache, write it to disk. Public entry
    point for cmd_refresh_earnings_calendar() and for tests."""
    today = date.today()
    days = _date_range(today)
    records = _pull_all_records(days)
    entries = _collapse_to_entries(records, today)
    cache = EarningsCalendarCache(pulled_date=today.isoformat(), entries=entries)
    save_cache(cache)
    return cache


def cmd_refresh_earnings_calendar() -> int:
    """`refresh-earnings-calendar` CLI entry point."""
    cache = refresh_earnings_calendar()
    print("=" * 70)
    print(f"EARNINGS CALENDAR REFRESH  |  pulled {cache.pulled_date}  |  "
          f"{len(cache.entries)} symbols")
    print("=" * 70)
    return 0