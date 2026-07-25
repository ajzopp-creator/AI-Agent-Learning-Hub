"""
FILE: chaikin_reader.py
VERSION: 1.0
DATE: 2026-07-03
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Scrapes the Chaikin Analytics Power Gauge Rating for a symbol via
    Playwright. Read-only external data source -- output feeds the P300
    Obsidian note as supplementary context for P_400, never the
    BUY/WATCH/PASS decision path (NFR-1).

    Session handling:
      First call with no saved session opens a VISIBLE browser and waits
      for the operator to log into Chaikin manually (handles 2FA/CAPTCHA
      without any code needing to know about them). Once login succeeds,
      Playwright's storage_state is saved to disk. Every call after that
      runs headless, reusing the saved session -- no browser window, no
      repeated login, until the session expires (Chaikin will redirect to
      a login page again; the same interactive-login path re-triggers).

    Non-blocking by design -- callers should catch ChaikinReadError and
    proceed without a Power Gauge value rather than block a signal.

CHANGELOG:
    - 2026-07-03 v1.0: Initial version.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from config import CHAIKIN_BASE_URL, CHAIKIN_SESSION_FILE
from schemas import PowerGaugeResult

logger = logging.getLogger(__name__)

# Chaikin's Power Gauge rating renders as an <h1> inside
# .rating-widget-wrapper, e.g. <h1 class="ip-color-neutral">Neutral</h1>
# (confirmed via DevTools inspection 2026-07-03, members.chaikinanalytics.com
# /pgr/etf/SPY). The class suffix changes with rating (ip-color-neutral,
# presumably ip-color-bullish/-bearish etc.) so we select on the stable
# wrapper class instead of the rating-specific one.
_RATING_SELECTOR = "div.rating-widget-wrapper h1"
_LOGIN_INDICATOR_SELECTOR = "div.rating-widget-wrapper h1"  # presence = logged in
_PAGE_LOAD_TIMEOUT_MS = 15_000
_INTERACTIVE_LOGIN_TIMEOUT_MS = 300_000  # 5 min for operator to complete login


class ChaikinReadError(Exception):
    """Raised when a Power Gauge value cannot be scraped for a symbol."""


def _ensure_session(playwright) -> None:
    """
    Verify a saved session works; if missing or expired, open a visible
    browser and wait for the operator to log in manually, then save the
    resulting session to disk.

    Non-headless on purpose: Chaikin login may involve 2FA/CAPTCHA that
    no scraper should attempt to automate around.
    """
    browser = playwright.chromium.launch(headless=False, channel="chrome")
    context_kwargs = {}
    if CHAIKIN_SESSION_FILE.exists():
        context_kwargs["storage_state"] = str(CHAIKIN_SESSION_FILE)
    context = browser.new_context(**context_kwargs)
    page = context.new_page()
    page.goto(CHAIKIN_BASE_URL, timeout=_PAGE_LOAD_TIMEOUT_MS)

    try:
        page.wait_for_selector(
            _LOGIN_INDICATOR_SELECTOR, timeout=_PAGE_LOAD_TIMEOUT_MS
        )
        logger.info("Chaikin session valid -- no login needed")
    except PlaywrightTimeoutError:
        logger.warning(
            "Chaikin session missing or expired -- waiting up to %d min "
            "for operator to log in manually in the opened browser window",
            _INTERACTIVE_LOGIN_TIMEOUT_MS // 60_000,
        )
        page.wait_for_selector(
            _LOGIN_INDICATOR_SELECTOR, timeout=_INTERACTIVE_LOGIN_TIMEOUT_MS
        )
        logger.info("Chaikin login detected -- saving session")

    CHAIKIN_SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(CHAIKIN_SESSION_FILE))
    context.close()
    browser.close()


def get_power_gauge(ticker: str) -> PowerGaugeResult:
    """
    Fetch the Power Gauge Rating for one symbol.

    First call (or any call after session expiry) opens a visible browser
    for interactive login; all subsequent calls run headless off the
    saved session.

    Args:
        ticker: Uppercase symbol, e.g. "ASTS".

    Returns:
        PowerGaugeResult with rating and scrape timestamp.

    Raises:
        ChaikinReadError: if the page loads but no rating element is found,
            or the page fails to load within timeout.
    """
    url = f"{CHAIKIN_BASE_URL}/pgr/stock/{ticker}"

    with sync_playwright() as playwright:
        if not CHAIKIN_SESSION_FILE.exists():
            _ensure_session(playwright)

        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(CHAIKIN_SESSION_FILE))
        page = context.new_page()

        try:
            page.goto(url, timeout=_PAGE_LOAD_TIMEOUT_MS)
            page.wait_for_selector(_RATING_SELECTOR, timeout=_PAGE_LOAD_TIMEOUT_MS)
        except PlaywrightTimeoutError:
            # Headless run hit a login page -- session expired since last
            # call. Close out, re-run interactive login, retry once.
            context.close()
            browser.close()
            logger.warning("Chaikin session expired for %s -- re-authenticating", ticker)
            _ensure_session(playwright)
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(storage_state=str(CHAIKIN_SESSION_FILE))
            page = context.new_page()
            try:
                page.goto(url, timeout=_PAGE_LOAD_TIMEOUT_MS)
                page.wait_for_selector(_RATING_SELECTOR, timeout=_PAGE_LOAD_TIMEOUT_MS)
            except PlaywrightTimeoutError as exc:
                context.close()
                browser.close()
                raise ChaikinReadError(
                    f"{ticker}: rating element not found after re-auth "
                    f"(page layout may have changed)"
                ) from exc

        rating_text = page.locator(_RATING_SELECTOR).inner_text().strip()
        score: Optional[float] = _try_parse_score(page)

        context.close()
        browser.close()

    if not rating_text:
        raise ChaikinReadError(f"{ticker}: rating element found but empty")

    return PowerGaugeResult(
        ticker=ticker,
        rating=rating_text,
        rating_score=score,
        scraped_at=datetime.now(),
        source_url=url,
    )


def _try_parse_score(page) -> Optional[float]:
    """
    Best-effort numeric score extraction, if Chaikin exposes one alongside
    the text rating. Returns None rather than raising -- the text rating
    alone is sufficient; a missing numeric score is not an error.
    """
    try:
        score_text = page.locator("[data-testid='power-gauge-score']").inner_text()
        return float(score_text.strip())
    except Exception:  # noqa: BLE001 -- deliberately broad, this is optional
        return None
