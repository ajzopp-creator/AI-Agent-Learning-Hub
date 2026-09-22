# Independent Review — WO-P025-EN.001

**Reviewer session:** Grok sandbox, 2026-09-15  
**WO:** WO-P025-EN.001 (opened 2026-09-04)  
**Deploy PEH:** `run_this_P025_20260904_170500.py`  
**Claimed Hub PEH:** PASS 2026-09-04 19:53 (yearly)  
**Verify PEH (no build):** `run_this_P025_20260915_215200.py`  
**Hub verify:** PASS 2026-09-15 22:02:14 from `verify\` with HUB_ROOT set. Analytics `*_20260915_2128`. pytest 13 passed.  
**WARN:** Fifo ticker ASX not in Trade_Log open-long set (3 open longs, 4 fifo tickers).  
**Follow-on:** WO-P025-EN.002 opened 2026-09-15 (FIFO vs status / ASX).  
**Verdict: DO NOT CLOSE EN.001** — live-disk checks passed; ASX parked on EN.002. PEH did not close the WO.

## Gate scorecard

| Gate | Sandbox source | Live Hub disk | Close? |
|------|----------------|---------------|--------|
| `HUB_ROOT` default is Hub path; OneDrive not in fallback | PASS — `config._DEFAULT_HUB_ROOT = C:\Users\Trader\AI-Agent-Learning-Hub` | NOT VERIFIED HERE | no |
| `python -m pytest tests/` on Hub `p140` | PASS sandbox: **13 passed** (2.70s) | PEH log claimed pytest OK on 2026-09-04; not re-run tonight | no |
| PEH PASS from `verify\` with `HUB_ROOT` set | PEH script exists and checks the right sheets | Memory: PASS 19:53, 427 trades, 253 market, fifo_lots=6, fifo_cost=5, cost_basis=5 | no |
| Workbook Fifo_Lots, Fifo_Cost; Positions cost SUMIF Fifo_Cost | PASS in source (`analytics_sheets.py` col E) | PEH checked Positions!E3 contains `Fifo_Cost` | no |
| Correlation off-diagonals are CORREL | PASS in source (`analytics_exposure.py`) | PEH checked Correlation!C5 contains `CORREL` | no |
| Geographic / Stress not placeholders | PASS titles + formulas in `analytics_scenarios.py` | PEH checked title cells | no |
| Cost_Basis labeled lifetime VWAP, not FIFO | PASS in `schemas.py` / `trade_processor.py` docstring | sheet headers are Ticker/Avg_Cost/Current_Shares/Total_Cost_Basis/Account — no “FIFO” label | no |
| Independent Review re-reads live disk | This memo | **Not done** | **NO CLOSE** |

## What the source tree actually implements

1. OneDrive fallback removed. Env `HUB_ROOT` wins; default is Hub path.
2. FIFO lots: longs open lots; closed longs self-consume; shorts consume only; PAPER is caller-filtered. Tests cover partial sell, closed long, naked short, two-account isolation.
3. Positions P&L cost = `SUMIF(Fifo_Cost!A:A, ticker, Fifo_Cost!D:D)` — remaining FIFO $ across accounts. Cost_Basis remains lifetime VWAP × remaining shares and is not wired into Positions cost.
4. Correlation: diagonal 1, off-diagonal `CORREL` via INDEX/MATCH on Market_Data, cap 20.
5. Geographic: SUMPRODUCT country × Positions MV.
6. Stress: linear MV shocks. Rate rows are **labels with 0 shock** (explicitly out of scope).
7. IRA_FEED_READY = True in current `config.py` (both AJZ6348 and 5232-9885). That flip is **outside** WO-P025-EN.001 intent list but is in the tree that PEH ran.

## Findings that do not block intent, but block CLOSE

**F1 — Live disk not in this session.** Cannot tick gate 8. Do not mark CLOSED.

**F2 — Docs drift.** `P_025_PROJECT_INSTRUCTIONS.md` §4 still says Positions cost via Cost_Basis VLOOKUP. Code uses Fifo_Cost SUMIF. AGENTS.md / style card still describe IRA gated False, blank Correlation, Geographic/Stress placeholders. Stale operator docs.

**F3 — FIFO row counts look thin.** PEH reported fifo_lots=6, fifo_cost=5, cost_basis=5 against 427 trades. Possible and legal if most names are closed. Independent Review on Hub should open Fifo_Lots and confirm remaining names match open longs in Trade_Log. Not a source defect by itself.

**F4 — Positions SUMIF is ticker-only.** Multi-account remaining cost is summed into one Positions row. Intent said multi-account cost; this is a roll-up, not per-account Positions rows. Acceptable unless Tony wants split rows.

**F5 — WO file on Hub ledger.** Draft lives in `docs\WO-P025-EN.001.md`. Gate “open the P_025 work-order ledger” is only done if that file was copied to `Agentic-Hub-Governance\work_orders\`. This session cannot confirm the copy.

**F6 — File-size limits.** All reviewed modules are under 300 lines. Closest: `trade_processor.py` 279, `excel_writer.py` 262, `analytics_sheets.py` 261.

## Required Hub checks before CLOSED (copy into a later session)

On Windows, with `HUB_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub`:

1. Confirm `Agentic-Hub-Governance\work_orders\WO-P025-EN.001.md` exists.
2. Confirm `python\config.py` `_DEFAULT_HUB_ROOT` has no OneDrive.
3. `C:\Users\Trader\.conda\envs\p140\python.exe -m pytest tests\` from `python\`.
4. Open latest `output\P_025_Portfolio_BUILT_Analytics_*.xlsx`:
   - sheets Fifo_Lots, Fifo_Cost
   - Positions!E3 formula contains `SUMIF` + `Fifo_Cost`
   - Correlation off-diagonal contains `CORREL`
   - Geographic / Stress titles do not contain “placeholder”
   - Cost_Basis header row does not say FIFO
5. Spot-check Fifo_Lots count vs open longs.
6. Only then: status CLOSED, Independent Review name + date on the WO.

## Close recommendation

**Keep OPEN.** Intent looks implemented in the sandbox tree and the 2026-09-04 PEH claim is consistent with the PEH script. Governance CLOSE needs a Hub-disk pass in a session that can see the live files. This is that review’s start, not its close stamp.
