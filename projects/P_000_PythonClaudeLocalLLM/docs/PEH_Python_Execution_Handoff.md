# PEH -- Python Execution Handoff
# P_000 Hub Governance | Created 2026-06-16 | v1.7 2026-08-09

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
any Windows-MCP file write -- Set-Content, Add-Content, New-Item, or a direct-write
tool. A write can return without error while the relay silently drops it. After any
MCP file write, confirm with Test-Path plus a Length or line-count read before
reporting success to Tony.

Payload size is NOT an established factor in these stalls (evidence table:
WO-P000-E11.001) -- a 4.1KB write succeeded and a ~5KB write silently failed in the
same session, with no controlled retry of the failing size once the relay recovered.
Do not chunk writes defensively based on size alone; chunk only when a write has
already failed once.

---

## Content Integrity (v1.5 diagnosis, v1.7 remedy)

Test-Path confirms a file EXISTS, not that it is the file you meant to write.
Durable Signal (above) covers writes that never land; this section covers writes
that land CORRUPT -- every case below passed Test-Path and a plausible line count
and was still broken. All three modes are failures of content embedded in a
**PowerShell command string** specifically -- see Remedy, below, for why that
scoping matters.

**Chunk-boundary merge.** PowerShell here-strings (`@' '@`) emit no trailing
newline, so chunked `AppendAllText` joins the last line of one chunk to the first
line of the next. Observed 2026-08-05 in domain\ranking.py: `    """` (chunk end)
+ `    span = ...` (next chunk start) merged onto one line -- SyntaxError, despite
Test-Path passing and the line count looking correct.

**Escape sequences in docstrings.** Windows paths inside a normal (non-raw)
docstring parse as escapes -- `tests\test_x.py` contains `\t`, `python\ dir`
contains an invalid `\ `. A plain syntax check misses these; only compiling with
warnings-as-errors catches them. Observed twice 2026-08-05 (conftest.py,
earnings_file.py).

**Self-terminating docstrings.** A literal `"""` written inside a `"""` docstring
closes it early, turning the remainder into stray code. Observed 2026-08-05
(conftest.py, quoting the triple-quote while explaining why it used a raw string).

### Remedy -- generated files (rewritten v1.7, ref WO-P000-E15.001)

**Default:** write directly to the Windows path via `filesystem:write_file` or
`windows-mcp:FileSystem` (mode=write; `append=True` only when appending). Content
passes as a tool parameter, not through a PowerShell command string, so none of
the three failure modes above can occur -- they are transport failures specific
to command-string embedding (escaping, command-length cap, chunk-boundary
merges), not properties of the content itself.

1. Write the file directly with the tool.
2. Validate on Windows: compile with p140 under `-W error::SyntaxWarning` before
   declaring the file good -- syntax-only checking remains insufficient (v1.5
   finding unchanged).
3. Test-Path + Length/line-count confirms the write landed (Durable Signal,
   above) -- a clean tool return is still not proof.

**Fallback -- oversized payload only.** Direct write is proven to 194 lines /
10,155 bytes in a single call; the Hub's 300-line hard file limit sits just
above that, so the untested band is narrow (194-300 lines). Use the fallback
only after confirming the content does not fit one direct-write call:
1. Build in the Linux sandbox (bash_tool).
2. Validate there: `py_compile` AND `compile(src, name, "exec")` under
   `-W error::SyntaxWarning`.
3. `sha256sum` and byte-count the validated source.
4. Transfer as base64 (`base64 -w0`) -- no whitespace/line boundaries to lose,
   so chunks concatenate safely.
5. Decode with `[System.Convert]::FromBase64String` +
   `[System.IO.File]::WriteAllBytes`.
6. Verify `Get-FileHash -Algorithm SHA256` matches the sandbox hash. Report the
   hash comparison, not "written successfully."

**Why the remedy changed:** v1.5's rule was correct for the failure it diagnosed
but was scoped to the only transport the authoring session used (PowerShell
command strings) and then written as unconditional. Two direct-write tools
(above) were already connected and idle. Evidence, live test 2026-08-09: an
822-byte file with non-ASCII content (em-dash, emoji, box-drawing, curly quotes)
and a 103-line Python module deliberately containing all four v1.5 failure
constructs both survived transit intact via `filesystem:write_file`, first
attempt, UTF-8 no-BOM confirmed byte-for-byte. Measured cost on a 5-file P_020
deployment: ~37 tool calls / 15-20K transport tokens under the old rule vs.
~7 calls / ~6K tokens under this one. The corruption diagnosis is unchanged --
only the remedy moved.

### Rule -- targeted edits to existing files
String replacement can succeed and still destroy content. Count structural
invariants BEFORE and AFTER the edit, in the same call, and abort on mismatch
rather than writing -- assertion count, `def ` count, `def test_` count, or
whatever occurrence count the edit should preserve.

Observed 2026-08-05: renaming `_sessions_since_earnings` ->
`sessions_since_earnings` in test_evaluate_signal.py also rewrote five
`def test_sessions_since_earnings_*` functions to `def testsessions_*`,
stripping the `test_` prefix -- pytest would have silently stopped collecting
them (green suite, five fewer tests, no error). The count check aborted the
write. Match on a trailing `(` for call sites when the symbol is also a
substring of definition names.

---

## Related, Not the Same -- Agentic-Hub-Governance\handoffs\ (v1.6)

verify\ (this doc) stages a self-testing run_this_*.py + context.txt pair that
Claude Code executes and reports PASS/FAIL against -- a verification loop.
handoffs\ (added 2026-08-07, ref WO-P000-E4.001/E14.001/E13.001 sessions) stages
a plain instruction prompt for a human to paste or @mention into Claude Code
Desktop's Code tab -- no PASS/FAIL loop, no .done marker, Claude Code just reads
and executes the task directly. Different shape for a different job -- do not
merge them or invent a third pattern. Use verify\ when the deliverable is a
script Claude Code should run and fix on failure; use handoffs\ when it's a
multi-step task description Claude Code should read once and act on.

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

**Anti-pattern -- inline `python -c` (v1.7).** Inline `python -c "..."` through
the PowerShell MCP relay stalled the full 4-minute ceiling twice, 2026-08-09,
P_020 session, unrelated calls. `Start-Process` invocations of a script file did
not fail the same way in that session. Prefer a small script file run via
`Start-Process` over an inline `-c` one-liner whenever a call seems likely to be
slow.

---

## Scope

Not limited to work orders. Applies to any Python execution or file-writing MCP
call:
  - WO implementation verification
  - Pipeline phase testing
  - Development sanity checks
  - Schema validation
  - Import path verification
  - Any Set-Content / Add-Content / New-Item / direct-write-tool call expected
    to land a file

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
- 2026-08-05 v1.5: added Content Integrity section (this doc was not updated
  when the skill file landed v1.5 on 2026-08-05 -- three revisions stale per
  WO-P000-E12.001's ALSO NOTED section; closed here as part of the WO-P000-E15.001
  pass). Diagnosed three corruption modes -- chunk-boundary merge, docstring
  escape sequences, self-terminating docstrings -- all specific to content
  carried in a PowerShell command string. Original remedy: sandbox-build +
  base64 + SHA-256 transfer for generated files; before/after invariant counts
  for targeted edits.
- 2026-08-07 v1.6: added "Related, Not the Same" section distinguishing
  verify\ (this doc's pattern) from the new Agentic-Hub-Governance\handoffs\
  pattern (plain instruction prompts, no PASS/FAIL loop). No existing rule
  changed.
- 2026-08-09 v1.7 (ref WO-P000-E15.001): Content Integrity remedy narrowed.
  Default for generated files is now a direct-write tool (filesystem:write_file
  / windows-mcp:FileSystem mode=write), validated on Windows with p140 under
  warnings-as-errors; sandbox-build + base64 + SHA-256 demoted to a labelled
  fallback for payloads too large for one tool call. Root cause: v1.5's remedy
  was scoped to PowerShell-command-string transport and written as
  unconditional, when two direct-write tools were already connected and idle.
  Live evidence and cost comparison in Content Integrity section, above. v1.5's
  corruption diagnosis is unchanged -- only the remedy moved. Also added:
  inline `python -c` relay-stall anti-pattern (Trigger Conditions, above).
