"""
P_025 Infrastructure — yfinance Client

Fetches historical closing prices and basic reference data.
Contains no business logic; only network I/O and light transformation
into the schemas defined in schemas.py.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Iterable

import yfinance as yf

from schemas import MarketDataRow, ReferenceData

logger = logging.getLogger(__name__)


def fetch_market_data(
    tickers: Iterable[str],
    start: date,
    end: date | None = None,
    timeout: int = 30,
) -> list[MarketDataRow]:
    """
    Download adjusted close prices for the given tickers.

    Returns a list of MarketDataRow objects, one per trading day.
    Missing prices are simply omitted from that day's dict.
    """
    ticker_list = sorted({t.upper() for t in tickers})
    if not ticker_list:
        return []

    end = end or date.today()
    start_str = start.isoformat()
    end_str = (end + timedelta(days=1)).isoformat()  # yfinance end is exclusive

    logger.info("Fetching yfinance data for %d tickers from %s to %s", len(ticker_list), start_str, end)

    try:
        raw = yf.download(
            tickers=ticker_list,
            start=start_str,
            end=end_str,
            group_by="ticker",
            auto_adjust=True,
            threads=True,
            progress=False,
            timeout=timeout,
        )
    except Exception as exc:
        logger.error("yfinance download failed: %s", exc)
        return []

    if raw.empty:
        logger.warning("yfinance returned empty DataFrame")
        return []

    # Normalise to a date → {ticker: close} structure
    rows: dict[date, dict[str, float]] = {}

    # yfinance returns different shapes for single vs multiple tickers
    if len(ticker_list) == 1:
        ticker = ticker_list[0]
        if "Close" in raw.columns:
            for idx, value in raw["Close"].items():
                d = idx.date() if hasattr(idx, "date") else idx
                if value == value:  # not NaN
                    rows.setdefault(d, {})[ticker] = float(value)
    else:
        for ticker in ticker_list:
            if ticker not in raw.columns.get_level_values(0):
                continue
            closes = raw[ticker]["Close"] if "Close" in raw[ticker].columns else None
            if closes is None:
                continue
            for idx, value in closes.items():
                d = idx.date() if hasattr(idx, "date") else idx
                if value == value:
                    rows.setdefault(d, {})[ticker] = float(value)

    result = [
        MarketDataRow(date=d, prices=prices)
        for d, prices in sorted(rows.items())
    ]
    logger.info("Fetched %d market-data rows", len(result))
    return result


def fetch_reference_data(tickers: Iterable[str]) -> list[ReferenceData]:
    """
    Pull basic reference information (name, sector, industry, country, beta)
    for each ticker. Failures for individual tickers are logged and skipped.
    """
    results: list[ReferenceData] = []
    for ticker in sorted({t.upper() for t in tickers}):
        try:
            info = yf.Ticker(ticker).info
            results.append(
                ReferenceData(
                    ticker=ticker,
                    company=info.get("longName") or info.get("shortName"),
                    sector=info.get("sector"),
                    industry=info.get("industry"),
                    country=info.get("country"),
                    beta=info.get("beta"),
                    asset_class=info.get("quoteType"),
                )
            )
        except Exception as exc:
            logger.warning("Could not fetch reference data for %s: %s", ticker, exc)
            results.append(ReferenceData(ticker=ticker))
    return results
