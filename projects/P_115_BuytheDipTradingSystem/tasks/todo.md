# P_115 To-Do

Working-state file. Read at every INIT STEP 3. Active task list.

---

## Open

- WO-P115-E3.001 -- BLOCKED ON TONY (2 items). (1) Replace claude.ai Project Instructions with corrected on-disk source docs\P_115_Project_Instructions.md -- the live claude.ai copy still orders three-gate sizing and options gates, and it outranks every other surface in session context. (2) Remove/replace stale Tracker_Log_Schema_v9_4_0_1.md from claude.ai Project Knowledge -- file does not exist on disk, still documents STEP 2 as Position Sizing / STEP 3 as Option Chain Analysis. Until both are done, the ZION 8/3 failure can recur.

## Done

- 2026-08-03 -- WO-P115-E3.001 (Imperative Sweep, arch v1.3/v1.4) OWNER_DONE. Live failure on ZION 8/3: a P_116-sourced signal produced a full three-gate sizing block, 7.09:1 R:R, premium cap math, and an options-chain request -- all P_400's since 7/24. Root cause: v1.3 was logged in changelogs but never swept into imperative rules; 9 live instructions across 4 surfaces still commanded sizing. Swept 14 edits across SKILL.md (10, incl. trigger words extended to P_116/P_117/P_118/P_910/P_920), P_115_Project_Instructions.md (5 lines), CLAUDE.md, SESSION_INITIALIZATION_PROMPT.md, OPTIONS_RISK_METHODOLOGY.md. All read back and verified. NOTE: first SKILL.md write corrupted line 1 (PowerShell function Write-Output folded into return value, destroyed YAML frontmatter delimiter -- skill would have stopped triggering); caught on readback, repaired, verified. New PowerShell rule: never Write-Output inside a function whose return value is assigned. Full detail in Agentic-Hub-Governance\work_orders\WO-P115-E3.001.md.
- 2026-07-25 -- WO-P115-E1.001 (Signal Emitter) advanced to TEST SIGNAL VERIFIED. Emitter code (emit_signal.py v2.2) was already built from a prior session but never exercised/closed under this WO. Ran the regression suite first (3/3 pass), then emitted a real signal for today's P_118 PSA BUY -- landed correctly at signals\2026-07-25_PSA_v2.0.json, read back and confirmed. Still open: 1-2 day live run + formal P_400 Ack before CLOSED. Full detail in Agentic-Hub-Governance\work_orders\WO-P115-E1.001.md.
- 2026-07-25 -- WO-P800-E4.001 (Chaikin Power Gauge Enrichment) P_115 Ack DONE. Ran RunChaikinBatch.ps1 -Schema P115 for real, 3 real BUY/WATCH notes enriched (EMR, OGN, PH), read back and confirmed correct. WO stays OWNER_DONE pending P_300 Ack. Full detail in Agentic-Hub-Governance\work_orders\WO-P800-E4.001.md, P_115-Side Verification section.
- 2026-06-09 — Created tasks\ working-state files.