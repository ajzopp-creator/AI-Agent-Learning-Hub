# P_300 System Initialization Prompt (SIP) v3.6

**File:** `docs/P_300_System_Initialization_Prompt_v3_1.md`  
**Version:** 3.6  
**Last Updated:** 2026-08-29  
**Pairs With:** `docs/P_300_System_Architecture_v2.7.md` + `p300-project-context/SKILL.md` + `CLAUDE.md`

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

**RULE: Complete Steps 0 through 7 before writing code or taking action. Steps 4–5c are uninterruptible.**

> Step order: 0 → 0.5 → 0.6 → 1 → 1A → 1B → 2 → 3 → 4 → 5 → 5b → 5c → 6 → 7.

### Step 0 — Environment Discovery
Call `tool_search` for `windows-mcp:FileSystem`/`PowerShell`. Available → Step 0.5. Unavailable → skip 5b/5c, warn in Step 6.

### Step 0.5 — Work Order Review
Query ledger at `...\Agentic-Hub-Governance\work_orders\`:
- Owner=P_300, not CLOSED → Display; **HALT** if action required first
- P_300 in Affects, Ack pending → Display; Ack after session work

Ledger unavailable → proceed with inline note.

### Step 0.6 — Promote Marker Check
Read `<project root>\P_300_promote_marker.json` (written by `promote-gate`, WO-P300-E5.005). Absent → no output, proceed silently.

Present → display `severity`, `created_at`, `staging_db_path`, `buy_delta_pp`, `pass_delta_pp`, and `next_action` verbatim.

- `severity: "STOP"` → **HALT**. A staged batch was blocked by the quality gate and is still on disk. The next `ingest-mined` run rebuilds staging from live via `shutil.copy2` and **will destroy it**. Resolve before any other work: promote deliberately, or discard and clear the marker.
- `severity: "WAIVED"` → display, do NOT halt. The batch was promoted, but the sample was below the `min_buy_n` floor so quality was never tested. Informational; nothing is at risk.
- File present but unparseable → **HALT**. Never treat an unreadable marker as "no problem outstanding."

This step exists because the gate's STOP path otherwise recreates the failure WO-P300-E5.005 was filed to fix: on 2026-07-25 a batch staged at 16:15, sat unpromoted, and was silently overwritten three days later. A log file only helps someone who remembers to open it. INIT runs every session.

### Step 1 — Session Header
Display: `P_300 [Day, Month DD, YYYY] [HH:MM] ET`. Time via `windows-mcp:PowerShell` or local system fallback.

### Step 1A — Preflight Freshness Reminder
Non-authoritative nudge (Step 5b reconciles for real). Never HALTs. Read `<project root>\P_300_preflight_status.json` — existence + `generated_at` only:
- Missing → `REMINDER: P_300_preflight_status.json not found -- run P_300_Preflight.bat now.`
- `generated_at` = today → no reminder.
- `generated_at` < today → `REMINDER: preflight status is from <date> -- re-run P_300_Preflight.bat.`

### Step 1B — Working-State Size Reminder
Non-authoritative nudge, same pattern as Step 1A. Never HALTs. No Python subprocess — read via `windows-mcp:FileSystem`.

`tasks/todo.md` — get size via `mode=info`; get line count by reading the file:
- Lines > 500 or size > 100KB → `REMINDER: tasks/todo.md is <N> lines / <KB> -- archive pass due (WO-P000-E8.001).`
- Under both caps → no output.

`tasks/lessons.md` — same size/line read, plus count entries matching `^#{2,3} (M|O|S)-\d+`:
- Entries > 40 or size > 70KB → `REMINDER: tasks/lessons.md is <N> lines / <E> entries / <KB> -- archive pass due (WO-P000-E8.001).`
- Under both caps → no output.

Each file's check is independent — one can fire while the other stays silent.

### Step 2 — Verify SKILL Loaded
Confirm `p300-project-context` active by referencing one rule unprompted. Missing → request manual paste; do not proceed.

### Step 3 — Working State Existence Check
Verify `<project>\tasks\lessons.md` and `<project>\tasks\todo.md` exist. Either missing → **HALT**; verify Stage 3 setup.

### Step 4 — Load Working State
Read via `windows-mcp:FileSystem`: `tasks/lessons.md` (M-series/O-series) + `tasks/todo.md` (active stage, queue, closures) + `CLAUDE.md` if present (architecture snapshot, key paths, Locked Decisions -- WO-P000-E8.001). -> Step 5.

### Step 5 — Load External Context
Read `P_000_Account_Parameters_Current.md` (balance, risk budget) + `P_010_RiskConfig.json` (market posture). Missing → note unavailable; do not invent.

Grep `python/config.py` for `CE_GATE_ENABLED`, `RISK_AVERSION_LAMBDA`, `CE_MIN_THRESHOLD`, `NARRATOR_ENABLED` → populates `Decision flags:` in Step 6 (catches silent gate/narrator flips). → Step 5b.

### Step 5b — Catalog State Reconciliation
**Read only — no Python subprocess (WO-P000-E4.001):** `windows-mcp:FileSystem read → <project root>\P_300_preflight_status.json`. Operator generates/refreshes via `P_300_Preflight.bat` (same model as AddPattern/DailyEval .bat files); INIT never invokes `python` directly here.

Missing → note `catalog status unavailable -- run P_300_Preflight.bat`; proceed flagged.

Staleness: compare `generated_at` vs. last `todo.md` closure.
- Fresh + `HEALTHY` → proceed; note counts from file.
- Fresh + `ATTENTION REQUIRED` or `hollow_count > 0` → **HALT**; display fields; reconcile.
- Stale or `ERROR` → warn "re-run `P_300_Preflight.bat`"; proceed flagged (catalog stays authoritative, M-017).

→ Step 5c.

### Step 5c — LM Studio Readiness Check
Task type `vantagepoint_analysis` → DeepSeek R1 14B. Same file as 5b — one read covers both steps.
- `lm_studio_running: true` + model match → populate Step 6 line.
- `lm_studio_running: false` → surface `lm_studio_message`/`error`; show launcher; **HALT** unless `--no-narrator`:
```
python C:\Users\Trader\AI-Agent-Learning-Hub\integrations\lm_studio\infrastructure\lm_studio_launcher.py
```
- File missing/stale → status unknown; proceed unless `--no-narrator` unset (then treat as `false`).

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
Decision flags:  CE_GATE_ENABLED=<bool> (lambda <val>) / NARRATOR_ENABLED=<bool>
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
| Preflight status missing or stale | Warn inline; proceed flagged (catalog authoritative; re-run `P_300_Preflight.bat`) |
| Preflight status `catalog_overall != HEALTHY` | HALT; reconcile |
| `P_300_promote_marker.json` severity STOP | HALT; staged batch will be destroyed by next ingest run |
| `P_300_promote_marker.json` present but unparseable | HALT; never read as "no problem outstanding" |
| LM Studio not ready (no `--no-narrator`) | HALT; show launcher |
| Work order blocks session | HALT; resolve first |

---

## Quick Reference

| Item | Value |
| :---- | :---- |
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\` |
| CLAUDE.md | `<project root>\CLAUDE.md` -- architecture + Locked Decisions, read at Step 4 |
| Working-state archives | `tasks\todo_archive.md`, `tasks\lessons_archive.md` (WO-P000-E8.001) |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Catalog | `db_utils.get_latest_catalog()` (glob `*catalog.db`) |
| Preflight script (operator-run) | `P_300_Preflight.bat` (project root) |
| Preflight status (INIT reads) | `<project root>\P_300_preflight_status.json` |
| Promote marker (INIT reads) | `<project root>\P_300_promote_marker.json` |
| LM Studio task type | `vantagepoint_analysis` → DeepSeek R1 14B |
| LM Studio launcher | `integrations\lm_studio\infrastructure\lm_studio_launcher.py` |
| Work orders | `C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\` |

---

## Recent Changelog

*Retention rule: this section keeps only the current + prior version. Older entries live in `docs/P_300_SIP_CHANGELOG_ARCHIVE.md`.*

### v3.6 — 2026-08-29
- **Step 1B added — Working-State Size Reminder** (WO-P300-E5.009). Non-HALTing nudge, same pattern as Step 1A: reads `tasks/todo.md` (lines/size) and `tasks/lessons.md` (lines/entries/size) via `windows-mcp:FileSystem`, no Python subprocess. Over cap (todo.md: >500 lines or >100KB; lessons.md: >40 entries or >70KB) → prints an archive-pass-due reminder referencing WO-P000-E8.001; under both caps → silent. The two checks are independent of each other.
- **Step order updated** to insert `1B` between `1A` and `2`.
- **Changelog retention enforced.** This section had drifted to three live entries (v3.5/v3.4/v3.3) against its own stated two-version rule. v3.4 and v3.3 moved to `docs/P_300_SIP_CHANGELOG_ARCHIVE.md`; back to current + prior only.

### v3.5 — 2026-07-28
- **Step 0.6 added — Promote Marker Check** (WO-P300-E5.005). Reads `P_300_promote_marker.json`. `STOP` severity HALTs; `WAIVED` displays without halting; present-but-unparseable HALTs. Placed immediately after the work-order review because both answer the same question: is there unresolved work from a previous session that must be handled before anything new begins.
- **Two fail-fast rows added** for the marker; marker path added to Quick Reference.
- **Why HALT rather than warn:** a STOP marker means a staged batch is sitting on disk and the next `ingest-mined` run rebuilds staging from live, destroying it. Unlike a stale preflight — recoverable any time by re-running a script — this one has a deadline. Precedent: the 2026-07-25 batch staged at 16:15, was never promoted, and was silently overwritten on 2026-07-28.

### Pre-v3.5 history
See `docs/P_300_SIP_CHANGELOG_ARCHIVE.md` (v2.8-v3.4).

---

## Maintenance

**Owner:** Anthony Zoppi (review), Claude (drafting)  
**Update trigger:** Architecture version bump or INIT sequence change  
**Pairs with:** `docs/P_300_System_Architecture_v2.7.md` + `p300-project-context/SKILL.md` + `CLAUDE.md`

---

**End of P_300 System Initialization Prompt v3.6**
