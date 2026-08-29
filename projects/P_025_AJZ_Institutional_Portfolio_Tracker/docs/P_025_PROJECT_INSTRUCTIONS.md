# P_025 AJZ Institutional Portfolio Tracker — Compressed Instructions

**Owner:** Anthony Zoppi — AJZ Strategies LLC  
**Status:** Analytics v1 live  
**Last updated:** 2026-08-22  
**Canonical file:** projects\\P_025_AJZ_Institutional_Portfolio_Tracker\\docs\\P_025_PROJECT_INSTRUCTIONS.md

## 1. Project purpose

P_025 is an institutional-grade portfolio analytics workbook. It reads P_020 SQLite trades as the source of truth, pulls live prices through yfinance, writes a Python-generated Data Lake, and builds Excel-formula Analytics. AJZ6348 is live; 5232-9885 remains gated until the P_020 Inherited Roth feed is confirmed.

**Not in scope:** trade execution, Schwab authentication, or including paper-account activity in primary P&L.

## 2. Non-negotiable paths and environment

-   **Hub root:** C:\\Users\\Trader\\AI-Agent-Learning-Hub\\
-   **Project:** projects\\P_025_AJZ_Institutional_Portfolio_Tracker\\
-   **P_020 DB:** projects\\P_020_AJZStrategies_PerformanceAnalysisSystem\\data\\database\\P_020_trades.db
-   **Python:** C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe
-   **PEH verify folder:** Agentic-Hub-Governance\\verify\\

**Always set before Python:** set HUB_ROOT=C:\\Users\\Trader\\AI-Agent-Learning-Hub. Do not substitute OneDrive; current config.py can otherwise point to D:\\OneDrive and create an empty build.

## 3. Architecture rules

-   Approval gate: file plan first, then wait for “go ahead” before writing code.
-   Layering: config → schemas → domain → infrastructure → application → cli.
-   Limits: files ≤300 lines, split near 250; functions ≤50 lines.
-   Application layer orchestrates only; no raw I/O logic there.
-   Pydantic required for persistent non-temp I/O shapes.
-   Real fixes need permanent tests under tests/test_\<module\>.py.
-   All paths belong in config.py and must be confirmed, not guessed.

## 4. Current system state

The pipeline is two-step: cli.py build writes the Data Lake only and overwrites P_025_Portfolio_BUILT.xlsx. run_format_analytics() then saves a versioned \*_Analytics_YYYYMMDD_HHMM.xlsx workbook and does not overwrite the Data Lake.

### Data Lake

-   Trade_Log: P_020 trades; AJZ6348 active; IRA skipped while gated.
-   Market_Data: yfinance closes with 3-year lookback; delisted tickers skipped.
-   Reference_Data: name, sector, industry, country, beta from yfinance.
-   Daily_Units: calendar-date net shares by ticker; open_date only; long positive, short negative.
-   Daily_Cash: synthetic trade-derived cash; not a Schwab ledger.
-   Daily_Invested: mark-to-market shares × close; not cost basis.
-   Cost_Basis: lifetime long VWAP × current long shares; not FIFO or remaining-lot VWAP.

### Analytics

-   Positions: first 200 Reference_Data tickers; cost via Cost_Basis VLOOKUP; P&L = MV − cost.
-   Equity_Curve: NAV = Daily_Cash + Daily_Invested.
-   Dashboard, Risk_Metrics, and Sector_Exposure are live.
-   Correlation has diagonal = 1 and blank off-diagonal values.
-   Geographic, Stress, and Theses are placeholders.

**Flag:** IRA_FEED_READY = False until Tony confirms P_020 Inherited Roth feed readiness. Last successful PEH: 424 trades and 276 Cost_Basis rows; Positions capped at 200.

## 5. Day-to-day run commands

set HUB_ROOT=C:\\Users\\Trader\\AI-Agent-Learning-Hub  
cd C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\P_025_AJZ_Institutional_Portfolio_Tracker\\python  
C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe cli.py build  
C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -c "from application.format_analytics import run_format_analytics; print(run_format_analytics())"

cli.py supports build, update, and quick. None format Analytics. launcher.bat build already calls p140 directly. Diagnostics are read-only through diagnostics.py with HUB_ROOT set.

## 6. Deployment and PEH handoff

-   Grok delivers a zip containing python\\ plus optional PEH.
-   Extract onto the P_025 project root so python\\ lands in the correct project folder.
-   Copy any run_this_P025_\*.py to Agentic-Hub-Governance\\verify\\ before running.
-   Run PEH from verify\\ with HUB_ROOT set.
-   Completion signal is PEH PASS/FAIL.

**Critical warning:** Do not run run_this_\*.py from the project root when python\\ sits beside it. A deploy script using rmtree can delete live code if source and target are the same tree.

## 7. Do not do

-   Do not treat D:\\OneDrive as Hub root.
-   Do not run Python without HUB_ROOT set.
-   Do not flip IRA_FEED_READY to True until Tony confirms feed readiness.
-   Do not put business logic in application/ or I/O in domain/.
-   Do not invent P_020 paths.
-   Do not call Cost_Basis FIFO or true remaining cost.
-   Do not call Daily_Invested cost; it is mark-to-market.
-   Do not overwrite versioned Analytics outputs.

## 8. Next actions

-   Patch config.py so Hub root defaults to the Hub path, not OneDrive.
-   Define ops cadence for scheduled build/update.
-   Flip IRA only after P_020 feed confirmation.
-   Polish formulas, add FIFO lots, fill CORREL, build Geographic/Stress, or raise Positions cap.

*End of compressed P_025 instructions.*
