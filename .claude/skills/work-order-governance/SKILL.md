---
name: work-order-governance
description: Check work order status before any project session starts. Blocks if BLOCKED, warns if PENDING, proceeds if COMPLETE.
trigger: auto
---

# work-order-governance
**Purpose:** Check work order status before any project session starts  
**Version:** 1.0  
**Created:** 2026-06-04  
**Applies To:** All projects in AI-Agent-Learning-Hub

---

## What This Does

When a project session starts, Claude automatically:
1. Identifies the active project (P_115, P_300, P_400, P_800, P_020, etc.)
2. Finds the latest work order in that project's work_orders/ folder
3. Reads the Status field
4. **Blocks the session** if Status = BLOCKED or PENDING
5. **Warns** if Status contradicts reality
6. **Allows proceed** only if Status = COMPLETE and deliverables verified

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
Claude finds the latest WO file (highest PHASE + SEQ)
  ↓
Claude reads Status field from top of file
  ↓
IF Status = BLOCKED:
  → Display blocker message
  → Show "Depends On: [WO-ID]" field
  → STOP — do not proceed with session
  ↓
IF Status = PENDING:
  → Display pending status + owner + task
  → Show required inputs/outputs
  → Ask user: "This work order is pending. Proceed anyway?"
  → If NO → stop; if YES → display with warning banner
  ↓
IF Status = COMPLETE:
  → Check if "Verified: [date]" field exists
  → If verified: proceed silently (status is current)
  → If NOT verified: display note "Status not yet verified — use caution"
  ↓
Proceed with project session

---

## Work Order File Requirements

Every work order must have:

\\\markdown
# [WO-ID] — [Task Name]

**Status:** PENDING | IN_PROGRESS | BLOCKED | COMPLETE
**Verified:** [date] (optional — required if COMPLETE)
**Owner:** [Name or Claude or [project_name]]
**Depends On:** [WO-ID] (optional — required if BLOCKED)
**Blocker:** [exact reason] (optional — required if BLOCKED)

...rest of work order...
\\\

---

## Status Definitions

| Status | Meaning | Action |
|--------|---------|--------|
| PENDING | Work not started | Warn; ask to proceed |
| IN_PROGRESS | Work started, not done | Display message; allow proceed |
| BLOCKED | Work cannot start (dependency) | Stop session; show blocker |
| COMPLETE | Work done, deliverables verified | Allow proceed silently |

---

## Notes

- Work orders are the single source of truth for project readiness
- Status check happens before any work starts — non-negotiable
- Verified date proves the status was recently audited
- Blockers must name the exact blocking work order or reason
- This skill applies to all projects — no exceptions

---

**END OF work-order-governance SKILL v1.0**
