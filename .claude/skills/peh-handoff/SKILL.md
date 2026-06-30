---
name: peh-handoff
description: >
  PEH — write run_this.py + run_this_context.txt to Agentic-Hub-Governance\verify\
  BEFORE every Windows-MCP Python call; on 4-min timeout, hand off to Claude Code
  instead of retrying. Applies to all Python execution under
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\.
---

# peh-handoff
v1.2 | Created 2026-06-16 | Applies to all projects under C:\Users\Trader\AI-Agent-Learning-Hub\projects\

## Trigger
- MCP Python call about to run, or already timed out (4-min ceiling, ~9/10 occurrence)
- Tony says "run/test/verify this" for Python code
- Any WO/phase step needing Python execution

## Sequence
1. Write run_this.py + run_this_context.txt to the verify folder (paths below).
2. Attempt the MCP call.
3. Timeout → give Tony the HANDOFF PROMPT. **Never retry MCP. Never substitute inline PowerShell.**
4. If timeout hits before files exist: write them now, then hand off.

## Fixed paths (never change)
```
C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this.py
C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_context.txt
```
Ephemeral — overwritten each handoff.

## Handoff prompt (verbatim to Tony)
```
Read C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_context.txt
then run C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this.py
using C:\Users\Trader\.conda\envs\p140\python.exe
Fix any errors until it prints PASS. Paste full output back to me.
```

## run_this.py
Self-contained, sets sys.path to project python\ folder, never modifies production files.
Ends: `print("PASS")` (success) or `print("FAIL:", reason)` + `sys.exit(1)` (failure).

## run_this_context.txt
Plain text: phase/WO/task + date, what the script tests (2-3 sentences), success criteria,
what Claude Code should fix on failure, "Do not change test assertions."

## Python env
`C:\Users\Trader\.conda\envs\p140\python.exe` — always p140, never a new venv.

## On Tony's return
PASS → mark step complete. FAIL → read error, propose production fix, ask Tony to re-run.
No PASS/FAIL in output → ask for full terminal output.

## Full docs
`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\docs\PEH_Python_Execution_Handoff.md`

## History
- v1.0 (6/16/26): created, replaces standalone PowerShell pattern. First use WO-P115-E2.001, PASS.
- v1.1 (6/16/26): scope broadened from P_115-118 to all Hub projects.
- v1.2 (6/19/26): canonical path switched 04-Shared-Resources → Agentic-Hub-Governance
  (same files via junction; removes "Shared Resources" hub-level naming ambiguity).
