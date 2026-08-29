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
    ACCOUNT_AJZ6348,
    ANALYSIS_MODE,
    IRA_FEED_READY,
    P020_DB_PATH,
    PRIMARY_ACCOUNTS,
    WORKBOOK_PATH,
    resolve_start_date,
)
from domain.trade_processor import (
    build_cost_basis_rows,
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
    Execute a rebuild of the portfolio workbook.

    mode
        full | yearly | ytd — lookback window. Defaults to ANALYSIS_MODE.
    """
    selected = (mode or ANALYSIS_MODE).strip().lower()
    logger.info("=== P_025 Full Build starting (mode=%s) ===", selected)

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
        )
        return snapshot

    end_date = date.today()
    start_date = resolve_start_date(end_date, selected)

    daily_units = calculate_daily_units(trades, start_date=start_date, end_date=end_date)
    daily_cash = calculate_daily_cash(trades, start_date=start_date, end_date=end_date)

    tickers = unique_tickers(trades)
    market_data = fetch_market_data(tickers, start=start_date, end=end_date)
    reference_data = fetch_reference_data(tickers)

    daily_invested = calculate_daily_invested(daily_units, market_data)
    cost_basis = build_cost_basis_rows(
        trades, daily_units, account_id=ACCOUNT_AJZ6348
    )

    snapshot = PortfolioSnapshot(
        trades=trades,
        market_data=market_data,
        reference_data=reference_data,
        daily_units=daily_units,
        daily_cash=daily_cash,
        daily_invested=daily_invested,
        cost_basis=cost_basis,
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
    )

    logger.info("=== P_025 Full Build complete → %s ===", WORKBOOK_PATH)
    return snapshot
