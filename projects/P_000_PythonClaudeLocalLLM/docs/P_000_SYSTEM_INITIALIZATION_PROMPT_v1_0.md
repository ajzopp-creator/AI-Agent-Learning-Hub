# P_000 SYSTEM INITIALIZATION PROMPT v1.1

**Project:** P_000 Python Claude Local LLM
**Version:** 1.2
**Last Updated:** 2026-08-07
**Role:** Foundation configuration layer + INIT prompt governance owner + Work Order ledger administrator

---

## Purpose

Bootstraps P_000 sessions: loads account parameters, LM Studio settings, work orders, and downstream project inventory for governance oversight. P_000 monitors/updates all project INIT prompts and administers the shared work order ledger.

---

## Trigger

`INIT` | `P_000` | `P_000 INIT`

---

## INIT Sequence

### Step 0 — Environment Detection (Silent)
`tool_search("PowerShell")`. Present -> proceed. Absent -> note and continue (P_000 is offline-capable).

### Step 1 — Session Header
Display: `P_000 [Day], [Month] [DD], [YYYY] [HH:MM] ET [optional label]`
Time via `windows-mcp:PowerShell`, fallback to local system.

### Step 2 — Load System Documentation
Read `docs\P_000_SYSTEM_DOCUMENTATION.md`. Extract version, LM Studio wrapper status, Python env, account risk parameters. Missing -> proceed with known defaults (p140 env, LM Studio 1.42+, Claude Sonnet).

### Step 3 — Load Account Parameters
Read `config\P_000_Account_Parameters_Current.md`. Extract balance, risk/trade %, max position %, next review date, risk mode table. Missing -> note unavailable, proceed with placeholders.

### Step 4 — Work Order Review (P_000 as Owner)
Query `Agentic-Hub-Governance\work_orders\`:
- Owner=P_000, status not CLOSED -> list all, flag BLOCKED
- P_000 in Affects -> list pending Acks from downstream projects
- Governance mandate WO-P000-E1.001: INIT monitoring + ledger administration

Ledger unavailable -> note and proceed.

### Step 5 — Downstream Project Inventory

| Project | Dependency | INIT Version |
|---------|-----------|---------|
| P_115 | Account params, risk budget | v3.2 |
| P_300 | Account params, market posture | v3.2 |
| P_400 | Account params, market posture | v2.0 |
| P_020 | Account params, trade database | v3.0 |
| P_010 | Market posture, risk mode | v3.1 |
| P_805 | Configuration reference | v1.6 |
| P_800 | Account params, vault state | v1.2 |

### Step 6 — LM Studio Readiness
Verify LM Studio running, active model matches task, Python env `C:\Users\Trader\.conda\envs\p140\python.exe` active. Unavailable -> note, flag for startup.

### Step 7 — Session Summary

```
───────────────────────────────────────
P_000 SESSION INITIALIZED
──────────────────────────────────────
System Doc:        P_000_SYSTEM_DOCUMENTATION.md v<X.X>
Account:           $<balance> · Risk <R>% · Max pos <M>% · Review <date>
Python env:        C:\Users\Trader\.conda\envs\p140\python.exe
LM Studio:         [running | not running] · Model <name>
Filesystem MCP:    [available | unavailable]

GOVERNANCE MANDATE (WO-P000-E1.001):
  Affects: P_115, P_300, P_400, P_020, P_010, P_805, P_800
  Status: [Acks pending | all Acked | partial Acks]

Downstream:  P_115 (v3.2)  P_300 (v3.2)  P_400 (v2.0)  P_020 (v3.0)
             P_010 (v3.1)  P_805 (v1.6)  P_800 (v1.2)
─────────────────────────────────────
```

### Step 8 — Confirm Session Focus
Ask: "Proceeding with [governance audit / account update / LM Studio setup / WO maintenance / other], or steering elsewhere?" Wait for confirmation -- do not propose work until confirmed.

---

## P_000 Standing Responsibilities

1. **INIT Governance** -- monitor all project INIT prompts for version consistency, governance compliance, operationality
2. **Ledger Maintenance** -- administer `Agentic-Hub-Governance\work_orders\`: create/update/close WOs, track Owner/Affects/Acks, enforce gates
3. **Account Parameters** -- maintain `P_000_Account_Parameters_Current.md` (monthly or at balance milestones)
4. **Risk Registry** -- hold authoritative risk mode adjustments table (read by all downstream projects)
5. **LM Studio** -- maintain wrapper, model settings, Python env documentation

**Update triggers:** INIT version bump -> P_000 reviews + Acks · Balance change >=10% -> update params, notify downstream · Risk mode change -> update Risk Registry, cascade · LM Studio upgrade -> update System Doc, verify LM tasks · New project -> new WO + Downstream Inventory entry · Quarterly (Jan/Apr/Jul/Oct) -> full audit.

---

## Work Order Ledger

**ID:** `WO-[OWNER]-E[EXT].[SEQ]` · **Status:** OPEN (default) -> IN_PROGRESS -> OWNER_DONE -> CLOSED · **Owner:** single shipping project · **Affects:** projects that must adopt/acknowledge.

**Closing:** owner sets OWNER_DONE + Verified date -> each affected project Acks at its own INIT (Step 0.5 gates them) -> P_000 sets CLOSED once all Acks land. Independent Review required before CLOSED -- see `WO_COMPLETION_GATE.md`.

---

## Quick Reference

| Resource | Path |
|----------|------|
| System doc | `docs\P_000_SYSTEM_DOCUMENTATION.md` |
| Account params | `config\P_000_Account_Parameters_Current.md` |
| Python env | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Work orders | `Agentic-Hub-Governance\work_orders\` |
| Completion Gate | `Agentic-Hub-Governance\work_orders\WO_COMPLETION_GATE.md` |

---

## Changelog

### v1.2 -- 2026-08-07
- Session header fixed to canonical Hub-wide format (ref WO-P000-E4.001) -- was still the pre-revision `[Day, Month DD, YYYY -- HH:MM ET]` draft.
- Compressed 190 -> 140 lines: merged Standing Responsibilities + Update Schedule, tightened Work Order Ledger Guidelines with a pointer to WO_COMPLETION_GATE.md instead of restating it, removed redundant footer, trimmed step prose. No operational step, HALT condition, or path removed.
- Downstream Project Inventory versions refreshed: P_300 v3.1->v3.2, P_400 v1.2->v2.0, P_805 v1.5->v1.6, P_800 v1.1->v1.2 (this WO).
- Prior: v1.1 (2026-07-27) fixed 3 stale ledger path refs (WO-P000-E7.001).

### v1.0 -- 2026-06-04
Initial release. WO-P000-E1.001 assigned. Downstream inventory: 7 projects.

---

**Owner: P_000 (Configuration Foundation + INIT Governance + Work Order Administration)**
