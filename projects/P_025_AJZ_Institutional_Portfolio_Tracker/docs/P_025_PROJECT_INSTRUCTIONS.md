# P_025 AJZ Institutional Portfolio Tracker — Compressed Instructions

**Canonical file:** `projects\P_025_AJZ_Institutional_Portfolio_Tracker\docs\P_025_PROJECT_INSTRUCTIONS.md`

## 1. Project purpose

P_025 is an institutional-grade portfolio analytics workbook. It reads P_020 SQLite trades as the source of truth, pulls live prices through yfinance, writes a Python-generated Data Lake, and builds Excel-formula Analytics.

**Accounts:** AJZ6348 + Inherited Roth (5232-9885) both live (`IRA_FEED_READY = True`).

**Not in scope:** trade execution, Schwab authentication, or paper-account activity in primary P&L.

## 2. Non-negotiable paths and environment

- **Hub root:** `C:\Users\Trader\AI-Agent-Learning-Hub\`
- **Project:** `projects\P_025_AJZ_Institutional_Portfolio_Tracker\`
- **Docs:** `projects\P_025_AJZ_Institutional_Portfolio_Tracker\docs\`
- **Code:** `...\python\`
- **Output:** `...\output\P_025_Portfolio_BUILT.xlsx` + versioned `*_Analytics_*.xlsx`
- **P_020 DB:** `projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db`
- **Python:** `C:\Users\Trader\.conda\envs\p140\python.exe`
- **PEH verify:** `Agentic-Hub-Governance\verify\`

**Always set before Python:**
```bat
set HUB_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub
```
`config.py` defaults to the Hub path. Do not set HUB_ROOT to OneDrive.

## 3. Architecture rules

- Approval gate: file plan first, then wait for “go ahead” before writing code.
- Layering: config → schemas → domain → infrastructure → application → cli.
- Limits: files ≤300 lines (split near 250); functions ≤50 lines.
- Application layer orchestrates only — no raw I/O logic there.
- Pydantic required for persistent non-temp I/O shapes.
- Real fixes need permanent tests under `tests/test_<module>.py`.
- All paths belong in `config.py` and must be confirmed, not guessed.
- PEH handoff: first line = exact Windows path of the `.py`, then full script only.

## 4. Current system state (2026-08-22)

**Pipeline (two-step):**
1. `cli.py build` writes Data Lake only → overwrites `P_025_Portfolio_BUILT.xlsx`.
2. `run_format_analytics()` saves a versioned `*_Analytics_YYYYMMDD_HHMM.xlsx` and does **not** overwrite the Data Lake.

### Flags / modes
```python
IRA_FEED_READY = True          # 5232-9885 included
ANALYSIS_MODE  = "full"        # full | yearly | ytd
LOOKBACK_DAYS_FULL   = 365*3   # trailing 3y
LOOKBACK_DAYS_YEARLY = 365     # trailing 365d
# ytd → 1 Jan of current year
```
Override via env `P025_ANALYSIS_MODE` or CLI `--mode`.

### Data Lake
- **Trade_Log** — P_020 trades (AJZ6348 + 5232-9885)
- **Market_Data** — yfinance closes; window from analysis mode; delisted skipped
- **Reference_Data** — name, sector, industry, country, beta
- **Daily_Units** — calendar-date net shares; long +, short −
- **Daily_Cash** — synthetic trade-derived cash (not Schwab ledger)
- **Daily_Invested** — mark-to-market (shares × close); **not** cost basis
- **Cost_Basis** — lifetime long VWAP × FIFO remaining shares; one row per account+ticker; not FIFO remaining-lot VWAP
- **Fifo_Lots / Fifo_Cost** — remaining long lots; shorts do not open lots; Positions cost = SUMIF Fifo_Cost

### Analytics
- **Positions** — cost via Cost_Basis VLOOKUP; P&L = MV − cost
- **Equity_Curve** — NAV = Daily_Cash + Daily_Invested
- **Dashboard, Risk_Metrics, Sector_Exposure** — live
- **Correlation** — diagonal = 1; off-diagonal CORREL on Market_Data closes (cap 20)
- **Geographic_Exposure / Stress_Testing** — live formulas (linear MV shocks)
- **Theses** — placeholder

Last known PASS scale: ~424 trades, ~276 Cost_Basis rows.

## 5. Day-to-day run commands

```bat
set HUB_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_025_AJZ_Institutional_Portfolio_Tracker

REM Full 3-year rebuild (default) — bats live in project root
launcher.bat build
launcher.bat build --mode full

REM Trailing 365-day analysis
launcher.bat build --mode yearly

REM Calendar year-to-date
launcher.bat build --mode ytd

REM Ops wrapper (build + format_analytics) — use after / with P_020 weekly
ops_wrapper.bat
ops_wrapper.bat yearly
ops_wrapper.bat ytd

REM Incremental / quick
launcher.bat update
launcher.bat quick
```

`launcher.bat` and `ops_wrapper.bat` live in the **project root** and call into `python\cli.py`.  
Diagnostics (read-only): `python\diagnostics.py` with HUB_ROOT set.

## 6. Deployment and PEH handoff

- Grok delivers a zip containing `python\` (+ optional PEH).
- Extract onto the P_025 project so `python\` lands in the correct folder.
- Copy any `run_this_P025_*.py` to `Agentic-Hub-Governance\verify\` before running.
- Run PEH from `verify\` with HUB_ROOT set.
- Completion signal is PEH PASS/FAIL.

**Critical:** Do not run `run_this_*.py` from the project root when `python\` sits beside it. A deploy script using `rmtree` can delete live code if source and target are the same tree.

## 7. Do not do

- Do not treat D:\OneDrive as Hub root.
- Do not run Python without HUB_ROOT set.
- Do not put business logic in `application/` or I/O in `domain/`.
- Do not invent P_020 paths.
- Do not call Cost_Basis FIFO or true remaining-lot cost.
- Do not call Daily_Invested “cost”; it is mark-to-market.
- Do not overwrite versioned Analytics outputs.
- Do not exceed 300 lines per file.

## 8. Open / next

- Positions cap 200
- Investment theses content
- Rate-aware stress (needs a rate series)
- File WO-P025-EN.001 on the Hub ledger (draft in docs/)

Govern with python-project-architecture + PEH. Prefer PEH handoffs for Windows execution. Ask for “go ahead” before writing code.

## 9. Sandbox vs Windows Hub

Grok’s “Computer” / bash / `/home/workdir/artifacts/...` is the **remote Linux sandbox** only. It is a drafting and packaging workspace.

| Environment | Role |
|-------------|------|
| **Sandbox** | Draft code, write docs, build zips/PEH. Paths look like `/home/workdir/artifacts/...` |
| **Windows Hub** | Live system. P_020 DB, Excel output, Task Scheduler, `p140`, real runs. Paths under `C:\Users\Trader\AI-Agent-Learning-Hub\` |

Delivery pattern: edit in sandbox → package (zip or `run_this_P025_*.py`) → extract/run on Hub with `HUB_ROOT` set. Grok cannot see or execute on the Hub disk directly.
