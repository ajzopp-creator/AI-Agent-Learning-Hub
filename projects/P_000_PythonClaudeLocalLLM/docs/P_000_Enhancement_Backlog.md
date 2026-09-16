# P_000 ENHANCEMENT BACKLOG
**Last Updated:** September 13, 2026
**Location:** docs/P_000_Enhancement_Backlog.md
**Scope:** Hub-wide, cross-project items -- not a single project's queue.
Project-specific enhancements stay in that project's own
`P_<ID>_Enhancement_Backlog.md` (e.g. `P_010_Enhancement_Backlog.md`).

---

## STATUS KEY
- [DONE]        -- Completed and verified
- [IN PROGRESS] -- Currently being built
- [KNOWN ISSUE] -- Documented problem, fix pending
- [QUEUED]      -- Approved, not yet started
- [IDEA]        -- Under consideration

---

## [DONE]


### [2026-09-13] Base-rate-adjusted lift standard (not raw win rate)
- **Problem:** No Hub-wide place existed for a durable, cross-project
  research-methodology standard -- only Work Orders (single build/decision,
  Completion Gate, Independent Review) and per-project Error Corrections
  Logs (project-scoped incident history) existed. A finding from
  WO-P010-E2.001 needed a home that any future project session could
  reference, not a one-off WO.
- **Finding:** Testing whether a candidate variable helps pick winning
  trades by comparing raw win rate across buckets is misleading -- raw
  win rate moves with the bucket's own ambient base rate. P_300 BUY
  signals looked stronger in OFF regime by raw win% (72.8% vs FULL's
  66.9%), but base-rate-adjusted lift ran the opposite direction (FULL
  +18.5pp vs OFF +14.6pp, 2025), and real closed P_020 trades agreed with
  the lift finding (FULL 61.5% win vs OFF 20.0%), not the raw number.
- **Fix:** Added a "Trading Research Standards" section to
  `Trading_Projects_Folder_Architecture.md` (Hub root) with the rule and
  its origin. Filed as an Enhancement, not a Work Order, since it is a
  standing methodology rule with no build/decision attached, not a
  closeable unit of work.
- **Applies to:** any future "does X help pick winners" question in
  P_115, P_400, P_300, or a new project.
- **Origin:** WO-P010-E2.001 (CLOSED 2026-09-13, decision: KEEP, no
  carve-out to P_010's OFF-mode size cut for P_300 BUY signals).

---
