# P_300 System Initialization Prompt (SIP) v3.1

**File:** `docs/prompts/P_300_System_Initialization_Prompt_v3_1.md`  
**Version:** 3.1  
**Last Updated:** 2026-06-04  
**Pairs With:** `docs/P_300_System_Architecture_v2.7.md` + `p300-project-context/SKILL.md`

---

## Purpose

Bootstraps every new P_300 chat. Loads account state, market posture, work orders, lessons, catalog, and LM Studio readiness so the AI starts oriented.

---

## How to Trigger

```
INIT  |  P_300  |  P_300 INIT
```

---

## INIT Sequence (Execute in Order)

**RULE: Complete Steps 0 through 6 before writing code or taking action. Steps 4–5c are uninterruptible.**

### Step 0 — Environment Discovery

Call `tool_search` for `windows-mcp:FileSystem` or `windows-mcp:PowerShell`. If available, proceed to Step 0.5. If unavailable, skip Steps 5b/5c and warn in Step 6.

### Step 0.5 — Work Order Review

Query shared work order ledger at `C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\work_orders\`:
- **Owner=P_300, status not CLOSED** → Display; **HALT** if action required before proceeding
- **P_300 in Affects, Ack pending** → Display; **ACTION REQUIRED** after session work to Ack

If ledger unavailable, proceed with inline note.

### Step 1 — Session Header

Display: `P_300 [Day, Month DD, YYYY -- HH:MM ET]`  
Get time via `windows-mcp:PowerShell` or fallback to local system.

### Step 2 — Verify SKILL Loaded

Confirm `p300-project-context` SKILL active by referencing one rule unprompted. If missing, request manual paste; do not proceed.

### Step 3 — Working State Existence Check

Verify both files exist:
- `<project>\tasks\lessons.md`
- `<project>\tasks\todo.md`

If either missing: **HALT** — prompt operator to verify Stage 3 setup.

### Step 4 — Load Working State

Read via `windows-mcp:FileSystem`:
- `tasks/lessons.md` — M-series rules, O-series lessons
- `tasks/todo.md` — Active stage, task queue, recent closures

**Proceed immediately to Step 5.**

### Step 5 — Load External Context

Read:
- `P_000_Account_Parameters_Current.md` → balance, risk budget
- `P_010_RiskConfig.json` → market posture for sizing

If missing: note unavailable; do not invent. **Proceed to Step 5b.**

### Step 5b — Catalog State Reconciliation

**Query catalog:**
```
$env:Path = "C:\Users\Trader\.conda\envs\p140;" + $env:Path
cd "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
python python\cli.py catalog-summary
```

**Cross-check:** symbols vs. most-recent `todo.md` closure.
- **Match** → proceed with inline note
- **Gap** → **HALT**; display both lists; prompt reconciliation
- **Timeout:** If mtime older than last closure, proceed flagged; if newer/unavailable, **HALT**

**Proceed immediately to Step 5c.**

### Step 5c — LM Studio Readiness Check

Task type: `vantagepoint_analysis` → DeepSeek R1 14B (primary).

```
$env:Path = "C:\Users\Trader\.conda\envs\p140;" + $env:Path
cd "C:\Users\Trader\AI-Agent-Learning-Hub"
python integrations\lm_studio\examples\p300_status_check.py
```

**Success** (`lm_studio_running: True`, model match) → populate LM Studio line in Step 6.  
**Failure** → surface `action_required`; display launcher command; **HALT** unless `--no-narrator`:
```
python C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\infrastructure\lm_studio_launcher.py
```
**Timeout** → warn inline; proceed.

### Step 6 — Display Session Summary

```
---------------------------------------------
P_300 SESSION INITIALIZED
---------------------------------------------
Architecture:    v2.7
Filesystem MCP:  [available | unavailable]
SKILL status:    [loaded | NOT LOADED]
Work Orders:     [status or OK]
Working state:   tasks/lessons.md OK | tasks/todo.md OK
Account:         $<balance> . Risk budget $<budget>
Market posture:  SPY <p> / QQQ <p> . Avg <avg>
Catalog:         <db filename> . <N> patterns / <M> symbols [reconciled | WARNING ...]
LM Studio:       [<model> ready | NOT READY | status unknown]
Active stage:    Stage <N> -- <stage name>
Next task:       <first unchecked item>
Open lessons:    <count>
---------------------------------------------
```

### Step 7 — Confirm Session Focus

> "Proceeding with `<next task>`, or steering elsewhere?"

Wait for operator confirmation. Do NOT propose work or take action until confirmed.

---

## What This SIP Does NOT Do

Load full architecture (on demand only), duplicate SKILL content, write code/files, or assume previous chat context.

---

## Fail-Fast Conditions

| Condition | Action |
| :---- | :---- |
| SKILL not loaded | Request manual paste; do not proceed |
| `tasks/` files missing | HALT; verify Stage 3 |
| Catalog symbols ≠ todo closure | HALT; reconcile (catalog wins) |
| `catalog-summary` timeout + mtime NEWER | HALT; manual paste |
| LM Studio not ready (no `--no-narrator`) | HALT; show launcher |
| Work order blocks session | HALT; resolve first |

---

## Quick Reference

| Item | Value |
| :---- | :---- |
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Catalog | `db_utils.get_latest_catalog()` (glob `*catalog.db`) |
| LM Studio task type | `vantagepoint_analysis` → DeepSeek R1 14B |
| Status check | `integrations\lm_studio\examples\p300_status_check.py` |
| Launcher | `integrations\lm_studio\infrastructure\lm_studio_launcher.py` |
| Work orders | `C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\work_orders\` |

---

## Recent Changelog

### v3.1 — 2026-06-04
- Added STEP 0.5 Work Order Review (governance).
- Compressed from 179 → 140 lines: condensed prose, removed old changelog, collapsed stage status, tightened fail-fast table.
- All 7-step sequence + catalog reconciliation + LM Studio readiness retained.

### v3.0 — 2026-05-29
- INIT sequence gate: Steps 4–5c uninterruptible block.
- Step 5/5b/5c restructured with "proceed immediately" directives.
- ~5% token reduction.

### v2.8 — 2026-05-29
- Step 5c LM Studio Readiness Check added.

---

## Maintenance

**Owner:** Anthony Zoppi (review), Claude (drafting)  
**Update trigger:** Architecture version bump or INIT sequence change  
**Pairs with:** `docs/P_300_System_Architecture_v2.7.md` + `p300-project-context/SKILL.md`

---

**End of P_300 System Initialization Prompt v3.1**
