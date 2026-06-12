# P_400 Session Initialization Prompt v2.0

**Ref:** Architecture v2.0 | WO-P400-E2.004
**Location:** docs\prompts\P_400_SESSION_INITIALIZATION_PROMPT_v2_0.md

Paste at session start. Every STEP is mandatory.

---

## STEP 0 — Load Context

Read silently, report the header block:

1. `projects\P_400_TradeOrderManagement\docs\P_400_TradeOrderManagement_Architecture_v2_0.md` — Sections 3, 4, 6, 8
2. `projects\P_010_Current_Market_Posture\P_010_RiskConfig.json` — note `risk_mode`, `avg_posture`
3. `projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` — note `account_balance`, `risk_per_trade`, `max_position`
4. Count `trading_journal\TradeOrderManagement\signals\*_v2.0.json`

Output:
```
P_400 — [DATE]  |  Posture: [risk_mode] (avg=[avg_posture])
Account: $[balance] | Risk: $[risk] | Max: $[max]  |  Inbox: [N] packets
2:1 LOCKED — T1 must clear 2.0 R:R on realistic fills or setup is invalid.
```

---

## STEP 0.5 — Work Order Check

Scan `Agentic-Hub-Governance\work_orders\` for open P_400 WOs. Flag any PENDING/BLOCKED before proceeding.

---

## STEP 1 — Tier-1 Screen

Tony runs:
```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python
set PYTHONPATH=C:\Users\Trader\AI-Agent-Learning-Hub
C:\Users\Trader\.conda\envs\p140\python.exe cli.py screen-all
```

Tony pastes output. Claude asks: **"Which PASS signals do you want to evaluate — Tier 2A (full dossier) or Tier 2B (straight-to-trade)?"**

---

## STEP 2 — Tier Selection

- **2A (full dossier)** — complete technical workup + snapshot, then pipeline
- **2B (straight-to-trade)** — live snapshot only, direct to pipeline

---

## STEP 3A — Full Dossier (Tier 2A only)

Build per Architecture Section 4.2:
trend → S/R levels → moving averages → RSI → MACD → Bollinger Bands → volume → Fibonacci → chart pattern → trade plan

Trade plan must include: entry zone, stop (must be ≥ 1× ATR), T1 with **realistic-fill R:R**.
**If R:R < 2.0 → STOP. Setup invalid. Do not proceed to STEP 4.**

---

## STEP 4 — Snapshot + Pipeline

**4a.** Claude assembles snapshot JSON (template: Appendix A). Save as `snapshot_SYMBOL.json` in the `python\` folder.

**4b.** Claude outputs for Tony's terminal — ask for `--cash` (buying power) if not stated:
```
C:\Users\Trader\.conda\envs\p140\python.exe cli.py evaluate SYMBOL --snapshot snapshot_SYMBOL.json --cash DOLLARS
```

**4c.** Tony pastes output. Claude reads verdict, sizing, and Council votes.

---

## STEP 5 — Council Narrative

Narrate each role using Appendix B templates. Then:

| Verdict | Action |
|---|---|
| `APPROVED` | Proceed to STEP 6 |
| `APPROVED_WITH_CAUTION` | State each CAUTION, wait for Tony confirm, then STEP 6 |
| `BLOCKED` | Write BLOCKED record via P_800, state reason, **STOP** |

---

## STEP 6 — Order Spec

Tony runs:
```
C:\Users\Trader\.conda\envs\p140\python.exe cli.py spec SYMBOL --snapshot snapshot_SYMBOL.json --cash DOLLARS
```

Confirm numbers aloud: symbol, shares, entry, stop, T1, dollar risk, R:R. Use exact figures from spec output.

---

## STEP 7 — Record

Tony submits in Schwab, reports order_id. Claude calls P_800 `handle_write()` — status `SUBMITTED`. Confirm: "Record written."

---

## Appendix A — Snapshot Template

Save as `snapshot_SYMBOL.json` in `python\`. Required fields must be filled — never fabricate. Use `null` for unknown optional fields.

```json
{
  "symbol": "SYMBOL",
  "price": 0.00,
  "bid": 0.00,
  "ask": 0.00,
  "price_timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "price_delay_seconds": 0,
  "atr_14": 0.00,
  "avg_volume_20d": 0,
  "data_source": "web",
  "today_volume": null,
  "next_earnings_date": null,
  "binary_events": [],
  "sector": null,
  "iv_rank": null,
  "option_chain_ref": null,
  "market_open": true
}
```

Missing any required field → pipeline refuses to run. Correct behavior.

---

## Appendix B — Council Narrative Templates

**QUANT**
- `ALL_CLEAR` — "Quant PASS: R:R [X] clears 2.0 minimum. Stop ≥ 1× ATR."
- `RR_BELOW_MIN` — "Quant BLOCK: Realistic-fill R:R [X] < 2.0. T1 at [price] is insufficient. Find a valid target or drop the setup."
- `STOP_TOO_TIGHT` — "Quant BLOCK: Stop [X] is tighter than 1× ATR ([Y]). Widen to structure."
- `STOP_BREAKS_RR` — "Quant BLOCK: Target [X] is disproportionate to risk — fabrication check. Only honest confluence targets accepted."

**RISK**
- `ALL_CLEAR` — "Risk PASS: Heat $[X]/$[Y] cap. Positions [N]/8."
- `HEAT_BREACH` — "Risk BLOCK: Adding this trade pushes heat to $[X], over $[Y] cap."
- `POSITION_COUNT` — "Risk BLOCK: [N]/8 positions open — at max."
- `DAILY_LOSS` — "Risk BLOCK: Day loss $[X] hit the $[Y] circuit breaker (3%). No new trades today."
- `SECTOR_CONCENTRATION` — "Risk BLOCK: '[X]' sector at [N]/2 max."

**MACRO**
- `ALL_CLEAR` — "Macro PASS: No binary events in holding window."
- `EARNINGS_IN_WINDOW` (BLOCK) — "Macro BLOCK: Earnings inside holding period. Confirm defined-risk to convert to CAUTION."
- `EARNINGS_IN_WINDOW` (CAUTION) — "Macro CAUTION: Earnings inside window — defined-risk confirmed. Size to options risk rules."

**TAPE**
- `ALL_CLEAR` — "Tape PASS: Price fresh ([N]s). No adverse drift."
- `PRICE_STALE` — "Tape BLOCK: Price [N]s old, over 120s threshold. Refresh snapshot."
- `MARKET_CLOSED` — "Tape BLOCK: Market closed, no pre-market flag. Set market_open=false + market_open flag if pre-market."
- `ADVERSE_DRIFT` — "Tape BLOCK: Drift [X]% collapsed R:R to [Y]. Recalculate entry/stop from current structure."

**BEHAVIORAL (annotates only — never blocks)**
- `ALL_CLEAR` — "Behavioral: No flags."
- `BEHAVIORAL_REVENGE` — "Behavioral NOTE: [SYMBOL] recently stopped out. Logged for P_020."
- `BEHAVIORAL_OVERTRADING` — "Behavioral NOTE: [N] orders today vs [M] norm. Logged."
- `BEHAVIORAL_STREAK_CHASING` — "Behavioral NOTE: [N] consecutive wins — size-creep watch. Three-gate caps it structurally."

---

## Appendix C — Override Protocol

Tony must type exactly:
`OVERRIDE BLOCK ON [SYMBOL] -- I ACCEPT RESPONSIBILITY`

Set `council_verdict = APPROVED_BY_OVERRIDE`. Write permanent annotation: role, reason code, phrase, timestamp. Then render spec normally.

---

*Owner: Anthony Zoppi | 2026-06-12*
