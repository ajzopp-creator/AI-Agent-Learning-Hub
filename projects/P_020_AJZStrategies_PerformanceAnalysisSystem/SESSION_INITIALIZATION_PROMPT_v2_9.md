# P_020 System Initialization Prompt (SIP) v3.1
**File:** `SESSION_INITIALIZATION_PROMPT_v2_9.md`
**Version:** 3.1
**Last Updated:** 2026-06-18
**Pairs With:** `docs\P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md`

---

## Purpose

Bootstraps every new P_020 chat. Runs the Python INIT block and surfaces DB/account/posture state. Domain rules (ThinkLog vocabulary, monthly review workflow, command blocks, database rules) live in the system doc — this file is steps only.

---

## How to Trigger

```
INIT  |  P_020  |  P_020 INIT  |  monthly review
```

---

## INIT Sequence (Execute in Order)

**RULE: Complete Steps 0 through 5 before taking action.**

### Step 0 — Environment Discovery
Call `tool_search("PowerShell")`. Present = Claude Desktop → proceed. Absent = web → STOP; ask user to switch to Desktop. Never claim environment without running this check.

### Step 0.5 — Work Order Review
Read `Agentic-Hub-Governance\work_orders\` for Owner=P_020 or P_020 in Affects, Status not CLOSED.
- BLOCKED → HALT; show Depends-On.
- PENDING → warn; ask proceed? (y/n).
- IN_PROGRESS or COMPLETE → note; proceed.

### Step 1 — Session Header
Display: `P_020 [Weekday, Month DD, YYYY] [HH:MM ET]`
Time via: `[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId((Get-Date),"Eastern Standard Time")`

### Step 2 — Run INIT Block
Use the `Start-Job + cmd /c` command block in `docs\P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md` Section 9.6. NEVER use `Start-Process -NoNewWindow`.

On MCP timeout: give Tony the one-liner for Anaconda Prompt; wait for paste; display the block.

On "monthly review" trigger: skip to Section 9.4 of system doc for the monthly workflow.

### Step 3 — Display Session Summary

```
---------------------------------------------
P_020 SESSION INITIALIZED
---------------------------------------------
Architecture:    v1.0
Filesystem MCP:  [available | unavailable]
Work Orders:     [status or OK]
[paste P_020_INIT.py output block here]
---------------------------------------------
```

### Step 4 — Flag Review
Surface any THRESHOLD or STALE flags from INIT output. On flag: prompt Tony to review account parameters and position sizing.

### Step 5 — Confirm Session Focus
> "Ready for trade import, monthly review, or something else?"
Wait for operator confirmation. Do NOT write code or take action until confirmed.

---

## What This SIP Does NOT Do

Carry domain rules. ThinkLog vocabulary, monthly review interpretation steps, INIT command block, database rules, and Schwab auth live in `docs\P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md` Sections 9.4–9.6 and `docs\SKILL.md` (p020-project-context).

---

## Fail-Fast Conditions

| Condition | Action |
|---|---|
| MCP unavailable | HALT; give one-liner; wait for paste |
| WO BLOCKED | HALT; resolve first |
| INIT script error | Display error; do not continue |
| THRESHOLD or STALE flag | Surface flag; prompt sizing review |

---

## Quick Reference

| Item | Value |
|---|---|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| System doc | `docs\P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md` |
| INIT command block | System doc Section 9.6 |
| ThinkLog vocabulary | System doc Section 9.5 |
| Monthly review | System doc Section 9.4 |
| Work orders | `Agentic-Hub-Governance\work_orders\` |

---

## Changelog

### v3.1 — 2026-06-18
- Full rewrite to P_300 SIP pattern. ThinkLog vocabulary, monthly review workflow, INIT command block migrated to system doc Sections 9.4–9.6. Start-Process -NoNewWindow reference removed (banned per ERROR 002). SKILL vocabulary source updated to system doc. SIP is now steps-only.

### v3.0 — 2026-06-04
- STEP 0.5 Work Order Review (shared ledger) added.

---

**End of P_020 SIP v3.1**