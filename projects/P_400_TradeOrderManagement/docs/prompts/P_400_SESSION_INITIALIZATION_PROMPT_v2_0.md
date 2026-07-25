# P_400 Session Initialization Prompt v2.5
**Ref:** Architecture v2.2 | Last Updated: 2026-07-24
**Location:** docs\prompts\P_400_SESSION_INITIALIZATION_PROMPT_v2_0.md
**Pairs With:** docs\P_400_TradeOrderManagement_Architecture_v2_0.md

Every STEP is mandatory. Templates and narrative scripts live in the architecture doc — this file is steps only.

---

## STEP 0 — Load Context
Read silently, report header:
1. Architecture doc — Sections 3, 4, 6, 8
2. P_010_RiskConfig.json — risk_mode, avg_posture
3. P_000_Account_Parameters_Current.md — balance, risk_per_trade, max_position
4. Count trading_journal\TradeOrderManagement\signals\*_v2.0.json

```
P_400 -- [DATE]  |  Posture: [risk_mode] (avg=[avg_posture])
Account: $[balance] | Risk: $[risk] | Max: $[max]  |  Inbox: [N] packets
2:1 LOCKED -- T1 must clear 2.0 R:R on realistic fills or setup is invalid.
```

## STEP 0.5 — Work Order Check
Scan Agentic-Hub-Governance\work_orders\ for open P_400 WOs. Flag PENDING/BLOCKED before proceeding.

## STEP 0.6 — Session Header
Display: `P_400 [Weekday, Month DD, YYYY] [HH:MM ET] [topic]`
Time via: `[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date),"Eastern Standard Time")`
This line is the suggested chat name — copy/paste as chat title.

## STEP 0.7 — Auto Tier-1 Screen (WO-P400-E3.007)
Runs automatically as part of INIT, right after STEP 0.6 -- not a separate
manual invocation later in the session. Same terminal, same command as
before:
```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python
set PYTHONPATH=C:\Users\Trader\AI-Agent-Learning-Hub
C:\Users\Trader\.conda\envs\p140\python.exe cli.py screen-all
```
Tony pastes output. FAIL packets auto-dispose (WO-P400-E2.018); PASS list
stays in inbox for STEP 1.

## STEP 1 — Tier Selection
From the PASS list already printed in STEP 0.7, ask: "Which PASS signals
— Tier 2A (full dossier) or Tier 2B (straight-to-trade)?"

## STEP 2 — Tier + Vehicle Selection
- **2A** — full technical workup + snapshot, then pipeline
- **2B** — live snapshot only, direct to pipeline
- **Options fork:** stock sizes to 0 OR R:R < 2:1 OR Tony requests options — add --options flag; Claude asks for chain file (arch doc Section 7.3) before STEP 4.

## STEP 3A — Full Dossier (2A only)
Run `cli.py dossier SYMBOL` (WO-P400-E4.003) -- computes items 1-8 live
(trend, S/R, MAs, RSI, MACD, BB, volume, Fib). Tony pastes output. Claude
narrates item 9 (chart pattern -- H&S, double top, cup-and-handle, flags)
over the printed table -- never auto-computed; geometric pattern ID is a
judgment call, not arithmetic (arch doc Section 4.2).
Trade plan: entry zone, stop (>= 1x ATR), T1 with realistic-fill R:R.
R:R < 2.0 — STOP, setup invalid.
Entry drifted > 1.5% AND no 2:1 target — STOP, write REVIEWED_NO_TRADE via P_800 (drop_reason=ENTRY_MISSED).

## STEP 4 — Snapshot + Pipeline
**4a.** Assemble snapshot_SYMBOL.json (arch doc Section 6.2). Save in python\.
**4b (options only).** Tony supplies chain_SYMBOL.json (arch doc Section 7.3). TOS first — ChartExchange — Yahoo — Barchart. Spreads need two files.
**4c.** Output command — ask --cash if not stated:

Stock:
```
C:\Users\Trader\.conda\envs\p140\python.exe cli.py evaluate SYMBOL --snapshot snapshot_SYMBOL.json --cash DOLLARS
```
Options single-leg:
```
C:\Users\Trader\.conda\envs\p140\python.exe cli.py evaluate SYMBOL --snapshot snapshot_SYMBOL.json --cash DOLLARS --options --chain chain_SYMBOL.json
```
Options spread (IV > 50 or premium breach):
```
C:\Users\Trader\.conda\envs\p140\python.exe cli.py evaluate SYMBOL --snapshot snapshot_SYMBOL.json --cash DOLLARS --options --chain chain_SYMBOL.json --spread
```
**4d.** Tony pastes output. Read verdict, sizing, Council votes.

## STEP 5 — Council Narrative
Narrate each role using templates in arch doc Section 4.9. Then:
- APPROVED — STEP 6
- APPROVED_WITH_CAUTION — state each caution, wait for confirm, STEP 6
- APPROVED_WITH_SEVERE_WARNING -- state each severe warning + open-position list (arch doc Section 4.3), wait for confirm, STEP 6
- BLOCKED — write BLOCKED record via P_800, state reason, STOP

## STEP 6 — Order Spec
Stock:
```
C:\Users\Trader\.conda\envs\p140\python.exe cli.py spec SYMBOL --snapshot snapshot_SYMBOL.json --cash DOLLARS
```
Options/spread: spec rendered at end of evaluate output (Pattern B or C). Confirm aloud: symbol, contracts, entry premium, stop trigger, T1, max loss, R:R.

## STEP 7 — Record
Tony submits in Schwab, reports order_id. Call P_800 handle_write() — status SUBMITTED. Confirm: "Record written."

---

## What This SIP Does NOT Carry

- **Snapshot JSON template** — arch doc Section 6.2
- **Chain JSON template** — arch doc Section 7.3
- **Council narrative scripts** — arch doc Section 4.9
- **Override protocol** — arch doc Section 2.5 item 5

---

## Changelog

### v2.5 -- 2026-07-24
- STEP 3A: screenshot-reading replaced with `cli.py dossier SYMBOL`
  (WO-P400-E4.003) -- items 1-8 computed live, item 9 (chart pattern)
  stays Claude-narrated only.

### v2.4 -- 2026-07-20
- RISK role never blocks (Tony directive): heat/position-count/daily-loss/sector checks downgraded BLOCK -> SEVERE_WARNING; new CASH_BELOW_RISK check added; open-position list attached to every RISK annotation. Matching Tier-1 change in domain/screen.py (HEAT_BREACH/POSITION_COUNT downgraded FAIL -> WARN, no longer auto-disposed). STEP 5 gains an APPROVED_WITH_SEVERE_WARNING branch. See Architecture v2.2.

### v2.2 — 2026-06-18
- Appendices A1, B, C removed; content migrated to architecture doc Sections 4.9, 6.2 (JSON template added). Steps 0–7 unchanged. SIP is now steps-only.

### v2.1 — 2026-06-16
- Phase E3 options pipeline integrated (WO-P400-E3.003); chain template added; options/spread CLI variants added.

---
*Owner: Anthony Zoppi | 2026-07-24 | v2.5*