---
name: peh-handoff
description: >
  PEH — before any Windows-MCP call expected to produce a file (Python execution
  or a direct file write like Set-Content/Add-Content/New-Item), stage a
  timestamped run_this_PROJECT_TIMESTAMP.py + _context.txt pair in
  Agentic-Hub-Governance\verify\; on 4-min timeout or relay stall, hand off to
  Claude Code instead of retrying. Start-Job/Get-Job do not survive across
  separate MCP tool calls — treat any "still running in background" assumption
  as false until confirmed by a file on disk, and treat a clean return from any
  file-writing MCP call the same way until Test-Path confirms it. Applies to all
  Python execution AND file writes under C:\Users\Trader\AI-Agent-Learning-Hub\projects\.
---

# peh-handoff
v1.4 | Created 2026-06-16 | Applies to all Python execution and file-writing MCP calls under C:\Users\Trader\AI-Agent-Learning-Hub\projects\

## Trigger
- MCP Python call about to run, or already timed out (4-min ceiling, ~9/10 occurrence)
- Any MCP file write (Set-Content, Add-Content, New-Item) expected to produce a file
- Tony says "run/test/verify this" for Python code
- Any WO/phase step needing Python execution or a file write

## Durable signal (v1.3 Job Persistence, renamed + broadened v1.4)
Start-Job / Get-Job do not survive across separate MCP tool calls — each call is
effectively a new process, so a backgrounded job is orphaned even if the call
"succeeds." The same failure shows up in plain file writes: a `Set-Content` or
`Add-Content` can return cleanly while the relay silently drops the write. Durable
signal = a file actually on disk, confirmed with Test-Path AND a Length / line-count
read — never "the call returned without error."

- Fast work (py_compile, small writes): one direct synchronous call, no
  backgrounding — but only if a plain `Write-Output "ping"` is currently fast.
- Detached/backgrounded work: `Start-Process -WindowStyle Hidden`, not Start-Job.
- Any MCP file write: after it returns, run Test-Path + Get-Item (Length) or
  Get-Content (line count) on the target BEFORE reporting success to Tony. A
  clean return is not confirmation.
- Payload size is NOT an established factor (ref WO-P000-E11.001 evidence
  table: a 4.1KB write succeeded, a ~5KB write silently failed, both retried
  as smaller chunks succeeded — n=1, confounded by a relay stall). Do not
  chunk defensively on size alone.
- Any call that hits ~4 min or returns "No result received": STOP. Ping first.
  If ping is slow too, the relay is down — tell Tony to restart it. If ping is
  fast, the earlier stall was the relay, not the work — retry fresh, don't
  assume the old dispatch is still running.

## Sequence
1. Pre-stage check: scan verify\ for any run_this_*.py with no matching .done
   file. If found, surface it to Tony before staging a new one — do not overwrite
   silently (ref WO-P000-E12.001, near-miss 2026-08-04: a P_020 handoff nearly
   clobbered an in-progress P_300 independent-review handoff).
2. Write run_this_<PROJECT>_<TS>.py + run_this_<PROJECT>_<TS>_context.txt to the
   verify folder (paths below). PROJECT = the Hub project ID (P_020, P_300, etc.),
   TS = YYYYMMDD_HHMMSS.
3. Attempt the MCP call (sync if fast, Start-Process if backgrounded), or the
   direct file write.
4. Timeout/stall → ping first, then give Tony the HANDOFF PROMPT if relay confirmed
   dead. **Never blind-retry MCP. Never substitute inline PowerShell.**
5. If timeout hits before files exist: write them now, then hand off.
6. On completion, run_this_<PROJECT>_<TS>.py writes a sibling .done file
   (timestamp, PASS/FAIL, exit code) — see "run_this script" below. This is the
   Test-Path-checkable completion signal.

## Filenames (timestamped, never fixed — v1.4)
```
Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>.py
Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>_context.txt
Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>.py.done   (written on completion)
```
TS = YYYYMMDD_HHMMSS. Two projects handing off the same day can no longer collide.
A single `Test-Path run_this_<PROJECT>_<TS>.py.done` answers whether a given
handoff was consumed, when, and PASS or FAIL — no forensics required.

## Retention
Completed sets (script + context + .done, all three present) older than 14 days
are archived to `verify\_archive\` by peh_helper.py's `archive_old_handoffs()` —
run it periodically. Incomplete handoffs (no .done) are never auto-archived; they
surface via the pre-stage check instead until resolved.

## Handoff prompt (verbatim to Tony — names the specific timestamped file)
```
Read C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>_context.txt
then run C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\run_this_<PROJECT>_<TS>.py
using C:\Users\Trader\.conda\envs\p140\python.exe
Fix any errors until it prints PASS. Paste full output back to me.
```

## run_this script
Self-contained, sets sys.path to project python\ folder, never modifies production
files. Ends:
```python
print("PASS")                    # or
print("FAIL:", reason); sys.exit(1)
```
then, before exit, writes its own .done marker (status, exit code, timestamp) next
to itself — three lines, see peh_helper.py's `done_marker_format()` docstring for
the exact format. Written inline, not via an imported helper, to stay self-contained
per the existing v1.0 design (ref WO-P000-E2.003 — no sys.path side-channels).

## run_this_context.txt
Plain text: phase/WO/task + date, what the script tests (2-3 sentences), success criteria,
what Claude Code should fix on failure, "Do not change test assertions."

## peh_helper.py (v1.4, maintenance-only — not imported by run_this scripts)
`Agentic-Hub-Governance\peh_helper.py`. Run directly (`python peh_helper.py`) or call
its functions before staging:
- `generate_handoff_filenames(project)` — returns the timestamped script/context paths
- `check_pending_handoffs()` — unconsumed-handoff list for the pre-stage check
- `archive_old_handoffs()` — retention sweep

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
- v1.4 (8/4/26): two fixes landed together to avoid a double version bump.
  (1) WO-P000-E12.001: fixed filenames replaced with timestamped
  run_this_<PROJECT>_<TS>.py, added .done completion marker, pre-stage
  unconsumed-handoff check, retention rule. Root cause: fixed-name collision
  nearly destroyed an in-progress P_300 independent-review handoff on 2026-08-04.
  (2) WO-P000-E11.001: section renamed Job persistence → Durable signal, scope
  broadened from Python execution only to any file-producing MCP call. Root
  cause: a Set-Content writing tasks\lessons.md stalled and silently never
  landed in a P_120 session on 2026-08-03 — v1.3 text didn't cover it because
  it was framed around Start-Job. Payload size confirmed NOT an established
  factor (evidence table in WO-P000-E11.001) — do not chunk defensively.