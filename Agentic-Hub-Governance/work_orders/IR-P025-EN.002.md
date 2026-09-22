# Independent Review — WO-P025-EN.002

**Reviewer session:** Grok sandbox draft from Hub operator report, 2026-09-20  
**WO:** WO-P025-EN.002 (opened 2026-09-15)  
**Deploy method:** `projects\P_025_AJZ_Institutional_Portfolio_Tracker\P_025_DeployPEH.bat`  
**Package:** `run_this_P025_20260920_103700.zip` (overlay `fifo_lots.py` + tests + PEH `221200`)  
**PEH:** `Agentic-Hub-Governance\verify\run_this_P025_20260915_221200.py`  
**Hub PEH:** PASS 2026-09-20 10:47 with HUB_ROOT + p140  
**Analytics:** `output\P_025_Portfolio_BUILT_Analytics_20260920_1046.xlsx`  
**Verdict: DO NOT CLOSE EN.002 in this session**

This note records the operator-reported PASS. It is not a live-disk re-read by a session other than DeployPEH. Governance CLOSE needs (1) this WO on the Hub ledger and (2) a separate Hub session that opens the files.

## Gate scorecard

| Gate | Operator / PEH report | This session live disk | Close? |
|------|------------------------|------------------------|--------|
| Overlay only; `python\` not deleted | Reported | Not visible here | no |
| Closed-long rule string in `fifo_lots.py` | PEH would FAIL without it; PEH PASS | Not re-read on Hub | no |
| pytest on Hub p140 | **15/15** | Not re-run here | no |
| Yearly rebuild | 443 trades, fifo_lots=4 | Not opened here | no |
| Live longs vs fifo **tickers** | 3 live longs; PEH PASS ⇒ no extra ticker names | Not opened here | no |
| Cost_Basis not labeled FIFO | PEH check | Not opened here | no |
| Positions cost SUMIF Fifo_Cost | PEH check | Not opened here | no |
| WO on `Agentic-Hub-Governance\work_orders\` | Operator: **no ledger file** | — | **no** |
| IR other than DeployPEH session | This draft is sandbox | Hub IR not done | **no** |

## Numbers that are allowed

PEH compares ticker sets, not lot-row counts. Four remaining lot rows on three live-long tickers is valid (two lots on one name). The 2026-09-15 ASX extra-**name** case would FAIL `221200`. PASS means that extra-name set was empty on this rebuild.

## Required Hub IR before CLOSED

On Windows, `HUB_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub`:

1. Copy `projects\P_025_AJZ_Institutional_Portfolio_Tracker\docs\WO-P025-EN.002.md` to `Agentic-Hub-Governance\work_orders\WO-P025-EN.002.md` if missing.
2. Confirm `python\domain\fifo_lots.py` contains `do not FIFO-steal older opens` and skips `status == "closed"` without consuming older lots.
3. `p140 -m pytest tests\` from `python\`.
4. Open `output\P_025_Portfolio_BUILT.xlsx`: Fifo_Lots tickers ⊆ Trade_Log live longs (`open`+`partial`); list any extra names.
5. Open Analytics `*_20260920_1046.xlsx`: Positions!E3 contains `SUMIF` and `Fifo_Cost`; Cost_Basis header has no “FIFO”.
6. Only then: status CLOSED, reviewer name + date on the WO.

## Close recommendation

**Keep OPEN.** Intent looks implemented and PEH PASS is on record. Missing ledger file + missing separate Hub IR block CLOSED.

Do not CLOSE EN.001 from this note.
