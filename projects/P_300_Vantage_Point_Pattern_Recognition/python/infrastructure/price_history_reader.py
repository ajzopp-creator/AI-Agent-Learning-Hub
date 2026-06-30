"""
Price history reader adapter.

Fetches daily OHLCV data from yfinance for a given ticker and date range.
Returns sorted (date_str, close) tuples for realized-return computation.

VERSION: 1.1
DATE: 2026-06-29
CHANGELOG:
    - 2026-06-29 v1.1: M-061 fix -- yf.download() returns MultiIndex columns
      even for a single ticker on the version installed in p140; row["Close"]
      against a MultiIndex returns a sub-Series, not a scalar, throwing
      "truth value of a Series is ambiguous" downstream in
      realized_return.compute_realized_returns(). Flatten columns to
      single-level immediately after download in both functions.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Tuple

try:
    import yfinance as yf
except ImportError:
    yf = None

logger = logging.getLogger(__name__)


def fetch_price_history(
    ticker: str,
    start_date: str,
    end_date: str,
) -> List[Tuple[str, float]]:
    """
    Fetch daily OHLCV data from yfinance for a ticker over a date range.
    
    Returns sorted list of (date_str, close_price) tuples.
    Dates are in YYYYMMDD format for alignment with signal_date in ledger.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        start_date: Start date in YYYYMMDD format (e.g., "20260603").
        end_date: End date in YYYYMMDD format (e.g., "20260703").
    
    Returns:
        List of (date_str, close) tuples, sorted ascending by date.
        Empty list if fetch fails or yfinance unavailable.
    """
    if yf is None:
        logger.error("yfinance not installed; cannot fetch price history.")
        return []
    
    try:
        # Convert YYYYMMDD to datetime objects for yfinance.
        start_dt = datetime.strptime(start_date, "%Y%m%d")
        end_dt = datetime.strptime(end_date, "%Y%m%d")
        
        # Add one day to end_dt (yfinance uses exclusive end date).
        end_dt = end_dt + timedelta(days=1)
        
        # Fetch data.
        data = yf.download(
            ticker,
            start=start_dt,
            end=end_dt,
            progress=False,  # Suppress download progress output.
        )
        
        # M-061: recent yfinance versions return MultiIndex columns
        # (e.g. ('Close', 'DE')) even for a single ticker. row["Close"]
        # against a MultiIndex returns a sub-Series, not a scalar, which
        # blows up downstream ("truth value of a Series is ambiguous").
        # Flatten to single-level columns; no-op if already single-level.
        if data.columns.nlevels > 1:
            data.columns = data.columns.get_level_values(0)
        
        if data.empty:
            logger.warning(
                f"yfinance returned no data for {ticker} "
                f"({start_date}–{end_date})"
            )
            return []
        
        # Extract close prices, sorted by date.
        closes = []
        for date, row in data.iterrows():
            # yfinance returns Timestamp; convert to date string YYYYMMDD.
            date_str = date.strftime("%Y%m%d")
            close_price = row["Close"]
            closes.append((date_str, close_price))
        
        # Sort by date ascending.
        closes.sort(key=lambda x: x[0])
        
        logger.info(
            f"Fetched {len(closes)} trading days for {ticker} "
            f"({start_date}–{end_date})"
        )
        return closes
    
    except Exception as e:
        logger.error(
            f"Failed to fetch price history for {ticker} "
            f"({start_date}–{end_date}): {e}"
        )
        return []


def fetch_price_on_date(ticker: str, date_str: str) -> float | None:
    """
    Fetch the close price for a specific ticker on a specific date.
    
    Args:
        ticker: Stock symbol.
        date_str: Date in YYYYMMDD format.
    
    Returns:
        Close price (float) if found, None if not available or error.
    """
    try:
        target_dt = datetime.strptime(date_str, "%Y%m%d")
        end_dt = target_dt + timedelta(days=1)
        
        data = yf.download(ticker, start=target_dt, end=end_dt, progress=False)
        
        # M-061: flatten MultiIndex columns (see fetch_price_history).
        if data.columns.nlevels > 1:
            data.columns = data.columns.get_level_values(0)
        
        if data.empty:
            logger.warning(f"No price data for {ticker} on {date_str}")
            return None
        
        close_price = float(data.iloc[-1]["Close"])
        logger.debug(f"Fetched close: {ticker} {date_str} = {close_price}")
        return close_price
    
    except Exception as e:
        logger.error(f"Failed to fetch close for {ticker} {date_str}: {e}")
        return None
