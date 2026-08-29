# P_025 AJZ Institutional Portfolio Tracker — System Documentation

**Project ID:** P_025  
**Version:** 1.1  
**Last Updated:** 2026-08-20  
**Maintained By:** Anthony Zoppi  
**Status:** In Development — Architecture + Data Design Locked  
**Governed By:** P_000 (`P_000_SYSTEM_DOCUMENTATION.md`) / `Agentic-Hub-Governance\work_orders\`  
**Primary AI Engine:** Grok 4.3 (xAI) under Agentic Hub

Note: Until Primary changes: All future Versions are maintained on Google Drive **How to Access the Document on Google Drive**

1.  Open this link in your browser: **Folder:** <https://drive.google.com/drive/folders/1yF0wOcmP11b8AcCxTu3-twqNHeNn_MI9>
2.  Inside the folder **P_025_AJZ_Institutional_Portfolio_Tracker**, click on the file: **P_025_SYSTEM_DOCUMENTATION_v1_1.md**
3.  Direct link to the file (if preferred): <https://drive.google.com/file/d/1_lgjt6Ln3NKOcugVkvjqnHC8mdRFDPmR/view?usp=drivesdk>

***

## 1. PROJECT OVERVIEW

### 1.1 Purpose

Build a professional, institutional-grade portfolio analytics workbook that consumes the clean, system-matched trade data produced by P_020 (SQLite single source of truth) and layers live market data, risk analytics, equity curve, correlation, VaR, stress testing, and Bloomberg-style presentation on top of it.

Supports two real-money accounts as distinct portfolios:

-   **AJZ6348** — Live brokerage (AJZ Strategies LLC)
-   **5232-9885** — Inherited Roth

### 1.2 Scope

**Covers:**

-   P_020_trades.db (or CSV exports) as authoritative trade history
-   Both AJZ6348 and 5232-9885 as first-class accounts
-   Live prices + reference data via yfinance
-   Pure Excel formula analytics
-   Bloomberg-style professional formatting
-   Append-only update script

**Does NOT cover:**

-   Schwab API / authentication (P_020 owns)
-   Trade execution or signal generation
-   Paper account in primary reporting

### 1.3 Accounts (Locked)

| account_id          | Full ID   | Name                          | Type   | Notes                                    |
|---------------------|-----------|-------------------------------|--------|------------------------------------------|
| AJZ6348             | AJZ6348   | AJZ Strategies LLC            | live   | Options + stocks                         |
| IRA9885 / 5232-9885 | 5232-9885 | AJZ Strategies Inherited Roth | invest | Inherited Roth — stocks/ETFs, 10-yr rule |
| PAPER               | PAPER     | Paper Account                 | paper  | Excluded from primary P&L by default     |

***

## 2. SYSTEM ARCHITECTURE (Summary)

```
P_020_trades.db
  ├── AJZ6348
  ├── 5232-9885 (Inherited Roth)
  └── PAPER (filtered out by default)
        +
yfinance
        ↓
build_portfolio.py / update_portfolio.py
        ↓
P_025_Portfolio_BUILT.xlsx
├── Data Lake (Python writes values)
└── Analytics (100% Excel formulas)
```

**Core Principles**

1.  P_020 is the single source of truth for trades.
2.  Both real accounts are first-class and separable.
3.  All calculations are Excel formulas (glass-box).
4.  Updates are append-only.
5.  Grok 4.3 produces all code and workbooks as artifacts.

***

## 9. DATA DESIGN & SHEET ARCHITECTURE

### 9.1 Sheet Inventory

| Sheet Name              | Type      | Populated By      | Purpose                                                |
|-------------------------|-----------|-------------------|--------------------------------------------------------|
| **Trade_Log**           | Data Lake | Python            | Clean view of P_020 trades (both accounts)             |
| **Market_Data**         | Data Lake | Python (yfinance) | Daily closing prices (rows = dates, columns = tickers) |
| **Reference_Data**      | Data Lake | Python (yfinance) | Company name, sector, industry, country, beta          |
| **Daily_Units**         | Data Lake | Python            | Shares held per ticker per day (from Trade_Log)        |
| **Daily_Cash**          | Data Lake | Python            | Cash balance per day per account                       |
| **Dashboard**           | Analytics | Excel formulas    | KPIs, NAV, allocation, equity chart                    |
| **Positions**           | Analytics | Excel formulas    | Current holdings with live P&L and weights             |
| **Equity_Curve**        | Analytics | Excel formulas    | Daily NAV, returns, drawdown                           |
| **Sector_Exposure**     | Analytics | Excel formulas    | Sector breakdown \$ and %                              |
| **Geographic_Exposure** | Analytics | Excel formulas    | Country breakdown \$ and %                             |
| **Correlation**         | Analytics | Excel formulas    | Correlation matrix of positions                        |
| **Risk_Metrics**        | Analytics | Excel formulas    | Sharpe, Sortino, Max DD, VaR, Beta, etc.               |
| **Stress_Testing**      | Analytics | Excel formulas    | Scenario analysis (−20%, −10%, +10%, etc.)             |
| **Investment_Theses**   | Analytics | Manual + formulas | Thesis / Catalyst / Edge per ticker (optional)         |

### 9.2 Account Handling Rules

-   Every Data Lake and Analytics sheet that contains trade or position data includes an **Account** column or filter.
-   Dashboard and Positions sheets support:
    -   View = AJZ6348 only
    -   View = 5232-9885 only
    -   View = Combined (both real accounts)
-   PAPER is excluded from all primary calculations and charts unless a explicit “Include Paper” toggle is set.
-   Inherited Roth (5232-9885) carries its own cash balance and is never mixed into live brokerage risk metrics without clear labeling.

### 9.3 Data Lake Schemas

#### Trade_Log

Source: P_020_trades.db (or v_trade_summary view) filtered to AJZ6348 + 5232-9885.

| Column                | Type     | Notes                          |
|-----------------------|----------|--------------------------------|
| trade_id              | Integer  | From P_020                     |
| account_id            | Text     | AJZ6348 or 5232-9885           |
| system                | Text     | P_115, P_300, TOS_Import, etc. |
| underlying_symbol     | Text     | Ticker                         |
| asset_type            | Text     | stock / etf / call / put       |
| direction             | Text     | long / short                   |
| open_date             | Date     |                                |
| open_datetime         | DateTime |                                |
| qty                   | Float    |                                |
| entry_price           | Float    |                                |
| stop_price            | Float    | Nullable                       |
| risk_amount           | Float    | From P_020                     |
| total_commissions     | Float    |                                |
| status                | Text     | open / partial / closed        |
| realized_pnl          | Float    | From P_020 view                |
| realized_R            | Float    | From P_020 view                |
| schwab_transaction_id | Text     | Dedup key                      |
| notes                 | Text     |                                |

#### Market_Data

| Column | Type  | Notes                                             |
|--------|-------|---------------------------------------------------|
| Date   | Date  | Trading days only                                 |
| AAPL   | Float | Closing price                                     |
| MSFT   | Float | …                                                 |
| …      | Float | One column per unique ticker across both accounts |

Python populates historical + latest closes. Formulas never hard-code prices.

#### Reference_Data

| Column     | Type  | Notes               |
|------------|-------|---------------------|
| Ticker     | Text  | Primary key         |
| Company    | Text  |                     |
| Sector     | Text  |                     |
| Industry   | Text  |                     |
| Country    | Text  |                     |
| Beta       | Float | vs SPY              |
| AssetClass | Text  | Equity / ETF / etc. |

#### Daily_Units

Rows = dates, Columns = tickers.  
Value = shares held at end of that day (calculated from Trade_Log by Python).  
Separate blocks or sheets can exist per account if needed for clarity.

#### Daily_Cash

| Date | Account   | Cash_Balance |
|------|-----------|--------------|
| …    | AJZ6348   | …            |
| …    | 5232-9885 | …            |

### 9.4 Analytics Sheet Formula Architecture

**Core Rule:**  
Python only writes raw values into Data Lake sheets.  
Every number the user sees on Analytics sheets is an Excel formula that references the Data Lake.

#### Positions (example formula pattern)

-   Shares → `=SUMIFS(Daily_Units[Ticker], Daily_Units[Date], MAX(Date), …)`
-   Current Price → `=INDEX(Market_Data[Ticker], MATCH(TODAY(), Market_Data[Date], 1))` or XLOOKUP
-   Market Value → `=Shares * Current_Price`
-   Cost Basis → from Trade_Log average cost
-   Unrealized P&L → `=Market_Value − Cost_Basis`
-   Weight → `=Market_Value / Total_NAV`
-   Account filter applied via SUMIFS / FILTER functions

#### Equity_Curve

-   Date
-   Cash (from Daily_Cash, filtered by account or combined)
-   Invested Value (`=SUMPRODUCT(Daily_Units * Market_Data prices)`)
-   Total NAV = Cash + Invested
-   Daily Return = `(NAV_t / NAV_t-1) − 1`
-   Cumulative Return
-   Drawdown = `(NAV − RunningMax) / RunningMax`

#### Risk_Metrics (key formulas)

-   Annualized Return → from Equity_Curve
-   Annualized Volatility → STDEV of daily returns × √252
-   Sharpe → `(Ann_Return − RiskFree) / Ann_Vol`
-   Sortino → downside deviation version
-   Max Drawdown → from Equity_Curve
-   Beta → COVAR / VAR vs SPY column in Market_Data
-   VaR 95% / 99% → historical or parametric from daily returns
-   CVaR → average of losses beyond VaR

#### Correlation

-   Matrix of daily returns of each position (or of the portfolio vs each ticker).
-   Conditional formatting: green (low) → yellow → red (high).

#### Stress_Testing

-   Scenario shocks applied to current Positions Market Value using Beta or direct % moves.
-   Output: estimated NAV impact for −20%, −10%, −5%, +10%, etc.

### 9.5 Formatting Standards (Bloomberg-style)

-   Font: Segoe UI
-   Header fill: dark navy `#1C2541`, white text
-   Positive numbers: green `#007A33`
-   Negative numbers: red `#B81D13`
-   Alternating row colors (zebra)
-   Freeze panes on header row + first column
-   Number formats: prices 2 decimals, % 1 or 2 decimals, large \$ with commas
-   Charts: clean line (Equity Curve), doughnut or bar (Allocation)

### 9.6 Update Flow

1.  P_020 weekly ingest runs → SQLite updated.
2.  User runs `python update_portfolio.py` (or `quick` for prices only).
3.  Script:
    -   Reads latest P_020 data for AJZ6348 + 5232-9885
    -   Appends new rows to Market_Data, Daily_Units, Daily_Cash
    -   Adds any new tickers to Reference_Data
4.  Excel formulas recalculate automatically.
5.  No rebuild of Analytics sheets required.

***

## 5. CHANGE LOG

#### v1.1 — 2026-08-20

**Added:** Full Section 9 — Data Design & Sheet Architecture (schemas, formula patterns, account handling, formatting, update flow).  
**Status:** Architecture + Data Design locked. Ready for implementation phase.

#### v1.0 — 2026-08-20

Initial architecture and account lock (including Inherited Roth 5232-9885).

***

**Document Classification:** Internal  
**Document Owner:** Anthony Zoppi — AJZ Strategies LLC  
**Next Step when resuming:** Begin `build_portfolio.py` or create detailed formula map workbook.

***

*End of P_025 SYSTEM DOCUMENTATION v1.1 — 2026-08-20*
