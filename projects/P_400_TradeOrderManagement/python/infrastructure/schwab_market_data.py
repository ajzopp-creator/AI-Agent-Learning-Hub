"""schwab_market_data.py -- live market data fetch (WO-P400-E4.002).

Infrastructure layer: all I/O, no business logic. Wraps
shared_resources.python_utils.schwab_client.get_client() for quote,
price-history, and option-chain calls. Every function returns None or
raises a clear exception on failure -- never fabricates a value. Callers
(application layer) decide what "clear message, exit without writing a
partial file" looks like for their command.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from domain.chain_selector import ChainCandidate
from shared_resources.python_utils.atr import Bar
from shared_resources.python_utils.schwab_client import get_client

logger = logging.getLogger("p400.schwab_market_data")


def get_quote_data(config_path: Path, token_path: Path, symbol: str) -> Optional[dict]:
    """Fetch a live quote. Returns None on any failure or missing quote key.

    Returns:
        dict with price, bid, ask, today_volume -- or None.
    """
    try:
        client = get_client(config_path, token_path)
        resp = client.get_quotes([symbol])  # plural -- get_quote() breaks on slash symbols like BRK/B (WO pending)
        if resp.status_code != 200:
            logger.warning("get_quote %s: status %s", symbol, resp.status_code)
            return None
        data = resp.json()
        entry = data.get(symbol)
        if entry is None or "quote" not in entry:
            logger.warning("get_quote %s: no quote data in response", symbol)
            return None
        q = entry["quote"]
        return {
            "price": q.get("lastPrice"),
            "bid": q.get("bidPrice"),
            "ask": q.get("askPrice"),
            "today_volume": q.get("totalVolume"),
        }
    except Exception as e:
        logger.warning("get_quote_data failed for %s: %r", symbol, e)
        return None


def get_daily_bars(
    config_path: Path, token_path: Path, symbol: str, lookback_days: int = 40
) -> Optional[list[Bar]]:
    """Fetch daily OHLCV bars, oldest-first, as atr.py Bar tuples + volumes.

    Returns:
        (bars, volumes) tuple, bars = list[Bar] (high, low, close),
        volumes = list[float] same order -- or None on failure.
    """
    try:
        client = get_client(config_path, token_path)
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=lookback_days * 2)  # buffer for weekends/holidays
        resp = client.get_price_history_every_day(symbol, start_datetime=start, end_datetime=end)
        if resp.status_code != 200:
            logger.warning("get_price_history %s: status %s", symbol, resp.status_code)
            return None
        candles = resp.json().get("candles", [])
        if not candles:
            logger.warning("get_price_history %s: no candles returned", symbol)
            return None
        candles = candles[-lookback_days:]
        bars = [(c["high"], c["low"], c["close"]) for c in candles]
        volumes = [c["volume"] for c in candles]
        return bars, volumes
    except Exception as e:
        logger.warning("get_daily_bars failed for %s: %r", symbol, e)
        return None


def get_chain_candidates(
    config_path: Path, token_path: Path, symbol: str, option_type: str
) -> Optional[list[ChainCandidate]]:
    """Fetch a range of strikes/expirations for the DTE-filtering selector.

    Args:
        option_type: "call" or "put".

    Returns:
        list[ChainCandidate] (unfiltered by DTE -- domain\chain_selector.py
        does that) -- or None on failure.
    """
    try:
        client = get_client(config_path, token_path)
        contract_type = client.Options.ContractType.CALL if option_type == "call" \
            else client.Options.ContractType.PUT
        resp = client.get_option_chain(symbol, contract_type=contract_type)
        if resp.status_code != 200:
            logger.warning("get_option_chain %s: status %s", symbol, resp.status_code)
            return None
        data = resp.json()
        exp_map_key = "callExpDateMap" if option_type == "call" else "putExpDateMap"
        exp_map = data.get(exp_map_key)
        if not exp_map:
            logger.warning("get_option_chain %s: no %s in response", symbol, exp_map_key)
            return None

        candidates: list[ChainCandidate] = []
        for exp_key, strikes in exp_map.items():
            expiration = exp_key.split(":")[0]  # Schwab format "YYYY-MM-DD:N"
            for strike_str, contracts in strikes.items():
                for c in contracts:
                    # "volatility" is Schwab's IV field name (percent, e.g. 32.15).
                    # NOT independently confirmed against a live response yet --
                    # flagged for PEH verification before this is trusted.
                    iv_pct = c.get("volatility")
                    if (c.get("bid") is None or c.get("ask") is None
                            or c.get("delta") is None or iv_pct is None):
                        continue  # never fabricate -- skip incomplete rows
                    candidates.append(ChainCandidate(
                        strike=float(strike_str),
                        expiration=expiration,
                        delta=c["delta"],
                        iv=iv_pct / 100.0,
                        bid=c["bid"],
                        ask=c["ask"],
                        open_interest=c.get("openInterest", 0),
                    ))
        return candidates if candidates else None
    except Exception as e:
        logger.warning("get_chain_candidates failed for %s: %r", symbol, e)
        return None