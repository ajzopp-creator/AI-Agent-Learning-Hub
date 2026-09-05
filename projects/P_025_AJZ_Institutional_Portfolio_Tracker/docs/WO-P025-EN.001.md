# WO-P025-EN.001

**Project:** P_025 AJZ Institutional Portfolio Tracker  
**Type:** EN (enhancement + config safety)  
**Opened:** 2026-09-04  
**Owner session:** Grok sandbox draft + Hub PEH run  
**Status:** OPEN — do not mark CLOSED in the deploy session

## Intent

1. Stop Hub-root fallback to OneDrive.
2. Fill Correlation, Geographic_Exposure, Stress_Testing.
3. Add FIFO remaining lots + multi-account cost; Positions P&L uses Fifo_Cost.
4. Open the P_025 work-order ledger.

## Hub filing path

`C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P025-EN.001.md`

Copy this file there. Grok cannot write that folder.

## Completion gate (copy before OWNER_DONE)

- [ ] `HUB_ROOT` default is Hub path; OneDrive is not in the fallback chain
- [ ] `python -m pytest tests/` PASS on Hub `p140`
- [ ] PEH `run_this_P025_20260904_170500.py` PASS from `verify\` with HUB_ROOT set
- [ ] Workbook has Fifo_Lots, Fifo_Cost; Positions cost SUMIF Fifo_Cost
- [ ] Correlation off-diagonals are CORREL formulas
- [ ] Geographic_Exposure and Stress_Testing are not placeholders
- [ ] Cost_Basis still labeled lifetime VWAP (not called FIFO)
- [ ] Independent Review session re-reads live disk before CLOSED

## Out of scope

Positions cap raise, theses content, rate series, Schwab ledger, paper P&L.

## Deploy

Extract `run_this_P025_20260904_170500.zip` onto the P_025 project root.  
Copy PEH to `Agentic-Hub-Governance\verify\`.  
Do not run the PEH from the project root beside `python\`.
