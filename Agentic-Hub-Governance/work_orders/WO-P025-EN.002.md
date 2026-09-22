# WO-P025-EN.002

**Project:** P_025 AJZ Institutional Portfolio Tracker  
**Type:** EN (FIFO remaining lots vs Trade_Log status)  
**Opened:** 2026-09-15  
**Depends on:** WO-P025-EN.001 (still OPEN, not CLOSED)  
**Status:** OPEN — Hub PEH `221200` PASS 2026-09-20 10:47. Ledger file was missing on Hub. Not CLOSED.

## Intent

Fifo_Lots must not keep a long lot when Trade_Log says that account+ticker is not a live long (`open` or `partial`), unless the mismatch is proven P_020 semantics and the verify rule is rewritten.

Trigger was PEH `215200` WARN 2026-09-15 22:02: extra FIFO name **ASX** (3 open-long tickers, 4 fifo tickers).

## Rule shipped

`domain/fifo_lots.py`:

- long `open` / `partial` → open a lot (partial keeps qty)
- long `closed` → do not open a lot and do not FIFO-steal older opens
- short → consume existing long lots only

Cost_Basis stays lifetime VWAP. Positions cost stays `SUMIF` Fifo_Cost.

Verify PEH: extra FIFO **ticker** vs live-long set is FAIL. Lot **row** count may exceed ticker count.

## Hub deploy (done)

- Package: `run_this_P025_20260920_103700.zip`
- Method: `P_025_DeployPEH.bat [zip-path]` — overlay only, no `rmtree python\`
- PEH: `Agentic-Hub-Governance\verify\run_this_P025_20260915_221200.py`
- Result: PASS 2026-09-20 10:47
- pytest 15/15
- yearly: 443 trades, fifo_lots=4 rows, live longs=3 tickers
- Analytics: `output\P_025_Portfolio_BUILT_Analytics_20260920_1046.xlsx`

`fifo_lots=4` and live longs=3 is legal if four lot rows sit on three live tickers. Extra **name** would have FAILed.

## Hub filing path

`C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P025-EN.002.md`

Copy this file there. Deploy PEH session does not write that folder and does not CLOSE this WO.

## Completion gate (copy before OWNER_DONE)

- [x] Closed-long rule in `domain/fifo_lots.py` (`do not FIFO-steal older opens`)
- [x] `tests/test_fifo_lots.py` covers closed long, partial keep, no steal of older open
- [x] `python -m pytest tests/` PASS on Hub `p140` (15/15, 2026-09-20)
- [x] PEH `run_this_P025_20260915_221200.py` PASS from `verify\` with HUB_ROOT set
- [x] Cost_Basis header does not say FIFO (PEH check)
- [x] Positions cost `SUMIF` Fifo_Cost (PEH check)
- [x] Extra FIFO ticker vs live-long set is FAIL (PEH check; this run had no extra names)
- [ ] WO file exists under `Agentic-Hub-Governance\work_orders\`
- [ ] Independent Review session re-reads live disk (not the DeployPEH session)
- [ ] CLOSED stamp + reviewer name/date

## Out of scope

EN.001 CLOSE stamp, Positions cap, theses, rate series, Schwab ledger, paper P&L, IRA flag flip.

## Deploy reuse

```
P_025_DeployPEH.bat [zip-path]
```

Do not run `run_this_*.py` from the project root beside `python\`.
