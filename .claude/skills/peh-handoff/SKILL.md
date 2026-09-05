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
  Windows with p140 under warnings-as-errors. Existing files default to a
  targeted PowerShell replace, not a full-file rewrite, since str_replace fails
  on these paths. Applies to all Python execution AND file writes under
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\.
---

# peh-handoff
v1.11 | Created 2026-06-16 | Applies to all Python execution and file-writing MCP calls under C:\Users\Trader\AI-Agent-Learning-Hub\projects\

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
  fast, the earlier stall was the relay, not the work -- but that is not license
  to retry the actual work call. Hand off to Claude Code immediately (see
  Sequence below). One confirmed-fast ping proves the relay can carry a
  small payload; it does not prove the larger work call will succeed a
  second time, and a second attempt is exactly the retry this skill exists
  to prevent.

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

**Unicode punctuation in PowerShell script anchors (new, discovered 2026-08-29).**
Em-dashes, arrows, and other non-ASCII characters typed directly into a
`.ps1` script's match/anchor string (e.g. `$old = "...em-dash..."`) can
silently fail to match content read from the SAME file via
`[System.IO.File]::ReadAllText()`, even though both reads are UTF-8.
Root cause: the `.ps1` script file itself and the PowerShell host parsing
it do not always round-trip non-ASCII bytes the same way `ReadAllText`
does -- observed twice 2026-08-29 (P_000_SYSTEM_DOCUMENTATION.md and
system-doc-initializer SKILL.md edits), both times as silent 0-occurrence
matches with no error, not a crash. Confirmed via a live probe (occurrence
count printed before any write): the full-paragraph anchor containing an
em-dash returned 0; the identical anchor with the em-dash stripped out
returned 1, same file, same content, same session.
Remedy: never type em-dash/arrow/other non-ASCII characters directly into
a `.ps1` anchor string. Use a shorter ASCII-only substring immediately
before or after the special character to `IndexOf()` a position, then
splice with `Substring()` -- never require the special character itself to
appear inside a matched-and-replaced string. If the special character must
appear in the REPLACEMENT text, build it from `[char]` codes
(`[char]0x2014` for em-dash, `[char]0x2192` for arrow) rather than typing
it, or just use plain ASCII (`--`, `->`) in new content going forward.
Always print an occurrence-count guard before writing (per the Rule below)
-- this is what surfaces the 0-vs-1 mismatch instead of a silent no-op.

**Backtick-as-escape-character corruption (new, discovered 2026-09-04).**
PowerShell backtick (`) is the escape character in double-quoted strings
and `@"..."@` here-strings -- typing a literal backtick immediately before a
letter that happens to form a recognized escape (`t` = tab, `n` = newline,
`r` = carriage return) silently substitutes that control character and
drops the letter, with no error. This corrupts markdown code-span
formatting specifically: ``tasks\lessons.md`` typed in a double-quoted
PowerShell string became a literal TAB followed by "asks\lessons.md" --
same failure shape as the Unicode-punctuation finding above (silent
0-vs-expected mismatch, not a crash), different root cause (PowerShells
own escape table, not a UTF-8 round-trip issue). Observed twice in one
P_000 session (2026-09-04, WO-P000-E20.001 doc edits): `t`asks\lessons.md
and three separate `t`est_*.py filenames, all corrupted the same way.
Also self-inflicted while fixing this same finding: an anchor string
containing an em-dash, typed directly into a PowerShell command
parameter (not a saved .ps1 file), silently failed to match this
files own heading -- the exact failure mode documented above,
confirming it applies to inline command strings through this tool, not
only saved .ps1 scripts. Remedy: never use double-quoted strings or
`@"..."@` here-strings for content containing literal backticks -- use
single-quoted strings (') or `@'...'@` here-strings instead, which do
not interpret any escape sequence. If backticks must combine with
variable interpolation, build the backtick from `[char]0x60` and
concatenate -- same pattern already established for em-dash/arrow
above. And separately: never type an em-dash or other non-ASCII
character directly into ANY match anchor, inline command parameter or
saved .ps1 alike -- use an ASCII-only anchor immediately before or
after it instead, per the existing remedy above. Always run the
existing occurrence-count guard after writing, not just before -- it
catches this class of corruption too, since the written content no
longer round-trips against the intended source text.

**Cross-file/cross-project claims stated without checking (new,
discovered 2026-09-04).** Told the operator two projects "use the same
file, same function, same endpoint" based on a shared-architecture
docs description of a wrapper as "shared interface for all Hub
projects" -- the doc was accurate about the wrapper existing, but did
not establish that a specific other project actually calls it for the
specific capability in question. Grepping and reading the other
projects actual code, done only after the operator pushed back, found
a completely separate, independently-built client (different endpoint,
different HTTP library, different timeout constant). Remedy: before
stating "X uses the same code/path/config as Y" to the operator, grep
and read Xs actual imports and call sites -- a shared-infrastructure
description in an architecture doc is a claim about what SHOULD be
true, never confirmation of what a specific caller actually does. Same
evidence-over-assumption principle this skill already applies to file
writes (Durable signal, Content integrity) -- extends here to claims
made about code that was not directly re-read in the same session.


### Rule — generated files (remedy rewritten v1.7, ref WO-P000-E15.001)
**Applies to genuinely new files.** For editing an existing file, see "Rule —
editing an EXISTING file" below first — that rule takes precedence when a file
already has content on disk.

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

### Rule — editing an EXISTING file (new, v1.8)
**A file that already has real content on disk is never a "generate a new
file" case, even when the edit touches most of it.** The rule above is for
files that don't exist yet. This rule governs every edit to something already
on disk — a WO, a skill file, a vault note, a config, a production module.

**Why this is its own rule, not a variant of the one above.** `str_replace`
(the actual line-level patch tool) fails outright on this Hub's Windows paths
— confirmed failure, WO-P020-E1.010.md, 2026-08-19 ("File not found" despite
the file existing and being readable). The fallback that's been used since is
reading the whole file, retyping it with the edit folded in, and writing the
full result back via `windows-mcp:FileSystem`. That reliably lands on disk
(Durable signal, above, still applies), but landing intact is not the same
question as landing IDENTICAL to the original outside the intended change —
and that second question was never being checked. Flagged live by Tony,
2026-08-19, P_400 session — not from a confirmed corruption incident, unlike
every other rule in this file. This is a preventive rule, on a risk Tony
identified before it produced a visible failure, not a root-caused one.

**Default for an existing file: a genuine targeted replace, not a full
rewrite.**
```powershell
$path = 'C:\...\target_file.ext'
$old  = 'exact old text, single-quoted to avoid backtick/escape corruption'
$new  = 'exact new text, same rule'
$content = Get-Content $path -Raw
$hits = ([regex]::Matches($content, [regex]::Escape($old))).Count
if ($hits -ne 1) {
    Write-Output "ABORT: expected exactly 1 occurrence of `$old, found $hits -- not writing"
} else {
    $updated = $content.Replace($old, $new)
    Set-Content -Path $path -Value $updated -NoNewline
    Write-Output "OK: replaced 1 occurrence"
}
```
Use `.Replace()` (literal), not `-replace` (regex) — avoids an entire class of
regex-metacharacter escaping mistakes for content that's usually code or prose,
not a pattern. The occurrence-count guard before writing extends v1.5's
existing "count structural invariants before/after" principle to the write
itself, rather than only checking after the fact.

**When a full read-and-rewrite is still the right call** (multi-project WO
files with several non-contiguous edited sections in one pass, a near-total
restructure, or content where `$old` can't be pinned to a single unique exact
string): it's still permitted, but requires an explicit diff-style check
before reporting success — not the spot-checks (byte count, grep for one new
marker) used up to this session. At minimum: capture line count and a hash
before AND after, and for anything Tony would treat as high-stakes (a WO, a
skill file, a vault record affecting a live position), read back a section
that was NOT supposed to change and confirm it's untouched, not just that the
new section is present.

**Both paths still end at Durable signal** (Test-Path + Length/line-count)
before reporting success to Tony — this rule adds a correctness check on TOP
of that, it doesn't replace it.

### Rule — targeted edits to existing files (v1.5, string-replacement risk)
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
- v1.11 (9/4/26, P_000 session): two Content integrity findings added
  together (same-version-bump precedent as v1.4). (1) Backtick-as-
  escape-character corruption -- PowerShell interprets `t`/`n`/`r`
  after a backtick as control characters inside double-quoted strings
  and @" "@ here-strings, silently destroying markdown code-span
  formatting with no error. Observed twice in one session (WO-P000-
  E20.001 doc edits). Remedy: single-quoted strings/@' '@ here-strings
  for any content with literal backticks. (2) A cross-project claim
  ("P_300 uses the same wrapper/timeout") was stated to the operator
  based on an architecture docs shared-infrastructure description,
  without reading the other projects actual code -- wrong, corrected
  only after operator pushback. Remedy: grep/read the actual caller
  before asserting what code path it uses, never infer from a shared-
  infrastructure description alone.
- v1.10 (8/30/26, P_010 session): closed the retry loophole in Durable
  signal above -- "if ping is fast, retry fresh" read as license for a second
  attempt at the actual work call, contradicting this skill's own header
  ("hand off ... instead of retrying"). Root cause: a P_010 session hit a
  stalled python.exe call, pinged (fast), then retried the real call two
  more times (3 total attempts, ~10 min) before handing off -- flagged
  live by Tony ("this trip took 10 min which unacceptable"). New rule: a
  confirmed-fast ping proves the relay is up, not that the work call will
  succeed on a second try -- hand off immediately, zero retries of the
  actual work call, full stop.
- v1.9 (8/29/26, P_000 session): added Content integrity finding -- Unicode
  punctuation (em-dash, arrow) typed directly into a .ps1 anchor string can
  silently fail to match against the same content read via
  [System.IO.File]::ReadAllText(), 0 occurrences, no error. Root-caused via
  live occurrence-count probe (ASCII-stripped anchor matched, original
  didn't) during WO-P000-E4.002/E19.001 doc edits. Remedy: ASCII-only
  anchors + IndexOf/Substring splicing; build special characters from
  [char] codes only when they must appear in replacement text.
- v1.8 (8/19/26, P_400 session): added "Rule — editing an EXISTING file",
  distinguishing it from the generated-files rule above it. Root cause:
  `str_replace` confirmed failing on Windows paths this session
  (WO-P020-E1.010.md edit, "File not found"), and the full-file
  read-and-rewrite used instead was never being checked for accidental drift
  outside the intended edit — only that the intended change landed. Flagged
  by Tony before any confirmed corruption, not after one; recorded honestly
  as a preventive rule rather than backfilling a fake incident to match this
  file's usual evidence-based format. New default: literal `.Replace()` with
  a before-write occurrence-count guard for existing files; full rewrite
  permitted only with an explicit diff-style check, not a spot-check.
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
