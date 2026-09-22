# WO-P025-EN.004

**Project:** P_025 AJZ Institutional Portfolio Tracker  
**Type:** EN (Equity_Curve cash = all primary accounts)  
**Opened:** 2026-09-20  
**Depends on:** WO-P025-EN.003 (PEH PASS; IR pending)  
**Status:** OPEN — code drafted 2026-09-20. Not CLOSED.

## Intent

Equity_Curve cash is `SUMIF` Daily_Cash by date across every primary account, not AJZ6348-only. Dashboard / Risk titles say combined primary accounts. Daily_Invested stays the existing date series. Not a Schwab ledger.

## Hub filing path

`C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P025-EN.004.md`

## Completion gate

- [ ] Equity_Curve!B2 contains SUMIF Daily_Cash and does not hard-code AJZ6348
- [ ] `tests/test_equity_curve_cash.py` PASS
- [ ] PEH from verify\ with HUB_ROOT
- [ ] Independent Review before CLOSED

## Out of scope

Positions cap, Theses, rate shocks, per-account Equity_Curve columns, Schwab cash, EN.003 CLOSE.

## Deploy

`P_025_DeployPEH.bat` on the EN.004 zip. Overlay only.
