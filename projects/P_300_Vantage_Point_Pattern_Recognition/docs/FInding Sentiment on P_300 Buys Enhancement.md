2. Using Python SDK + openbb-adanos (Reddit/X/Polymarket)
For a more programmatic, quant-friendly approach, use the OpenBB Python SDK with the openbb-adanos community extension.

Install
bash
pip install openbb
pip install openbb-adanos
Basic usage
python
from openbb import obb

# Reddit trending stocks (last N days)
reddit_trending = obb.adanos.reddit.trending(days=2)
print(reddit_trending)

# Reddit sentiment for specific tickers
reddit_sentiment = obb.adanos.reddit.sentiment(symbols=["AAPL", "TSLA"], days=2)
print(reddit_sentiment)

# X/Twitter sentiment for specific tickers
x_sentiment = obb.adanos.x.sentiment(symbols=["AAPL", "TSLA"], days=2)
print(x_sentiment)

# Polymarket sentiment (prediction markets)
polymarket_sentiment = obb.adanos.polymarket.sentiment(symbols=["AAPL"], days=2)
The openbb-adanos extension adds:

Reddit: 50+ subreddits, buzz scores, bullish/bearish sentiment

X/Twitter: stock sentiment from posts

Polymarket: prediction-market sentiment

See the extension docs for full parameters:
pip install openbb-adanos and usage like obb.adanos.reddit.trending(days=2).

3. Combining with price data for your own models
For a quantitative workflow (which fits your background), you can combine sentiment with price:

python
import pandas as pd
from openbb import obb

# Price data
price = obb.equity.price.historical("AAPL", start_date="2025-01-01").to_dataframe()

# X/Reddit sentiment
x_sent = obb.adanos.x.sentiment(symbols=["AAPL"], days=30).to_dataframe()

# Merge on date and compute correlations, signals, etc.
df = price.join(x_sent, on="date")
print(df[["close", "bullish_score", "bearish_score"]].tail())
You can then:

Aggregate sentiment by 15-minute, hourly, or daily buckets

Create buzz scores, bullish/bearish ratios

Backtest sentiment-based entry/exit signals alongside your existing pattern recognition system.

Summary
Quick CLI: use stocks/ba → reddit_sent, infer, wsb, headlines, snews.

Programmatic/quant: install openbb-adanos and use obb.adanos.reddit.* and obb.adanos.x.* for Reddit and X sentiment.

Combine sentiment with price/volume data in pandas for backtesting or real-time signal generation.

Do you want a concrete example script that:

pulls X/Twitter sentiment for a list of tickers,

merges it with price data, and

computes a simple sentiment-based signal?

2. Using Python SDK + openbb-adanos (Reddit/X/Polymarket)
Make this an md or a copy paste module

python
# openbb_social_sentiment.py
"""
OpenBB SDK module for social media stock sentiment (Reddit, X/Twitter, Polymarket).

Requirements:
    pip install openbb
    pip install openbb-adanos

Usage:
    python openbb_social_sentiment.py
    or import into your own scripts:
        from openbb_social_sentiment import (
            get_reddit_trending,
            get_reddit_sentiment,
            get_x_sentiment,
            get_polymarket_sentiment,
            get_sentiment_for_tickers,
        )
"""

from typing import List, Optional
from openbb import obb


def get_reddit_trending(days: int = 2) -> "obb.Data":
    """
    Get trending stocks on Reddit (across 50+ subreddits) for the last N days.

    Returns:
        Data object with buzz scores, bullish/bearish sentiment, and mentions.
    """
    return obb.adanos.reddit.trending(days=days)


def get_reddit_sentiment(
    symbols: List[str],
    days: int = 2,
) -> "obb.Data":
    """
    Get Reddit sentiment for specific tickers.

    Args:
        symbols: List of ticker symbols, e.g. ["AAPL", "TSLA"]
        days: Number of recent days to look at

    Returns:
        Data object with sentiment metrics per ticker.
    """
    return obb.adanos.reddit.sentiment(symbols=symbols, days=days)


def get_x_sentiment(
    symbols: List[str],
    days: int = 2,
) -> "obb.Data":
    """
    Get X (Twitter) sentiment for specific tickers.

    Args:
        symbols: List of ticker symbols
        days: Number of recent days

    Returns:
        Data object with X sentiment metrics per ticker.
    """
    return obb.adanos.x.sentiment(symbols=symbols, days=days)


def get_polymarket_sentiment(
    symbols: List[str],
    days: int = 2,
) -> "obb.Data":
    """
    Get Polymarket (prediction market) sentiment for specific tickers.

    Args:
        symbols: List of ticker symbols
        days: Number of recent days

    Returns:
        Data object with Polymarket sentiment metrics.
    """
    return obb.adanos.polymarket.sentiment(symbols=symbols, days=days)


def get_sentiment_for_tickers(
    tickers: List[str],
    days: int = 2,
    include_reddit: bool = True,
    include_x: bool = True,
    include_polymarket: bool = False,
) -> dict:
    """
    Fetch sentiment for a list of tickers from multiple sources.

    Args:
        tickers: List of ticker symbols
        days: Number of recent days
        include_reddit: Whether to include Reddit sentiment
        include_x: Whether to include X/Twitter sentiment
        include_polymarket: Whether to include Polymarket sentiment

    Returns:
        Dict with keys:
            - "reddit" (optional)
            - "x" (optional)
            - "polymarket" (optional)
    """
    result = {}

    if include_reddit:
        result["reddit"] = get_reddit_sentiment(tickers, days=days)

    if include_x:
        result["x"] = get_x_sentiment(tickers, days=days)

    if include_polymarket:
        result["polymarket"] = get_polymarket_sentiment(tickers, days=days)

    return result


def demo():
    """
    Demo script: fetch and print sentiment for a few tickers.
    """
    tickers = ["AAPL", "TSLA", "NVDA"]
    days = 2

    print("Fetching Reddit sentiment...")
    reddit_df = get_reddit_sentiment(tickers, days=days).to_dataframe()
    print(reddit_df.head())

    print("\nFetching X sentiment...")
    x_df = get_x_sentiment(tickers, days=days).to_dataframe()
    print(x_df.head())

    print("\nFetching Reddit trending stocks...")
    trending_df = get_reddit_trending(days=days).to_dataframe()
    print(trending_df.head())


if __name__ == "__main__":
    demo()
Quick usage in your own code
python
from openbb_social_sentiment import get_sentiment_for_tickers
import pandas as pd

tickers = ["AAPL", "TSLA", "NVDA"]
sentiment = get_sentiment_for_tickers(tickers, days=3, include_x=True, include_reddit=True)

# Convert to DataFrame
reddit_df = sentiment["reddit"].to_dataframe()
x_df = sentiment["x"].to_dataframe()

print("Reddit sentiment:")
print(reddit_df)

print("\nX sentiment:")
print(x_df)
