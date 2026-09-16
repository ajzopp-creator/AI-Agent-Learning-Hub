# P_010 System Initialization Prompt (SIP) v2.10
**File:** `docs/SESSION_INITIALIZATION_PROMPT.md`
**Version:** 2.10
**Last Updated:** 2026-08-26
**Pairs With:** `P_010_System_Documentation_v3.md`

---

## Purpose

Bootstraps every new P_010 chat. Reads today's posture state and surfaces it. Domain rules (risk mode thresholds, VXX overlay, intraday hierarchy, file locations, PowerShell execution rules) live in the system doc — this file is steps only.

---

## How to Trigger

```
INIT  |  P_010  |  P_010 INIT  |  INIT daily  |  INIT intraday
```

---

## INIT Sequence (Execute in Order)

**RULE: Complete Steps 0 through 5 before taking action.**

### Step 0 — Environment Discovery
Call `tool_search("PowerShell")`. Present = Claude Desktop → proceed. Absent = web → STOP; ask user to switch to Desktop. Never claim environment without running this check.

### Step 0.5 — Work Order Review
Read `Agentic-Hub-Governance\work_orders\` for Owner=P_010 or P_010 in Affects, Status not CLOSED.
- BLOCKED → HALT; show Depends-On.
- PENDING → warn; ask proceed? (y/n).
- IN_PROGRESS or COMPLETE → note; proceed.

### Step 1 — Session Header
Display: `P_010 [Weekday, Month DD, YYYY] [HH:MM ET]`
Time via: `[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date),"Eastern Standard Time")`

### Step 2 — Read Posture State
Read `P_010_RiskConfig.json` (project root). Check the `timestamp` field vs today (not `posture_date` -- that field does not exist in the schema; corrected 2026-08-26, WO-P010-E1.003):
- `MORNING_RUN_FAILED.flag` present in project root → display `MORNING RUN FAILED -- see flag file and today's P_010_Daily_*.log`; do not treat RiskConfig as current even if the JSON parses cleanly (WO-P010-E1.003 guard).
- Today's data present, no failure flag → display risk_mode, avg_posture, SPY_posture, QQQ_posture, vxx_signal, intraday_signal.
- Missing or stale → display: `POSTURE NOT CURRENT — run INIT daily to generate.`
- Missing `morning_risk_mode` field → flag; ERROR 001 risk (see error corrections log).

### Step 3 — Display Session Summary

```
---------------------------------------------
P_010 SESSION INITIALIZED
---------------------------------------------
Architecture:      v3
Filesystem MCP:    [available | unavailable]
Work Orders:       [status or OK]
Posture date:      [today YYYY-MM-DD | STALE — run INIT daily]
risk_mode:         [FULL | HALF | OFF]
avg_posture:       [value]
SPY / QQQ:         [spy_posture] / [qqq_posture]
intraday_signal:   [UPGRADE | CONFIRM | DOWNGRADE | not run]
vxx_signal:        [BULLISH_CONFIRM | NEUTRAL | CAUTION | WARNING | not run]
---------------------------------------------
```

### Step 4 — If INIT daily or INIT intraday Triggered
Use the MCP command blocks in `P_010_System_Documentation_v3.md` Section 8 (Manual Triggers).
PowerShell execution rule: ALWAYS Start-Job + cmd /c. NEVER Start-Process -NoNewWindow.

### Step 5 — Confirm Session Focus
> "Posture loaded, or run INIT daily/intraday first?"
Wait for operator confirmation. Do NOT write code or take action until confirmed.

---

## What This SIP Does NOT Do

Carry domain rules. Risk mode thresholds, VXX overlay, intraday hierarchy, file locations, and PowerShell command blocks live in `P_010_System_Documentation_v3.md` Sections 4, 3, and 8.

---

## Fail-Fast Conditions

| Condition | Action |
|---|---|
| MCP unavailable | HALT; ask for Desktop |
| WO BLOCKED | HALT; resolve first |
| P_010_RiskConfig.json missing | Surface INIT daily prompt |
| Posture date stale | Surface INIT daily prompt |
| morning_risk_mode field missing | Flag ERROR 001 risk |
| MORNING_RUN_FAILED.flag present | Display as failed run; do not present RiskConfig as current (WO-P010-E1.003) |

---

## Quick Reference

| Item | Value |
|---|---|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Master config | `P_010_RiskConfig.json` (project root) |
| Failure flag | `MORNING_RUN_FAILED.flag` (project root) -- WO-P010-E1.003 |
| System doc | `P_010_System_Documentation_v3.md` (project root) |
| Error log | `docs\P_010_Error_Corrections_Log.md` |
| Work orders | `Agentic-Hub-Governance\work_orders\` |

---

## Changelog

### v2.10 — 2026-08-26
- WO-P010-E1.003 IMPERATIVE SWEEP closure: documented MORNING_RUN_FAILED.flag
  fail-loud mechanism (Step 2, Fail-Fast Conditions, Quick Reference) --
  this SIP had no mention of it despite the mechanism being live since
  2026-08-10. Corrected Step 2/Step 3 field references: posture_date
  (never existed in the schema) -> 	imestamp; intraday_adjustment/
  NONE-HALF-REDUCED (stale v4 field) -> intraday_signal/
  UPGRADE-CONFIRM-DOWNGRADE (current V5.0 field, matches live
  P_010_RiskConfig.json and the corrected p010-project-context SKILL.md).

### v2.9 — 2026-06-18
- Full rewrite to P_300 SIP pattern. Domain rules (risk thresholds, VXX, intraday hierarchy, file locations) removed — live in system doc. PowerShell execution rules migrated to system doc Section 8 + error corrections log. SIP is now steps-only.

### v2.8 — 2026-06-01
- Added PowerShell execution rules + ERROR 002; added market health step.

---

**End of P_010 SIP v2.10**


