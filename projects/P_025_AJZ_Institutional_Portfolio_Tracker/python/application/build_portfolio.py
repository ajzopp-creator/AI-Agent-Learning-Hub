"""
P_025 Application — Full Portfolio Build

Orchestrates a complete rebuild of the Data Lake from P_020 + yfinance.
No business logic lives here; it only sequences calls to domain and
infrastructure modules.
"""

from __future__ import annotations

import logging
from datetime import date

from config import (
    ANALYSIS_MODE,
    IRA_FEED_READY,
    P020_DB_PATH,
    PRIMARY_ACCOUNTS,
    WORKBOOK_PATH,
    resolve_start_date,
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


def run_full_build(mode: str | None = None) -> PortfolioSnapshot:
    """
    Execute a full rebuild of the portfolio workbook.

    Parameters
    ----------
    mode:
        Analysis window: "full" (3y trailing), "yearly" (365d trailing),
        or "ytd" (1 Jan of current year). Defaults to config.ANALYSIS_MODE.

    Steps
    -----
    1. Read trades from P_020 (AJZ6348 + 5232-9885 when IRA_FEED_READY)
    2. Filter to primary accounts
    3. Derive daily units, daily cash, daily invested for the chosen window
    4. Fetch market data + reference data for all tickers
    5. Write everything to the Data Lake sheets
    """
    effective_mode = (mode or ANALYSIS_MODE).lower()
    logger.info("=== P_025 Full Build starting (mode=%s) ===", effective_mode)

    raw_trades = read_trades(
        db_path=P020_DB_PATH,
        account_ids=PRIMARY_ACCOUNTS,
        ira_feed_ready=IRA_FEED_READY,
    )
    trades = filter_primary_accounts(raw_trades, PRIMARY_ACCOUNTS)
    logger.info("Trades after primary-account filter: %d", len(trades))

    if not trades:
        logger.warning("No trades available — writing empty Data Lake")
        snapshot = PortfolioSnapshot()
        write_data_lake(
            WORKBOOK_PATH,
            trades=[],
            market_data=[],
            reference_data=[],
            daily_units=[],
            daily_cash=[],
            daily_invested=[],
            cost_basis=[],
            fifo_lots=[],
            fifo_cost=[],
        )
        return snapshot

    end_date = date.today()
    start_date = resolve_start_date(end_date, effective_mode)
    logger.info("Analysis window: %s → %s", start_date, end_date)

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

    logger.info("=== P_025 Full Build complete → %s ===", WORKBOOK_PATH)
    return snapshot
