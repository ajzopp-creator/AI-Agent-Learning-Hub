"""earnings_lookup.py -- Per-symbol earnings/sector lookup for batch-2b,
sourced from the automated earnings calendar cache.

Application layer: orchestration only. Replaces batch-2b's use of the manual
earnings_YYYY-MM-DD.json file (infrastructure/earnings_file.py -- now unused
by batch-2b as of this WO; left on disk, not deleted, flagged as dead code
rather than silently orphaned -- Tony's call, no unilateral deletion).

Dates come from the monthly-refreshed cache (Nasdaq public calendar, one
call per day, merged -- see refresh_earnings_calendar.py). Sector is a live
per-symbol Nasdaq company-profile call at lookup time.

Absence-from-cache handling (WO-P400-E6.004, twice-revised 2026-08-19):
a symbol missing from the cache is now treated as genuinely clear --
next_earnings_date=None, evaluated normally -- not skipped and not
batch-fatal. This is the second revision same day; the first only fixed
the batch-abort blast radius (a miss killed every OTHER symbol too), still
skipping the missed symbol itself. That first fix exposed the real
question underneath: MACRO's actual gate (domain/earnings_window.py,
Tony's call 2026-07-28) only ever checks 3 days forward / 2 days back from
today -- not the signal's holding period, not a wide lookahead. The
calendar pull's window was cut from 83/7 days to 7/5 (config.py) to match
that gate with a small buffer, not the old FMP-era caution margin. Given
that match, "nothing found in this narrow, gate-matched window" IS the
correct clear signal -- functionally identical to earnings_in_window(None)
already returning False for an honestly-unknown date. This is different
from the original FMP-era danger this design was built against: FMP's
absence meant "not a mega-cap," unrelated to earnings timing, a real blind
spot. A miss in a 7/5-day Nasdaq pull means "no report in the only window
that matters," which is the actual answer, not a data-source gap.
WO-P400-E5.002 (original design), WO-P400-E6.004 (both revisions).
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
        EarningsCacheMissing: no cache on disk yet (the whole cache, not a
            single symbol -- this one is still batch-fatal by design, since
            it means the refresh was never run at all).

    Every requested symbol gets an entry in the returned dict -- a symbol
    missing from the cache gets a constructed EarningsEntry with
    next_earnings_date=None (confirmed clear, not unknown -- see module
    docstring) rather than being omitted. No caller-side skip path exists
    for this case anymore as of WO-P400-E6.004's second revision.
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
        sector = _lookup_sector(symbol)
        if cached is None:
            logger.info(
                "No earnings calendar entry for %s in the %s pull -- "
                "narrow window now matches MACRO's actual gate, so this is "
                "a confirmed clear, not a skip (WO-P400-E6.004, revised).",
                symbol, cache.pulled_date,
            )
            entries[symbol] = EarningsEntry(
                symbol=symbol,
                next_earnings_date=None,
                last_earnings_date=None,
                sector=sector,
                source="nasdaq_calendar_confirmed_clear",
                date_confirmed=True,
            )
            continue
        entries[symbol] = cached.model_copy(update={"sector": sector})
    return entries