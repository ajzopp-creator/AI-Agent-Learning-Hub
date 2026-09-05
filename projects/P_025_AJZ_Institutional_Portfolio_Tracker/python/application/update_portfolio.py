"""
P_025 Application — Incremental Portfolio Update

Append-only update path. Designed for daily / weekly runs after the
initial full build. Currently performs a full refresh of the recent
window; true row-level append logic can be added later once the
workbook is in production use.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from config import (
    IRA_FEED_READY,
    LOOKBACK_DAYS_UPDATE,
    P020_DB_PATH,
    PRIMARY_ACCOUNTS,
    WORKBOOK_PATH,
)
from domain.fifo_lots import process_fifo_lots, summarize_fifo_cost
from domain.trade_processor import (
    build_cost_basis_for_accounts,
    calculate_daily_cash,
    calculate_daily_invested,
    calculate_daily_units,
    filter_primary_accounts,
)
from domain.portfolio_metrics import unique_tickers
from infrastructure.excel_writer import write_data_lake
from infrastructure.p020_reader import read_trades
from infrastructure.yfinance_client import fetch_market_data, fetch_reference_data
from schemas import PortfolioSnapshot

logger = logging.getLogger(__name__)


def run_update(quick_prices_only: bool = False) -> PortfolioSnapshot:
    """
    Incremental update entry point.

    Parameters
    ----------
    quick_prices_only:
        If True, only refresh Market_Data for the recent window
        (useful for intra-day price checks). Trade history is left untouched.
    """
    logger.info("=== P_025 Update starting (quick=%s) ===", quick_prices_only)

    end_date = date.today()
    start_date = end_date - timedelta(days=LOOKBACK_DAYS_UPDATE)

    if quick_prices_only:
        # Minimal path — only prices
        # (In a future iteration we would read existing tickers from the workbook)
        logger.info("Quick-prices mode not fully implemented yet — falling back to full recent window")
        # Fall through to normal update for now

    raw_trades = read_trades(
        db_path=P020_DB_PATH,
        account_ids=PRIMARY_ACCOUNTS,
        ira_feed_ready=IRA_FEED_READY,
    )
    trades = filter_primary_accounts(raw_trades, PRIMARY_ACCOUNTS)

    if not trades:
        logger.warning("No trades available for update")
        return PortfolioSnapshot()

    daily_units = calculate_daily_units(trades, start_date=start_date, end_date=end_date)
    daily_cash = calculate_daily_cash(trades, start_date=start_date, end_date=end_date)

    tickers = unique_tickers(trades)
    market_data = fetch_market_data(tickers, start=start_date, end=end_date)
    reference_data = fetch_reference_data(tickers)
    daily_invested = calculate_daily_invested(daily_units, market_data)
    fifo_lots = process_fifo_lots(trades)
    fifo_cost = summarize_fifo_cost(fifo_lots)
    cost_basis = build_cost_basis_for_accounts(
        trades, fifo_cost, PRIMARY_ACCOUNTS
    )

    snapshot = PortfolioSnapshot(
        trades=trades,
        market_data=market_data,
        reference_data=reference_data,
        daily_units=daily_units,
        daily_cash=daily_cash,
        daily_invested=daily_invested,
        cost_basis=cost_basis,
        fifo_lots=fifo_lots,
        fifo_cost=fifo_cost,
    )

    write_data_lake(
        WORKBOOK_PATH,
        trades=snapshot.trades,
        market_data=snapshot.market_data,
        reference_data=snapshot.reference_data,
        daily_units=snapshot.daily_units,
        daily_cash=snapshot.daily_cash,
        daily_invested=snapshot.daily_invested,
        cost_basis=snapshot.cost_basis,
        fifo_lots=snapshot.fifo_lots,
        fifo_cost=snapshot.fifo_cost,
    )

    logger.info("=== P_025 Update complete → %s ===", WORKBOOK_PATH)
    return snapshot
