"""earnings_lookup.py -- Per-symbol earnings/sector lookup for batch-2b,
sourced from the automated earnings calendar cache.

Application layer: orchestration only. Replaces batch-2b's use of the manual
earnings_YYYY-MM-DD.json file (infrastructure/earnings_file.py -- now unused
by batch-2b as of this WO; left on disk, not deleted, flagged as dead code
rather than silently orphaned -- Tony's call, no unilateral deletion).

Dates come from the monthly-refreshed cache (Nasdaq public calendar, one
call per day, merged -- see refresh_earnings_calendar.py). Sector is a live
per-symbol Nasdaq company-profile call at lookup time.

Absence-from-cache handling: a symbol missing from the cache is a HARD FAIL
(EarningsDataMissing), same as the old file-based design -- NOT an honest
null. This was originally built as honest-null under the assumption that
cache absence meant "genuinely nothing in this window," which held for a
comprehensive data source but did NOT hold for the first data source tried
(FMP's free tier, capped to ~73 large-cap symbols) -- absence there meant
"not a mega-cap," unrelated to earnings timing, which would have silently
disabled the MACRO earnings-BLOCK gate for most real signals. Switched to
Nasdaq's public calendar (full coverage, confirmed live 2026-08-08) fixes
the coverage problem, but the hard-fail is kept anyway as the correct
default: a data-source gap should stop that one symbol's evaluation, never
silently pass it through as clear. WO-P400-E5.002.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from infrastructure.earnings_calendar_cache import is_stale, load_cache
from infrastructure.earnings_calendar_client import NasdaqRequestError, fetch_company_sector
from schemas import EarningsEntry

logger = logging.getLogger("p400.earnings_lookup")


class EarningsCacheMissing(Exception):
    """Raised when the cache has never been built -- run
    refresh-earnings-calendar before batch-2b."""


class EarningsDataMissing(Exception):
    """Raised when a symbol has no entry in the earnings calendar cache.
    Deliberately fatal for that symbol rather than defaulting to clear --
    see module docstring."""


def _lookup_sector(symbol: str) -> Optional[str]:
    """Live per-symbol Nasdaq company-profile call. Failure degrades to
    None (sector is not safety-critical the way earnings dates are) rather
    than failing the whole batch -- logged, not raised."""
    try:
        return fetch_company_sector(symbol)
    except NasdaqRequestError as exc:
        logger.warning("Sector lookup failed for %s: %s", symbol, exc)
        return None


def build_entries_for_symbols(symbols: List[str]) -> Dict[str, EarningsEntry]:
    """Build the Dict[str, EarningsEntry] batch_2b_scoring.py expects, for
    exactly the symbols passed in (today's PASS list) -- not the whole cache.

    Raises:
        EarningsCacheMissing: no cache on disk yet.
        EarningsDataMissing: a requested symbol has no cache entry.
    """
    cache = load_cache()
    if cache is None:
        raise EarningsCacheMissing(
            "No earnings calendar cache found. Run "
            "`cli.py refresh-earnings-calendar` before batch-2b."
        )
    if is_stale(cache):
        logger.warning(
            "Earnings calendar cache is stale (pulled %s) -- dates may fall "
            "outside the gate's effective coverage.", cache.pulled_date,
        )
        print(f"[WARN] Earnings calendar cache is stale (pulled {cache.pulled_date}) "
              "-- run `cli.py refresh-earnings-calendar` when convenient.")

    entries: Dict[str, EarningsEntry] = {}
    for symbol in symbols:
        symbol = symbol.upper()
        cached = cache.entries.get(symbol)
        if cached is None:
            raise EarningsDataMissing(
                f"No earnings calendar entry for {symbol}. Cache pulled "
                f"{cache.pulled_date} found nothing in its window -- verify "
                "manually before evaluating this symbol."
            )
        sector = _lookup_sector(symbol)
        entries[symbol] = cached.model_copy(update={"sector": sector})
    return entries