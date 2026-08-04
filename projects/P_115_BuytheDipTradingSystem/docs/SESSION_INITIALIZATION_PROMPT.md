# P_115 System Initialization Prompt (SIP) v3.5
**File:** `docs/SESSION_INITIALIZATION_PROMPT.md`
**Version:** 3.5
**Last Updated:** 2026-07-24
**Pairs With:** `docs/P_115_System_Architecture.v1.0.md`

---

## Purpose

Bootstraps every new P_115 chat. Loads account state, market posture, and work orders so the AI starts oriented. Domain rules (scoring, signal emission, schema, chart patterns) live in the architecture doc — this file is steps only.

---

## How to Trigger

```
INIT  |  P_115  |  P_115 INIT
```

---

## INIT Sequence (Execute in Order)

**RULE: Complete Steps 0 through 6 in order before taking action. No step may be silently skipped. Step 1 (Session Header) and Step 4 (Summary) are BOTH required visible output every run — emitting one never satisfies the other.**

### Step 0 — Environment Discovery
Call `tool_search("PowerShell")`. Present = Claude Desktop → proceed. Absent = web → STOP; ask user to switch to Desktop. Never claim web/Desktop status before running this check.

### Step 0.5 — Work Order Review
Read `Agentic-Hub-Governance\work_orders\` for Owner=P_115 or P_115 in Affects, Status not CLOSED.
- BLOCKED → HALT; show Depends-On.
- PENDING → warn; ask proceed? (y/n).
- IN_PROGRESS or COMPLETE → note; proceed.

### Step 1 — Session Header  ⛔ MANDATORY — NEVER SKIP, NEVER SUBSTITUTE
**Emit this exact formatted line as Step 1. A bare `Date: ...` line is NOT a substitute and does not satisfy this step. If the Step 4 summary has appeared without this header line shown first, Step 1 was skipped — stop and emit it.**

Display: `P_115 [Weekday, Month DD, YYYY] [HH:MM] ET [optional session-type label]`
Example: `P_115 Friday, June 19, 2026 09:13 ET Market Analysis`
Time via: `[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date),"Eastern Standard Time")`

### Step 2 — Load Account Parameters
Read `P_000_Account_Parameters_Current.md` (authoritative source):
- Extract: Balance, Base Risk$, Max Position$, Next Review, Risk Mode Adjustments table (keyed by risk_mode).
- Missing file → use STANDARD row, flag.

### Step 3 — Load Market Posture
Read `P_010_RiskConfig.json`. Extract risk_mode (authoritative), avg_posture, intraday_signal.
Fail → STANDARD risk, flag.
**Posture MUST be re-read fresh before every STEP 2 packet emission (P_115 does no sizing -- v1.3) — this read is INIT snapshot only.**

### Step 4 — Display Session Summary

```
---------------------------------------------
P_115 SESSION INITIALIZED
---------------------------------------------
Architecture:    v1.0
Filesystem MCP:  [available | unavailable]
Work Orders:     [status or OK]
Account:         $<balance>  Risk: $<risk>  MaxPos: $<maxpos>  Review: <date>
Market posture:  SPY <p> / QQQ <p>  Avg <avg>  risk_mode: <MODE>  <intraday if present>
Trading mode:    [HOT | STANDARD | CORRECTION]
Strategies:      P_115 BuyDip | P_116 Launchpad | P_117 Outside | P_118 EddieZ
Schema:          27-col LOCKED  |  PatternType = READ FROM CHART (P_118)
---------------------------------------------
```

### Step 5 — Validation Reminder
Run one known-good cross-check before first signal output: MOD 3-3-2-3 → BUY | ATI 3-2-2-3 → BUY.

### Step 6 — Confirm Session Focus
> "Ready for trade signals, or steering elsewhere?"
Wait for operator confirmation. Do NOT write code or take action until confirmed.

---

## What This SIP Does NOT Do

Carry domain rules. All scoring (HybridTier, FundamentalsTier, 200-MA penalty, CandleTier), signal emission (Stop Derivation Rule, SIGNAL_V2 packet build), Fund Verification protocol, chart pattern definitions, schema, and options methodology live in `docs/P_115_System_Architecture.v1.0.md` Sections 2.4, 8.2, 8.4, 8.5, 9.3, and `docs/OPTIONS_RISK_METHODOLOGY.md`. Position sizing, R:R validation, stop/target authority, and order formatting are P_400's job (P_400 architecture doc Section 3.1) -- not P_115's, as of 2026-07-24.

---

## Fail-Fast Conditions

| Condition | Action |
|---|---|
| MCP unavailable | HALT; ask for Desktop |
| WO BLOCKED | HALT; resolve first |
| Account file missing | Proceed STANDARD, flagged |
| Posture file missing | Proceed STANDARD, flagged |

---

## Quick Reference

| Item | Value |
|---|---|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Account params | `projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` |
| Posture | `projects\P_010_Current_Market_Posture\P_010_RiskConfig.json` |
| Work orders | `Agentic-Hub-Governance\work_orders\` |
| Architecture | `docs\P_115_System_Architecture.v1.0.md` |

---

## Changelog

*Retention rule: this section keeps only the current + prior version. Older entries live in `docs/P_115_SIP_CHANGELOG_ARCHIVE.md`.*

### v3.4 — 2026-06-19
- **Step 1 hardened against runtime skip.** A live INIT run produced the Step 4 summary but never emitted the Step 1 header line, substituting a bare `Date:` line. Step 1 now marked MANDATORY / no-substitute with an explicit self-check, and the top RULE states no step may be silently skipped and that Step 1 and Step 4 are independently required output. Header format updated to the canonical Hub standard with the optional session-type label slot (WO-P000-E4.001 v1.1): `P_115 [Weekday, Month DD, YYYY] [HH:MM] ET [optional label]`.

### v3.3 — 2026-06-18
- Full rewrite to P_300 SIP pattern. Domain rules migrated to architecture doc Sections 2.4, 8.2, 8.4, 8.5. SIP is now steps-only.
- Content migrated: FundTier map, 200-MA penalty table, AsymmetricSetup conditions, CandleTier pattern names, 2-Tranche exit rule, Fund Verification protocol, P_118 chart pattern definitions (4 patterns).

### Pre-v3.3 history
See `docs/P_115_SIP_CHANGELOG_ARCHIVE.md` (v3.2 and earlier).

---

**End of P_115 SIP v3.4**