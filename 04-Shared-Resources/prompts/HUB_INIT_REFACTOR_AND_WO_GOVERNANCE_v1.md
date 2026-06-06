# HUB INIT REFACTOR + WORK ORDER GOVERNANCE -- Generic Prompt v1.1
Applies To: ALL AI-Agent-Learning-Hub projects (P_010, P_020, P_115, P_116,
P_117, P_118, P_300, P_301, P_400, P_800, P_805, D_130, ...). Plain ASCII.
Last Updated: 2026-06-04
v1.1 change: governance moved to a single SHARED LEDGER with 1-to-many
(one Owner, many Affects) work orders + per-consumer Acks.

================================================================================
PURPOSE
================================================================================
Run this in any project to (A) compress that project's existing initialization
prompt into an efficient deterministic form, and (B) wire it to the shared work
order ledger. Output is a rewritten init prompt that any project executes the
same way.

================================================================================
SHARED LEDGER -- single source of truth
================================================================================
LEDGER = C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\work_orders
  - ONE folder. Every work order lives here once. Status written once.
  - A work order is 1-to-many: one Owner (does the work), many Affects
    (consumers who must adopt). Per-consumer Acks close the loop.
  - No per-project work_orders folders. No duplicate files. No syncing.

================================================================================
HOW TO INVOKE
================================================================================
User types:  REFACTOR INIT [PROJECT_CODE]      e.g.  REFACTOR INIT P_115
If PROJECT_CODE omitted, ask once, then proceed.

================================================================================
PHASE 1 -- DISCOVER (never hardcode paths; glob by project code)
================================================================================
Acknowledge today's date first.

1. Environment: tool_search("PowerShell"). Windows-MCP:PowerShell present ->
   Claude Desktop, proceed. Absent -> stop, ask user to switch to Desktop.

2. Resolve project folder (folder names drift from prompt assumptions):
   Get-ChildItem "C:\Users\Trader\AI-Agent-Learning-Hub\projects" -Directory |
     ? { $_.Name -like "[CODE]*" } | Select -Expand FullName
   0 hits -> report + stop. >1 -> list + ask.

3. Locate existing init prompt: Get-ChildItem $proj -Recurse -Filter *.md |
   ? Name -match "INIT|INITIALIZATION". None -> generate skeleton. Many -> newest.

4. Governance is the SHARED LEDGER (above), NOT a per-project folder.
   (Any legacy project-local work_orders folder is deprecated -- migrate to LEDGER.)

5. Report a one-line path map (project folder, init file, LEDGER).

================================================================================
PHASE 2 -- WORK ORDER REVIEW (shared ledger, 1-to-many)
================================================================================
Read all WO-*.md in LEDGER. For project [CODE], run TWO filters:

(1) MUST DO   = Owner == CODE AND Status != CLOSED
      OPEN / IN_PROGRESS -> show task + Deliverable; this session may work it.
      OWNER_DONE         -> deliverable shipped + verified; list which Acks
                            are still pending (waiting on consumers to adopt).

(2) WAITING ON = CODE in Affects AND my Ack == pending AND Status != CLOSED
      Owner still working (OPEN/IN_PROGRESS) -> note "waiting on [Owner] for [WO]".
      Status OWNER_DONE -> ACTION REQUIRED: adopt the change, then set my
                            Ack = done [date] on that WO in the LEDGER.

Blocking verdict (applies to MUST-DO set):
  Any MUST-DO WO with Status BLOCKED (or Depends-On not CLOSED) -> STOP;
    show Depends-On + Blocker.
  Else proceed.

Print a 2-line governance summary in the init: my open WOs (Owner), my pending
adoptions (Affects). If CODE appears in neither filter -> NO_WO (caution).

================================================================================
PHASE 3 -- COMPRESS THE INIT PROMPT
================================================================================
Rewrite the discovered init (change form, not behavior):
  - Strip prose to imperatives. One action per line.
  - Repeated key/value text -> tables. Deduplicate: state each rule once.
  - Replace hardcoded paths with the Phase-1 discovery commands.
  - Keep exact thresholds, gates, schemas, lifecycle states verbatim.
  - Preserve MUST / MUST NOT lists; compress wording, keep meaning.
  - ASCII only. No emoji. Only === and --- as rules.
  - Compress where it does not lose clarity; no fixed ratio.
  - Insert the Phase-2 ledger review as a numbered STEP (e.g. 0.5) after
    environment detection and before any sizing/build logic.

================================================================================
PHASE 4 -- EMIT
================================================================================
Output, in order:
  1. Path map (project folder, init file, LEDGER).
  2. Governance summary (my open WOs; my pending adoptions).
  3. Rewritten init prompt in full (single code block).
  4. Exact Windows save path (overwrite the discovered init file; back up first).
  5. 3-line diff summary: old line count -> new, what was removed.
Do NOT write to disk until user confirms. Then back up original, then write.

================================================================================
DROP-IN: STANDARD LEDGER REVIEW STEP (paste into every project init)
================================================================================
### STEP [n]: Work Order Review (shared ledger)
$LEDGER = "C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\work_orders"
Read all WO-*.md. CODE = this project.
  MUST DO   = Owner==CODE & Status!=CLOSED   (OPEN/IN_PROGRESS=work it; OWNER_DONE=await acks)
  WAITING   = CODE in Affects & my Ack=pending & Status!=CLOSED
              (OWNER_DONE -> adopt change, set my Ack=done [date])
  Any MUST-DO BLOCKED or Depends-On not CLOSED -> STOP (show blocker).
Print: my open WOs + my pending adoptions. Neither -> NO_WO caution.

================================================================================
STANDARD WORK ORDER SCHEMA (shared ledger; 1 Owner, many Affects)
================================================================================
File name: WO-[OWNERCODE]-[PHASE].[SEQ].md      e.g. WO-P800-E2.001.md
Header (exact field names):
  # WO-[OWNERCODE]-[PHASE].[SEQ] -- [Task Name]
  **Status:** OPEN | IN_PROGRESS | OWNER_DONE | CLOSED
  **Owner:** [CODE]                  (does the work; exactly one)
  **Affects:** [CODE, CODE, ...]     (consumers who must adopt; may be empty)
  **Deliverable:** [path/artifact the owner must produce]
  **Verified:** [date]               (deliverable confirmed to exist)
  **Depends On:** [WO-ID]            (optional)
  **Blocker:** [reason]              (required if BLOCKED/Depends-On open)
  **Acks:**                          (one line per Affects entry)
    [CODE]: pending | done [date]
  ...body...

State transitions:
  OPEN -> IN_PROGRESS  (owner starts)
       -> OWNER_DONE   (deliverable exists AND Verified set)
       -> CLOSED       (OWNER_DONE AND every Ack=done; if Affects empty, CLOSED at Verified)

Why 1-to-many: a schema/interface change has one producer but many consumers.
Owner-done is NOT loop-done -- each consumer must adopt and Ack before CLOSED.

================================================================================
END -- HUB INIT REFACTOR + WORK ORDER GOVERNANCE v1.1
Save: C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\prompts\HUB_INIT_REFACTOR_AND_WO_GOVERNANCE_v1.md
================================================================================
