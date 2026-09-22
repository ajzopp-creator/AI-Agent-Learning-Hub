"""
P_025 Domain — Excel Formula Templates

Pure formula strings and patterns used by the Analytics layer.
No I/O. No openpyxl. Fully testable.
"""

from __future__ import annotations


def positions_headers() -> list[str]:
    return [
        "Ticker",
        "Shares",
        "Last Price",
        "Market Value",
        "Cost Basis",
        "Unrealized P&L",
        "Unrealized %",
        "Weight %",
        "Account",
    ]


def positions_shares_formula(row: int) -> str:
    """Remaining FIFO shares for ticker A + account I."""
    return (
        f"=IFERROR(SUMIFS(Fifo_Cost!$C:$C,Fifo_Cost!$A:$A,A{row},"
        f"Fifo_Cost!$B:$B,I{row}),0)"
    )


def positions_cost_formula(row: int) -> str:
    """Remaining FIFO $ for ticker A + account I. Not lifetime VWAP."""
    return (
        f"=IFERROR(SUMIFS(Fifo_Cost!$D:$D,Fifo_Cost!$A:$A,A{row},"
        f"Fifo_Cost!$B:$B,I{row}),0)"
    )


def positions_last_price_formula(row: int) -> str:
    return (
        f'=IFERROR(LOOKUP(2,1/(Market_Data!A:A<>""),'
        f"INDEX(Market_Data!A:ZZ,0,MATCH(A{row},Market_Data!$1:$1,0))),0)"
    )


def equity_curve_cash_formula(row: int) -> str:
    """Sum synthetic cash across all primary accounts on that date."""
    return f"=SUMIF(Daily_Cash!A:A,A{row},Daily_Cash!C:C)"


def equity_curve_headers() -> list[str]:
    return [
        "Date",
        "Cash",
        "Invested Value",
        "Total NAV",
        "Daily Return",
        "Cumulative Return",
        "Drawdown",
        "Peak NAV",
    ]


def dashboard_kpi_labels() -> list[str]:
    return [
        "Total NAV",
        "Cash",
        "Invested Value",
        "Unrealized P&L",
        "Day Change $",
        "Day Change %",
        "YTD Return %",
        "Max Drawdown %",
        "Positions Count",
        "As Of Date",
    ]


def risk_metrics_labels() -> list[str]:
    return [
        "Annualized Return",
        "Annualized Volatility",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Max Drawdown",
        "VaR 95% (1-day)",
        "CVaR 95%",
        "Beta vs SPY",
        "Observation Days",
    ]


def sector_exposure_headers() -> list[str]:
    return ["Sector", "Market Value", "Weight %", "Position Count"]


# Example formula patterns (to be adapted to actual sheet layout by the formatter)
# These are illustrative; the formatter builds the final cell formulas.

def formula_last_price(ticker_cell: str, market_data_sheet: str = "Market_Data") -> str:
    """XLOOKUP-style last price for a ticker (Excel 365 / 2021+)."""
    return (
        f'=IFERROR(XLOOKUP(9.9E+307,{market_data_sheet}!$A:$A,'
        f'{market_data_sheet}!{ticker_cell}:{ticker_cell},, -1),0)'
    )


def formula_sumifs_shares(
    units_sheet: str = "Daily_Units",
    date_col: str = "A:A",
    ticker_col: str = "B:B",
) -> str:
    """Placeholder — actual formula is built per-column by the formatter."""
    return f'=SUMIF({units_sheet}!{date_col},MAX({units_sheet}!{date_col}),{units_sheet}!{ticker_col})'
