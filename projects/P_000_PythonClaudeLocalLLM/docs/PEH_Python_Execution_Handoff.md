# PEH -- Python Execution Handoff
# P_000 Hub Governance | Created 2026-06-16 | v1.4 2026-08-04

---

## Purpose

Claude Desktop has a hard 4-minute MCP timeout on Python execution, and the same
relay can silently drop plain file writes too. When either fires during any project
phase (WO implementation, pipeline testing, development verification, etc.), the
Python Execution Handoff (PEH) pattern applies. Claude Desktop writes two files to
the Hub governance verify folder, then the user pastes a standard prompt into
Claude Code for execution and error resolution.

---

## File Locations (timestamped, v1.4)

  C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>.py
  C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>_context.txt
  C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>.py.done

PROJECT = the Hub project ID (P_020, P_300, etc.). TS = YYYYMMDD_HHMMSS.

Prior to v1.4 these were fixed filenames (run_this.py / run_this_context.txt),
overwritten on every handoff. That collided: two projects handing off the same day
silently destroyed each other's files, and there was no on-disk signal that a
handoff had ever been consumed. Both are fixed in v1.4 -- see Change Log. The
.done file is written on completion and is the durable, Test-Path-checkable signal
that a given handoff ran, when, and PASS or FAIL.

---

## Standard Claude Code Prompt (names the specific timestamped file)

  Read C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>_context.txt
  then run C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>.py
  using C:\Users\Trader\.conda\envs\p140\python.exe
  Fix any errors until it prints PASS. Paste full output back to me.

---

## Python Environment

  Executable : C:\Users\Trader\.conda\envs\p140\python.exe
  Rule       : Never create a new venv. Always use p140.

---

## What Claude Desktop Writes

run_this_<PROJECT>_<TS>.py
  Self-contained test script for the current task. Always ends with
  print("PASS") or print("FAIL:", reason); sys.exit(1). Sets sys.path explicitly
  to the target project's python\ folder -- no relative import assumptions, and
  no import of a shared helper (keeps the script self-contained; ref WO-P000-E2.003
  on sys.path side-channels). Before exiting, writes its own sibling .done file:
  three lines -- timestamp, status (PASS|FAIL), exit_code.

run_this_<PROJECT>_<TS>_context.txt
  One-paragraph brief: what phase/WO/task this belongs to, what success
  looks like, what Claude Code should fix if it fails.

---

## Pre-Stage Check (v1.4)

Before writing a new run_this_<PROJECT>_<TS>.py, scan verify\ for any
run_this_*.py with no matching .py.done sibling. An unconsumed handoff found
this way is surfaced to Tony, not silently left in place. This is what the fixed
filename scheme could not do -- see Change Log v1.4 for the incident that drove it.

---

## Durable Signal -- Applies Beyond Python Execution (v1.4)

The same "clean return is not proof" rule that governs Start-Job/Get-Job applies to
any Windows-MCP file write -- Set-Content, Add-Content, New-Item. A write can return
without error while the relay silently drops it. After any MCP file write, confirm
with Test-Path plus a Length or line-count read before reporting success to Tony.

Payload size is NOT an established factor in these stalls (evidence table:
WO-P000-E11.001) -- a 4.1KB write succeeded and a ~5KB write silently failed in the
same session, with no controlled retry of the failing size once the relay recovered.
Do not chunk writes defensively based on size alone; chunk only when a write has
already failed once.

---

## Retention (v1.4)

Completed handoff sets (script + context + .done, all three present) older than 14
days are archived to verify\_archive\ by peh_helper.py's archive_old_handoffs().
Incomplete handoffs are never auto-archived -- they stay in verify\ and surface via
the pre-stage check until resolved.

---

## peh_helper.py (v1.4, maintenance-only)

C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\peh_helper.py

Not imported by run_this scripts -- run directly, or call its functions before
staging a new handoff:
  generate_handoff_filenames(project)  -- timestamped script/context paths
  check_pending_handoffs()             -- unconsumed-handoff list, pre-stage check
  archive_old_handoffs()               -- retention sweep, 14-day default

---

## What Claude Code Does

1. Reads run_this_<PROJECT>_<TS>_context.txt for context.
2. Runs run_this_<PROJECT>_<TS>.py with p140 python.
3. Fixes any import or runtime errors (does not change test assertions).
4. Re-runs until PASS.
5. Pastes full terminal output back into the Claude Desktop chat.

(The .py.done marker is written by the script itself on exit -- Claude Code does
not need to write it, and should not skip a fix-and-rerun cycle just because a
.done file with FAIL status already exists from an earlier attempt.)

---

## Trigger Conditions

PEH fires whenever Claude Desktop hits the 4-minute MCP ceiling on a Python call
(~9/10 occurrence rate), or when any MCP file write needs its result confirmed
durably rather than trusted on a clean return. Claude Desktop should write
run_this_<PROJECT>_<TS>.py and its context file BEFORE attempting the MCP Python
call so the files are ready if timeout occurs.

---

## Scope

Not limited to work orders. Applies to any Python execution or file-writing MCP
call:
  - WO implementation verification
  - Pipeline phase testing
  - Development sanity checks
  - Schema validation
  - Import path verification
  - Any Set-Content / Add-Content / New-Item expected to land a file

---

## First Use

2026-06-16 | WO-P115-E2.001 stop field enrichment | PASS on first run.
signal_builder.py already had all three stop fields. Claude Code ran clean,
no fixes needed.

---

## Change Log

- 2026-06-16 v1.0: Document created. Pattern established.
- 2026-08-04 v1.4: Two fixes landed together (same-day, avoids a double version
  bump against the skill file).
  (1) WO-P000-E12.001 -- fixed filenames (run_this.py) replaced with timestamped
  run_this_<PROJECT>_<TS>.py; added .py.done completion marker; added pre-stage
  unconsumed-handoff check; added 14-day retention/archival via peh_helper.py.
  Root cause: on 2026-08-04, a P_020 session nearly overwrote an in-progress
  P_300 independent-review handoff because the fixed filename gave no collision
  protection and no on-disk record of whether the P_300 run had already
  completed -- confirming it required forensics instead of a lookup.
  (2) WO-P000-E11.001 -- durable-signal rule extended from Python execution to
  any file-producing Windows-MCP call (Set-Content/Add-Content/New-Item). Root
  cause: a Set-Content writing tasks\lessons.md stalled for the full 4-minute
  ceiling and silently never created the file, in a P_120 session on
  2026-08-03. Also corrected a path reference stale since 2026-07-11: this doc
  described 04-Shared-Resources, which was retired and renamed to
  Agentic-Hub-Governance three revisions ago in the skill file; this doc had
  not been updated to match until now.