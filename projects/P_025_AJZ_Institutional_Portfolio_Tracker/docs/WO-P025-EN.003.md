# WO-P025-EN.003

**Project:** P_025 AJZ Institutional Portfolio Tracker  
**Type:** EN (Positions by account)  
**Opened:** 2026-09-20  
**Depends on:** WO-P025-EN.002 (IR PASS 11:20; CLOSE is a human ledger edit)  
**Status:** OPEN — code drafted 2026-09-20. Hub overlay + PEH required. Not CLOSED.

## Intent

Positions is one row per (ticker, account_id) from Fifo_Cost. Cost and shares are SUMIFS on ticker + account. Last price stays Market_Data. Do not raise the 200-row cap. Do not fill Theses. Do not change rate shocks.

## Hub filing path

`C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P025-EN.003.md`

## Completion gate

- [ ] Positions title says by account
- [ ] Positions!I is account_id, not PRIMARY
- [ ] Positions!E contains SUMIFS + Fifo_Cost
- [ ] Same ticker can appear on two accounts
- [ ] `tests/test_positions_by_account.py` PASS on Hub p140
- [ ] PEH from `verify\` with HUB_ROOT set
- [ ] Independent Review before CLOSED

## Out of scope

Positions cap raise, Theses, rate series, Equity_Curve account split, Schwab ledger, paper P&L, IRA flag, EN.001/EN.002 CLOSE.

## Deploy

`P_025_DeployPEH.bat` on the EN.003 zip. Overlay `python\` only. Do not rmtree.
