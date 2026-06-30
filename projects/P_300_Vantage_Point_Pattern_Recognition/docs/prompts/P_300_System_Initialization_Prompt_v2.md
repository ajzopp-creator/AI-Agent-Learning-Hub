# P_300 System Initialization Prompt (SIP) v2

**File:** `docs/prompts/P_300_System_Initialization_Prompt_v2.md`
**Version:** 3.2
**Last Updated:** 2026-06-09
**Pairs With:** `docs/P_300_System_Architecture_v2.7.md`
**SKILL Companion:** `C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\p300-project-context\SKILL.md`

---

## Purpose

Bootstraps every new P_300 chat. Loads live operating state (account params, market posture, lessons, task queue, catalog state, LM Studio readiness) so the AI starts oriented. The SKILL provides protection rules and schema shorthand; the SIP loads state.

---

## How to Trigger

```
INIT  |  P_300  |  P_300 INIT
```

If the SKILL auto-loaded, the AI executes the sequence below automatically. Otherwise paste this file directly.

---

## INIT Sequence (Mandatory — Execute in Order, No Skipping)

**RULE: Complete every step through Step 6 before writing any file, logging any lesson, or taking any action. Steps 4 through 5c are a single uninterruptible block.**

### Step 0 — Environment Discovery (Silent)

Call `tool_search` before displaying anything. Look for `windows-mcp:FileSystem`, `windows-mcp:PowerShell`, `filesystem:read_text_file`, or equivalent.

- **Available** → INIT proceeds with live disk reads (Steps 3–5c)
- **Unavailable** → fall back to upload/download pattern; skip Steps 5b and 5c; warn in Step 6

### Step 1 — Session Header

Display:
```
P_300 [Day, Month DD, YYYY -- HH:MM ET]
```
Get time via `bash_tool` (`TZ='America/New_York' date '+%A, %B %d, %Y -- %H:%M ET'`). If unreachable, try `windows-mcp:PowerShell` (`[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, "Eastern Standard Time").ToString("dddd, MMMM dd, yyyy -- HH:mm")`). Use `time not available` only if both fail.

### Step 2 — Verify SKILL Loaded

Confirm `p300-project-context` SKILL is active by referencing one rule unprompted. If not loaded: notify operator, request manual paste of the SKILL file, do not proceed.

### Step 3 — Working State Existence Check

Verify both files exist via `windows-mcp:FileSystem` info mode:
- `<project>\tasks\lessons.md`
- `<project>\tasks\todo.md`

If either missing: **HALT** — prompt operator to verify Stage 3 setup.

### Step 4 — Load Working State (then immediately continue to Step 5)

Read via filesystem MCP (NOT project-attached snapshots — per M-015):

| File | Purpose |
| :---- | :---- |
| `tasks/lessons.md` | M-series rules, O-series lessons, open items |
| `tasks/todo.md` | Active stage, task queue, recent closures |

**Do not pause here. Proceed immediately to Step 5.**

### Step 5 — Load External Context (then immediately continue to Step 5b)

| File | Purpose |
| :---- | :---- |
| `P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` | Account balance, risk budget |
| `P_010_Current_Market_Posture\P_010_RiskConfig.json` | Market posture for sizing |

If missing: note unavailable; do not invent values.

**Decision-flag read (filesystem MCP, not import):** grep `python\config.py` for the four flag assignment lines and capture the literal values for the Step 6 summary:
```
RISK_AVERSION_LAMBDA: float = <v>
CE_MIN_THRESHOLD:     float = <v>
CE_GATE_ENABLED:      bool  = <v>
NARRATOR_ENABLED:     bool  = <v>
```
Match on the `: type =` form to exclude comment-block mentions. This captures the committed default in force at session start; any in-session flip is operator-visible and out of scope. If `config.py` unreadable: note flags unknown; do not invent. **Proceed immediately to Step 5b.**

### Step 5b — Catalog Health Check (then immediately continue to Step 5c)

Catalog DB is authoritative and is grown OUTSIDE Claude via the AddPattern .bat files. The live count is whatever the .bat runs have produced; it is NOT tracked per-session in `todo.md` and is NOT compared against any stored figure. Step 5b confirms the catalog is HEALTHY and reports its live size as informational context — nothing more.

**1. Query catalog** via `windows-mcp:PowerShell`:
```
$env:Path = "C:\Users\Trader\.conda\envs\p140;" + $env:Path
cd "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
python python\cli.py catalog-summary
```
Capture for the Step 6 summary: pattern_instances count, distinct symbols, hollow-record count, OVERALL health.

**2. Get catalog mtime** via `windows-mcp:FileSystem` info on `models\<mmddyy>catalog.db` (informational — confirms which DB resolved newest).

**Health gate (the only HALT here):**
- `OVERALL != HEALTHY` **OR** hollow records > 0 → **HALT**: surface the summary; the catalog may be mid-write or corrupted; do not let Claude touch it until resolved.
- Otherwise → populate the Catalog line in Step 6 (count + symbols + HEALTHY + mtime) and proceed. A count higher than any prior session is normal .bat growth, not a divergence — never flag it.

**Timeout / unavailable fallback (~4-min limit):** count unverified this session — note `count unverified` on the Catalog line and proceed. The catalog is still authoritative; Claude simply did not read it. If the live number is needed for the session's work, prompt the operator to paste `catalog-summary` from the ISE; otherwise proceed without it.

**Proceed immediately to Step 5c.**

### Step 5c — LM Studio Readiness Check

P_300 task type: `vantagepoint_analysis` → primary tier (DeepSeek R1 14B).

```
$env:Path = "C:\Users\Trader\.conda\envs\p140;" + $env:Path
cd "C:\Users\Trader\AI-Agent-Learning-Hub"
python integrations\lm_studio\examples\p300_status_check.py
```

- **Success** (`lm_studio_running: True`, `model_mismatch: False`) → populate LM Studio line in Step 6
- **Failure** → surface `action_required` message, display launcher command, **HALT** unless operator confirms `--no-narrator`:
  ```
  python C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\infrastructure\lm_studio_launcher.py
  ```
- **Timeout/error** → warn inline; proceed; narration may fail at runtime

---

### Step 6 — Display Session Summary

```
---------------------------------------------
P_300 SESSION INITIALIZED
---------------------------------------------
Architecture:    v2.7 (loaded on demand from docs/)
Filesystem MCP:  [available | unavailable]
SKILL status:    [loaded | NOT LOADED]
Working state:   tasks/lessons.md OK  tasks/todo.md OK
Account:         $<balance> . Risk budget $<budget>
Market posture:  SPY <p> / QQQ <p> . Avg <avg>
Catalog:         <db filename> . <N> patterns / <M> symbols
                 (last write <mtime> -- HEALTHY [| count unverified])
LM Studio:       [<model name> ready | NOT READY -- <action_required> | status unknown]
Decision flags:  CE gate <ON | OFF> (lambda <v>, min <v>) . Narrator <ON | OFF>
Active stage:    Stage <N> -- <stage name>
Next task:       <first unchecked item from active stage>
Open lessons:    <count of items in Section 4 of lessons.md>
---------------------------------------------
```

### Step 7 — Confirm Session Focus

> "Proceeding with `<next task>` as the session focus, or steering elsewhere?"

Wait for operator confirmation. Do NOT propose work, write code, or take action until confirmed.

---

## What This SIP Does NOT Do

- Load the full architecture doc (on demand only)
- Duplicate SKILL content (protection rules live in the SKILL)
- Write code or files (operator approves file plan first per M-003)
- Assume previous chat context (every chat starts fresh)

---

## Fail-Fast Conditions

| Condition | Action |
| :---- | :---- |
| SKILL not loaded | Request manual paste; do not proceed |
| `tasks/lessons.md` or `tasks/todo.md` missing | Halt; suggest Stage 3 verification |
| `tasks/todo.md` shows no active stage | Halt; prompt operator to confirm stage |
| `windows-mcp:FileSystem` unavailable | Notify; upload-based delivery; skip 5b + 5c |
| Catalog `OVERALL != HEALTHY` or hollow records > 0 | HALT; surface summary; do not touch catalog until resolved |
| `catalog-summary` non-zero exit | Warn inline; surface stderr; proceed flagged |
| `catalog-summary` timeout or unavailable | Note `count unverified`; proceed (catalog still authoritative; offer ISE paste if number needed) |
| LM Studio not ready or model mismatch | Surface `action_required`; show launcher command; HALT unless `--no-narrator` |
| `config.py` decision flags unreadable | Warn inline (flags unknown); do not halt |

Never proceed past a fail-fast condition silently.

---

## Quick Reference

### Critical Paths
| Item | Value |
| :---- | :---- |
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Active catalog | `db_utils.get_latest_catalog()` (glob `*catalog.db` digit-first) |
| ISE profile | `D:\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShellISE_profile.ps1` |
| LM Studio task type | `vantagepoint_analysis` → DeepSeek R1 14B |
| LM Studio status check | `integrations\lm_studio\examples\p300_status_check.py` (Hub root, p140) |
| LM Studio launcher | `integrations\lm_studio\infrastructure\lm_studio_launcher.py` |

### Tooling
- **`windows-mcp:FileSystem`** — direct file writes (M-007)
- **`windows-mcp:PowerShell`** — Steps 5b + 5c; ~4-min timeout; fallback = drop script, operator runs in ISE, pastes output
- **Unsigned-script bypass** — `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### Stage Status (as of 2026-05-29)
Stages 1–9 + Stage 9-followup: ALL COMPLETE/SEALED. See `tasks/todo.md` for live state. Milestone 6 Trade Management: parked.

---

## Manual Fallback

If SKILL and SIP both unavailable, paste:

```
P_300 INIT.

Read in order: (1) p300-project-context SKILL.md, (2) tasks/lessons.md, (3) tasks/todo.md,
(4) P_000_Account_Parameters_Current.md, (5) P_010_RiskConfig.json.

Run `python python\cli.py catalog-summary` (p140 on PATH) from project root. HALT only if
OVERALL != HEALTHY or hollow records > 0 (mid-write/corruption). Count is informational --
.bat growth outside Claude is normal, never a divergence. Timeout/unavailable → note count
unverified and proceed; catalog stays authoritative.

Run `python integrations\lm_studio\examples\p300_status_check.py` from Hub root (p140). If not
ready, surface action_required, show launcher:
  python C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\infrastructure\lm_studio_launcher.py

Display session summary block. Ask session focus. Do not propose work until confirmed.
```

---

## Changelog

### v3.2 — 2026-06-09
- **Step 5b reframed: Catalog State Reconciliation → Catalog Health Check.** Catalog grows outside Claude via AddPattern .bat files; per-session count tracking in `todo.md` produced false "divergence" HALTs on every INIT for what is normal .bat growth. Live count is now informational only — never compared against a stored figure. The sole HALT is real corruption: `OVERALL != HEALTHY` OR hollow records > 0. Symbol-gap and mtime-newer divergence logic removed. Timeout no longer forces a HALT-or-trust decision — count noted unverified, catalog stays authoritative, proceed. Fail-fast table and Manual Fallback updated to match. Catalog remains authoritative (M-017 unchanged); only the count-drift comparison is retired.

### v3.1 — 2026-06-09
- **Decision-flag surfacing added:** Step 5 now greps `python/config.py` for the four behavior-affecting flags (`RISK_AVERSION_LAMBDA`, `CE_MIN_THRESHOLD`, `CE_GATE_ENABLED`, `NARRATOR_ENABLED`) and Step 6 displays a `Decision flags:` line. Catches a committed CE-gate or narrator flip that would otherwise silently change production behavior with no session-start reminder. Read-at-INIT by design — captures the committed default; in-session flips are operator-visible. Grep (filesystem MCP), not import — no PowerShell dependency. Fail-fast row added: flags unreadable → warn inline, do not halt.

### v3.0 — 2026-05-29
- **INIT sequence gate added:** explicit rule that Steps 4 through 5c are an uninterruptible block — no files, lessons, or actions permitted until Step 6 summary is displayed. Prevents step-skipping regression observed this session.
- **Steps 5, 5b, 5c** restructured with "proceed immediately to next step" directives at each boundary.
- **Token reduction (~5%):** redundant prose trimmed throughout; Step 0/1/2 condensed; "What This SIP Does Not Do" shortened; Quick Reference converted to table; Stage Status collapsed to one line; Manual Fallback condensed; changelog entries prior to v2.5 removed (stable history).

### v2.9 — 2026-05-29
- Step 5c failure block now displays exact launcher command.

### v2.8 — 2026-05-29
- Step 5c LM Studio Readiness Check added. Session summary gained LM Studio line.

### v2.7 — 2026-05-20
- Architecture + SIP version bumped to v2.7. Stage 9-followup entry added.

### v2.6 — 2026-05-19
- Stages 7, 8, 9 SEALED. No structural INIT changes.

### v2.5 — 2026-05-18
- Step 5b catalog-summary timeout fallback added.

### v2.4 — 2026-05-16
- Step 5b Catalog State Reconciliation added (M-017).

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** Architecture version bump, or change to INIT sequence
- **Pairs with:** `docs/P_300_System_Architecture_v2.7.md` + `p300-project-context\SKILL.md`

---

**End of P_300 System Initialization Prompt v3.2**
