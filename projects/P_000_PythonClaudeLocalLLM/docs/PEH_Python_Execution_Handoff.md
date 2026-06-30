# PEH -- Python Execution Handoff
# P_000 Hub Governance | Created 2026-06-16

---

## Purpose

Claude Desktop has a hard 4-minute MCP timeout on Python execution. When that
ceiling is hit during any project phase (WO implementation, pipeline testing,
development verification, etc.), the Python Execution Handoff (PEH) pattern
fires. Claude Desktop writes two files to the Hub governance verify folder,
then the user pastes a standard prompt into Claude Code for execution and
error resolution.

---

## Fixed File Locations

  C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\verify\run_this.py
  C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\verify\run_this_context.txt

Both files are overwritten on every handoff. They are ephemeral -- do not
treat them as permanent artifacts. The README at that folder points here.

---

## Standard Claude Code Prompt (pin this)

  Read C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\verify\run_this_context.txt
  then run C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\verify\run_this.py
  using C:\Users\Trader\.conda\envs\p140\python.exe
  Fix any errors until it prints PASS. Paste full output back to me.

---

## Python Environment

  Executable : C:\Users\Trader\.conda\envs\p140\python.exe
  Rule       : Never create a new venv. Always use p140.

---

## What Claude Desktop Writes

run_this.py
  Self-contained test script for the current task. Always ends with
  print("PASS") or print("FAIL:", reason). Sets sys.path explicitly --
  no relative import assumptions.

run_this_context.txt
  One-paragraph brief: what phase/WO/task this belongs to, what success
  looks like, what Claude Code should fix if it fails.

---

## What Claude Code Does

1. Reads run_this_context.txt for context.
2. Runs run_this.py with p140 python.
3. Fixes any import or runtime errors (does not change test assertions).
4. Re-runs until PASS.
5. Pastes full terminal output back into the Claude Desktop chat.

---

## Trigger Conditions

PEH fires whenever Claude Desktop hits the 4-minute MCP ceiling on a Python
call. This is a ~9/10 occurrence rate for any Python execution via Windows-MCP.
Claude Desktop should write run_this.py and run_this_context.txt BEFORE
attempting the MCP Python call so the files are ready if timeout occurs.

---

## Scope

Not limited to work orders. Applies to any Python execution need:
  - WO implementation verification
  - Pipeline phase testing
  - Development sanity checks
  - Schema validation
  - Import path verification

---

## First Use

2026-06-16 | WO-P115-E2.001 stop field enrichment | PASS on first run.
signal_builder.py already had all three stop fields. Claude Code ran clean,
no fixes needed.

---

## Change Log

- 2026-06-16 v1.0: Document created. Pattern established.