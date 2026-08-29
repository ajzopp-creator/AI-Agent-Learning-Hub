# P_810 — Current State (todo.md)
Last updated: 2026-08-20 (v1.2 scaffold session — ID churned 810 -> 820 -> 810)

## Status
Docs + folder structure created. No Python written. Sender whitelist is
headers-only, zero rows. Project ID was briefly changed to P_820 mid-session,
then reverted back to P_810 (Tony had confused P_820 with a separate planned
project, Order Signal Capture). No code existed at any point, so nothing
downstream broke.

## Done this session (2026-08-20)
- Created project root and folder scaffold (python/domain,infrastructure,
  application,tests,logs; data/daily,monthly; docs; tasks)
- Wrote docs\P_810_SYSTEM_DOCUMENTATION.md v1.0
- Renamed project to P_820 (v1.1), then reverted to P_810 (v1.2)
- Wrote README.md
- Wrote data\sender_sheet.csv (headers only: email_address, sender_name,
  date_added, category, enabled)
- Registered WO-P810-E1.001 (through the P_820 detour and back)
- P_000_SYSTEM_DOCUMENTATION.md Section 1.4 Related Projects settled on P_810

## Known issues -- carry forward
None yet -- no code exists to have bugs.

## Queued (priority order)
1. Get real AJZ Strategies tax sender list from Tony -- hard blocker,
   not guessing this
2. Promote P_805's mbox/IMAP/header-decode layer into
   shared_resources\python_utils\ (separate approval-gated code task,
   touches P_805's working code -- treat carefully)
3. Phase 1 file-and-line-count plan for P_810 itself, once 1 and 2 are done

## Next session first task
Ask Tony whether he has the tax sender list ready. If not, nothing else
in Phase 1 can start.
