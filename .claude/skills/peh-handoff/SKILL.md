---
name: peh-handoff
description: >
  PEH — write run_this.py + run_this_context.txt to Agentic-Hub-Governance\verify\
  BEFORE every Windows-MCP Python call; on 4-min timeout or relay stall, hand off
  to Claude Code instead of retrying. Start-Job/Get-Job do not survive across
  separate MCP tool calls — treat any "still running in background" assumption
  as false until confirmed by a file on disk. Applies to all Python execution
  under C:\Users\Trader\AI-Agent-Learning-Hub\projects\.
---

# peh-handoff
v1.3 | Created 2026-06-16 | Applies to all projects under C:\Users\Trader\AI-Agent-Learning-Hub\projects\

## Trigger
- MCP Python call about to run, or already timed out (4-min ceiling, ~9/10 occurrence)
- Tony says "run/test/verify this" for Python code
- Any WO/phase step needing Python execution

## Job persistence (v1.3, 2026-07-12)
Start-Job / Get-Job do not survive across separate MCP tool calls — each call is
effectively a new process, so a backgrounded job is orphaned even if the call
"succeeds." Durable signal = a file actually on disk, checked with Test-Path /
Get-Content — never "the call returned without error."
- Fast work (py_compile, small writes): one direct synchronous call, no
  backgrounding — but only if a plain `Write-Output "ping"` is currently fast.
- Detached/backgrounded work: `Start-Process -WindowStyle Hidden`, not Start-Job.
  Redirect to a uniquely-named output file — never reuse a generic name like
  init_out.txt (risk of reading stale leftovers from a prior run).
- Any call that hits ~4 min or returns "No result received": STOP. Ping first.
  If ping is slow too, the relay is down — tell Tony to restart it. If ping is
  fast, the earlier stall was the relay, not the work — retry fresh, don't
  assume the old dispatch is still running.

## Sequence
1. Write run_this.py + run_this_context.txt to the verify folder (paths below).
2. Attempt the MCP call (sync if fast, Start-Process if backgrounded).
3. Timeout/stall → ping first, then give Tony the HANDOFF PROMPT if relay confirmed
   dead. **Never blind-retry MCP. Never substitute inline PowerShell.**
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
- v1.3 (7/12/26): added Job Persistence rule. Root-caused in a P_020 session:
  Start-Job does not survive across separate MCP tool calls (confirmed via a
  trivial "hello" write test that never landed).
