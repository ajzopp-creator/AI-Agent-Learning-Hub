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
  file-writing MCP call the same way until Test-Path confirms it. Test-Path proves
  existence, NOT correctness — generated files are written directly via
  filesystem:write_file or windows-mcp:FileSystem (mode=write) and validated on
  Windows with p140 under warnings-as-errors; sandbox-build + base64 + SHA-256 is
  a fallback only for payloads too large for one tool call; targeted edits are
  count-verified. Applies to all Python execution AND file writes under
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\.
---

# peh-handoff
v1.7 | Created 2026-06-16 | Applies to all Python execution and file-writing MCP calls under C:\Users\Trader\AI-Agent-Learning-Hub\projects\

## Trigger
- MCP Python call about to run, or already timed out (4-min ceiling, ~9/10 occurrence)
- Any MCP file write (Set-Content, Add-Content, New-Item, or a direct-write tool) expected to produce a file
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

## Content integrity — diagnosis (v1.5)
Test-Path confirms a file EXISTS. It does not confirm the file is the one you
meant to write. Durable signal (above) covers writes that never land; this covers
writes that land CORRUPT — every instance below passed Test-Path and a plausible
line count, and was still broken. All three failure modes are specific to content
embedded in a **PowerShell command string** (see Rule — generated files, below,
for why that matters to the remedy).

**Chunk-boundary merge.** PowerShell here-strings (`@' '@`) emit no trailing
newline. Chunked `AppendAllText` therefore joins the last line of chunk N to the
first line of chunk N+1. Observed 2026-08-05 writing domain\ranking.py: chunk 1
ended `    """` and chunk 2 began `    span = ...`, producing
`    """    span = ...` on one line — SyntaxError, after Test-Path passed and a
141-line count looked exactly right.

**Escape sequences in docstrings.** Windows paths inside a normal (non-raw)
docstring parse as escapes: `tests\test_x.py` contains `\t` (tab), `python\ dir`
contains an invalid `\ `. A plain syntax check passes these; only compiling with
warnings-as-errors catches them. Observed twice 2026-08-05 (conftest.py,
earnings_file.py).

**Self-terminating docstrings.** A literal `"""` written inside a `"""` docstring
closes it early and turns the remainder into stray code. Observed 2026-08-05
(conftest.py explaining why it used a raw docstring — by quoting one).

### Rule — generated files (remedy rewritten v1.7, ref WO-P000-E15.001)
**Default:** write directly to the Windows path via `filesystem:write_file` or
`windows-mcp:FileSystem` (mode=write; `append=True` only when appending).
Content passes as a tool parameter, not through a PowerShell command string, so
none of the three failure modes above can occur — they are all command-string
transport failures (escaping, command-length cap, chunk-boundary merges), not
properties of the file content itself.

1. Write the file directly with the tool.
2. Validate on Windows: compile with p140 under `-W error::SyntaxWarning` before
   declaring the file good — syntax-only checking remains insufficient (v1.5
   finding unchanged).
3. Test-Path + Length/line-count confirms the write landed (Durable signal,
   above) — a clean tool return is still not proof.

**Fallback — oversized payload only.** Direct write is proven to 194 lines /
10,155 bytes in a single call; the Hub's 300-line hard limit sits just above
that, so the untested band is small (194-300 lines). If content doesn't fit one
tool call, fall back to the pre-v1.7 procedure — do not use it by default:
1. Build in the Linux sandbox (bash_tool).
2. Validate there: `py_compile` AND `compile(src, name, "exec")` under
   `-W error::SyntaxWarning`.
3. `sha256sum` and byte-count the validated source.
4. Transfer as base64 (`base64 -w0`) — no whitespace/line boundaries to lose,
   so chunks concatenate safely.
5. Decode with `[System.Convert]::FromBase64String` +
   `[System.IO.File]::WriteAllBytes`.
6. Verify `Get-FileHash -Algorithm SHA256` matches the sandbox hash. Report the
   comparison, not "written successfully."

Confirm the content actually doesn't fit one direct-write call before reaching
for the fallback — it exists for the oversized case, not as the default path.

### Rule — targeted edits to existing files
String replacement can succeed and still destroy content. Count structural
invariants BEFORE and AFTER, in the same call, and abort on mismatch rather than
writing:
- assertion count, `def ` count, `def test_` count, expected occurrence count

Observed 2026-08-05: replacing `_sessions_since_earnings` ->
`sessions_since_earnings` in test_evaluate_signal.py also rewrote five
`def test_sessions_since_earnings_*` functions to `def testsessions_*`, stripping
the `test_` prefix. Pytest would have silently stopped collecting them — green
suite, five fewer tests, no error. The count check aborted the write. Match on a
trailing `(` for call sites when the symbol is also a substring of definition
names.

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
4. Timeout/stall → ping first, then give Tony the HANDOFF PROMPT if relay
   confirmed dead. **Never blind-retry MCP. Never substitute inline PowerShell**
   — inline `python -c "..."` through the relay stalled the full 4-min ceiling
   twice 2026-08-09 (P_020 session, unrelated calls); `Start-Process`
   invocations of a script file did not fail the same way in that session.
   Prefer a small script file + `Start-Process` over an inline `-c` one-liner
   whenever a call seems likely to be slow.
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

## Related, Not the Same -- Agentic-Hub-Governance\handoffs\

verify\ (this skill) stages a self-testing run_this_*.py + context.txt pair that
Claude Code executes and reports PASS/FAIL against -- a verification loop.
handoffs\ (added 2026-08-07, ref WO-P000-E4.001/E14.001/E13.001 sessions) stages
a plain instruction prompt for a human to paste or @mention into Claude Code
Desktop's Code tab -- no PASS/FAIL loop, no .done marker, Claude Code just
reads and executes the task directly. Different shape for a different job; do
not merge them or invent a third pattern. Use verify\ when the deliverable is
a script Claude Code should run and fix on failure; use handoffs\ when it's a
multi-step task description Claude Code should read once and act on.

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
- v1.7 (8/9/26, ref WO-P000-E15.001): transport remedy narrowed for
  generated files. Default is now a direct-write tool (filesystem:write_file
  / windows-mcp:FileSystem mode=write), validated on Windows with p140 under
  warnings-as-errors; sandbox-build + base64 + SHA-256 demoted to a labelled
  fallback for payloads too large for one tool call. Root cause: v1.5's
  remedy was scoped to PowerShell-command-string transport (the only path
  the authoring session used) and written as an unconditional rule — two
  direct-write tools were already connected and idle. Evidence: an 822-byte
  non-ASCII file and a 103-line Python module (containing all four v1.5
  failure constructs deliberately) both survived transit intact via
  filesystem:write_file, first attempt; a 5-file P_020 deployment dropped
  from ~37 tool calls / 15-20K transport tokens to ~7 calls / ~6K tokens.
  v1.5's corruption diagnosis is unchanged — only the remedy moved. Also
  added: inline `python -c` relay-stall anti-pattern (Sequence, above),
  confirmed twice same day in a P_020 session.
- v1.6 (8/7/26): added "Related, Not the Same" section cross-referencing the
  new Agentic-Hub-Governance\handoffs\ pattern (plain instruction prompts for
  Claude Code Desktop's Code tab) against this skill's verify\ pattern
  (self-testing PASS/FAIL scripts), so a future session doesn't invent a
  third staging convention. No existing rule changed.
- v1.5 (8/5/26): added Content integrity section. Durable signal (v1.3/v1.4)
  covered writes that never land; v1.5 covers writes that land CORRUPT. Root
  cause: three broken files shipped to Tony in one P_400 session, all passing
  Test-Path with plausible line counts -- a here-string chunk-boundary merge in
  domain\ranking.py, and two invalid-escape docstrings. Also records the
  test_evaluate_signal.py near-miss where a blanket rename would have silently
  removed five tests from pytest collection. New rules: sandbox-validate under
  warnings-as-errors, base64 + SHA-256 transfer for generated files, before/after
  invariant counts for targeted edits.
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
  landed in a P_120 session on 2026-08-03. Payload size confirmed NOT an
  established factor (evidence table in WO-P000-E11.001) — do not chunk
  defensively.
