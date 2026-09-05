# P_300 Lessons Log

**File:** `tasks/lessons.md`
**Status:** Live working document
**Last Updated:** 2026-08-31 (M-119). Full per-session update history moved to tasks/lessons_archive.md, fourth pass.
**Maintained By:** Anthony Zoppi + Claude (architect)

---

## Purpose & Relationship to Other Files

This file is the **live working lessons doc** for P_300. It stages lessons before they are structurally embedded.

| File | Role |
| :---- | :---- |
| `docs/P_300_System_Architecture_v2.7.md` §6 (EC Log) | Permanent archive of *structurally embedded* lessons (encoded in schema, SKILL, or code) |
| `tasks/lessons.md` (this file) | Live working lessons -- staging area; methodology rules; recent corrections not yet promoted |
| `.claude/skills/p300-project-context/SKILL.md` | Concise auto-loaded protection rules; populated from promoted lessons |

**Promotion path:** New correction -> `tasks/lessons.md` -> applied immediately for current chat -> when generalizes, promoted to EC log + encoded structurally in SKILL/code/schema.

This file is loaded at session start by the SIP per the INIT protocol.

---

## Working-State Doc Retention (WO-P000-E8.001)

This file is capped at ~40 live entries / ~70KB. When it crosses that,
the oldest / most-settled entries move to tasks/lessons_archive.md
(full text preserved, nothing deleted), and verbose retained entries get
a compression pass (prose tightened, no rule/path/number removed --
same standard as the SIP's own compression passes). First pass:
2026-07-22, 37 entries archived. Second pass: 2026-07-26, 28 more
entries archived + a compression pass on the ~10 heaviest retained
entries -- file dropped 138.4KB/1,392 lines -> ~63KB. See
tasks/lessons_archive.md for the removed entries and WO-P000-E8.001 for
the retention standard.

Third pass: 2026-08-29 -- 23 Section 1 entries archived oldest-first, skipping IDs still referenced in SKILL/SIP/CLAUDE.md (M-015); Last-Updated history line moved to the archive. Script: verify\run_this_P300_20260829_104500.py.

Fourth pass: 2026-08-31 -- 8 more Section 1 entries (M-042/043/044/045/046/047/048/051) archived oldest-first, same cross-check (M-015/M-054/M-109 kept, still referenced in CLAUDE.md). Same session also fixed a duplicate ID -- M-111 had been assigned to two unrelated lessons; the newer one (headless OAuth token refresh, 2026-08-19) renamed to M-118, its one cross-reference in M-113 updated to match, M-112's reference to the other M-111 verified untouched. Script: verify\run_this_P300_20260831_081556.py.

---
## Section 1 -- Session Methodology Rules (Active)

### M-111 -- A WO's Status header is a claim about its own body, not a substitute for reading it
**Rule:** A work order's `**Status:**` line can go stale independently of the body beneath it -- the body can accumulate real, verified evidence (PEH steps, real production runs, closed follow-ups) while the header line is simply never touched. Reading only the header and reporting it as current status is a distinct failure from M-054 (a *closure note in tasks/*.md* is a claim, not evidence) -- this is the WO document's own internal header/body contradiction, and it can make Claude confidently report an ACTIVE WO as unverified when it's actually done, not just report a DONE WO as active. Caught 2026-08-12: WO-P300-E4.006's header read "BUILT, NOT YET PEH-VERIFIED" while its own body documented four PASSED PEH steps, a real production migration, and a closed byte-identity regression, all dated 2026-07-19/21 -- three weeks of drift, propagated into an INIT summary and a downstream WO's (E5.008) false blocker before Tony's own pushback triggered a full re-read. **Prevention: for any WO whose Status is being reported, quoted, or relied on for a downstream decision (blocking another WO, an INIT summary, a work-order-governance display), read the full body -- not just the header -- before stating status as fact. A header/body mismatch is itself worth surfacing, not silently resolved toward whichever one seems more current.**

### M-089 -- `db_utils.get_latest_catalog()` returns a plain `str`, not a `Path`
**Rule:** Other callers rely on the plain-`str` return for direct
`sqlite3.connect(f"file:{path}...")` use -- wrap in `Path()` before calling
any `Path`-only method (`.stat()`, `.name`) on it. Caught 2026-07-13 in a
diagnostic script; script-local bug, not a `db_utils.py` defect.

### M-015 -- Live filesystem MCP reads override project attachments for `tasks/*.md`
**Rule:** When INIT loads `tasks/lessons.md` and `tasks/todo.md`, ALWAYS read via filesystem MCP (`filesystem:read_text_file`), NEVER trust project-attached versions. Attachments lag disk. (Identified 2026-05-15.)

## Section 2 -- Operational Lessons Specific to P_300 (Not Yet in EC Log)

### O-001 -- Pattern file bar overage
**Lesson:** VP exported files may contain 1-2 extra bars beyond nominal pattern length. This is a VP export artifact, not corruption. `pattern_instances.window_length` = actual bar count. Never truncate.

### O-004 -- Empty DB is not a clean baseline for current schema
**Lesson:** `empty__catalog.db` uses the original Perplexity 7-table schema. Archival only -- not a restore point.

### O-005 -- Skill scatter across 5+ locations is a known issue
**Lesson:** P_300 SKILL at `.claude/skills/p300-project-context/SKILL.md`. Consolidation is future work.

### O-006 -- VP History Grid XLSX uses merged top-row headers
**Lesson:** openpyxl returns the merge value only at the first cell of each group; continuation cells return `None`. Sub-header row has two format variants (abbreviated vs full Triple Cross names). Existing parser handles both. (Captured 2026-05-14.)

### O-009 -- Symbol case in pattern filenames must be strictly uppercase
**Lesson:** The filename validator in `vp_xlsx_reader.py` enforces `Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx` with uppercase SYMBOL. A single lowercase character (e.g. `RCl` instead of `RCL`) causes an immediate ValueError, catalog unchanged, file not deleted -- it stays in `data\historical_patterns\` requiring a manual rename before re-run. Caught twice (2026-06-16 RCl). Before running AddPattern.bat, visually confirm every filename has an uppercase symbol. Windows Explorer does not flag case mismatches.

**Fix when it happens:** `Rename-Item "...\Pattern_YYYYMMDD_YYYYMMDD_RCl.xlsx" "Pattern_YYYYMMDD_YYYYMMDD_RCL.xlsx"` then re-run the bat.

(Captured 2026-06-16)

### O-008 -- VantagePoint .ptf portfolio file is XML; symbol list parseable programmatically (2026-05-21)
**Lesson:** `.ptf` files are XML. Symbol list accessible via `xml.etree.ElementTree`. P_300_WatchList_May2026.ptf yielded 5 symbols in under 1 second. Future: read .ptf -> extract symbols -> drive Pipeline B eval runs. Candidate for P_800 integration.

---

## Section 3 -- Anti-Patterns Reminder (Quick Reference)

- **Never** `df.tail(N)` or `df.head(N)` truncation in converter or ingest layer
- **Never** write TEXT into an INTEGER FK column
- **Never** raw dollar values in cross-symbol similarity matching (use normalized columns)
- **Never** mock data dictionaries in production decision engines
- **Never** hardcoded paths outside `config.py`
- **Never** mix layers (domain doing I/O, infrastructure making business decisions)
- **Never** merge Pipeline A and Pipeline B into a single script
- **Never** put LLM-generated output in the BUY/WATCH/PASS decision path
- **Never** write directly to the master DB -- Lock + Temp-DB + Atomic Move only
- **Never** name a module after a Python stdlib module (M-018)
- **Never** emit Unicode through stdout when invoking from PowerShell -- ASCII only (M-019)
- **Never** treat `forward_labels.return_pct` as a percentage; decimal fraction, x100 at display boundary (M-020)
- **Never** use `SETLOCAL ENABLEDELAYEDEXPANSION` + `!VAR!` in Windows batch files on this system (M-032)
- **Never** issue a `python` command to the operator without first verifying interpreter via `(Get-Command python).Source` (M-035)
- **Never** use 4 x `.parent` from a file in `python/application/` to reach Hub root -- requires 5 x `.parent` (M-036)
- **Never** reach into another project's internals via `sys.path` injection -- always use the Hub interface in `shared_resources/python_utils/` (M-038)
- **Never** use bare `>` redirection for script output -- use `| Out-File -Encoding utf8`; read the file back directly (M-039)
- **Never** hardcode a success string (`[OK]`, `DONE`, `written`, etc.) -- output only after the real call returns without exception (M-051)
- **Never** assume a rejected AddPattern file is self-clearing -- failed ingests leave the source XLSX in `data\historical_patterns\`; it will block every future batch with the same error until deleted or renamed (M-058)
- **Never** assume daily-evaluate fired signals are duplicate-free -- `insert_fired_signal()` has no uniqueness guard; a re-run on an already-fired signal_date stacks a new row every time (M-059)
- **Never** assume a date string's format without checking its actual source column -- this hub mixes YYYYMMDD (filenames) and YYYY-MM-DD (catalog/ledger) conventions; M-060 was a 26-day, 100%-failure-rate silent bug from this exact assumption
- **Never** assume yfinance returns single-level columns for a single ticker -- flatten MultiIndex columns immediately after download (M-061)
- **Never** write an "unfilled" query against the FIRST field a multi-stage fill populates -- check the LAST field, or partial rows get permanently skipped (M-062)
- **Never** trust a clean exit / "0 errors" log as proof of correctness when the actual counter ("Filled 0/142") still reads zero -- a quiet run can hide a silent persist bug just as easily as a crash hides a parse bug (M-064)
- **Never** assume a downstream parser still matches a report/console format after that format changes -- a fixed-column regex fails silently (None, no exception) rather than throwing when a column is added (M-067)
- **Never** trust a --clean batch's silence as proof every emit succeeded (or failed) -- logging.disable(logging.WARNING) spans the whole run and swallows any function reporting only via the logging module; if it doesn't also print(), it's invisible either way (M-068)
- **Never** pass a decimal-fraction stat (mean_return_pct, or anything in M-020's decimal-space convention) into a %-formatted string without the *100 scaling applied at that call site -- each consumer scales independently, there's no single place it happens automatically (M-068)

---

---

## Section 1.6 -- M-054

### M-054 -- A "DONE"/closure note in tasks/*.md is a claim, not evidence; verify the file before trusting it
**Rule:** tasks/todo.md and tasks/lessons.md entries claiming a fix landed (e.g. "M-051 closure") describe what a prior session believed it did, not what the file on disk actually contains. Before relying on such a closure note -- especially before building new work on top of it, or telling the operator a known bug is fixed -- verify directly: read the file's version header/changelog, or grep for the specific pattern the bug involved. A closure note with no verification is not closure.

**Failure mode captured 2026-06-17:** tasks/todo.md and tasks/lessons.md both stated `print_signal_report_clean()`'s hardcoded `[OK] written to vault` / `ARCHIVE OK` strings (M-051) were fixed and confirmed 2026-06-12 via Claude Code. `report_writer.py` was still v1.7 (2026-06-09) with the exact bug verbatim -- no version bump, no changelog entry for any fix. The bug ran live in production for at least 5 days (2026-06-12 through 2026-06-17) undetected, because the tracking doc said it was already handled -- including a literal stale `data/processed/2026-05.zip` path in the fabricated archive line, and a false `[OK] {ticker} written to vault` claim for PASS-classified signals (CRML, NNE) that never get a real vault write at all. Caught only because the operator uploaded a live DailyEval console log and it was read line-by-line against the actual pipeline code, rather than trusted on the strength of the prior closure note.

**Pairs with:** M-040 (test execution paths, not just imports -- the same discipline applies one level up: verify a CLAIMED fix, not just a NEW one).

(Captured 2026-06-17)

### M-055 -- INIT must never call python via windows-mcp:PowerShell; read a pre-generated status file instead
**Rule:** Any INIT step that previously needed live Python output (catalog-summary, LM Studio check) must be redesigned as: (1) an operator-run `.bat` writes a status JSON outside the chat session, (2) INIT reads that JSON via `windows-mcp:FileSystem`. INIT itself never invokes `python` via `windows-mcp:PowerShell` for these steps -- not even via `python script.py`. M-030 already banned `python -c`; this extends the same prohibition to script invocation specifically on the INIT path, where the ~4-min subprocess ceiling has now been confirmed twice in this file alone as a recurring failure (2026-06-10/11 entries), not an edge case.

**Why now (2026-06-18):** SIP Steps 5b/5c had quietly encoded an assumption -- that a live subprocess call during INIT was acceptable -- that the rest of this Hub already knew was false (M-030, peh-handoff SKILL, the 2026-06-10/11 "count unverified due to PowerShell MCP timeout" entries in todo.md). The fix (WO-P000-E4.001) generalizes beyond P_300: any project's INIT step needing Python output should use the same operator-run-bat-plus-status-file pattern, not a live call.

**Pairs with:** M-030 (`python -c` hangs reliably), M-039 (pipe multi-line output to a file, read it back -- same instinct, different mechanism: a status file replaces the live call entirely rather than just fixing the encoding of its output).

(Captured 2026-06-18)

### M-056 -- A clipboard paste can silently overwrite a production launcher; verify file integrity, don't trust a stray error block

**Rule:** Operator-facing `.bat`/`.ps1` launchers are vulnerable to an editor-window mixup: copying console text intending to paste it elsewhere (e.g. into chat) but the target window is actually the launcher file open in an editor, overwriting the real script with a fragment of console text. When the operator reports a script "acted weird" or produced unexpected console messages and says they ignored them, do not assume the script is intact -- check the file's size/mtime/content directly before re-running or debugging the logic. A script behaving strangely is a cheaper signal to check file integrity than to debug application logic.

**Failure mode captured 2026-06-23:** `P_300_AddPattern.bat` (real script, last legitimate edit 2026-05-21) was reduced to 101 bytes containing a single stray line of PowerShell console text (`XLSX    : PS C:\Users\Trader\...`). Caused by Tony copying a filename/path intending to paste it into chat, with the `.bat` file actually focused in an editor at the time -- the paste (and save) landed there instead. Tony noticed the resulting console messages looked wrong and closed/ignored them rather than investigating, then flagged the file size next session. No on-disk backup or VS Code local history existed to recover the literal original; the file had to be reconstructed from `cli.py`'s real subcommands plus a console transcript of a prior run, then verified end-to-end on a real ingest (TSLA, pattern_instance_id=320) before being trusted as a faithful rebuild.

**Operator-side habit to flag when relevant:** if a launcher prints something unrecognized or malformed immediately on open, stop and check the file before closing the window -- closing/ignoring an error is what let this go undetected until the next session.

**Pairs with:** M-054 (a closure note is a claim, not evidence -- same root instinct: verify the actual file/state rather than trusting that things are as expected).

(Captured 2026-06-23)

### M-057 -- windows-mcp Python calls have a hard ~4-min ceiling; a near-the-line job still completes server-side after the client gives up -- check outputs before assuming failure

**Rule:** `windows-mcp:PowerShell` enforces a system-level ~4-minute ceiling on any single call, independent of any script-internal timeout param passed. This is NOT the same failure mode as M-030 (`python -c` hangs, never completes) -- a job that runs slightly past ~4 min (e.g. 4:30-4:40) DOES finish successfully server-side; the client just cancels a few seconds before completion. Before assuming a timed-out python call failed or needs a re-run, check whether its expected output actually landed.

**Failure mode captured 2026-06-28:** Two `run_eval_loop.py` invocations (331 patterns x 5 horizons, ~4:30-4:40 actual runtime) via `windows-mcp:PowerShell` both timed out client-side at ~4 min. Checking `outputs\reports\eval\` afterward showed BOTH had written complete, valid reports 37-40 seconds after the client gave up. No re-run needed -- the existing output was read and used directly.

**Correct response to a windows-mcp Python timeout:**
1. Do not assume the job failed or is wedged.
2. Check the expected output location via `windows-mcp:FileSystem` first.
3. Fall back to PEH handoff only if the output genuinely isn't there, or pre-emptively for any job expected to run near/past ~4 min (known in advance from catalog size).
4. Never retry the same call directly -- it won't run faster the second time.

**Distinction from M-030/M-055:** those describe calls that may never finish. This describes a clean, correctly-working script that simply outruns an external ceiling unrelated to its own logic -- a different root cause, same "don't call python directly via windows-mcp:PowerShell for anything non-trivial" conclusion.

(Captured 2026-06-28)

### M-058 -- A failed AddPattern ingest leaves the source file in place; same filename will block every subsequent run until the operator removes it

**Rule:** When `add-pattern` rejects a file as already-ingested (`source_file_id` collision) or for any other validation failure, the catalog is untouched by design (M-024/M-025 family) -- but the source XLSX is also left untouched in `data\historical_patterns\`, since only successful ingests get archived/deleted (Step 2 never runs on failure). A duplicate filename will throw the identical error on every future AddPattern batch until an operator explicitly deletes or renames the file. Before re-running a batch that previously had a rejection, confirm the rejected file is gone or corrected -- don't assume the failure was self-clearing.

**Failure mode captured 2026-06-28:** `Pattern_20260109_20260203_DOCU.xlsx` rejected mid-batch (`source_file_id=277` already existed -- a true duplicate, distinct from the M-053 case where DOCU needed re-capture with more history). 31/32 other files in the same batch ingested clean; catalog reconciled at 362 patterns / 245 symbols, 0 hollow, HEALTHY. File confirmed still present in `data\historical_patterns\` post-run; operator verified it was a genuine duplicate and deleted it (folder confirmed empty after).

**Pairs with:** O-009 (same failed-ingest-leaves-file-in-place mechanic, different root cause -- case mismatch there, true duplicate here).

(Captured 2026-06-28)

### M-063 -- ledger_fill.py's fetch window (+25 calendar days) could never reach the h20 horizon regardless of elapsed time

**Rule:** Calendar days and trading days are not interchangeable at the comment-author's assumed ratio. 25 calendar days yields ~17-18 trading days (5/7 ratio), but h20 needs `history[20]`, i.e. at least 21 trading days of data. The window was structurally incapable of ever reaching h20 -- not a timing issue, a math error in the original implementation. Fixed to +35 calendar days (~25 trading days, comfortable margin past 21 even with US holidays in the window). When computing a fetch/lookback window from a trading-day target, multiply by ~7/5 and add a holiday buffer -- never assume calendar days ≈ trading days.

### M-066 -- "N trading days have elapsed" claims must be computed against the actual calendar (holidays included), not estimated; a held-as-fact note can be wrong the same way a closure note can

**Rule:** A statement that a signal "hit its Nth trading day" on a specific date is a calculation, not an observation -- it must be derived by counting actual trading days (weekdays minus US market holidays) from the real signal_date, not estimated by eye. The same discipline M-054 requires for closure notes (verify, don't trust) applies to date-math claims embedded in lesson/todo entries.

**Failure mode captured 2026-06-30:** The 2026-06-29 M-064 capture stated DE/COHR (signal_date 2026-06-02) "hit their 20th trading day on 06-29." Recount: Jun 2 -> Jun 30 spans 21 weekdays, but Juneteenth (Jun 19, 2026, a Friday) is a federal market holiday -- 20 actual trading days through Jun 30, and Jun 30 itself hadn't closed at the time ledger-fill was run (15:53 ET). Real count: 19 completed sessions past the anchor close, h20 needs 20 sessions past anchor (21 total data points, index 0-20) -- short by ~2 sessions. `cli.py ledger-fill` run 2026-06-30 correctly returned `Filled 0 / 154` -- the code (M-060/061/063/064 fixes) is NOT broken; the prior day-count claim was. Expected real availability: after 2026-07-01 close, assuming no further holidays.

**Pairs with:** M-063 (calendar days != trading days, same confusion previously caught in code; this is the same error recurring in a human/session note instead).

(Captured 2026-06-30)

---

## Section 5 -- Stage Methodology Notes

### S-001 -- Decision before draft
Each new stage opens with a planning conversation, not a draft. Architecture decisions get locked first.

### S-002 -- Fork-in-the-road questions get a recommendation, not a menu
When the AI surfaces a choice, it always recommends one with rationale. The operator may override but never has to choose blind.

### S-003 -- Stage transition requires document update
At the end of each stage, the architecture doc Change Log gets a new entry. The Stage roadmap in §7 gets updated. The SKILL gets reviewed. New lessons get promoted from this file to the EC log where structurally embedded.

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** Any new methodology rule, operational lesson, or correction during a session
- **Promotion review:** End of each stage, lessons in Sections 1, 2, 4 reviewed for promotion to EC log

---

**End of P_300 Lessons Log**

### M-075 -- A function that accepts scratch-path overrides for SOME of its I/O but not all of it is a test-isolation trap; every persistent side-effect needs its own override parameter

**Rule:** Before treating any function as safely testable via path overrides, enumerate EVERY persistent side effect it has (every file write, DB write, checkpoint, append) and confirm each has its own override parameter -- not just the ones already exposed. A function is only as test-isolated as its least-overridable side effect.

**Trigger (2026-07-08):** `run_bulk_extraction()` accepted `master_db`/`temp_db` overrides but had NO parameter for the checkpoint file path -- always read/wrote the real `BULK_CHECKPOINT_FILE`. A test run (itself triggering the real M-074 bug) wrote a real file into the LIVE checkpoint as "completed" with 0 detections. Every subsequent test run -- including after the M-074 fix -- silently skipped the file, looking exactly like "the sweep found nothing" rather than the real bug.

**Fix:** Added `checkpoint_path: Path = BULK_CHECKPOINT_FILE` as a fourth parameter, threaded through the load/save helpers (both changed from optional-default to required-positional internally). Docstring now states explicitly: overriding master_db/temp_db without also overriding checkpoint_path risks live-checkpoint pollution.

**Pairs with:** M-017, M-054, M-080 (same root cause recurred, different WO: reports_dir there, checkpoint_path here).

(Captured 2026-07-08)
### M-079 -- A mechanically-detected pattern is not a curated pattern; corpus composition is a calibrated input, not just data volume

**Date:** 2026-07-10
**Trigger:** WO-P300-E2.003 staging merge of 495 STRICT bulk patterns into the 508-pattern live analog pool dropped walk-forward BUY win rate 68.8% -> 63.6% while nearly doubling BUY volume (157 -> 316). Promotion correctly withheld -- the staging-eval-before-promote gate (decision 2) did exactly its job. CIEN head-to-head then explained WHY: manual and STRICT detection have EQUAL precision (80%/80% into >=15% risers on real data) but catch DIFFERENT phases -- the detector fires at crossover ignition (condition 1), Tony's picks are mid-trend continuation entries (condition 1 failed on all 5 of his picks, including all 4 winners). Merging them into one analog pool mixes two different setup populations under thresholds (M-034) calibrated for only one of them.

**Generalized rules:**
1. Never merge a mechanically-detected corpus into a human-curated analog pool without a staging-copy eval comparison first -- and treat the comparison as the decision, not a formality. Detection-rule conformance is a proxy for setup quality, not the thing itself.
2. When two signal sources have equal precision but different coverage, the right integration is usually a FUNNEL (breadth source feeds the precision gate) not a UNION (both dumped into one pool). Scanner -> eyeball -> catalog preserves both edges; merge destroys the curation edge.
3. A validation gate that fires (blocks a promotion) is a success, not a failure -- log the numbers that fired it, don't work around it.

**Pairs with:** M-034 (threshold calibration is corpus-specific), WO-P300-E2.001's original merge deferral (the isolation that made this test possible), WO-P300-E2.003 closure state (bridge built, verified, parked).

(Captured 2026-07-10)


### M-085 -- A resolution heuristic's negative result ("couldn't find a match") gets silently trusted as ground truth unless exhaustively checked against a wider search

**Rule:** A heuristic that returns "no match" reads the same whether the answer is genuinely absent or just outside its search radius -- only a materially wider search (or manual check) can tell the two apart. When a "no match found" bucket is large enough to meaningfully change a headline number if wrong, spot-check it against a wider search before trusting it as ground truth.

**Trigger (2026-07-13):** WO-P300-E3.002 ground-truth validation. `resolve_pick()` tried 4 combinations per pick (direction x {nearest bar, idx-1, idx+1}); non-matches got filed OUTCOME-INVALID across multiple validation rounds as settled. A session-close spot-check widened to both directions across idx-2..idx+2 (10 checks) on a 17-symbol sample: only 3 (AME/PCAR/SHW) held up as genuinely invalid -- 14/17 qualify somewhere the narrower search never looked. Additional finding: several of the 14 (AMZN, GOOGL, CIEN, SPY) qualify under a DIFFERENT class than their recorded inferred direction -- mtdiff-sign direction inference at the exact pick bar may be noisy/transitional. Not root-caused.

**Status:** Open -- next session: widen `resolve_pick` to the full exhaustive search and re-run the 84-anchor validation. If the 14/17 ratio holds across the full 24-pick bucket, true HITS is likely ~78-80/84 (93%+), not 60/84 (71.4%).

**Pairs with:** M-084.

(Captured 2026-07-13)
## M-094 -- atomic_move's own backup is single-level, overwrites every promote (no built-in deep history)

**Status:** Noted, not yet resolved -- Tony's call pending on scope.

**What happened (2026-07-14):** Before the first real WO-P300-E3.002 production batch (5,584 mined candidates), Tony asked for a catalog backup, framing it as "should be built in." `atomic_move()`'s docstring confirms it renames the current master to `<master>.bak`, explicitly "overwriting any previous backup" -- confirmed via `models/` listing, every dated catalog has exactly one `.bak`, never a rolling history. A second promote after a large batch would overwrite the only recovery point before any issue surfaces.

**Interim fix:** explicit manual backup to `models/archive/databases/pre_mine_batch_071026catalog_20260714.db` (verified byte-identical via `mode=info`), using the pre-existing archive-snapshot convention.

**Open question, Tony's call:** should a pre-promote snapshot to `models/archive/databases/` become automatic inside `promote_staging_to_live()` (size-threshold or unconditional)? Not decided.

(Captured 2026-07-14)
## M-103 -- PowerShell here-string quoting silently corrupts markdown backticks and drops trailing newlines

**Trigger:** Wrote a todo.md log entry containing markdown code-ticks (e.g. `` `run_incremental_post_batch` ``) via a PowerShell double-quoted here-string (`@"..."@`). PowerShell interpreted backtick+letter as an escape sequence (`` `r `` = carriage return, `` `n `` = newline) instead of literal backtick + text, splitting `` `run_incremental_post_batch` `` into a stray CR mid-word and silently eating the identifier's leading characters. No error, no warning -- the write succeeded and reported a byte count, but the content was wrong. Caught by re-reading the file back, not by the write itself.

**Second bug, same fix attempt:** Switched to a single-quoted here-string (`@'...'@`, which treats backtick literally) and the identifiers came out correct, but the line immediately before the closing `'@` lost its trailing newline -- PowerShell here-string syntax excludes the final line break before the terminator. This merged a `---` separator directly into the next entry's `**>>>` header with no line break.

**Fix:** For any file write containing literal backticks, use a single-quoted here-string (`@'...'@`), never double-quoted. Always leave a deliberate blank line (empty line) before the closing `'@` when the content must end in a newline, since the line directly preceding the terminator gets its own trailing newline stripped. Always re-read the written region back before trusting the write (ties to M-051 -- no `[OK]` without a real verifying read).

**Applies to:** Any windows-mcp:PowerShell write of markdown/code content containing backticks -- todo.md, lessons.md, WO files, or any Python/config file edited via inline PowerShell rather than `windows-mcp:FileSystem` mode=write with `content` passed as a parameter (which does not go through PowerShell string-escape parsing at all and is the safer default for content with backticks).

(Captured 2026-07-18)

---

## M-105 -- A WO's claimed permanent test file is a claim, not evidence -- two instances found missing from disk in one session, both caught only by independent re-verification

**Rule:** A WO/lessons.md entry stating a permanent test file was built (with a line count and "N/N PASS") describes what the writing session believed, not a guarantee the file landed on disk -- M-054's rule applied to test-file existence specifically. When reviewing a prior WO's claimed deliverables, run (or at minimum filename-search) the actual file before treating its coverage as real. A `__pycache__` listing is a cheap secondary signal -- a `.pyc` for every sibling test file but none for the claimed one is a strong tell.

**Trigger (2026-07-20/21):** Two instances, same session, both caught by an independent-review chat: (1) WO-P300-E4.005 claimed `tests/test_similarity.py` (113 lines, 7/7 PASS) -- zero matches anywhere, no `__pycache__` trace. (2) M-095's own entry claimed `tests/test_get_latest_catalog_path_safety.py` -- same result, absent. Both rebuilt from scratch same night, both real and verified passing (7/7 and matching checks, real PEH via Claude Code Desktop). The underlying correctness claims (JIT byte-identity, the dedup fix) were independently true and separately evidenced -- only the permanent-test-file ARTIFACT was missing, twice.

**Applies to:** Any independent-review session evaluating a prior WO's stated deliverables -- test files, migrations, reports.

(Captured 2026-07-20/21, filed after Tony's explicit "yes make entry.")
## M-106 -- Bulk pattern-mining exports land in data\bulk\mine\, not data\historical_patterns\

**Rule:** `data\historical_patterns\` is the single-pattern AddPattern drop folder (Pipeline A, `add_pattern_pipeline.py`). The bulk pattern-mining path (mine-patterns -> ingest-mined, used for pre-export-checked multi-symbol batches) reads from `DATA_BULK_MINE` (`config.py`, = `data\bulk\mine\`). These are two different pipelines with two different drop folders -- VP pattern exports for a bulk batch go in `data\bulk\mine\`, never `data\historical_patterns\`.

**Trigger:** Tony corrected a session instruction that told him to drop the 16-symbol pre-export-checked batch's pattern files in `data\historical_patterns\` -- wrong folder for this pipeline. Confirmed against the real `config.py` constant (`DATA_BULK_MINE: Path = DATA_BULK / "mine"`, `DATA_BULK = DATA_DIR / "bulk"`) and the real directory (`data\bulk\mine\` exists on disk; `data\historical_patterns\` is Pipeline A's folder, unrelated to this batch).

**Fix:** Before naming a drop folder for a pattern-export batch, check which pipeline the batch is going through (single-pattern AddPattern vs. bulk mine-patterns) and grep `config.py` for the actual constant rather than assuming from a prior single-pattern-flow habit.

**Applies to:** Any session directing Tony to export/drop VP pattern files for a bulk (multi-symbol, pre-checked) batch.

(Captured 2026-07-21, Tony's direct correction.)


---

## M-109 -- A file's absence from memory/context is not evidence it doesn't exist on disk -- check before writing to any path claimed as "new"

**Rule:** Before writing to any file path as if creating it fresh, run `windows-mcp:FileSystem mode=info` first. Absence from Claude's own context (memory, this session's reads, a WO's file plan) is not evidence the file doesn't exist on the real machine -- it only proves Claude hasn't seen it yet (M-015's principle applies with equal force to "no attachment mentioned it").

**Trigger (2026-07-22):** WO-P000-E8.001 pilot -- wrote a fresh `CLAUDE.md` for P_300 root, reasoning from an earlier audit that checked other projects but never P_300 itself. Wrote via `mode=write, overwrite=true` without a prior `mode=info` check. A follow-up `mode=info` (routine mtime confirmation) showed `Created: 2026-06-18` -- a real, actively-maintained file had been silently overwritten. `overwrite=true` succeeds identically whether creating or clobbering.

**Recovery:** No `.bak`, no VS Code local history. Hub root is a git repo -- `git log --oneline -- <path>` (run by Tony directly, since `git log` hangs through the MCP relay, same family as M-030/M-076) found one commit; `git show <commit>:<path>` recovered the content. First copy-paste round mixed in unrelated scrollback (M-056's family); redirecting straight to a file and reading it back avoided a second lossy paste. Recovered content also carried pipe encoding corruption (M-019's family) -- restored using the project's ASCII convention.

**Fix:** `mode=info` before any `mode=write` to a path not already confirmed present-and-current this session -- not just for edits (M-015 covers those), but for any write framed as "creating" something.

**Pairs with:** M-015, M-054, M-056, M-019.

(Captured 2026-07-22, Claude's own mistake, self-caught via the mtime-verification habit M-054 already established.)
## M-110 -- Multi-segment PowerShell array assembly: verify the FULL result before Set-Content, every time, not just the pieces you remember editing

**Rule:** When building a file edit out of multiple array segments (`$before + $new + $after`), the failure mode is never in the individual pieces -- it's in the ASSEMBLY. After any multi-segment assembly and `Set-Content`, do a full re-read of the affected region (not just boundary lines): `ast.parse()` (catches truncation/syntax breaks), then an actual import (catches undefined names), then a real execution for logic changes (catches structurally-valid-but-wrong code, which nothing short of running it reliably catches).

**Trigger (2026-07-23):** Three real, distinct mistakes in one PowerShell session on `ingest_mined_pipeline.py`: (1) `$result` written before all segments were appended, silently truncating everything after the last-appended piece; (2) an array element modified in place (`$lines[51] = ...`) then `$before`/`$after` built from ranges excluding that index, silently dropping the edit; (3) two new pieces (a function def and a call meant for a different function) assembled in the wrong relative order -- syntactically valid but structurally wrong (a call nested inside its own function's body instead of `main()`; `main()` lost its `return 0`).

None of the three were caught by boundary-line verification prints -- all confirmed the edges of referenced segments, not completeness or order. `ast.parse()` didn't catch #3 either (nested-wrong code is still syntactically valid).

**Pairs with:** M-109 (check before write), M-054 (a claim -- "the boundaries look right" -- is not evidence the whole thing is right).

(Captured 2026-07-23, three of Claude's own mistakes in one session, all self-caught.)

## M-118 -- M-097's "persists indefinitely" theory was wrong; headless Claude Code OAuth tokens do not reliably refresh

**Rule:** `claude -p` (headless/non-interactive) does NOT share the same reliable auto-refresh behavior as an interactive session. Per Anthropic's own Claude Code CLI issue tracker (multiple confirmed reports: anthropics/claude-code #28827, #50743, #79685, #80091), the OAuth access token has a short TTL (~8 hours) and is not reliably refreshed when the CLI is invoked headlessly, while a concurrent interactive session on the same machine keeps working. A script that calls `claude -p ... --chrome` roughly once a day should be expected to hit a 401 on a routine basis, not treated as rare. M-097's "a login persists indefinitely under normal use, so this was a one-time bootstrap gap" was reasoned from Anthropic's docs on LOGIN expiry (the multi-day/long-lived kind, code.claude.com/docs/en/authentication's 3-day warning) -- a separate, longer-lived mechanism from the short-lived ACCESS TOKEN refresh problem specific to headless mode. Two different expiry mechanisms were conflated.

**Trigger:** Real recurrences on 2026-08-12 and 2026-08-19 (a third, 2026-08-18, per Tony directly -- undocumented in todo.md, matching the exact recording-gap risk M-097 itself warns about). Three occurrences in five weeks, the last two on consecutive days, directly contradicts "very likely a one-time gap."

**Fix:** Not built this session. Two real candidate directions surfaced, neither yet tested: (1) route the Chaikin batch through Tony's already-running interactive Claude Code session (`--continue`/`--resume`) instead of an independent `-p` spawn, since interactive sessions don't hit this bug; (2) `claude setup-token` issues a long-lived (1-year) credential, but per code.claude.com/docs/en/authentication it "can only make model requests, so it can't establish Remote Control sessions" -- unconfirmed whether `--chrome` browsing counts as a Remote Control session, which would rule this option out for this specific use case. This entry corrects M-097's root-cause claim only; M-097's actual fix (the `claude auth status --text` pre-flight guard, loud-not-silent) remains valid and unaffected.

**Pairs with:** M-097 (corrects its stated root cause, not its shipped fix), WO-P300-E4.009 (loud-detection WO this failure mode keeps exercising).

(Captured 2026-08-19, Claude's own correction of a prior session's theory, prompted by Tony asking for root cause on a recurrence.)








## M-112 -- A WO's "WHAT WAS BUILT" section can go stale even when the WO itself is never touched -- a LATER, unrelated WO can quietly retire the code it describes

**Rule:** M-111 documents drift in a WO's own Status header. This is a different failure: WO-P300-E4.009's Status header was never wrong, but its "WHAT WAS BUILT" section (Tee-Object capture + failure-phrase match + red banner + $LOG line, built into P_300_RunAllDailyEvals.ps1's inline Chaikin chain) stopped describing real production code on 2026-08-12, when WO-P800-E4.001's schema-driven migration replaced that inline chain with a call to Hub-root RunChaikinBatch.ps1 -- a script with no output capture, no phrase matching, no banner, and no log file at all. Nobody cross-checked E4.009 against the code WO-P800-E4.001 was replacing, because E4.009 wasn't the WO being worked. A WO can be 100% internally consistent (header matches body) and still be entirely wrong about what code currently exists, if a later WO in a different project changes the ground under it.

**Trigger:** 2026-08-21, first real Chaikin batch failure since the migration (0/8 notes updated, WebFetch-403 fallback instead of a login wall). Went looking for the promised red banner and $LOG entry to confirm E4.009's detection fired -- neither exists in the current code. The failure WAS caught, just by a different, undocumented mechanism (P_300_RunAllDailyEvals.ps1's post-run vault-note check, added by WO-P800-E4.001 for an unrelated reason -- verifying enrichment succeeded, not originally framed as E4.009's replacement).

**Prevention:** When a WO changes a shared call path (a script another WO's "WHAT WAS BUILT" section describes calling into), grep the ledger for other WOs referencing that same script/mechanism before closing -- not just the WOs in Affects:. WO_COMPLETION_GATE.md's Caller Propagation check (ref WO-P115-E2.001) covers callers of a changed function; it doesn't currently cover WOs whose own acceptance criteria describe the code being replaced. Candidate fix, not yet proposed to Tony: extend Caller Propagation's checklist item to include "other WOs describing this code path" as a category to search, not just active call sites.

**Pairs with:** M-111 (header/body drift within one WO), M-054 (live artifact over any document), WO-P300-E4.009, WO-P800-E4.001.

(Captured 2026-08-21, Claude's own finding, prompted by Tony providing real failure-run console output and flagging "not clean.")


## M-113 -- Claude in Chrome "Your approved sites" is a persistent, browser-level grant, not per-conversation -- but two known Anthropic-side bugs can make it misbehave

**Rule:** Once a site shows under the extension's Permissions -> "Your approved sites" with a Revoke button, that's an "always allow" grant that persists across separate sessions/tab groups/conversations until manually revoked -- confirmed live 2026-08-21: Tony approved members.chaikinanalytics.com in his own side panel, and a completely separate MCP tab-group session (this chat) navigated to the same domain immediately after with zero prompt. Not scoped to the approving conversation.

**Known failure modes (Anthropic-side, not ours), if the prompt ever recurs unexpectedly:**
1. anthropics/claude-code#74715 -- "Always allow" sometimes persists as `duration:"once"` instead of `duration:"always"` in the extension's storage; the site never actually lands in the approved list despite the user clicking Always Allow, so the prompt keeps firing every action.
2. anthropics/claude-code#58464 / #57219 -- domain shows correctly under "Your approved sites" (recent Last Used timestamp and all) but `navigate` calls still return "permission_required" / "Navigation to this domain is not allowed" anyway -- a sync gap between the approval store and the navigate permission check.

Neither hit us on 2026-08-21 -- the approval stuck cleanly and navigate worked immediately, no retry needed. Listed here so a future recurrence isn't mistaken for something P_300 broke.

**Accepted workaround (Tony's call, 2026-08-21):** if Chaikin (or any approved site) unexpectedly re-prompts, Tony manually re-approves once -- acceptable as a one-off. Becomes worth real investigation only if it recurs repeatedly (pattern, not a single blip) -- same one-off-vs-repeatable threshold this Hub already applies to the Chaikin OAuth 401 recurrences (M-111).

**Pairs with:** M-118 (headless auth reliability, same "one-off is fine, pattern needs investigation" threshold), WO-P300-E4.009 (this permission model is the foundation of the MCP-driven Chaikin pull that replaced `claude -p --chrome` for today's real batch).

(Captured 2026-08-21, Tony's own policy call after Claude found and explained the two known upstream bugs.)



## M-114 -- "No usable cache, full O(N^2) rescore required" was declared from the JSON fingerprint alone; the eval already existed on disk, and the machinery to rebuild it in minutes had been built a month earlier

**Rule:** Before declaring that a long recompute is required, check ALL THREE places a walk-forward result can live, not just one: (1) `outputs\reports\eval\walkforward_*.txt` -- every promote writes a post-batch report for the full catalog, named after the STAGING db (`walkforward_staging_ingest_mined_*`), which is byte-identical to the live catalog it was promoted to; (2) `topk_cache` on the live catalog -- maintained on every promote via `update_for_new_batch` (new pids scored + all displaced existing pids rechecked, including backfilled anchor dates); (3) only then the JSON cache (`models\eval_cache\`), whose fingerprint is keyed to the PRE-batch catalog and will miss after every promote by design. If (1) is missing, `application\reconstruct_pre_batch.py` (WO-P300-E5.004 Part A, 130s at N=14,812, 25/25 exact vs. real DTW) rebuilds the batch from (2). `run_eval_loop.py` is the cold-path tool for a catalog with no `topk_cache` -- it must never be pointed at the live catalog.

**Trigger:** 2026-08-27/28 session concluded WO-P300-E5.006 step 3 was BLOCKED on a ~214.5h uncached run, built `P_300_RunEvalLoop_KeepAwake.bat`, and planned a checkpoint/resume layer -- all because `read_cached_walk_forward` returned None on the 42,955-fingerprint JSON. Verified 2026-08-29: `walkforward_staging_ingest_mined_default_20260826_130212.txt` already holds all 44,399 patterns x 5 horizons (221,996 lines, last row VYX 2026-07-28 corpus_size 44,396), written by the 08-26 promote (`BulkAddPattern_20260826_111500.log`: "topk_cache populated on staging: 1444 new pids, 42341 existing pids rechecked"). The backfill concern (1,438 of 1,444 new pids with historical anchor dates) is exactly what the recheck loop handles.

**Prevention:** Any "must rescore" conclusion in this project cites the report-folder listing and the live `topk_cache` row count in the same message. The KeepAwake eval wrapper stays on disk but is not run; the checkpoint plan is dropped. A blocker entry in a WO gets the same evidence bar as an acceptance criterion (M-100) -- "no cache" was asserted from one lookup, not three.

**Pairs with:** M-082 (re-deriving instead of re-running proven logic -- E5.004 solved this exact shape), M-100 (premises need evidence), M-054 (live artifact over session memory), WO-P300-E5.004, WO-P300-E5.006.

(Captured 2026-08-29, Claude's own finding after Tony challenged the 214.5h estimate: "we definitely did not build this environment correctly that any process would take this long on 44,000 records.")


## M-115 -- WO ownership field (Owner) is not "whichever project's data the WO touches most" -- Affects lists collaborators, Owner decides who acts

**Rule:** A WO's Owner field is the single project responsible for acting on it; other projects named in Affects are informed or impacted, not co-owners, even when their data matters more to the outcome than the Owner's own project does. Reading a WO's Affects list as shared ownership routes the work to the wrong session type.

**Trigger (2026-08-29):** Summarizing the P_300 INIT session's action queue, WO-P010-E2.001 (Owner: P_010, Affects: P_400/P_300) was described as "sitting with P_010/P_400," implying P_400 shared ownership. Tony corrected: P_010 owns it and it needs a P_010 session; P_400 is named in Affects only because question 2 needs the P_400/P_020 trade ledger for P_300-sourced trades -- that doesn't make it a P_400 task, and nothing on it is owed from P_400 today.

**Fix:** When stating which session type a WO needs, cite Owner alone. Affects explains why other projects are named in the WO body; it is not a routing signal for who acts next.

(Captured 2026-08-29, Tony's direct correction.)


## M-116 -- "I did not find it on file" needs a full-file search, not just the ranges already read this session for an unrelated purpose

**Rule:** Before concluding a fact is undocumented ("not explained anywhere on file", "new finding"), search the ENTIRE relevant file, not just the sections already read earlier in the session for a different task. A partial read establishes coverage of what was read, not of the file.

**Trigger (2026-08-29):** Independent-reviewing WO-P300-E4.009, flagged 2026-08-26_BRK_A's missing Chaikin section as "not explained anywhere on file" and guessed, unconfirmed, that a BRK_A vs BRK.A ticker-format mismatch was breaking the URL. Tony corrected: this was already investigated and documented in tasks/todo.md's 2026-08-27 entry (around line 448), which this session had never read -- INIT read only offset 0-120 and 470-573 of a 595-line file, skipping the middle section that held the answer. The real finding on file is more complete than the guess: BRK_A/BRK_B both fail to resolve on Chaikin under the underscore ticker format from _last_prompt.txt; retried with the period format Chaikin actually uses, BRK.B showed real data (a pure ticker-format bug, fixed by hand each pull) but BRK.A was confirmed genuine no-coverage even with the correct format -- Chaikin does not rate the A-share at all. Verified three separate times (08-27 period-format retry, Tony's own screenshot, 08-28 re-confirmation).

**Fix:** A claim that something is undocumented is itself a claim requiring evidence -- grep or fully read the specific file before asserting absence, not just rely on whatever portions of it happen to have been read earlier in the session for a different task.

(Captured 2026-08-29, Tony's direct correction.)

## M-117 -- windows-mcp:FileSystem mode=write silently converts LF-only files to CRLF; a full-file rewrite must be byte-verified after write, not just line-count-verified

**Trigger (2026-08-29):** Building WO-P300-E5.009, rewrote docs/P_300_System_Initialization_Prompt_v3_1.md (confirmed LF-only before editing) via windows-mcp:FileSystem mode=write, passing content built with plain LF line breaks. Post-write byte scan (done as routine PEH-style verification, not because anything looked wrong) found CR_COUNT=205 where it should have been 0 -- the write tool itself had normalized every line ending to CRLF on the way to disk, silently, with no error or warning. Line count, content, and every text spot-check still passed; only a raw byte scan caught it.

**Fix:** After any full-file rewrite via windows-mcp:FileSystem mode=write, byte-scan the result for CR bytes (or CRLF pairs) and compare to the line-ending convention confirmed before the edit -- do not trust line-count or content spot-checks alone, they do not detect this. If the file is supposed to stay LF-only and the write introduced CRLF, normalize immediately with a .NET ReadAllText -> -replace "``r``n","``n" -> WriteAllText(UTF8, no BOM) pass and re-verify CR_COUNT=0 before considering the edit done. This is a distinct failure mode from the PowerShell .Replace() line-ending mismatches already logged this session (M-054/M-055 era fixes) -- those broke targeted `.Replace()` matches; this one silently corrupts a file's established convention on a clean full-file write with no match failure to signal it.

(Captured 2026-08-29, self-caught during WO-P300-E5.009 build, not a Tony correction.)

## M-119 -- Verify a stdlib keyword argument exists on p140's actual Python version before using it; don't assume API knowledge transfers across versions

**Rule:** Before passing an unfamiliar or infrequently-used keyword argument to a stdlib function/method, confirm it's supported on p140's actual version (3.12), not on whatever version general API knowledge assumes. A keyword argument added in a later Python release raises a hard TypeError immediately -- not a silent bug, but still a wasted PEH round-trip a one-line version check would have prevented.

**Trigger (2026-08-31):** The lessons.md archive-pass script (run_this_P300_20260831_081556.py) called Path.read_text(encoding='utf-8', newline=''), written specifically to guard against M-117's CRLF-conversion failure mode. First run failed on p140: pathlib.Path.read_text() does not accept a newline parameter on Python 3.12 -- that parameter was added in 3.13. Fix: switched to the plain builtin open(path, encoding='utf-8', newline='') instead, which has supported newline='' raw passthrough for a long time -- same guarantee, older API. No assertions changed; re-run passed clean.

**Fix:** When a script needs a stdlib feature that isn't rock-solid common knowledge (recently-added kwargs, new stdlib modules, syntax features), either check p140's version first or default to the older/more broadly-supported API (open() over Path.read_text() for anything beyond the plainest read) rather than reaching for whichever spelling comes to mind first.

**Pairs with:** M-117 (the CRLF guard this script existed to enforce -- the fix here didn't touch that guard, just its API surface), M-035 (verify interpreter identity before issuing a python command).

(Captured 2026-08-31, caught by Tony running the script -- first real PEH round-trip on this script, one clean fix, no retry needed.)

## M-120 -- A "matches known value" sanity check printed as a comment is not a check unless the code actually asserts it; M-020 recurs in ad-hoc analysis scripts, not just production display code

**Rule:** M-020 (return_pct is a decimal fraction; x100 at display) applies to ANY script reading a `*_return_pct` field, including one-off diagnostic scripts, not just production report_writer paths -- the field doesn't know it's being read by a "real" script versus a throwaway one. Separately: a script that claims to sanity-check its own output against a known-correct number, printed as a comment or f-string next to the computed value, provides zero real protection unless that comparison is a live assertion that fails the script on mismatch. A claimed match nobody verified programmatically is the same failure shape as M-051's hardcoded success string.

**Trigger (2026-08-31):** run_this_P300_20260831_093649.py (h5 ledger gap diagnosis) read h5_return_pct directly from buy_ledger.db and printed it with a bare `%` suffix, skipping the x100 scaling M-020 already covers -- same mistake for every *_return_pct field in the by-week and by-symbol breakdowns. The script's own header line even printed "(matches calibration report's -0.75% / 51.1% -- sanity check)" next to an actual value of -0.007%, an order-of-magnitude mismatch the script never checked itself; Tony caught it by eye against the known baseline. n, win_rate%, and both concentration ratios (week/symbol share of total negative return) were unaffected -- ratios of two equally-unscaled numbers cancel the error; only the raw average/total return figures needed correcting.

**Fix:** (1) Apply x100 at the exact point any *_return_pct field is formatted for display, in every script that touches one, including throwaway analysis scripts -- not just files that already carry the anti-pattern-list warning. (2) When a script prints a "should match X" comparison, make it a real `assert abs(computed - known) < tolerance, f"..."` that fails the run -- never a comment or f-string asserting agreement that nothing actually diffed.

**Pairs with:** M-020, M-051 (hardcoded success claims), M-054 (a claim is not evidence).

(Captured 2026-08-31, Tony's direct correction.)
