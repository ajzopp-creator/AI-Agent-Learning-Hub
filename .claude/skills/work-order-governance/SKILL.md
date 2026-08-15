---
name: work-order-governance
description: Check work order status before any project session starts. Lists all open work orders (not just the latest), sequenced. Blocks if any is BLOCKED, warns if any is PENDING, proceeds if all COMPLETE/CLOSED.
trigger: auto
---

# work-order-governance
**Purpose:** Check work order status before any project session starts
**Version:** 1.1
**Created:** 2026-06-04
**Applies To:** All projects in AI-Agent-Learning-Hub

---

## What This Does

When a project session starts, Claude automatically:
1. Identifies the active project (P_115, P_300, P_400, P_800, P_020, etc.)
2. Finds ALL work orders in that project's work_orders/ folder with Status
   NOT IN {COMPLETE, CLOSED} — never just the single highest PHASE+SEQ file
3. Sorts the result by PHASE+SEQ ascending (e.g. E1.010, E1.011, E1.012)
4. Reads the Status field from each
5. **Blocks the session** if ANY listed WO = BLOCKED
6. **Warns** if ANY listed WO = PENDING
7. **Displays every open WO**, one line each, regardless of block/warn outcome
   — a WO with no blocking status still gets surfaced, not silently skipped
8. **Allows proceed** only once every listed WO is COMPLETE/CLOSED or
   acknowledged per the rules below

**Fix note (v1.1, 2026-08-09):** v1.0 found only the single WO with the
highest PHASE+SEQ and evaluated that one file's status alone. Real sessions
carry multiple concurrently open WOs per project (e.g. P_020 had three:
E1.010 IN_PROGRESS, E1.011 PENDING, E1.012 IN_PROGRESS at once) — v1.0
silently dropped every WO except the newest, so E1.010 (older, still open)
never surfaced at session start. Root cause: "latest" was read as "most
relevant" instead of "one of several still-open items."

---

## When It Triggers

**Explicit:** User types INIT or INIT [project_name]
**Implicit:** Session starts with a project reference (P_115, P_400, etc.)
**Manual:** User types /check-workorder at any time

---

## Execution Flow

User types "INIT" or project session starts
  ↓
Claude queries work_orders/ folder for the project
  ↓
Claude collects EVERY WO file for that project where Status is not
COMPLETE and not CLOSED (includes PENDING, IN_PROGRESS, BLOCKED,
OWNER_DONE — OWNER_DONE is open until Independent Review moves it to
CLOSED, per WO_COMPLETION_GATE.md)
  ↓
Claude sorts that set by PHASE+SEQ ascending
  ↓
Claude displays the full sequenced list, one line per WO:
  [WO-ID] — [one-line task] — Status — (blocker/next-step if any)
  ↓
IF any WO in the set = BLOCKED:
  → Display that WO's blocker message + "Depends On: [WO-ID]"
  → STOP — do not proceed with session
  ↓
ELSE IF any WO in the set = PENDING:
  → Ask user once: "N work order(s) pending — proceed anyway?"
  → If NO → stop; if YES → proceed, list stays visible with warning banner
  ↓
ELSE (all IN_PROGRESS / OWNER_DONE, none BLOCKED or PENDING):
  → Proceed, list stays visible — no yes/no gate required
  ↓
IF the set is empty (nothing open):
  → Proceed silently, per v1.0 COMPLETE behavior

---

## Work Order File Requirements

Every work order must have:

\\\markdown
# [WO-ID] — [Task Name]

**Status:** PENDING | IN_PROGRESS | BLOCKED | OWNER_DONE | COMPLETE | CLOSED
**Verified:** [date] (optional — required if COMPLETE/CLOSED)
**Owner:** [Name or Claude or [project_name]]
**Depends On:** [WO-ID] (optional — required if BLOCKED)
**Blocker:** [exact reason] (optional — required if BLOCKED)

...rest of work order...
\\\

---

## Status Definitions

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Work not started | Listed; warn; ask to proceed |
| IN_PROGRESS | Work started, not done | Listed; allow proceed |
| BLOCKED | Work cannot start (dependency) | Listed; stop session; show blocker |
| OWNER_DONE | Implemented, awaiting Independent Review | Listed; allow proceed |
| COMPLETE | Work done, deliverables verified | Not listed |
| CLOSED | Work done + independently reviewed | Not listed |

---

## Notes

- Work orders are the single source of truth for project readiness
- Status check happens before any work starts — non-negotiable
- ALL open WOs for the active project are surfaced, every session — not
  just the newest one; sessions have gone stale relying on "latest only"
- Verified date proves the status was recently audited
- Blockers must name the exact blocking work order or reason
- This skill applies to all projects — no exceptions

---

**END OF work-order-governance SKILL v1.1**
