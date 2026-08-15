"""earnings_calendar_client.py -- Nasdaq public API client for the earnings
calendar automation.

Infrastructure layer: I/O only, no business logic. Raises on any failure --
caller decides how to handle. Uses httpx (already a proven dependency in
this env via schwab-py). No API key -- these are Nasdaq's public,
unauthenticated endpoints; a browser-like User-Agent header is required or
Nasdaq blocks the request. See config.py's earnings-calendar section for why
this replaced the original FMP design. WO-P400-E5.002.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import httpx

from config import NASDAQ_API_BASE_URL, NASDAQ_USER_AGENT

logger = logging.getLogger("p400.earnings_calendar_client")

_HEADERS = {"User-Agent": NASDAQ_USER_AGENT}


class NasdaqRequestError(Exception):
    """Raised when a Nasdaq public API call fails (network, HTTP status,
    or malformed body)."""


def fetch_earnings_for_date(day: str) -> List[dict]:
    """Pull every company reporting earnings on one calendar date.

    Nasdaq's endpoint is per-date, not per-range -- the monthly refresh
    calls this once per day across the window and merges results.

    Args:
        day: ISO YYYY-MM-DD.

    Returns:
        Raw list of Nasdaq calendar records (dicts with at least "symbol").
        Caller validates/transforms.

    Raises:
        NasdaqRequestError: network failure, non-200 status, or malformed body.
    """
    url = f"{NASDAQ_API_BASE_URL}/calendar/earnings"
    params = {"date": day}
    try:
        resp = httpx.get(url, params=params, headers=_HEADERS, timeout=30)
    except httpx.HTTPError as exc:
        raise NasdaqRequestError(f"Nasdaq earnings calendar request failed for {day}: {exc}") from exc

    if resp.status_code != 200:
        raise NasdaqRequestError(
            f"Nasdaq earnings calendar for {day} returned HTTP {resp.status_code}: {resp.text[:300]}"
        )

    try:
        data = resp.json()
    except ValueError as exc:
        raise NasdaqRequestError(f"Nasdaq earnings calendar for {day} returned non-JSON body: {exc}") from exc

    rows = ((data or {}).get("data") or {}).get("rows")
    if rows is None:
        # No earnings that day (weekend/holiday) is a real, common, non-error
        # state -- Nasdaq returns data.rows: null, not an empty list.
        return []
    if not isinstance(rows, list):
        raise NasdaqRequestError(
            f"Nasdaq earnings calendar for {day} expected a list of rows, "
            f"got {type(rows).__name__}: {str(rows)[:300]}"
        )
    return rows


def fetch_company_sector(symbol: str) -> Optional[str]:
    """Pull one symbol's sector from Nasdaq's company-profile endpoint.

    Called lazily per PASS symbol at lookup time, matching the original
    per-symbol-not-bulk design intent (Nasdaq's profile endpoint has no
    bulk form anyway).

    Returns:
        Sector string, or None if Nasdaq has no profile / no sector for
        this symbol (honest-null, not fabricated).

    Raises:
        NasdaqRequestError: network failure or non-200 status.
    """
    url = f"{NASDAQ_API_BASE_URL}/company/{symbol.upper()}/company-profile"
    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=30)
    except httpx.HTTPError as exc:
        raise NasdaqRequestError(f"Nasdaq company-profile request failed for {symbol}: {exc}") from exc

    if resp.status_code != 200:
        raise NasdaqRequestError(
            f"Nasdaq company-profile for {symbol} returned HTTP {resp.status_code}: {resp.text[:300]}"
        )

    try:
        data = resp.json()
    except ValueError as exc:
        raise NasdaqRequestError(f"Nasdaq company-profile for {symbol} returned non-JSON body: {exc}") from exc

    sector_field = ((data or {}).get("data") or {}).get("Sector") or {}
    sector = sector_field.get("value")
    return sector or None