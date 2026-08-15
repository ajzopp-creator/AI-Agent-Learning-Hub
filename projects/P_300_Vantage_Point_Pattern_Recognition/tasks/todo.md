# P_300 Task Queue

**>>> 2026-08-14 (Sonnet) -- DailyEval + Chaikin batch clean, live production run; WO-P300-E4.009 base WO still not closable (no failure occurred to exercise the detection):**

`P_300_RunAllDailyEvals.ps1` run, 11 symbols (BBY, EPD, ESS, FICO, LRN, MSCI, NCLH, PPC, RBLX, RDDT, SMPL), anchor 2026-08-13. All 11 evaluations completed, 0 errors. 7 BUY/WATCH candidates (BBY, EPD, FICO, MSCI, RBLX, RDDT, SMPL) fed to the shared Chaikin scanner (`RunChaikinBatch.ps1 -Schema P300`) -- 7/7 enriched, no login prompts, session pre-authenticated.

**Spot-verified 2/7 vault notes directly** (not taking console output at face value -- M-054): `2026-08-13_BBY.md` and `2026-08-13_FICO.md`, both `Created`/`Modified` 06:17 today. Chaikin ratings match console exactly (BBY Neutral, FICO Bearish), full Quick Stats + Summary sections present, no truncation, `note_version: 1`, `write_route` frontmatter clean.

**WO-P300-E4.009 base WO (whole-batch failure detection) still not closable off this run** -- today's batch had zero failures (no login wall, no extension drop), so the WO's own designed detection was never exercised. Confirms the happy path is clean end-to-end on the schema-driven scanner; does not supply the still-owed real-failure confirmation.

LM Studio confirmed running by Tony (INIT preflight had flagged NOT READY at session start; resolved before this batch ran).

---

**>>> 2026-08-12 (3rd, Sonnet) -- WO-P800-E4.001 P_300 Ack DONE for real -- 6 real notes enriched, independently read back, all confirmed correct:**

Tony hit the auth blocker from the prior entry, refreshed the Claude Code CLI token (`/login`, browser OAuth), re-ran `RunChaikinBatch.ps1 -Schema P300` standalone. Console reported all 6 candidates (CLIX, NSLR, RWT, STLA, SYNA, XPO) enriched.

**Did not take that at face value** -- the standalone script bypasses `P_300_RunAllDailyEvals.ps1`'s own wrapper-level readback check (that only fires when Chaikin runs as part of a full daily-eval batch), so this session read all 6 notes directly off disk. All 6 confirmed: real, complete `## Chaikin Power Gauge` sections, ratings matching the console exactly, `LastWriteTime` 14:08-14:09 today, no truncation or malformed markdown, `write_route` frontmatter unchanged (NFR-1 held). CLIX correctly handled as a no-coverage ETF (`Rating: None` + ETF Profile stats, not the stock Quick Stats template) -- confirms the skip-list mechanism and Chaikin's own per-symbol coverage gaps are two separate, correctly-independent things (CLIX isn't skip-listed and shouldn't be; it just has no rating).

**WO-P800-E4.001 updated: P_300 Ack -> DONE**, matching P_115's 2026-07-25 standard exactly. Both Acks now done. Status stays OWNER_DONE (not CLOSED) -- this session wrote the skip-list extension code earlier today, so per WO_COMPLETION_GATE's Independent Review Requirement it can't also close the WO. A fresh session that wrote none of the skip-list code owes the final CLOSED move.

**Real finding, not this WO's scope:** today's `claude -p --chrome` 401 was the Claude Code CLI's own OAuth token expiring (confirmed via code.claude.com/docs/en/errors), NOT a separate Chaikin-specific Chrome-extension credential as first guessed and initially written into the WO -- corrected same session before Tony acted on the wrong fix.

---

**>>> 2026-08-12 (2nd, Sonnet) -- WO-P800-E4.001 Chaikin skip-list extension BUILT + PEH-verified (5/5); P_300_RunAllDailyEvals.ps1 migrated to schema-driven scanner; Ack itself still owed on next real BUY/WATCH:**

**4-file plan (Tony-approved) built in delivery order, config -> domain -> infrastructure -> application, all in `shared_resources\chaikin_enrichment\`:** `config.py` v1.0->v1.1 (+27 ln, `SCHEMA_SKIP_LISTS` dict, per-schema, P_115 unaffected via empty default); `domain\candidate_filter.py` v1.0->v1.1 (+~20 ln, `is_candidate()`/`filter_candidates()` gained an optional `skip_symbols` param defaulting to empty frozenset -- backward compatible, existing tests needed zero changes); `infrastructure\skip_list_reader.py` (NEW, 39 ln, `read_skip_list(schema) -> dict[symbol, reason]`, graceful empty-dict fallback); `application\run_chaikin_batch.py` v1.0->v1.1 (+~20 ln, wires the reader in, prints `[SKIP] SYMBOL -- reason` for qualifying-but-skipped symbols by calling `filter_candidates()` twice rather than re-deriving qualification logic, M-082).

**PEH-verified same day, 5/5 PASS** (`Agentic-Hub-Governance\verify\run_this_P300_20260812_chaikin_skiplist.py`, Tony ran it): full import chain across all 4 files; existing `test_candidate_filter.py` assertions re-run directly, still pass unmodified; new skip-exclusion behavior confirmed both directions; a REAL read of P_300's actual `chaikin_skip_list.csv` returns exactly the 6 known symbols (XYLD, BITX, CRPT, CDPYF, CNSWF, EDVMF); P_115 confirmed to get an empty skip map.

**`P_300_RunAllDailyEvals.ps1` migrated in the same pass** -- inline log-parsing + direct `claude -p --chrome` call replaced with `& RunChaikinBatch.ps1 -Schema P300`. Candidate list for the post-batch vault-note readback (WO-P300-E4.009's discipline, preserved unchanged -- never trust claude's prose, verify the actual vault file) now comes from the scanner's own `_last_prompt.txt` artifact, mtime-checked against `$batchStartTime` since the wrapper's exit code alone can't distinguish "no candidates" from "candidates existed, claude's exit code passed through." PowerShell syntax verified via real `[System.Management.Automation.Language.Parser]::ParseFile()` -- 0 errors, ran directly (no python.exe involved, so no MCP wedge risk).

**Real trade-off, disclosed in the WO, not hidden:** the old script's best-effort failure-phrase matching (login wall / extension-not-connected prose detection) didn't port to the shared script and wasn't rebuilt here -- out of scope for the approved 4-file plan. The load-bearing safety net (real vault-note readback) is fully preserved, so a silent failure still can't be mistaken for success; only the specific "probable cause" hint text is lost. Flagged as a possible small follow-up, not filed as its own WO.

**WO-P800-E4.001 updated** with a full "P_300-Side Build" section (Acks line changed from "pending" to "build done, Ack still owed"). **Ack itself still not complete** -- zero real BUY/WATCH candidates existed within `LOOKBACK_DAYS=1` at build time (most recent P_300 vault note was 5 days stale; Tony was mid-export of today's live grids when this was first found, same session, earlier). Real Ack -- matching P_115's own 2026-07-25 standard -- is owed on the next real DailyEval batch that produces a BUY or WATCH.

**Three windows-mcp:PowerShell wedges on python.exe calls this session** (Chaikin scanner check, sqlite3 topk_cache check, this build's verification script) -- all handed off via PEH rather than retried blind, all came back clean. Plain PowerShell (ping, PowerShell's own AST parser) worked reliably throughout; only python.exe subprocess calls wedged. Broader than the 2026-07-20 todo.md entry's "narrowed to sqlite3 specifically" finding -- today's evidence (2 of 3 wedges were non-DB) suggests python.exe-via-MCP is the more general risk factor this session, not sqlite3 alone. Not filed as a new M-lesson (M-030 already states the general rule); noted here as a session data point.

---

**>>> 2026-08-12 (Sonnet) -- WO-P300-E4.006 status header was stale for 24 days (actually CLOSED); WO-P300-E5.008 unblocked; P_800 Chaikin Ack still open (data + shared-code gaps found):**

**WO-P300-E4.006 corrected: stale header said "BUILT, NOT YET PEH-VERIFIED," body proved otherwise.** This session's own INIT summary initially repeated that stale header to Tony as fact. Caught only because Tony pushed back asking what the E4.006/E5.004 distinction meant -- re-reading the FULL 670-line WO body (not just the header) showed PEH Steps 1-4 all PASSED 2026-07-19 (unit tests, full import chain, dry-run migration against a catalog copy, then the real migration against the live catalog), and the one flagged gap (byte-identity regression vs. a full rescore) was closed 2026-07-20/21 (12/12 exact match). The Status line itself was simply never updated to match -- pure documentation drift, not a code problem. Independently re-verified today against the CURRENT live catalog (080526catalog.db, 31,845 patterns, vs. the WO's own 071726catalog.db/10,761-pattern evidence): topk_cache table real, 636,632 rows, 31,839/31,845 pattern_instances covered, 20.00 avg rows/pattern (exact TOP_K_MATCHES=20 match), 6 uncovered = the known degenerate-corpus pids. Confirms the design has held through 21,084 patterns of real growth, not just on ship day. WO-P300-E4.006 moved to CLOSED (Completion Gate checklist added -- none existed before; Independent Review section added, fresh session, wrote none of the original code, per WO_COMPLETION_GATE). Verification script staged/run via PEH after a windows-mcp:PowerShell wedge on the sqlite3-against-live-catalog call (exact known M-030 failure shape -- not retried blind; relay recovered for non-DB calls afterward, confirmed via a plain ping before handing off): Agentic-Hub-Governance\verify\check_topk_cache_20260812.py, read-only, Tony ran it, real output pasted back.

**WO-P300-E5.008 unblocked as a direct consequence.** Its Depends On, OUT OF SCOPE, and RISKS AND UNVERIFIED ITEMS sections all cited E4.006's stale header (copied verbatim when E5.008 was filed 2026-08-07) as an open blocker on run_incremental_post_batch's contract. All three corrected in place -- E5.008 can now be scoped and built (retire vs. replace the orphaned reuse-fraction test coverage) against the real, settled contract. E5.008's own Status stays PENDING -- the retire-vs-replace decision itself still hasn't been made; only the false blocker is gone.

**New lesson filed: M-111** -- a WO's own Status header line is not authoritative over its own body; both must be checked, and a contradiction between them is itself a signal worth surfacing, not silently resolved in either direction. See lessons.md.

**WO-P800-E4.001 (P_300's Chaikin Ack) -- still open, two real gaps found, neither resolved yet:**
1. **Data gap:** the schema-driven scanner's LOOKBACK_DAYS=1 means a real Ack needs a fresh BUY/WATCH note from today or yesterday. Most recent P_300 vault note on disk at session start was 2026-08-07 (5 days stale) -- zero real candidates exist to test against. Tony was mid-export of today's live grids (NSLR, RWT) when this was found; today's DailyEval batch (Tony's own operator-run step, not run this session) is the real unblock.
2. **Shared-code gap, more consequential:** shared_resources\chaikin_enrichment\ (the new schema-driven scanner P_800 built) has zero awareness of P_300's chaikin_skip_list.csv (WO-P300-E5.007, shipped 2026-08-05 -- OTC/ETF symbols Chaikin structurally can't rate: EDVMF, XYLD, BITX, CRPT, CDPYF, CNSWF). Folding P_300_RunAllDailyEvals.ps1's inline Chaikin chain over to RunChaikinBatch.ps1 -Schema P300 as-is would silently reintroduce the exact bug E5.007 fixed one week ago. 4-file plan proposed to Tony, not yet approved: chaikin_enrichment\config.py (+~8 ln, per-schema SCHEMA_SKIP_LISTS dict, P_115 unaffected via empty default), domain\candidate_filter.py (+~15 ln, exclude skip-set symbols), a small infra CSV-read helper (+~10 ln), and P_300_RunAllDailyEvals.ps1 itself (~-100/+10 ln, inline chain replaced with the schema-driven call, note-readback/summary logic kept). Extends WO-P800-E4.001 directly (P_300-owned cross-project WO already) -- no new WO needed. Awaiting Tony's go-ahead before any code is written.

---

**>>> 2026-07-30 (Sonnet) -- WO-P300-E5.002 status-line self-contradiction resolved, completion-gate fail-path test built and PASSED in production:**

**WO-P300-E5.002 ledger self-contradiction, resolved.** Tony flagged the
WO's status line reading BUILT while an inline 2026-07-28 note said "this
status is probably wrong" directly beneath it. Independently re-verified
against source (not trusting the WO's own prior confirmation note --
M-054): `catalog_merge_pipeline.py`'s `promote_staging_to_live()` really
does call `verify_and_promote()` with a real `expected_delta` and raises
on failure. BUILT was correct; the 2026-07-28 note was the (already-
answered) trigger for that finding, not live doubt. Tagged RESOLVED
inline, kept as audit trail. Also found while in `verify_ingestion.py`:
the stale `check_topk_cache=True` claim the WO already caught once in the
changelog is duplicated in the module docstring AND `verify_and_promote()`'s
own function docstring -- 3 copies, same wrong claim, none functionally
wrong, all doc drift. Logged, not yet fixed.

**Completion-gate fail-path test -- BUILT and PASSED, real production
run.** `python/tests/test_verify_ingestion.py` (262 lines, 3 checks)
written this session, targeting `verify_and_promote()` directly (smallest
input that proves the guarantee -- not the full `promote_staging_to_live()`
orchestration, which would require real DTW/top-K population for no
additional coverage). Pre-delivery, run against a verbatim sandbox
reconstruction of `verify_ingestion.py` with a negative control (gate
deliberately disabled -> test correctly failed, exit 1; gate restored ->
exit 0) to confirm the test isn't vacuous. Tony then ran it for real via
the p140 interpreter against the actual file: **ALL CHECKS PASSED (exit
0)** -- wrong `expected_delta` blocked (master untouched), hollow
`pattern_instance` blocked even with correct deltas (master untouched),
clean data promoted with `.bak` backup preserved. This closes the
FAIL-branch gap noted below -- both WO-P300-E5.002 and WO-P300-E5.005 now
have real-run confirmation of success AND failure paths, not just code
inspection. **Neither WO marked CLOSED** -- WO_COMPLETION_GATE: the
session that writes the test cannot also close the WO. Needs fresh-session
independent review.

**>>> 2026-07-29 (Sonnet) -- test-directory consolidation, WO-P300-E5.005/E5.002 closure work, TKO/Chaikin investigations:**

**tests/ (project root) vs python/tests/ -- consolidated, tests/ now empty
(.gitkeep only).** Root cause: the WO-P300-E5.005 2026-07-26 approved plan
dropped the `python/` prefix for its two test-file rows only (every
production-file row had it); the build then added 2 more test files
following that precedent. Separately, and worse: a 2026-07-20 independent-
review session checked the WRONG directory and wrongly concluded
test_similarity.py and test_get_latest_catalog_path_safety.py were "never
on disk," triggering two unnecessary full rebuilds that sat unreconciled
in tests/ ever since. Resolved 2026-07-29:
  - 11 misplaced-but-not-duplicated files moved to python/tests/, each
    file's _PYTHON_DIR path-bootstrap line fixed for the new location,
    version bumped, changelog entry added. Verified via PEH from the new
    location.
  - test_get_latest_catalog_path_safety.py: the 2026-07-14 original was
    genuinely OBSOLETE (fails against current code -- tests the M-095
    wrap pattern that WO-P300-E4.002 superseded with get_latest_catalog_
    path()). Confirmed via a real side-by-side PEH run (original 2/4 FAIL,
    2026-07-20 version 6/6 PASS) before deleting the original and
    promoting the current one into python/tests/.
  - test_similarity.py: both versions' 6 core checks were functionally
    equivalent (real coverage, not a stale/current split like the above).
    Consolidated into one file -- kept this file's assert-based style,
    adopted the duplicate's structurally-independent full-matrix reference
    DTW oracle (real improvement: the original's rolling-row reference
    shared its computational shape with production's own rolling-row
    dtw_distance(), weaker for exactly that reason), unioned both fixture
    sets (6 -> 12).
  - Running the orphaned files surfaced 2 REAL, pre-existing, unrelated
    staleness bugs (confirmed via source, not guessed) -- both FIXED:
    smoke_stage6_files_1_and_2.py expected SIMILARITY_FEATURES=10, config.py
    has been at 9 since v1.4 (volume_zscore removed, confirmed noise via
    feature ablation); config.py's own changelog says so directly.
  - **PARKED, not fixed: test_eval_incremental.py.** Imports
    assemble_incremental_post_batch, which WO-P300-E4.006 REMOVED outright
    (not renamed) -- the whole reuse-fraction "attempt incremental or skip"
    decision it tested no longer exists; the cached path (run_cached_post_
    batch) is unconditional now. application/incremental_post_batch.py
    ITSELF is fully current (v2.0, correctly wired) -- this is an orphaned
    test, not a production gap. Real rewrite needed: new fixtures (likely a
    temp SQLite catalog, since run_incremental_post_batch now opens a real
    DB connection for existing_cache), and a decision on whether the
    reuse-fraction tests get retired outright or replaced with coverage of
    the new unconditional-path guarantee. Tony's call: park for now, revisit
    as its own plan-gated task later -- do not fold into a quick fix.

**WO-P300-E5.005 -> all 4 REMAINING BEFORE CLOSE items done** (progress
logging built + verified via real smoke test against live catalog data;
independent review; PS1 transcript re-verified on a real production run,
072826->072926catalog.db, +1222 patterns; investigation done). Not CLOSED --
no one has yet run a deliberately-broken-staging-copy test proving the
FAIL branch of verify_and_promote() actually blocks a bad promote; success
path is proven in production, failure path is not.

**WO-P300-E5.002 -> BUILT**, ledger corrected from stale PENDING/DISPUTED
(M-017 -- code was ground truth, ledger was wrong). Real production
confirmation same day. Not CLOSED for the same reason as E5.005 above.

**TKO real-run investigation (BulkAddPattern, 2026-07-29 batch):** one bad
VP-exported pred_range value (-0.30, should never be negative) killed
parsing for TKO's entire file, not just the one bad row -- bulk_grid_
reader.py's _extract_bars() has no per-row try/except, confirmed by
direct PEH read of the pulled-from-zip file. TKO still got a valid signal
(WATCH) and its full Chaikin enrichment the same day via the DailyEval
path, which doesn't depend on today's mining success -- the failure was
scoped to the historical-pattern catalog only, nothing downstream.

**Chaikin per-symbol-miss (WO-P300-E4.009 FOLLOW-UP) -- CLOSED, no code
built.** Root cause of the CDPYF (2026-07-24) and CNSWF (2026-07-27/29)
misses confirmed via Tony's own Chaikin UI screenshots: both are OTC
pink-sheet mirror tickers for TSX-primary Canadian companies (CNSWF=
Constellation Software/CSU, CDPYF=Canadian Apartment Properties REIT/
CAR.UN). Chaikin simply doesn't carry them -- permanent, not a retry-able
failure. Tony's call: no detection code needed for this failure shape.


**lessons.md retention pass (2nd):** 28 more entries archived (mechanical,
header-boundary extraction -- not hand-retyped) + a compression pass on the
~10 heaviest retained entries (M-085, M-109, M-110, M-075, M-034, M-105,
M-051, M-094, M-032, plus the retention note itself). File dropped
138.4KB/1,392 lines -> 62.4KB, under the ~70KB cap for the first time in
weeks. tasks/lessons_archive.md grew to 115.7KB, nothing lost. Full
verification pass run after (header count, no duplicates, no truncation,
archived numbers confirmed absent, retained numbers confirmed present,
section structure intact) -- clean.

**Independent review, real code check (not just prose) against all 4
OWNER_DONE/PENDING-review WOs:**
- **WO-P300-E5.003 -> CLOSED.** All 3 files match the WO's claims exactly
  (line counts, versions, function signatures). Real PEH already existed
  (Tony, 5/5 PASS); this review supplies the missing independent-authorship
  piece.
- **WO-P300-E4.008/E4.009/E4.010 -> stay OWNER_DONE**, now with independent
  code-review confirmation. Real 2026-07-25 production data (21-symbol
  DailyEval batch + a BulkAddPattern run) exercised all three fixes' SUCCESS
  paths cleanly (0 [ERROR]s, 0 IntelliScan WARNINGs, honest "21/21 complete"
  branch) -- but none of the three failure-detection paths have fired against
  a real failure yet. Real execution on an actual failure case remains the
  owed gate for CLOSED on all three.

**Real finding, not from the log file -- from checking actual vault-note
artifacts directly (M-054 discipline):** Tony reported "no output" from the
2026-07-25 evening run. Both runs actually succeeded:
- **DailyEval (18:10-18:29):** 21/21 clean. Chaikin enrichment succeeded for
  18/19 actionable symbols (real Power Gauge sections, vault-note mtimes
  18:30:21-18:36:00) -- but silently missed **CDPYF** (correctly in the
  actionable list, no error anywhere). WO-P300-E4.009's whole-batch phrase
  matching was never built to catch a single-symbol miss inside an otherwise-
  successful batch -- not a defect in that WO. Folded into **WO-P300-E4.009** as a FOLLOW-UP section (Tony's direct call -- same WO, not a standalone one), detection-only design proposed: check vault notes for ## Chaikin Power Gauge per actionable symbol after the batch, loud line + $LOG write on any miss.
- **BulkAddPattern (~16:15-16:58):** also succeeded -- `staging_ingest_mined.db`
  grew to 121MB (was 110MB), both walk-forward reports generated,
  `data\bulk\mine\` emptied by the archive step. Not promoted (by design --
  manual step). This script has **no log file at all** (100% console-only
  Write-Host) -- confirmed as the real reason "no output" looked true: there
  was nothing to check once the console closed, even though the run worked.

**Tony's direct request, same session:** "I see no reason to manually
promote unless there is an issue." Filed **WO-P300-E5.005** (PENDING,
design proposal only, NOT built) -- auto-promote `ingest-mined` staging
batches automatically unless the existing M-079 walk-forward comparison
flags a regression. Proposed gate (Tony's sign-off owed before build):
BUY precision drop >3pp OR PASS accuracy drop >3pp vs. pre-batch baseline
blocks auto-promote and falls back to today's manual-command path; BUY
volume shift >50% is flagged but not blocking. 3pp chosen with real margin
below the one confirmed real regression this project has measured
(WO-P300-E2.003, a 5.2pp precision drop that the same M-079 mechanism
correctly caught and blocked). Bundled into the same WO: add a $LOG file to
P_300_RunBulkAddPattern.ps1 (currently has none), same pattern as
P_300_RunAllDailyEvals.ps1's $LOG. Plan-gate applies -- full file-level plan
required before any code, per standing practice; this WO is documentation
only so far, nothing built.

---
**>>> 2026-07-25 (2nd, Sonnet) WO-P800-E3.003 P_300 Ack DONE -- vault path rename, WO now CLOSED (all sides done):**

P_800's hub-wide `TradeManagement` -> `TradeOrderManagement` vault rename (P_800 + P_400 sides already done). P_300's piece: `application/daily_evaluate_pipeline.py` line 437 -- `signal_source_link` f-string updated from `TradeManagement/P300/` to `TradeOrderManagement/P300/` (new signals were pointing at a now-empty folder since P_800's merge). Single string swap, backed up first.

**Real bug found along the way, not part of the ask:** `test_signal_emitter_dry_run.py` was still calling `emit_signal_packet()` with the old v1.0 signature (`vault_root=...`, no `chosen_horizon`) -- stale since the emitter moved to v2.0/SIGNAL_V2 in June, so this test had been silently broken since then. Fixed same pass: real v2.0 call signature, `write_to_vault` monkeypatched (no live write), validated against the real `SignalV2` schema from `shared_resources`. Added a new assertion on `signal_source_link` itself -- the old test never actually checked that field, only used it as fixture input.

**Real PEH pass, Tony ran it, full output pasted back:** 4/4 steps. Syntax + import clean, exact-string check on the live pipeline file (0 old-path hits, 1 new-path hit), full re-run of the corrected dry-run test -- 7/7 internal steps PASS including the new `signal_source_link` assertion, full JSON packet inspected.

WO-P800-E3.003.md updated (Acks: P_300 done, Still Open items 3-4 struck through, new P_300-Side Implementation section, Status -> CLOSED -- all four Acks now landed, P_800/P_400/P_300 all done).

---

**>>> 2026-07-25 (Sonnet) WO-P300-E5.003 OWNER_DONE -- check-pattern CLI built, real PEH pass 5/5, design changed mid-session to match Tony's real workflow:**

Original plan (per the WO's own RESOLVED interface) was a required `--symbol X` flag. Tony redirected before build: his actual process exports "History Grid (SYMBOL).xlsx" files to `data/live/` manually first, then wants to check all of them at once -- not retype tickers. Revised design, approved before any code written: default mode (no args) scans `config.DATA_LIVE` for `History Grid (SYMBOL).xlsx` files and checks every ticker found; `--symbol` (comma-separated) kept as an explicit override for an ad-hoc check with nothing exported yet.

**Built (3 files):** `infrastructure/catalog_writer.py` v1.0.3->v1.0.4 (+`get_anchor_dates_for_ticker()`, sibling to the existing `pattern_exists_for_ticker_anchor()` boolean guard -- 354 lines, was already over the 300 cap at 328 before this edit, flagged not fixed). `utilities/check_pattern.py` v1.0 NEW (185 lines) -- reuses `vp_xlsx_reader._parse_live_filename()` for the ticker regex (M-082, same parser Pipeline B trusts) and `config.DATA_LIVE` for the path. `cli_commands/utility.py` v1.0->v1.1 (+`check-pattern` subcommand, 157 lines).

**Real PEH pass, Tony ran it, full output pasted back:** 5/5 steps. Syntax + imports clean. `get_anchor_dates_for_ticker()` cross-checked against a real dynamically-selected known-populated ticker (count matched raw SQL exactly) and a real known-absent sentinel (`[]` as expected); cross-checked agreement with the existing boolean guard on the same ticker/date. Both `--symbol` mode and default directory-scan mode ran clean, exit 0. **Real result against the actual `data/live/` folder (21 files):** 20 tickers clear to export, MSI already has 1 pattern captured (anchor_date 2026-02-11), 2 non-matching files correctly named and skipped rather than silently dropped.

**Catalog identity note:** this PEH run resolved to `072326catalog.db` -- newer than the `072226catalog.db` the 2026-07-23 preflight status still reports (14,812/341 as of that stale snapshot). Real pattern count on `072326catalog.db` not yet independently pulled -- preflight re-run still owed, flagged at this session's INIT and still open.

**Cannot self-close** -- this session wrote both the code and the PEH verification script, so Tony's real run proves the code works but isn't an independent review of it (WO_COMPLETION_GATE.md). Needs a fresh session/subagent re-verification before CLOSED. WO-P300-E5.003.md updated with full BUILD RECORD + PEH VERIFICATION sections.

---

**>>> 2026-07-23 (3rd, Sonnet) WO-P300-E5.004 Part A PEH VERIFICATION PASSED -- both parts CLOSED:**

Fresh-session INIT (this chat did not write the Part A code). Reviewed the staged `run_this.py`, then Tony ran it for real and pasted full output. All 5 checks PASS: (1-3) syntax/imports/synthetic-fixture reconstruction test PASS; (4) 25 real pids sampled from the live catalog's date range, real `score_one()` (DTW) vs. `score_one_from_topk_cache()` -- 25/25 exact match, 17.5s; (5) full `reconstruct_pre_batch_from_topk_cache()` against the REAL `072226catalog.db` (14,812 patterns) -- 130.0s wall time, `n_patterns=14812`/`n_degenerate=6` both matching the pre-registered expectation from last session's Part A research exactly.

**Independent verification performed this session, not taken on the paste alone (M-054):** confirmed all 4 built files exist on disk with real 2026-07-23 timestamps (`domain/reconstruct_from_topk.py`, `application/reconstruct_pre_batch.py`, `tests/test_reconstruct_from_topk.py`, plus the `ingest_mined_pipeline.py` edit) -- closes the M-105 claimed-but-missing-test-file risk before trusting this closure. Grepped `ingest_mined_pipeline.py` directly: `_run_pre_batch()` really does import and call `reconstruct_pre_batch_from_topk_cache()` first on a cache miss (line 289) -- confirms this is now the LIVE production path for the next real `ingest-mined` run that hits a cold "pre" cache, not a dormant alternative needing a flag flip. Catalog identity cross-checked: this session's own fresh `P_300_Preflight.bat` run (14812/341, 0 hollow, HEALTHY) matches the verification run's numbers exactly.

**Timing, reported honestly:** step 5 ran 130.0s (~2.2 min), not "well under a minute" as `run_this_context.txt`'s own success bar hoped -- flagged by the script itself, no fix attempted per its instructions. Still a ~660x improvement over the ~24h full serial rescore this WO exists to prevent (WO-P300-E4.005's measured formula projects ~23.88h at N=14,812) -- the real target (never silently run for hours) is met by a wide margin even though the softer "sub-minute" hope wasn't.

**WO-P300-E5.004 -- BOTH PARTS now CLOSED** (WO file updated directly: PART A BUILD + PART A PEH VERIFICATION sections added, status header corrected). Part B's confirm-gate stays in place as the fallback for any future cache-miss scenario reconstruction itself can't resolve (`TopkCacheReconstructionNotViable`) -- complementary, not superseded.

**Next real task:** WO-P300-E5.001 (import-linter) and WO-P300-E5.002 (promote-path verification fold) remain PENDING, not started. E4.008/E4.009/E4.010 remain OWNER_DONE, real PEH still owed on all three.

---

**>>> 2026-07-23 (2nd, Sonnet) WO-P300-E5.004 Part A BUILT -- topk_cache-based reconstruction, PEH verification STAGED but NOT YET RUN:**

Built candidate 2 from the Part A research (topk_cache is already correctly, comprehensively maintained at every real promote -- confirmed against the live catalog; the DTW similarity step it stores is the only expensive part of the M-079 "pre" walk-forward batch). 4 files: domain/reconstruct_from_topk.py (new -- score_one_from_topk_cache(), classify_topk_gap() distinguishing correctly-empty degenerate cases from real gaps), application/reconstruct_pre_batch.py (new -- orchestrator, O(N log N) corpus_size precompute not the naive O(N^2), real per-pattern gap fallback to fresh DTW), application/ingest_mined_pipeline.py (edit -- _run_pre_batch() tries reconstruction first on a cache miss, only falls through to the existing confirm-gated full rescore if reconstruction itself cannot proceed), tests/test_reconstruct_from_topk.py (new -- proves reconstruction is byte-identical to real run_walk_forward() DTW output, using REAL domain.topk_cache.seed_full_catalog() for the fixture's topk data, not hand-crafted).

**NOT YET DONE -- PEH verification staged, not run.** Chat closed before Tony could run it. run_this.py + run_this_context.txt are sitting in Agentic-Hub-Governance\verify\, ready to run as-is: (1) syntax, (2) imports, (3) the synthetic equivalence test, (4) a real 25-pattern sample from the live catalog compared against real DTW, (5) a full run of reconstruct_pre_batch_from_topk_cache() against the real 14,812-pattern live catalog with real wall-clock timing (read-only, does not write to the cache). Next session: read this entry, check whether Tony already ran it and has output to paste, or run the staged script as-is before trusting any of this build. Do not mark WO-P300-E5.004 Part A complete until that real verification has actually run and passed -- code being written is not the same as code being verified (M-054).

---

**>>> 2026-07-23 (Sonnet) WO-P300-E5.004 Part B CLOSED -- overnight 8.8h run killed and root-caused; confirm-before-rescore gate built + verified:**

Tony let P_300_RunBulkAddPattern.ps1 run overnight; ingest-mined (no --promote) hit a cold M-079 "pre" walk-forward cache and silently fell back to a full, uncached, serial run_walk_forward() over the whole 14,812-pattern live catalog -- no estimate, no confirmation, no visible progress. Real process confirmed still alive (100+ min real CPU over 8.8h wall time, not hung) via Get-Process; killed on Tony's instruction once confirmed nothing live had been touched. Root-caused via real evidence, not guesswork: WO-P300-E4.005's own 2026-07-19 measurement (0.7836ms x corpus_size, integrated) predicts ~12.5h at N=10,738 and ~24h at tonight's N=14,812 -- this morning's real promote (ingest-mined --promote -> promote_staging_to_live()) never refreshes the walk-forward cache, so the first ingest-mined run after ANY promote is guaranteed to hit this. WO-P300-E4.006's topk_state_cache fix only covers the "post" (staging) side, not this "pre" (live) cold-cache fallback -- the original 2026-07-15 problem all that optimization work targeted is still fully reachable here.

Filed WO-P300-E5.004: Part A (the real fix -- promote-time cache refresh vs. extending incremental caching to the pre side vs. diff-and-extend) explicitly left as research, not decided, per Tony -- more research needed before committing to an approach. Part B (never auto-rescore; estimate + require confirmation) built and closed same day: config.py constant, domain/eval_scoring.py's estimate_full_rescore_seconds(), ingest_mined_pipeline.py's FullRescoreConfirmationRequired + gated _run_pre_batch(), --confirm-full-rescore CLI flag, new regression test. Fails closed (refuse + clear message + non-zero exit, reusing the .ps1 wrapper's existing pause-on-error) rather than a live interactive prompt, since a prompt buried in redirected output is close to what may have compounded tonight's incident.

Real mistakes made and caught during the build (M-110 filed): ingest_mined_pipeline.py truncated mid-edit (recovered via a pre-edit .pyc decompiled with dis.dis(), the file isn't git-tracked); tests/test_eval_scoring.py hit two further assembly mistakes (a dropped import, a misnested function call) before a full re-read + real execution run confirmed everything correct. All four edited files + the test file PEH-verified for real (syntax, imports, real execution, exit code 0) before this closure.

---

**>>> 2026-07-22 (2nd, Sonnet) WO-P000-E8.001 P_300 PILOT COMPLETE -- SIP bumped to v3.4, CLAUDE.md separator error caught and reverted:**

Finished the WO-P000-E8.001 pilot: SIP updated to v3.4 (Step 4 now reads CLAUDE.md, Quick Reference + Pairs-With updated, v3.2 changelog entry moved to docs/P_300_SIP_CHANGELOG_ARCHIVE.md per the SIP's own existing retention rule). While editing the SIP, found the live file already carries a "Header separator dropped" amendment under v3.3 (WO-P000-E4.001 v1.1) that the project-attached copy at session start did not show -- session header format is `P_300 [Day, Month DD, YYYY] [HH:MM] ET`, NO `--` separator. Earlier this same session, CLAUDE.md was incorrectly "corrected" in the opposite direction based on that stale attachment; reverted once the real live SIP was checked directly. This session used the wrong (with-separator) header format throughout as a result -- fix goes into effect starting next session.

WO-P000-E8.001 updated to P_300 PILOT COMPLETE (not CLOSED -- Hub-wide rollout to P_115/P_400/P_020/P_805/P_010/P_800 and the P_000_SYSTEM_DOCUMENTATION.md canonical-pattern recording are still open, logged honestly as not-done rather than silently dropped). Full pilot recap: CLAUDE.md restored+merged after an accidental overwrite mid-build (M-109 filed), tasks/lessons.md split (37/108 entries archived, real-evidence-based not the full ~40-target cut), tasks/todo.md split (339 lines archived), SIP v3.4. Non-blocking size-check INIT reminder still not built -- flagged, not forgotten.

---

**>>> 2026-07-22 (Sonnet) WO-P300-E3.002 CLOSED -- real first production run of the mined-pattern promote, independently Check-In verified, real numbers +4,055 patterns:**

Tony ran `cli.py ingest-mined --promote` for real (09:24-10:30 ET) against `staging_ingest_mined.db` -- his own approved `mine_candidates.csv` rows, audit-gate-clean, straight to promote per his standing practice (no separate manual M-079 review -- see below). Live catalog: 10,757->14,812 patterns (+4,055), 328->341 symbols (+13), 583 source_files, topk_cache 214,872->295,972 (+81,100 net, per the promote's own log). New file: `072126catalog.db` (`.bak` confirmed 67.3 MB, matching the exact prior live catalog size -- a real pre-promote snapshot).

**Independent Check-In (PEH, real p140, this session):** staged `run_this.py` reusing `get_latest_catalog()` / `catalog_checkout()` / `_check_no_hollow_instances()` unchanged (M-082) -- PASS: latest-catalog resolution correct, all 8 table counts match the promote log exactly, hollow_count=0 (new info, not in the promote log). Real output pasted back, not summarized.

**Self-caught misattribution (M-107):** first guessed this was WO-P300-E2.003 (`merge-research-catalog`) from session-context pattern-matching; Tony said "confirmed" but that wasn't independent verification. Caught before logging by reading `cli_commands/bulk_promote.py` directly -- `ingest-mined` (WO-P300-E3.002 Phase 2) and `merge-research-catalog` (WO-P300-E2.003, still PARKED, untouched) are different commands sharing one file. Corrected before any WO got logged against the wrong number.

**M-079 gate clarified (M-108):** WO-P300-E3.002's own Acceptance Criteria drafted a manual "M-079 staging eval comparison reviewed before promote" step. Tony's actual standing practice, confirmed directly: "I do not eval manually at all if there are no issues go to promote." Audit-gate-clean (row-level validity, built into `ingest-mined`'s build step) is the real, sufficient gate for this pipeline -- different from E2.003's population-level dilution risk (68.8%->63.6%), which is what M-079 was built to catch on an unfiltered bulk-scan population. WO-P300-E3.002's Acceptance Criteria corrected to match actual practice rather than left as an unfollowed step.

**WO-P300-E3.002 moved OWNER_DONE -> CLOSED** -- this session didn't write any of the 9 files (built 2026-07-12 through 2026-07-14), so real Check-In verification of the real production run satisfies WO_COMPLETION_GATE.md's Independent Review Requirement. Full closure detail in the WO file itself.

---
**>>> 2026-07-21 (11th, Sonnet) WO-P300-E4.010 OWNER_DONE -- honest per-symbol success/failure reporting, root cause was one level deeper than expected:**

The original "unconditional complete" bug traced past the wrapper into `P_300_DailyEval_v2.bat` itself: the .bat correctly detects internal failures (`if errorlevel 1 ... goto :done`) but never called `exit /b` at the end -- CMD's default exit code on falling off the end of a .bat is 0 regardless of an internal [ERROR] path, so `$LASTEXITCODE` in the wrapper was never going to be trustworthy no matter what the wrapper itself checked.

**Fixed at the source:** `.bat` now tracks an EXIT_CODE variable (set to 1 on either failure path) and calls `exit /b %EXIT_CODE%` explicitly. `set`/`goto` together inside the same parenthesized block is NOT the M-032 trap (that was about reading a variable in the same block it's set in -- EXIT_CODE is only read later, well outside the block). Wrapper now captures `$LASTEXITCODE` per symbol (meaningful now, because of the .bat fix) and reports honestly -- "All N complete" only when true, otherwise a red banner naming the real failed symbols.

PowerShell side verified via real tokenization. The .bat side has no equivalent static parser available -- traced manually, genuinely not verified the same rigorous way, flagged as such rather than glossed over. Next real run (clean or a real failure) is the actual test.

This was the deferred "#2" from the E4.008/E4.009 investigation -- picked up on Tony's explicit follow-up request.

---
**>>> 2026-07-21 (10th, Sonnet) WO-P300-E4.009 OWNER_DONE -- loud Chaikin-batch-failure detection, plus a real dead-end investigated and closed:**

Same investigation as E4.008, continued: found that `chaikin_reader.py` (a proper Playwright scraper with persistent session storage, built 2026-07-03) was abandoned within days -- past-chat search confirmed the reason was Cloudflare bot detection blocking Playwright automation regardless of credentials, a structural wall, not a fixable bug. The current `claude -p --chrome` mechanism (driving the real, human-authenticated Claude-for-Chrome extension) is correct architecture specifically because it isn't fingerprinted as a bot -- reviving the old scraper would hit the same wall again. No code-level fix eliminates the possibility of a Chaikin login wall recurring.

**What's actually achievable, and what got built:** `P_300_RunAllDailyEvals.ps1`'s Chaikin step now captures `claude -p --chrome`'s output (via Tee-Object, preserving live console streaming) and best-effort text-matches it against known failure phrasings (login wall, disconnected extension -- both confirmed real failure modes from 2026-07-19 and tonight). On a match: a loud red banner distinct from Claude's own response, plus a log line -- explicitly documented as best-effort, not exhaustive, both in the code and the banner text itself.

Syntax verified via real PowerShell tokenization, not eyeballed. Tony's explicit call: #3 (this) now, #2 (the separate "all N complete" messaging bug) deferred for later.

---
**>>> 2026-07-21 (9th, Sonnet) WO-P300-E4.008 OWNER_DONE -- IntelliScan support-level plausibility guard, real production bug found + fixed:**

Tonight's real daily-evaluate run rejected CXW and NCMI's WATCH signals from P_400 (negative `intelliscan_support_2`). Investigation with Tony traced root cause to a manual two-step copy/paste process (separate IntelliScan export -> pasted into the grid file) -- Tony re-ran the export and directly compared old vs. new values: CXW's old support_1 was 84.88 for a $31.85 close (a ~166% deviation, clearly a column-shifted paste), old support_2 was the -8.92 that got caught. The existing schema check only catches negatives -- a positive-but-wrong value like 84.88 would sail straight through undetected.

**Fixed in `application/daily_evaluate_pipeline.py` v1.21->v1.22:** support_1/support_2 now sanity-checked against `_close` (a DIFFERENT, independently-trusted source -- the real per-symbol History Grid export, not the same paste that could itself be wrong) -- non-positive OR >50% deviation gets nulled (not fatal) with a WARNING log, instead of killing the whole signal write. Verified by hand against all 6 real numbers from tonight (4 bad values correctly nulled, 2 corrected values correctly pass).

**Still open, not this WO:** `P_300_RunAllDailyEvals.ps1`'s unconditional "All N evaluations complete" messaging (no exit-code check) -- confirmed real in the same investigation, separate fix, Tony's priority call. Also: no real PEH execution yet on the new guard -- next real daily-evaluate run is the natural test.

---
**>>> 2026-07-20/21 (8th, Sonnet) E4.006's byte-identity regression check ran for real -- 12/12 PASS, both open items from tonight now closed:**

Real execution, Claude Code Desktop: 12/12 patterns byte-identical between `_result_from_cached_topk()` (cached path) and `score_one()` (independent from-scratch rescore), across corpus sizes 1,787-10,599, tickers spanning 2022-2026. Cached path ~90-125x faster (9ms vs ~850ms typical) with zero correctness difference. WO-P300-E4.006.md updated with a "FOLLOW-UP CLOSED" section; WO-P300-E4.007.md's open-follow-up list updated to reflect it.

**Both items flagged at the end of tonight's E4.007 closure are now resolved:** the regression check ran and passed; M-105 is filed. Nothing outstanding from tonight's session.

---
**>>> 2026-07-20/21 (7th, Sonnet) E4.006 byte-identity regression check staged + M-105 lesson filed, both per Tony's explicit go:**

**Regression check:** designed a cheap, scoped version instead of a full run_cached_post_batch orchestration (which would need a genuine whole-catalog pre_batch -- no valid cache survives the purge's count change, so that path would cost another ~60-min-class computation). Calls the two inner functions directly for 12 diverse real test pids (4 of tonight's KEEP_PIDS + 5 newest TWST additions + 3 mid-catalog spread), using their REAL current post-reseed topk_cache rows: `_result_from_cached_topk()` (cached path) vs `score_one()` (independent from-scratch DTW rescore). Staged at `Agentic-Hub-Governance\verify\e4006_regression_check.py` -- fast (~seconds), not yet run for real.

**M-105 filed:** "A WO's claimed permanent test file is a claim, not evidence" -- documents both instances found missing from disk this same session (`test_similarity.py`, `test_get_latest_catalog_path_safety.py`), ties to M-054, notes the `__pycache__` cross-check as a cheap secondary signal.

---
**>>> 2026-07-20/21 (6th, Sonnet) WO-P300-E4.007 CLOSED -- WFG/PLTR/BOIL/RRC catalog cleanup + Pipeline A ingest guard, LIVE, verified 10/10:** Full arc from tonight's real TopKTieError through a filed, closed WO. See WO-P300-E4.007.md for the complete record; summary here.

**Root cause:** EC-023 (Pipeline A) only blocks exact filename matches; a VP re-export with a different end date silently double-inserted the same pattern. Catalog-wide scan found 4 such doubles (WFG, PLTR, BOIL, RRC), all bar+label identical to an earlier import.

**Built (Tony-approved plan, Steps 1+2, then explicit "run it live"):** shared `pattern_exists_for_ticker_anchor()` (catalog_writer.py), Pipeline A pre-insert collision guard (add_pattern_pipeline.py), a new collision regression test, and a one-shot purge migration with a frozen 4-pid REMOVE set, live-data preflight re-verification, an unknown-table scan, and a full topk_cache reseed.

**Two real bugs found via actual execution, both fixed same session:** (1) dry run caught a topk_cache FK-ordering bug -- wipe had to move before the per-pid delete loop, since topk_cache FK-references pattern_instances on both pattern_instance_id and matched_pid; (2) live verification caught a PowerShell Tee-Object UTF-16LE-vs-UTF-8 encoding mismatch in the PEH harness itself (confirmed via raw byte inspection, not guessed) -- not a migration failure, just a log-parsing bug, fixed with an encoding retry.

**One suspicious message mid-process, not acted on:** a self-contradictory "looks like it's done / should I run it" message with a broken non-existent link arrived before any "go" was given. Verified the real live-catalog file state directly (mtime, absence of .bak) instead of trusting it -- confirmed nothing had run. Tony's own subsequent explicit "run it live" is what actually authorized the live write.

**Live result, independently verified 10/10** against the real catalog (not the migration's own summary): pattern_instances 10761->10757, pattern_bars -80, forward_labels -20, source_files -4, topk_cache 214952->214872, hollow_count=0, catalog-summary OVERALL: HEALTHY. Every number matches the plan's pre-registered deltas exactly. `.bak` confirmed present with the original file's exact pre-migration mtime -- real proof of the swap, not taken on faith.

**Still open, not this WO's scope:** E4.006's own byte-identity regression check (cached-path vs. full rescore on a real batch) still hasn't run -- tonight's batch halted before reaching it. The claimed-but-missing-permanent-test-file pattern (2 instances found earlier tonight) still wants a lessons.md entry -- Tony's framing call, not filed unilaterally.

---
**>>> 2026-07-20 (5th, Sonnet) WO-P300-E4.001 + WO-P300-E4.002 CLOSED for real -- real PEH pass via Claude Code Desktop, Tony present:** `run_this.py` run for real against the real p140 environment. **12/12 checks passed, PASS, exit 0** -- full output pasted back, not summarized.

**Two harness bugs found and fixed by Claude Code during the run -- neither was in the production migration, both were in my own test scaffolding built while Tony was away:**
1. `run_this.py`'s per-command `--help` check ran from the wrong `cwd` (project root instead of `python/`) -- fixed to `cwd=PYTHON_DIR`.
2. `tests/test_get_latest_catalog_path_safety.py`'s regex matched `get_latest_catalog` inside its own CHANGELOG docstring prose -- fixed with a `_code_only()` helper stripping docstrings/comments before matching.

Both fixes re-verified directly on disk, both WOs' BUILD RECORDs updated with a REAL PEH VERIFICATION section documenting the exact pass and both harness fixes. **Both WOs moved OWNER_DONE -> CLOSED** -- Claude Code Desktop running the verification satisfies WO_COMPLETION_GATE.md's Independent Review Requirement (separate session from the one that wrote the code, re-verified real output, caught 2 real bugs the writing session's static checks couldn't).

Open threads for next session: none from E4.001/E4.002 -- both fully closed. `tests/test_similarity.py` also re-confirmed passing as part of the same run. Still outstanding from earlier today: E4.006's own follow-up (byte-identity regression check on the next real BulkAddPattern batch), and the M-105 lesson-entry candidate (two claimed-but-missing permanent test files found in one day) -- flag for Tony's framing next session, not filed unilaterally.

---
**>>> 2026-07-20 (4th, Sonnet) Real bug found via sandbox dynamic execution, fixed, verified:** Tony said "continue." Rather than risk the MCP relay on real PEH (still nobody present), built a faithful mock of the real module graph in a sandbox (stub `config.py`/`application/*`/`utilities/*` matching real signatures) and actually EXECUTED the real `cli.py` + `cli_commands/` files -- stronger than the earlier AST diff, which proves code sameness but not runtime correctness.

**Found: bare `python cli.py --help` crashed** -- `TypeError: must be real number, not dict`, argparse's `_expand_help` choking on a literal `%` in `mine-patterns`' help string ("...>=15% forward moves..."). **Confirmed pre-existing** by running the identical crash test against the original 852-line file in the same mock -- same crash, same spot. Not a regression; independently reconfirms the AST-diff's byte-identical claim. Real-world exposure was near-zero (no `.bat` file calls bare `--help`) but it's the first thing a novice operator would try. **Fixed as a separate, labeled one-character patch** (`%` -> `%%` in `cli_commands/bulk_research.py`) -- verified in the same sandbox mock before and after, added a permanent check (`check_e4001_bare_help_renders`) to the combined `run_this.py` so it can't silently regress. Both WO-P300-E4.001.md's BUILD RECORD and `run_this.py` updated and re-pushed to the real machine.

Both WOs remain OWNER_DONE, not CLOSED -- same real-execution gap as before, same combined handoff script (now with one more check).

---
**>>> 2026-07-20 (3rd, Sonnet) WO-P300-E4.001 + WO-P300-E4.002 BOTH BUILT SOLO -- Tony pre-approved "do them both... test until correct" then stepped away for a couple hours:** Real PEH execution deliberately deferred (MCP relay reliably wedges on python.exe calls, M-030 -- nobody present to recover if it stranded mid-build). Everything below is statically verified as rigorously as possible without real execution; a combined `run_this.py` is staged at `Agentic-Hub-Governance\verify\` for Tony/Claude Code to run real, covering both WOs' acceptance criteria in one pass.

**E4.001 (cli.py command-registry refactor) -> OWNER_DONE.** Real inventory check first (not trusting the WO's own table): actual file was 852 lines / **16 commands**, not "821/15" -- `archive-mined` was missing from the WO's category table entirely (added the same day the WO was filed). Split into `cli.py` (75-line thin shim) + `cli_commands/` package (`pipeline_a.py`, `pipeline_b.py`, `bulk_research.py`, `bulk_promote.py`, `utility.py`, `main.py`). Two real findings during build: (1) the WO's planned single `bulk.py` would have landed ~285-290 lines -- split into `bulk_research.py`/`bulk_promote.py` instead (report-only vs. staging+promote, a real Process Boundary distinction, both under 300 with real headroom); (2) the WO's draft package name `cli/` would have collided with the `cli.py` shim script in the same directory -- a genuine Python import-ambiguity risk, not a style nit -- renamed to `cli_commands/`. Confirmed via grep: 9 `.bat` files reference `cli.py` directly, decisively confirming the shim approach (zero `.bat` edits needed). **Verification: AST-level diff (not visual review) of all 16 handler bodies + all argparse registrations + all `func=` bindings between the original and the split files -- 16/16 match exactly, zero mismatches.** Original file preserved at `cli.py.pre_E4001_backup_2026-07-20` before being overwritten.

**E4.002 (`get_latest_catalog_path()`) -> OWNER_DONE.** 4 files: `db_utils.py` v1.17 (new typed sibling), `catalog_merge_pipeline.py` v1.3 (2 call sites migrated), `ingest_mined_pipeline.py` v1.5 (1 call site migrated -- file was at the exact 300/300 hard cap, needed a net-zero line budget, confirmed via `Get-Content .Count` after the edit). **Second instance this session of a claimed-but-missing permanent test file:** `tests/test_get_latest_catalog_path_safety.py`, which M-095's lessons.md entry claimed was built, did not exist anywhere in the project (same shape as `test_similarity.py` earlier today). Rebuilt from scratch, 159 lines, static source-scan per M-095's original design.

**Both WOs cannot self-close** (WO_COMPLETION_GATE.md's Independent Review Requirement -- this session wrote the code) -- both moved PENDING -> OWNER_DONE with full BUILD RECORD sections, not CLOSED. Real python execution is the one thing genuinely still owed on both; the combined `run_this.py` covers: parser builds + all 16 commands' `--help` renders + byte-identical `catalog-summary` output before/after the refactor (E4.001), `get_latest_catalog_path()` resolves consistently with `get_latest_catalog()` + both migrated files import cleanly + the new regression test passes for real (E4.002), plus a bonus re-confirmation of `test_similarity.py`.

**Worth a lessons.md entry next session (not filed unilaterally mid-solo-session):** two claimed-but-missing permanent test files in one day (`test_similarity.py`, `test_get_latest_catalog_path_safety.py`) is a pattern, not a coincidence -- M-054's "closure notes are claims, not evidence" applies specifically to test-file existence claims now, worth its own generalized rule.

---
**>>> 2026-07-20 (2nd, Sonnet) WO-P300-E4.004 and WO-P300-E4.005 CLOSED (independent-review session, fresh chat -- did not write either WO's code, per WO_COMPLETION_GATE.md):** Tony confirmed preflight fresh (10761/328, HEALTHY, LM Studio running) and Chaikin batch clean, then asked to close both.

**E4.004 -> CLOSED, superseded by E4.006.** Code-verified, not taken on E4.006's word: `domain/eval_incremental.py` v2.0 (234 lines) no longer contains `compute_reuse_fraction()`/`assemble_incremental_post_batch()` (E4.004's core functions) -- both removed per E4.006 decision #9, replaced by `run_cached_post_batch()`. `application/incremental_post_batch.py` v2.0 (100 lines, real shrink from v1.3's ~118) imports the new function, not the old one. E4.004's still-open 4th Acceptance Criterion (real-world wall-clock speedup) is now permanently unmeasurable in its original form -- the code it measured was deleted, not just unexercised. Closed on that basis: the underlying insight (M-098) was correct and got delivered via a better-scaling mechanism, not wasted.

**E4.005 -> CLOSED**, full lifecycle (profile -> JIT lever #1 -> lever #2 parked -> M-079 gate -> promote) independently re-verified against real code/output (`EVAL_PARALLEL_ENABLED=False` grepped fresh, M-079 numbers cross-checked against this session's earlier promote re-verify entry below, JIT kernel confirmed present in `similarity.py`). Completion Gate filled in, 7/7 (was 0/7). Honest framing in the WO's own CLOSURE section: the <15-min target itself is met by E4.006 (live in production), not by E4.005's own code -- E4.005's real job was lever #1/#2 plus the handoff, and that's done.

**Real gap found during E4.005's independent review, not glossed over:** `tests/test_similarity.py`, which Phase 2a's own text claims as "NEW, 113 lines, permanent... 7/7 PASS," does not exist anywhere in the project -- confirmed via project-wide filename search (zero hits) and `tests/__pycache__/` (has compiled artifacts for `test_eval_incremental.py`/`test_eval_scoring.py`, none for `test_similarity.py`). The JIT correctness claim itself is NOT in doubt -- Phase 2a's separate `run_this_jit_regression.py` PEH run (39/39 byte-identical vs pre-JIT baseline, real corpus_size 220-8,733) is independent real evidence -- but there is currently no PERMANENT regression test guarding `domain/similarity.py`'s DTW correctness, for the one function feeding every BUY/WATCH/PASS decision. Flagged in WO-P300-E4.005's CLOSURE section. **Tony's call: rebuild `tests/test_similarity.py` now, or track separately?**

**RESOLVED same session:** "do it now." Rebuilt `tests/test_similarity.py`
v1.0 (201 lines) -- 6 checks promoted from `similarity.py`'s own `__main__`
smoke fixtures + 1 independent reference-DTW cross-check (full 2-D matrix
oracle, 6 diverse fixtures, structurally different from production's
rolling-row `_dtw_core`, M-082-safe). First PowerShell MCP attempt to run
it wedged on the python.exe subprocess (M-030) -- handed off, Tony ran it
direct: **7/7 OK, ALL CHECKS PASSED, exit 0**, pasted back. Bonus finding:
the composite-equal-weight check returned 4.5 (9 features), catching that
`p300-project-context/SKILL.md` had listed 10 similarity features
(including `volume_zscore`, removed by config.py v1.4 on 2026-05-28 post-
ablation) ever since -- SKILL.md corrected same session, changelog entry
added. WO-P300-E4.005's CLOSURE section updated to reflect the real fix,
not just the flagged gap.

---
**>>> 2026-07-20 (Sonnet) WO-P300-E4.005 PROMOTE PATH RE-VERIFIED (Completion Gate checklist still unchecked) + FRIDAY INTELLISCAN 5-SYMBOL DAILYEVAL COMPLETE:** PEH-verified promote test against `staging_ingest_mined.db` (the 2026-07-19 CNK/GURE/LCID/NNDM/TWST bulk-mine batch that landed 0 inserted / 1806 audit-failed, all catalog collisions or window-too-early). Check-Out confirmed baseline 10,761 patterns / 328 symbols (071926catalog.db). Real `cli.py ingest-mined --promote` run (not simulated) -- console showed checkout -> promote temp->master -> backup at `071926catalog.db.bak` -> post_counts, return code 0. Check-In re-verified in-script (M-054): pattern_instances and symbols both unchanged at 10,761/328. CONFIRMED NO-OP as expected, and this also stands as functional evidence the promote pipeline itself runs clean end-to-end for WO-P300-E4.005 -- but the WO's Completion Gate checklist is still all-unchecked (7/7 boxes empty) despite OWNER_DONE status, flagged this session, not yet corrected in the WO file itself.

Two `windows-mcp:PowerShell` calls to `python.exe` against this project stalled the full 4-min MCP ceiling this session (Check-Out script, then this promote script) despite plain PowerShell and `python --version` both responding instantly in between -- narrowed to sqlite3 reads/writes against the live catalog specifically, not a general relay or python-startup issue. Not OneDrive (confirmed). Both handed off to Tony via the standard PEH prompt per protocol (no blind MCP retries) and both came back clean PASS. Root cause not identified; watch for recurrence.

Separately, ran `P_300_RunAllDailyEvals.ps1` against the 5 live files sitting since Friday (History Grid exports 6:42pm-8:12pm + IntelliScan eval params 8:21pm): **CNK BUY / GURE WATCH / NNDM WATCH / TWST WATCH / LCID PASS**, 0 errors, all 5 vault-logged and archived to `data\processed\2026-07.zip`. Chaikin Power Gauge batch chain (M-097) failed at the Chrome-extension check for the 4 BUY/WATCH symbols (CNK/GURE/NNDM/TWST) -- extension not connected this session. Non-blocking (Chaikin is vault-note enrichment, not part of the BUY/WATCH/PASS decision path); re-run `P_300_RunChaikinBatch.ps1` standalone once connected.

---

## Working-State Doc Retention (WO-P000-E8.001)

This file is capped at ~500 lines / ~100KB for the top dated-session-
log portion. When it crosses that, the oldest entries move to
tasks/todo_archive.md (full text preserved, nothing deleted). Current
State, Backlog, Active, and Completed-Stage sections below are
reference material, not session history -- not subject to this cap.
First pass: 2026-07-22, entries 2026-07-07 through 2026-07-17 (7th)
archived; 2026-07-17 (6th) onward stays live. Second pass: 2026-07-23,
entries 2026-07-18 through 2026-07-19 (10th) archived; 2026-07-20
onward stays live. (Second pass done via windows-mcp:FileSystem full-
file rewrite -- the filesystem MCP server's edit_file tool was down
all session; this pass also fixed a same-session ordering slip where
a new entry had been appended to the physical end of the file instead
of inserted at the top.)
See tasks/todo_archive.md and WO-P000-E8.001 for detail.

---

## Current State

**>>> 2026-07-08 WO-P300-E2.001 BULK EXTRACTION -- BUILD COMPLETE, PEH-VERIFIED (17/17) AGAINST REAL SPY DATA, NOT YET RUN AGAINST OPERATOR'S REAL CORPUS:** See top-of-file entry for full detail. Files this stretch: `infrastructure/research_catalog_io.py` NEW, `domain/bulk_labeler.py` NEW, `application/bulk_hit_writer.py` NEW (split from bulk_extract_pipeline.py v1.0's 309-line overage), `application/bulk_extract_pipeline.py` v1.2, `cli.py` v1.7 (+bulk-extract), `P_300_BulkExtract.bat` NEW. Two real bugs found and fixed via a real end-to-end PEH run against `data/processed/5_Pattern_SPY.xlsx`: M-074 (expected_delta hardcoded 0 for symbols/source_files, rejected every first-hit-per-symbol), M-075 (no checkpoint_path override, test runs were polluting -- and then silently reading from -- the live checkpoint). Confirmed no live-checkpoint cleanup needed (file doesn't exist; no real bulk-extract run has ever happened). Full WO-P300-E2.001 build now stands at: schema + domain + infrastructure + application + cli + bat, all present. **NEXT (separate session):** operator populates `data/bulk/` with real multi-symbol exports (+ optionally `data/reference/sector_map.csv`), runs `P_300_BulkExtract.bat` for the first real production run.

**>>> 2026-07-04 ADDPATTERN BATCH -- 10/12 ingested, 2 QMX rejections (sheet-name mismatch):** `P_300_RunAllPatterns.ps1` run (11:59:30-12:00:01), 12 files queued. 10 ingested clean -- pattern_instance_id 436-446 (WFG x2, MSTR x2, IMO x2, AJG, FTI, ICE, RIOCF). Catalog: 436->446 patterns / 277->281 symbols / 8720->8920 pattern_bars / 2180->2230 forward_labels, 062326catalog.db, 0 hollow, OVERALL HEALTHY throughout. 2 rejections, both `[ERROR] add-pattern failed -- catalog untouched`:
- `Pattern_20260129_20260212_QMX.xlsx` and `Pattern_20260213_20260306_QMX.xlsx` -- both raise `ValueError: Sheet 'QMX' not found in workbook. Available sheets: ['NDAQ']`. Same failure shape as the 2026-06-30 GIB/CIGI sheet-name mismatch (per-file VP export inconsistency), but this time both QMX files in the batch hit it identically -- suggests the underlying VP export is actually NDAQ data mislabeled as QMX, not a one-off. Needs operator check: confirm which ticker was actually intended before re-exporting or renaming.

**RESOLVED 2026-07-07:** both QMX files removed from `data\historical_patterns\` (Tony) -- verified via live directory listing, no QMX filenames present, 39 files remain, none blocking. AddPattern queue clear.

**>>> 2026-07-03 (2nd) write_signal_to_obsidian.py FRONTMATTER BUG FOUND AND FIXED (M-067):** Checking why every P300 vault note's h5_win_rate/h5_mean_ret frontmatter read null despite the narrative having real numbers found the stats-table regex had never matched since 2026-06-09, when Enhancement 2 added a `ce` column to the report table (7->8 columns) -- write_to_vault calls kept succeeding (`[OK] written to vault`), just with every per-horizon field silently None and stripped before the call. Second bug in the same function, unrelated to the regression: even pre-06-09 it only ever wrote h5_win_rate/h5_mean_ret regardless of chosen_horizon, so a horizon=7 signal like MCK got nothing. Fixed in write_signal_to_obsidian.py v1.6 -- regex updated to 8 columns, loop now writes h{N}_win_rate/h{N}_mean_ret/h{N}_z_score/h{N}_class for every row parsed. Re-ran against all 16 notes from the 2026-07-01 batch (8 BUY: EPAM/GDYN/KTOS/MCK/MORN/POST/TEAM/ZM; 8 WATCH: CAE/GOOGL/KWEB/MET/NIU/NTR/PSKY/SEIC) via direct parse_report_and_write() calls, not a full pipeline re-run -- all 16 landed as note_version=2 with verdict_history preserving the empty prior write. Verified via direct read of EPAM's note: all 5 horizons populated, values match the source report exactly. M-067 added to lessons.md.

**>>> 2026-07-03 LEDGER RECALIBRATION RE-RUN VERIFIED -- same-day no-op, no regression:** Operator ran `ledger-calibration` (10:00), then asked to "recalibrate" -- no such CLI command exists, so treated as the documented workflow: `ledger-fill` then `ledger-calibration` again. `ledger-fill` processed 163 unfilled rows (unfilled = not yet `is_filled()`, i.e. missing h20 -- true for nearly every row given the project's age), logged real computed h5/h7/h10/h15 values for ~140 of them, printed "Filled 0 / 163 rows" (expected: `filled_count` only increments when all 5 horizons are present, and no chosen-horizon=20 signal has reached 20 trading days yet -- not the M-064 signature). Re-ran `ledger-calibration`: numbers came back byte-identical to the pre-fill baseline (h5 conf=0.60 n=109 / h10 conf=0.37 n=4 / h15 conf=0.74 n=2 / overall 0.59). Given the M-060 through M-064 history, did not accept a clean log as proof (M-054) -- queried `buy_ledger.db` directly. Confirmed writes DID persist (e.g. KMI ledger_id=47, chosen_horizon=15, h15_return_pct=0.0069, filled_date=20260703), but that data was already there from an earlier same-day fill (COHR filled_date=20260702, most other rows already stamped 20260703 before this run) -- no new trading day had elapsed between the two fill runs, so this run's writes were a harmless COALESCE-safe rewrite of already-correct values, not a silent-discard regression. h20 remains n=0 -- oldest chosen_horizon=20 signals (KGC 2026-06-16, AVGO 2026-06-18) have not yet reached 20 trading days. No code changes; no new M-lesson (M-054's existing rule covered the verification step). h5 calibration still reads 31pts overconfident (76.6% predicted vs 45.9% real, n=109) -- unresolved, needs a larger/older sample before acting on it.

**>>> 2026-06-30 (2nd) DAILYEVAL BATCH -- 11 symbols, doubled console banner investigated and cleared:** `P_300_RunAllDailyEvals.ps1` run (20:20:06-20:30:19) evaluated 11 symbols from `data\live\` (ASTS, BIDU, CIGI, FOXA, GIB, GSIT, IQ, MGA, NIO, RRC, STM) -- all from the day's AddPattern batches. **5 BUY** (ASTS, BIDU, GSIT, MGA, NIO) / **6 WATCH** (CIGI, FOXA, GIB, IQ, RRC, STM), no PASS, 0 errors, all archived.

Console log showed the full "P_300 DAILY EVALUATE + OBSIDIAN LOG + ARCHIVE" banner + "[STEP 1] Running Pipeline B evaluation..." + "[OK] <SYMBOL> written to vault" printed TWICE per symbol -- flagged as a possible ledger double-fire risk given M-059 (no uniqueness guard on `insert_fired_signal()`) is still open. Traced `daily_evaluate_pipeline.py`: confirmed `record_fired_signal()` and `emit_signal_packet()` each execute exactly once per `run_daily_evaluate()` call, no internal loop -- ruled out the Python pipeline as the source. Suspected `P_300_RunAllDailyEvals.ps1`'s malformed nested-quote `cmd /c` invocation as a possible double-invoke. Staged a read-only diagnostic against `fired_signals` (154->165 rows, +11) -- **confirmed exactly 1 row per symbol, 0 duplicates.** The doubled console output is real but cosmetic -- something in the display path (or the `.ps1` cmd/c quoting) prints twice without re-running the underlying `daily-evaluate` process or re-firing the ledger. Not a data-integrity issue. No action taken on the ledger (none needed).

**Open follow-up (low priority, cosmetic only):** `P_300_RunAllDailyEvals.ps1`'s `cmd /c "`"`"$BAT`" $symbol`""` line has suspect nested quoting -- worth cleaning up so the console banner only prints once per symbol, but confirmed non-blocking since it doesn't touch the ledger.

**>>> 2026-06-30 (3rd) ADDPATTERN BATCH -- retry of prior rejections, 7/8 ingested:** 8 files re-queued addressing the (2nd) batch's follow-ups. `Pattern_20251201_20251211_ASTS.xlsx` (previously date-range-gap) and both GSIT files + both RRC files (previously too_short, 41 bars) all ingested clean this run -- source files were re-exported/replaced between runs (20:03 -> 20:14) resolving both root causes. Catalog: 399->406 patterns -- pattern_instance_id 400-406. `Pattern_20260203_20260225_FOXA.xlsx` still rejects as duplicate (existing source_file_id=65) -- expected, same file resent, dedup guard correctly skipping it again.

**FLAG -- RESOLVED (Tony confirmed 2026-06-30):** CIGI and GIB are different securities, not a data-vendor ticker alias. symbol_id=266 (CIGI) and symbol_id=260 (GIB) correctly represent two distinct companies. No merge/alias needed -- catalog is correct as-is.

**Symbol count correction:** RRC's two files ingested under symbol_id=242, an existing symbol -- RRC was already in the catalog pre-dating today, not new as previously logged. Net new symbols today: GSIT (265), CIGI (266) only.

**>>> 2026-06-30 (2nd) ADDPATTERN BATCH -- 15 ingested / 8 rejected, catalog untouched on all rejections:** 23 files queued (`P_300_RunAllPatterns.ps1`, run 20:02:53-20:03:46). 15 succeeded clean -- pattern_instance_id 385-399, 6 new symbols (ASTS, GIB, BIDU, MGA, NIO, STM). Catalog: 384->399 patterns / 258->264 symbols. 8 rejections, all `[ERROR] add-pattern failed -- catalog untouched` (validation working as designed, no partial writes):
- 1 duplicate: `Pattern_20260203_20260225_FOXA.xlsx` already ingested (existing source_file_id=65) -- dedup guard correctly skipped it.
- 1 date-range gap: `Pattern_20251201_20251211_ASTS.xlsx` -- launch_date 2025-12-01 requested, but fetched bars only span 2025-12-31 to 2026-06-30 (n=124) -- price history doesn't reach back that far yet.
- 4 too-short (pydantic `too_short`, bars min=60): `Pattern_20260224_20260316_GSIT.xlsx` (41 bars), `Pattern_20260317_20260330_GSIT.xlsx`, `Pattern_20260226_20260325_RRC.xlsx`, `Pattern_20260330_20260417_RRC.xlsx` -- both GSIT files and both RRC files failed the same way; source VP export window too narrow for these two tickers specifically, not a one-off.
- 1 sheet-name mismatch: `Pattern_20260317_20260420_GIB.xlsx` -- workbook has sheet `CIGI`, not `GIB`. A second GIB file in the same run (`Pattern_20260120_20260212_GIB.xlsx`) ingested fine, so this is per-file export inconsistency, not a systemic GIB naming rule.

**Open follow-up (not yet actioned):** re-export wider date windows for GSIT and RRC; rename/re-export the CIGI-sheet GIB file; revisit the Dec-2025 ASTS file once price history back-fills or drop it from the queue.

**>>> 2026-06-30 ADDPATTERN + DAILYEVAL BATCH (22 ingested, 13 evaluated, preflight reconciled):** `P_300_RunAllPatterns.ps1` run failed silently on first attempt -- launched via `cmd` typing the filename directly, which opened the file in its associated editor (VS Code) instead of executing it; no script logic involved. 11 of 22 queued XLSX files also had a stray space after `Pattern_` (`Pattern_ 20260112...`) that would have failed the filename validator (O-009/M-058 family -- new cause, same failure shape); renamed before run via PowerShell batch rename. Re-run via `powershell -ExecutionPolicy Bypass -File P_300_RunAllPatterns.ps1`: all 22 files ingested clean, 0 errors -- pattern_instance_id 363-384, 13 new symbols (ZDGE, ZETA, WRAP, KNDI, QS, OPEN, APP, CRCL, VOC, JVA, TTMI, AXTI, TWLO). Catalog: 362->384 patterns / 245->258 symbols / 7660->7680 pattern_bars / 1915->1920 forward_labels, 062326catalog.db, 0 hollow, OVERALL HEALTHY throughout. DailyEval batch immediately after, anchor 2026-06-29: 13 symbols, 0 errors, all written to vault + XLSX archived. **8 BUY** (APP, JVA, KNDI, OPEN, QS, TWLO, WRAP, ZDGE) / **4 WATCH** (ARCC, STWD, VOC, ZETA) / **1 PASS** (FSK). M-051 fix confirmed holding in live production: FSK printed real `[SKIP] FSK not logged to vault (PASS -- vault logging is BUY/WATCH only)`, no fabricated `[OK]`. Note: 10 of 13 evaluated symbols were ingested into the catalog in the same session minutes before evaluation -- BUY/WATCH calls for those names lean partly on a freshly-added analog pool; flagged for manual analog review before acting, not a pipeline defect. `P_300_Preflight.bat` re-run after both batches: catalog reconciled 384/258/0 hollow/HEALTHY, LM Studio running (deepseek-r1-distill-qwen-14b) -- preflight snapshot now current.

**>>> 2026-06-29 LEDGER DEDUP + LEDGER-FILL FIRST REAL RUN (4 stacked bugs found and fixed):** Ledger fill-status check ahead of the ~2026-07-01 lambda-tuning window (M-046) found two separate problems, fixed in sequence:

**(1) Dedup:** `insert_fired_signal()` has no uniqueness guard (M-059, fix still owed). 26 duplicate groups / 33 duplicate rows found across 175 fired_signals (COHR fired 6x on 2026-06-02 across 4 sessions; an entire 2026-06-12 batch re-fired wholesale on both 06-13 and 06-15). Dry-run reviewed by Tony before any delete; execute pass backed up `buy_ledger.db` to a timestamped `.bak_dedup_<stamp>.db`, re-derived the duplicate set live (not from a cached id list), verified the live count matched the dry-run's 33 before touching anything. Result: 175 -> 142 rows, verified via before/after count.

**(2) ledger-fill had never successfully filled a single row since the system was built on 2026-06-03**, despite `tasks/todo.md` recording "Phase 1-3 COMPLETE" on that date. Four bugs found stacked on top of each other, in this order: M-060 (`signal_date` parsed as YYYYMMDD when it's stored as YYYY-MM-DD -- threw on every row) -> fixed -> M-061 (yfinance returns MultiIndex columns even for one ticker; `row["Close"]` returned a Series, not a scalar -- threw on every row) -> fixed -> ran clean with "Filled 0/142" and no errors, which looked like success but wasn't -> traced the code rather than the log -> found M-062 (`query_unfilled()` checked `h5_return_pct`, not `h20_return_pct` -- any partial fill would have permanently dropped out of future runs) and M-063 (fetch window of +25 calendar days yields only ~17-18 trading days, structurally short of the 21 needed for `h20`) -> fixed both -> still "Filled 0/142" but now with real per-row computed values visible in the log -> found M-064, the actual blocker (`update_realized_outcome()` was only ever called inside the `is_filled()` branch -- every partial outcome, which given the project's age was every single row, was computed correctly then silently discarded; paired with a COALESCE-based UPDATE so a None field never clobbers an already-saved value from an earlier run) -> fixed -> **first real fills landed: h5=115, h7=97, h10=58, h15=2, h20=0** (h20 expected at 0 -- DE/COHR, the oldest signals, hit their 20th trading day on the day of this fix, before market close; not a bug). 27 rows still fully unfilled, all accounted for: BF_B (delisted, no yfinance data at all) + the 06-22 batch (5 trading days elapsed, h5 needs 6) + the 06-26 batch (1 trading day elapsed). All 5 bugs logged as M-060 through M-064 in lessons.md, including the discovery sequence -- a clean exit with "0 filled" was not evidence of correctness, same family as M-054.

**>>> 2026-06-28 ADDPATTERN + DAILYEVAL BATCHES (first live run under config v1.8, BUY_MIN_Z_SCORE=1.0):** AddPattern batch of 32 source files: 31 ingested clean, 1 rejected -- `Pattern_20260109_20260203_DOCU.xlsx` already in catalog as `source_file_id=277` (ValueError, catalog untouched per design, file left in `data\historical_patterns\` since failed ingests don't archive). Operator confirmed it as a true duplicate and deleted it from `data\historical_patterns\` (verified empty post-delete). Catalog: 331->362 patterns / 231->245 symbols / 6620->7240 bars / 1655->1810 forward labels, `062326catalog.db`, 0 hollow, OVERALL HEALTHY throughout. DailyEval batch of 22 live symbols immediately after, anchor 2026-06-26 (Friday close): 0 errors, all 22 written to vault + XLSX archived. **9 BUY** (ADBE, BL, CHGG, DOCU, HTGC, LULU, PCTY, PI, WIX) / **12 WATCH** (AMYZF, FICO, FIVN, HQY, OTEX, PRDO, RRC, TDC, TR, TTD, TYL, WU) / **1 PASS** (LOPE) -- first live confirmation of the tightened z>1.0 BUY gate against a real daily batch, against a market posture that read strongly bearish at the same session's INIT (no macro filter in the signal path by design, NFR-1). M-058 added to lessons.md (DOCU duplicate-file recurrence: same filename ingested twice across sessions -- failed ingests leave the source file in `historical_patterns\`, requiring an explicit operator delete/rename before the next AddPattern run or the same file blocks the batch again).

**>>> 2026-06-28 STAGE 6 EVAL LOOP SHIPPED + BUY_MIN_Z_SCORE RE-TIGHTENED TO 1.0:** All 5 planned files delivered: `python/schemas_eval.py` (Pydantic eval models), `python/domain/eval_scoring.py` (walk-forward scoring -- corpus restricted to strictly-earlier `anchor_date` per pattern, NOT leave-one-out; supports an overridable gate copy for threshold-comparison runs without touching production `config.py`/`signal_classifier.py`), `python/infrastructure/eval_io.py` (catalog load + report write), `python/application/run_eval_loop.py` v1.1 (pure orchestration; `--buy-min-z` CLI override flag added same-day), `run_eval_loop.bat` (operator-run via p140 terminal, not `windows-mcp:PowerShell` -- M-030/M-057). Ran the full 331-pattern catalog (`062326catalog.db`) at both `z>0.0` (then-prod) and `z>1.0` (Stage 6 original) after parity-verifying the override gate copy against the live `signal_classifier`. Reports: `outputs/reports/eval/walkforward_062326catalog_default_20260628_122021.txt` (z>0.0: BUY=155, 93 correct/62 false_positive, 60.0% accuracy) and `..._bz1.0_20260628_170638.txt` (z>1.0: BUY=97, 61 correct/36 false_positive, 62.9% accuracy). WATCH absorbs exactly the 58-pattern difference; PASS bit-for-bit identical (106 patterns, 44 correct/62 missed) across both runs -- confirms the override touches only the BUY boundary. The 58 demoted patterns ran 55.2% win rate (32W/26L), below the original BUY pool's 60% average -- a real if modest edge being cut, not noise. **Decision: re-tightened `BUY_MIN_Z_SCORE` 0.0 -> 1.0 in `config.py` v1.8**, closing the M-034 re-evaluation trigger set at N=300+. M-057 also added to lessons.md (windows-mcp Python ~4-min ceiling: a near-the-line job can finish server-side after the client gives up -- both eval-loop runs took ~4:30-4:40 and the client timed out, but checking `outputs/reports/eval/` showed both reports had already written cleanly; no re-run needed). Closes the previously-pending work-order item ("Stage 6 eval loop design... pending verification of live function signatures before orchestrator can be written") -- signatures verified, orchestrator built and run successfully this session.

**>>> 2026-06-23 P_300_AddPattern.bat CORRUPTED + REBUILT:** Tony accidentally pasted PowerShell console text into the `.bat` file (clipboard mixup -- meant to paste into chat, the launcher was focused in an editor instead), reducing it to 101 bytes of stray console text. No on-disk backup or VS Code local history existed. Rebuilt from `cli.py`'s real subcommands (`add-pattern`, `archive-pattern`, `catalog-summary`) + a console transcript of a prior live run; day-rollover catalog-backup logic (no source existed anywhere) was reconstructed in pure batch, avoiding M-032's delayed-expansion trap. Verified end-to-end on a real ingest -- TSLA, pattern_instance_id=320, 227 symbols / 320 patterns / 6400 bars / 1600 labels, archived to `2026-06.zip`, clean exit. M-056 added to lessons.md.

**>>> 2026-06-18 WO-P000-E4.001 P_300 INIT EXECUTION BYPASS SHIPPED (pilot):** SIP Steps 5b/5c previously invoked `python` via `windows-mcp:PowerShell` for catalog-summary and the LM Studio check -- the exact call shape M-030/peh-handoff document as hanging on most attempts, and confirmed twice in this file already (2026-06-10/11 entries below, both "count unverified due to PowerShell MCP timeout"). Fix: new `python/utilities/preflight_status.py` (reuses `db_utils.get_latest_catalog`, `verify_ingestion._check_no_hollow_instances`, `lm_studio_api.get_wrapper_status` -- no catalog or LM Studio logic reimplemented) + `python/schemas_preflight.py` (Pydantic `PreflightStatus`) write `P_300_preflight_status.json` to the project root. New `P_300_Preflight.bat` (operator-run, outside the chat session -- same model as `P_300_AddPattern.bat` / `P_300_DailyEval_v2.bat`) invokes it. SIP bumped to v3.2 -- Steps 5b/5c rewritten to read the JSON via `windows-mcp:FileSystem` instead of invoking `python` directly; zero subprocess calls remain in INIT. `p300-project-context` SKILL.md updated to match (Critical Paths row, Layer Architecture tree, Session-Start Checklist line, Pairs-With table path fix, changelog). Session header format (`P_300 [Day, Month DD, YYYY -- HH:MM ET]`) confirmed already canonical -- P_300 was the source pattern being adopted Hub-wide; no change needed on that half of the WO. Hub-wide rollout to P_115/116/117/118/400/800 and the `P_000_SYSTEM_DOCUMENTATION.md` standard entry remain P_000's open items on WO-P000-E4.001. P_300-side Ack appended to the WO. M-055 added to lessons.md.

**>>> 2026-06-17 M-051 REAL FIX SHIPPED (correcting the false 2026-06-12 closure):** Operator uploaded live DailyEval console output (AEM/CRML/NNE) showing `print_signal_report_clean()` still printing a hardcoded `[OK] {ticker} written to vault` for every signal class -- including CRML and NNE, both PASS, where no vault write of any kind happens (daily_evaluate_pipeline only calls the real obsidian-write hook for BUY/WATCH, per LEDGER_LOG_CLASSES) -- plus a fully fabricated `[STEP 3] Archiving eval file... ARCHIVE OK -- zip: data/processed/2026-05.zip` block with zero real call behind it and a dead stale path/month. This is the exact M-051 bug from 2026-06-12 -- except `report_writer.py` was still v1.7 (2026-06-09), unchanged, the whole time. The 2026-06-12 todo.md/lessons.md entries claiming this was fixed via Claude Code were never verified against the file. Bug ran live in production 2026-06-12 through 2026-06-17 (5+ days, includes 2026-06-15/16 sessions). Fix: `report_writer.py` v1.8 -- vault-write line now gated on `LEDGER_LOG_CLASSES` (`[OK]` for BUY/WATCH, honest `[SKIP] ... not logged to vault` for PASS); fabricated archive block removed entirely (archiving is reported for real by the separate `.bat` STEP 2 / `cli.py archive-eval`); DONE footer corrected to match. Paired `daily_evaluate_pipeline.py` v1.20 -- M-043 fix, `_obsidian_write()`'s True/False return was being discarded; a clean False now logs WARNING instead of vanishing silently. Verified via PEH harness (`04-Shared-Resources/verify/run_this.py`), 9 checks: BUY case shows real `[OK]`/no fabricated archive text/correct footer; PASS case shows `[SKIP]`/no `[OK]`/no fabricated archive text/correct footer. All PASS, 2026-06-17 (Tony ISE run). M-054 added to lessons.md: a closure note in tasks/*.md is a claim, not evidence -- verify the file before trusting a prior session's DONE.

**>>> 2026-06-17 WO-P300-E1.003 STOP GUARD FIX SHIPPED:** atr_adjusted_stop = max(intelliscan_support_1, ATR floor) assumed support_1 always sits below entry. Caught by P_400 via DRD (support_1=25.46 above entry=25.40, max() picked the invalid above-entry value as the stop -- would've been used silently as P_400's primary stop input). Isolated to DRD, not systemic. Fix: `application/daily_evaluate_pipeline.py` v1.19 -- support_1 only counts as a max() candidate when it's below entry; otherwise falls back to ATR floor alone. `shared_resources/python_utils/signal_schemas.py` SignalV2 bumped to v2.3 -- added a validator rejecting any packet where atr_adjusted_stop >= guideline_entry (the acceptance criterion's reject-not-silent-pass requirement, also a safety net against recurrence). Verified the schema validator only (4 cases, PASS) -- the pipeline-side guard is inline, not a standalone function, so it wasn't unit-tested; real-world confirmation pending next live run that hits a symbol with an IntelliScan level above entry. OWNER_DONE appended to WO-P300-E1.003. P_400 Ack pending.

**>>> 2026-06-17 WO-P300-E1.002 TARGET GENERATION FIX SHIPPED:** Architecture 3.5 (Target Selection Standard) was decided but never implemented -- guideline_target was unconditionally entry + 2x ATR, ignoring any VP resistance level in the same packet. Caught by P_400 via the AG dossier (intelliscan_support_2=21.27 sitting unused above entry=19.42, target still set to 21.84 off ATR). Consequence: R:R always read exactly 2.00 by construction, so P_400's Tier-1 R:R gate couldn't filter anything. Fix: `infrastructure/signal_emitter.py` v2.2 -- `_build_signal_v2_packet` now checks both intelliscan_support_1/_2 for any level above entry, uses the nearer one as guideline_target (target_source="vp_resistance"); falls back to 2x ATR (target_source="atr_extension") only when neither clears entry. Does not hardcode support_2 as "the resistance field" -- AG happened to have support_1 below entry and support_2 above, but the check is field-agnostic. `shared_resources/python_utils/signal_schemas.py` SignalV2 bumped to v2.2 -- added target_source field + validator; without this the audit trail field would be silently dropped by write_to_vault's validation. Verified via PEH harness, 4 cases (AG real numbers, true price-discovery/no IntelliScan data, support_1-above-entry case, both-levels-above-entry case): PASS. OWNER_DONE appended to WO-P300-E1.002 (single physical file under both Agentic-Hub-Governance and 04-Shared-Resources paths -- confirmed junction, not duplicate copies). P_400 Ack pending: confirm R:R varies by symbol on re-run.

**>>> 2026-06-17 vp_xlsx_reader v1.4 FIX + BACKLOG CLEARED:** v1.3's filename.upper() regression (M-053) fixed -- 100% AddPattern failure since 2026-06-16 traced to uppercasing the whole filename before a case-sensitive regex match. Fix: re.IGNORECASE on `_FILENAME_PATTERN`, symbol-only uppercase post-match. First re-run after fix: 13/18 succeeded. Remaining 5 were genuine data issues, not the bug: DOCU (insufficient setup history) and EDVMF x2 (41 bars, need 60) recaptured with more history and re-ingested clean (3/3) -- catalog now 279 patterns / 209 symbols / 061726catalog.db (pattern_instance_id 277-279). RCl / RCL (`Pattern_20260123_20260211` and `Pattern_20260226_20260303`) -- both opened to a sheet named WDC, not RCL; both deleted by Tony as bad captures. 18/18 of the original blocked batch now resolved (16 ingested, 2 deleted).

**>>> 2026-06-16 WO-P300-E1.001 INTELLISCAN STOP INTEGRATION SHIPPED:**
- `python/utilities/intelliscan_reader.py` v1.0 NEW -- reads `data/live/P_300_HistoryGrid_IntelliscanEvalParameters.xlsx`; returns `(support_1, support_2)` per symbol; non-blocking when file absent.
- `shared_resources/python_utils/signal_schemas.py` v2.1 -- `atr_adjusted_stop`, `intelliscan_support_1`, `intelliscan_support_2` added to `SignalV2` as `Optional[float] = None`; validator added. Backward compatible.
- `python/infrastructure/signal_emitter.py` v2.1 -- 3 new optional params wired through `_build_signal_v2_packet` and `emit_signal_packet`.
- `python/application/daily_evaluate_pipeline.py` v1.18 -- `load_intelliscan()` called once at pipeline start; `get_support_levels()` per symbol; `atr_adjusted_stop = max(support_1, close - 1xATR)` or ATR floor when grid absent. All 3 fields passed to emitter.
- **Smoke test PASS**: 12 symbols, both support levels correct vs live IntelliScan grid.
- **WO-P115-E2.001 OPEN**: same integration needed for P_115 signals (separate session).
- **M-052 added**: stop architecture rule -- emit both VP support levels; P_400 decides which clears risk parameters.

**>>> 2026-06-12 PRINT_SIGNAL_REPORT_CLEAN() FIX + P_800 HUB INTERFACE CONFIRMED:**
- Hardcoded `[OK] {ticker} written to vault` and `ARCHIVE OK` strings in `report_writer.py` `print_signal_report_clean()` replaced with real call-driven output via Claude Code. M-051 closure.
- P_800 Hub interface confirmed working end-to-end: `signal_emitter.emit_signal_packet()` -> `write_to_vault("SIGNAL_V2", ...)` -> P_800 write_handler -> Obsidian vault. Validated by `2026-06-12_COF.md (version 2)` written automatically on BUY/WATCH -- no extra step needed.
- The vault write was always wired correctly via Enhancement 1 (2026-06-08). The hardcoded strings in `print_signal_report_clean()` were the only defect; the actual write path was never broken.

**>>> 2026-06-12 GOVERNANCE + DOC UPDATES:**
- WO-P300-E1.001 created (BACKLOG): resistance lookup to replace VP predicted high as target formula. Scope: P_300 emits resistance-derived `target_price` in SignalV2 only; P_400 remains final target authority (M-050). Gated on lambda tuning + CE gate flip (~2026-07-01).
- system-doc-initializer SKILL v3.0: compressed ~40% token reduction + Protocol D Loop F added (falsified output / M-051 global rule). Non-negotiable: no `[OK]`/`DONE`/`written` without real call return.
- CLAUDE.md updated: WO table corrected (P_115/P_800 CLOSED with dates; P_000-E2.003 accurate scope), `schemas_signal_packet.py` flagged vestigial in layer architecture block, last-updated bumped to 2026-06-12.
- M-051 added to lessons.md (P_300-level) and system-doc-initializer SKILL (Hub-level global rule).

**>>> 2026-06-11 ATR OPERATOR RUNTIME CHECK DONE:**
- CGBD BUY h=5, n=20, wr=0.90, z=2.55 -- signal class byte-identical to NFR-1 replay. BUY/WATCH/PASS unaffected by ATR upgrade. ✅
- guideline_stop: 10.7377, guideline_target: 11.4646, atm_at_signal: 0.2423 -- present and non-zero. ✅
- Pipeline clean exit (--no-narrator; LM Studio was not running at time of check).
- 061026catalog.db detected at INIT (newer than last known 060826catalog.db) -- catalog has grown; count unverified due to PowerShell MCP timeout. Health check deferred to next session INIT.

**>>> 2026-06-11 ENHANCEMENT 2 GATE-ON PREREQUISITES COMPLETE:**
- **report_writer smoke PASS** (2026-06-11): All 3 scenarios clean -- dense format (horizons/matches/vol-divergence/narrative), clean format with narration, clean format with narrator_warning forced on. None-CE renders as N/A in the ce column. No crashes. sys.path removal did not break imports.
- **NFR-1 determinism replay PASS** (2026-06-11): `tasks/nfr1_determinism_replay.py` ran CGBD BUY h=5 twice with `CE_GATE_ENABLED=False`, `narrator_enabled=False`. signal_class, chosen_horizon, n_matches, win_rate, mean_return_pct, std_return_pct, z_score, certainty_equivalent -- ALL IDENTICAL across both runs. CE observe-mode does NOT alter BUY/WATCH/PASS. NFR-1 confirmed for Enhancement 2.
- **ledger_record.py M-019 fix**: Unicode `->` (U+2192) in logger.info f-string replaced with ASCII `->`. Was triggering cp1252 UnicodeEncodeError on every BUY/WATCH ledger write (non-blocking but noisy). Fixed in-session.
- **Junk ledger entries cleaned**: Replay ran CGBD as a real BUY both passes, writing ledger_ids 41 and 42. Both deleted via `tasks/cleanup_replay_ledger_entries.py`. fired_signals back to 40 rows.
- **One prerequisite remaining before flipping CE_GATE_ENABLED=True:** tune lambda against ledger (requires ledger-fill at 20-trading-day mark -- earliest eligible signals from 2026-06-02; fill window opens ~2026-07-01).

**>>> 2026-06-09 INIT CATALOG RECONCILIATION (ground truth reset):** Live `catalog-summary` (operator ISE paste, PowerShell timed out in-session) = **N=186 pattern_instances / 155 symbols / 186 source_files / 3720 pattern_bars / 930 forward_labels / 0 hollow / OVERALL HEALTHY** on `models/060826catalog.db` (mtime 2026-06-08 10:43:43). Most recent: id=186 BF_B (anchor 2026-03-25), 185 BF_B, 184 BF_B, 183 BATRA, 182 HTHT. Baseline WR 61.3% @ h5/h15/h20, 60.8% @ h7/h10; avg returns +3.39/+4.18/+4.92/+5.82/+5.02% across horizons. **Three prior tracking claims corrected by this entry:** (1) the 2026-06-03 closure N=156 was the last tracked figure -- catalog has since grown +30 instances across untracked sessions (gap closed here); (2) the 2026-06-08 "N=175 / 147 symbols" growth note was never the live count -- live is 186/155; (3) the 2026-06-08 "AVXL #2 / CRK / HP #2 FAILED to ingest" entry is FALSE -- all three are present in the live catalog (AVXL 2 patterns, CRK 1, HP 2). Whatever forward-bar concern was logged that day, the ingests landed. Per M-017 the catalog is authoritative; tracking is now reset to 186/155. No partial/hollow state (0 hollow confirmed). Catalog DB naming note: latest is 060826catalog.db (not 060326).

**>>> NEXT SESSION LEAD ITEM -- DONE 2026-06-09:** Surface behavior-affecting config flags in the INIT session summary. SHIPPED: SIP v3.0->v3.1 (Step 5 greps config.py for RISK_AVERSION_LAMBDA / CE_MIN_THRESHOLD / CE_GATE_ENABLED / NARRATOR_ENABLED; Step 6 gains `Decision flags:` line; fail-fast row for unreadable flags) + SKILL aligned (checklist confirmation line, SIP ref v3.1, changelog). Grep-at-INIT not import (no PowerShell dependency; captures committed default, in-session flips operator-visible). Live flags this session: CE gate OFF (lambda 20.0, min 0.0) / Narrator ON. Doc/protocol change, no code. M-048 captured (filesystem:edit_file atomic-batch rollback).

- **Stage 1 Audit:** Complete.
- **Stage 2 Architecture:** Complete.
- **Stage 2 Closing Deliverables:** Complete.
- **Stage 3 Execution:** SEALED 2026-05-14.
- **Stage 4 Execution:** SEALED 2026-05-15.
- **Stage 5 Execution:** SEALED 2026-05-16.
- **Stage 6 Execution:** SEALED 2026-05-18.
- **Stage 7 Execution:** SEALED 2026-05-19.
- **Stage 8 Execution:** SEALED 2026-05-19.
- **Stage 9 Execution:** SEALED 2026-05-19.
- **Stage 9-followup (post-SEAL):** COMPLETE 2026-05-20.
- **2026-05-21 Pipeline A Tooling:** COMPLETE. P_300_AddPattern.bat v1.5 + archive_pattern_file.py v1.0 + cli.py v1.5.
- **2026-05-21/22 Catalog Growth:** N=25 -> N=91 (66 new patterns across two sessions).
- **2026-05-22 to 2026-05-26 Catalog Growth:** N=92 -> N=104 (13 patterns, earlier sessions).
- **2026-05-27 INIT Reconciliation:** Catalog confirmed N=104 / 052626catalog.db.
- **2026-05-27 Catalog Growth:** N=105 -> N=116 (12 patterns, 052726catalog.db mtime 2026-05-27 22:02:42).
- **2026-05-28 Pipeline B Clean Console:** daily_evaluate_pipeline.py v1.5 + report_writer.py v1.5 delivered.
- **2026-05-28 Feature Ablation + Threshold Sweep:** volume_zscore removed; BUY_MIN_Z_SCORE lowered to 0.0. config.py v1.5.
- **2026-05-29 Pipeline B Patching:** daily_evaluate_pipeline.py v1.9 + cli.py v1.6 + SIP v2.9. NVDA PASS @ h=20 validated.
- **2026-05-30 Process Boundary Refactor + Eval Session:** Process Boundary Standard formalized at Hub level. Dead code cleanup complete. Evals: ARLP BUY, COTY WATCH, DOX BUY, DD WATCH, EQX WATCH. 23 new patterns ingested (N=116->N=139 / 053026catalog.db) -- not tracked at time; gap closed 2026-05-31.
- **2026-05-31 P_800 Obsidian Note Standard + Bug Fix:** Gap 6 fixed (write_signal_to_obsidian.py v1.1). M-038 added. P_800 Obsidian Note Standard v1.1 drafted. Hub interface migration + backfill pending.
- **2026-06-03 INIT Reconciliation:** Catalog confirmed N=156 / 136 symbols / 060326catalog.db (mtime 2026-06-03 08:33:35). +17 patterns / +15 symbols added across 3 untracked sessions (060126/060226/060326) -- not tracked at time; gap closed this entry. 156 source_files / 3120 pattern_bars / 780 forward_labels / 0 hollow / OVERALL: HEALTHY. Baseline WR 60.3% @ h5, 60.9% @ h15/h20. Most recent: id=156 ENB, 155 AOS, 154 AME, 153 CMI, 152 DNOW.
- **2026-06-03 Ledger Calibration System (Phase 1-3 COMPLETE):** Signal-outcome measurement layer delivered. Captures BUY/WATCH fired signals -> ledger records. Realized returns backfilled via yfinance. Confidence factors computed (realized_WR / predicted_WR). All tests passed. **WORKFLOW REMINDER:** (1) Daily eval fires BUY/WATCH -> ledger record. (2) Wait 20+ trading days. (3) `python cli.py ledger-fill` -> backfills realized returns. (4) `python cli.py ledger-calibration` -> prints confidence report. Per-horizon metrics: sample_count, pred_WR, real_WR, confidence_factor, avg_realized_return.
- **2026-06-08 Enhancement 1 (P_300 -> P_400 Signal Packet) SHIPPED:** On BUY/WATCH, Pipeline B emits a SIGNAL_V2 JSON packet to P_400 via the P_800 Hub interface (write_to_vault SIGNAL_V2 -> trading_journal/TradeOrderManagement/signals/<date>_<SYMBOL>_v2.0.json), alongside the Obsidian md note. signal_emitter.py v2.0 + daily_evaluate_pipeline.py v1.15 (Stage 5a). Fixed the v1.14 vault_root TypeError that crashed every BUY. Boundary: P_300 emits asset_class=stock + position_size=0 sentinel; P_400 sizes (no P_000 coupling). Gate widened BUY-only -> (BUY, WATCH). COHR live BUY @ h=15 validated -> packet written, stock variant passed P_800 validation. schemas_signal_packet.py now vestigial (removal in Backlog). Architecture v2.7 Enhancement Log + Change Log + M-045. P_300 producer side of Phase E1 DONE; P_400 JSON reader + E2 remain.
- **2026-06-08 Catalog Growth:** AVXL #2 (id=173, anchor 2026-03-24), CRK (id=174, new symbol, anchor 2026-01-30), HP #2 (id=175, anchor 2026-04-21). All ingested + archived to 2026-06.zip. Catalog: 175 patterns / 147 symbols / 3500 pattern_bars / 875 forward_labels / OVERALL HEALTHY.
- **2026-06-09 Enhancement 2 (Certainty-Equivalent BUY Gate) SHIPPED -- OBSERVE-ONLY:** Risk-adjusted reasoning added to Pipeline B per Kochenderfer "Algorithms for Decision Making" Ch. 6 (maximum expected utility). CARA exponential utility u(r)=-exp(-lambda*r) scores each top-K analog's forward return; inverted mean utility = certainty-equivalent (CE) return, CE = -(1/lambda)*ln(mean(exp(-lambda*r))). For any non-degenerate spread CE < arithmetic mean; the gap is the risk penalty (fat-tailed analog distributions penalized INSIDE the decision, not just flagged afterward). Decimal-space throughout (M-020); lambda applied to decimal fractions, default RISK_AVERSION_LAMBDA=20.0 (meaningful band ~10-40). Pure domain math -- NFR-1 preserved, no LLM in path. **CE_GATE_ENABLED defaults False:** CE computed + displayed but does NOT alter any signal until flag flipped after lambda tuning. 6 files: config v1.6->v1.7, schemas_pipeline_b v1.2->v1.3 (optional certainty_equivalent field), domain/utility.py v1.0 NEW (~210 ln incl harness; longest fn ~30 ln), aggregator v1.0->v1.1, signal_classifier v1.0->v1.1 (CE term on BUY branch only, guarded), report_writer v1.6->v1.7 (ce column + lambda-stamped header). M-046 (lambda provenance) + M-047 (harness honesty) added to lessons. Validation: utility.py smoke PASS (dispersed cluster mean +4.5% -> CE -3.7% at lambda=20, 8.2pt penalty). Files over 300-ln (M-031): schemas_pipeline_b, aggregator -- splits stay backlogged, one-field/minimal adds only.
  **OWED before gate-on (do NOT flip CE_GATE_ENABLED until done):**
  - [x] signal_classifier smoke: gate-ON cases added + VERIFIED 2026-06-09 (v1.2, CE GATE: PASS -- CE>=0 keeps BUY, CE<0 blocks to WATCH, gate-OFF ignores CE). Caught + fixed a double-import test bug (flag now flipped on sys.modules[__module__]) and a stale case-4 expectation (z gate is 0.0 per M-034, not 1.0).
  - [x] report_writer smoke run (None-CE render confirm) + e2e daily-evaluate determinism replay vs pre-change run (NFR-1 proof observe-mode changed nothing) -- DONE 2026-06-11. Both PASS. See 2026-06-11 session entry above.
  - [ ] tune lambda against ledger before flipping; stamp lambda into ledger record at flip (gated on ledger-fill ~2026-07-01)
  - [x] architecture v2.7 Enhancement Log + Change Log entry DONE 2026-06-09 (in-place addendum, no version bump per Appendix G -- Change Log + §7 Enhancement Log both carry Enhancement 2). signal_classifier bumped to v1.2 (harness).

**>>> 2026-06-10 ATR UPGRADE (shared Wilder util) SHIPPED + RUNTIME CHECK DONE 2026-06-11:**
Replaced P_300's high-low-only simple-average ATR proxy with full True Range + Wilder smoothing. NEW shared hub util `shared_resources/python_utils/atr.py` v1.0 (`true_range` + `compute_atr_wilder`; pure domain; takes (h,l,c) tuples -- decoupled from any project's bar type) + `test_atr.py` (9/9 PASS, incl hand-computed Wilder 86/27; run from the P_300 dir so it also proves the shared import resolves). `daily_evaluate_pipeline.py` v1.15->v1.16 (removed local `_compute_atr_from_bars`; imports the shared util via the editable install -- NOT the _HUB_ROOT sys.path insert; call site adapts `candidate.bars`, confirmed chronological oldest-first). signal_emitter.py docstring clarified (candidate/baseline; P_400 resolves final). ATR is NOT in the classification path (only feeds atm_at_signal -> guideline stop/target) -- BUY/WATCH/PASS unaffected. **Architecture decisions (Tony; M-049/M-050):** (1) all evaluating projects emit the same baseline shape (guideline entry/target/stop); (2) P_400 is the single target authority -- resolves final entry/stop/target + RR + sizing (today only `packet_classifier.classify` exists; enforcement OWED in P_400 build-out); (3) ATR computed at eval time on bars in hand, not P_400-owned (avoids a re-fetch), shared via the editable install across the <=5 eval projects.
  - [x] Operator runtime check DONE 2026-06-11: CGBD BUY h=5 -- signal class byte-identical, guideline stop/target + atm_at_signal present and non-zero. ATR upgrade confirmed clean.
  - [ ] P_000: add `shared_resources/python_utils/atr.py` to the P_000_SYSTEM_DOCUMENTATION Document Index (WO-P000-E3.001 Completion Gate).

**>>> 2026-06-10 Cross-project ENH notes drafted (handed to owners):** (a) ENH-P000 -- promote LM Studio status to a Hub interface in `shared_resources/python_utils/` + move the external-service check out of P_300's application layer (daily_evaluate_pipeline.py line 487); blocks the E2.003 sys.path rows for that file + the three `integrations/lm_studio/infrastructure/*.py` inserts (editable install does NOT cover `integrations`, so removing those inserts breaks imports). Filed at P_000/docs/notes/. (b) ENH-P800 -- rename the `p115_`-prefixed SignalMetadata fields to `session_date`/`chart_timeframe` (origin artifact; P_300 packets carry p115_ keys that misname the owner); no P_400 consumer reads them yet, so the rename is free now. Filed at P_800/docs/. Both for the owner project to convert to a WO.

---

## Completed -- Stage 3: File System Cleanup + Empty New Schema (SEALED 2026-05-14)

**Approved file plan (6 files, ~550 lines total).**

### 3.1 Foundation files
- [x] `python/config.py`
- [x] `python/schemas.py`

### 3.2 Migration scripts
- [x] `python/migrations/stage_3a_folder_setup.py`
- [x] `python/migrations/stage_3b_archive_cruft.py`
- [x] `python/migrations/stage_3c_init_new_catalog.py`

### 3.3 Surgical edit
- [x] `python/utilities/db_utils.py`

### 3.4 Documentation
- [x] `docs/migrations/STAGE_3_MIGRATION_LEDGER.md`

---

## Completed -- Stage 4: Rebuild Pipeline A (Add Pattern) (SEALED 2026-05-15)

11 of 11 files delivered. Pipeline A end-to-end validated on AAPL + OII. Full closeout: `docs/migrations/STAGE_4_CLOSEOUT.md`.

---

## Completed -- Stage 5: Re-Ingest Historical Patterns (SEALED 2026-05-16)

5 POC symbols ingested clean (AAPL, OII, SPY, QQQ, NVDA). Regression-verified. OVERALL: HEALTHY.

---

## Completed -- Stage 6: Rebuild Pipeline B (Daily Evaluate) (SEALED 2026-05-18)

10 of 10 files delivered. Decisions A-F locked. All success criteria green.

---

## Completed -- Stage 7: Broader Catalog Ingest (SEALED 2026-05-19)

20-symbol curated set ingested. ID-007 RESOLVED. Baseline win-rates below 1.0 at all 5 horizons. BUY now structurally reachable.

---

## Completed -- Stage 8: Local LLM Integration (SEALED 2026-05-19)

5 files delivered. NFR-1 preserved. `--no-narrator` flag added.

---

## Completed -- Stage 9: Parameter Sweep + Outcome Attribution (SEALED 2026-05-19)

3 utilities delivered. Sparse-N caveat alive; re-run at catalog >= 50 (Backlog).

---

## Completed -- Stage 9-followup (post-SEAL): Volatility-Divergence Flag + Process Runbooks (2026-05-20)

7 files delivered. Doc-bump SEAL complete 2026-05-20.

---

## Parked -- Milestone 6: Trade Management Module

Gated on live P_300 trading first. Consumes Aggregator output, produces position-sizing recommendation.

---

## Backlog -- Future Candidates (Not Scheduled)

- Parameter sweep + ablation re-run at N=300+ (re-tighten BUY_MIN_Z_SCORE toward 1.0 when z becomes discriminating)
- `return_pct` schema field rename to `return_fraction` (bundle with NormalizedBar shared-base refactor)
- NormalizedBar / PatternBarRecord shared-base refactor (DEBT NOTE from `schemas_pipeline_b.py`)
- `schemas_pipeline_b.py` file split (408 lines at v1.2, ~108 over; split candidates named in DEBT NOTE)
- Date-validity pre-check utility (M-026)
- Real-time intraday evaluation mode
- PEAK-anchor framing (second ingest pass)
- Legacy 14-symbol Gemini-era CSVs (abandoned 2026-05-18 -- no launch-window data)
- P_800 Obsidian Note Standard v1.1 implementation (~545 lines; pending operator approval)
- Historical note backfill (~60 existing P300 notes with wrong h5_win_rate / h5_mean_ret values)
- **schemas_signal_packet.py removal** -- file is vestigial (superseded by SignalV2 in shared_resources.python_utils.signal_schemas). Remove when convenient; no active imports confirmed.
- **Batch ingester (unattended catalog growth)** -- ~150 lines / 2 new files + config.py edit. Plan approved 2026-06-03; build deferred per operator priorities.
- **cli.py command-registry refactor (NEW, 2026-07-14)** -- WO-P300-E4.001 created (PENDING, not started). cli.py hit 821 lines / 15 subcommands via WO-P300-E3.002's ingest-mined addition, well past the 300-line file limit with no natural split point left in the flat design. Proposed fix: split into python/cli/main.py (~30 lines, loops category modules) + one file per category (pipeline_a.py, pipeline_b.py, bulk.py, utility.py), each exporting register(subparsers). Terminal-facing commands unchanged (no new syntax, no prefix). Tony's call (2026-07-14): finish WO-P300-E3.002 (files #8-9 + PEH) first -- done; WO doc written and awaiting separate go-ahead before build starts (3+ file structural change, plan-gate applies).
- **M-094 auto-snapshot before promote (NEW, 2026-07-14)** -- `atomic_move()`'s built-in `.bak` is single-level and overwrites every promote (no depth). First real WO-P300-E3.002 batch used a manual backup instead (`models/archive/databases/pre_mine_batch_071026catalog_20260714.db`). Tony's call: proceed with the manual backup for this batch, scope an automatic pre-promote snapshot (in `promote_staging_to_live()` or its CLI wrapper, size-threshold or unconditional -- not decided) as a follow-up after seeing how the real 5,584-candidate batch goes.
- **WO-P300-E1.001 (BACKLOG): Resistance lookup target formula** -- replace VP predicted high with nearest grid resistance above close as `target_price` in SignalV2. Gated on lambda tuning + CE gate flip (~2026-07-01). Scope: P_300 emits only; P_400 resolves final (M-050).
- **P_400 Trade Order Management integration** -- E1 P_300 producer side DONE 2026-06-08. REMAINING: P_400 builds JSON reader (E1 consumer side); then E2 (remove P_300 STEP 2 md output so P_400 reads JSON as sole input).
- **BUY-precision investigation + social-sentiment confirmation layer** -- levers in order: (1) measure actual fired-BUY outcomes vs predicted LOO precision; (2) re-tighten BUY_MIN_Z_SCORE toward 1.0 at N=300+; (3) openbb-adanos sentiment as post-decision confirmation.
- **WO-P300-E2.001 (bulk pipeline) first real production run** -- operator populates `data/bulk/` with real multi-symbol exports (+ optionally `data/reference/sector_map.csv`), runs `P_300_BulkExtract.bat`. Build itself is COMPLETE and PEH-verified (17/17) as of 2026-07-08; only the real-corpus run remains.
- **WO-P300-E3.002 pattern_miner.py -- widen resolve_pick + re-run validation (M-085)** -- current real HITS 60/84 (71.4%) is very likely an undercount; a session-close spot-check found 14/17 sampled OUTCOME-INVALID picks actually qualify once the search widens past resolve_pick's 4 combinations. Widen to idx-2..idx+2/both-directions, re-run full 84-anchor validation, expect ~78-80/84. Also investigate the AMZN/GOOGL/CIEN/SPY direction-mismatch pattern found during the same spot-check.

---

## Active -- Live WATCH Tracking

**NOTE: All WATCH classifications below were made at N=25 baseline (WR ~0.60). Catalog is now N=186+ with baseline WR ~0.61. Re-evaluate all symbols against a fresh anchor before acting.**

**Watchlist portfolio:** `P_300_WatchList_May2026.ptf` (5 symbols: AEM, NOC, NVDA, SNY, VZ).

| Symbol | Class @ horizon | wr | mean | z | Vol flag | Notes |
|--------|-----------------|----|------|---|----------|----|
| NOC | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=175 baseline. |
| VZ | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=175 baseline. |
| SNY | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=175 baseline. |
| AEM | Pending | -- | -- | -- | -- | Not yet evaluated. |
| NVDA | PASS @ h=20 | -- | -- | -- | -- | Evaluated 2026-05-29 with 9-feature config (post-ablation). |

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (architect)
- **Update trigger:** Every stage transition, every task completion, every newly-scoped task
- **Loaded by:** SIP at session start (Step 4 via `windows-mcp:FileSystem`, per M-015)

---

**End of P_300 Task Queue**


---

## 2026-07-23 (4th, Sonnet) -- APPENDED OUT OF ORDER (filesystem MCP edit tool still down; see prior entry's tooling note)

**First real production batch through WO-P300-E5.004 Part A -- fired correctly, not promoted:**
`P_300_MinePatterns.bat` -> `P_300_IngestMined.bat`, 14 XLSX files (`data\bulk\mine\`).

Mine-patterns: 14 files, 2,479 candidates (uptrend=1,414 / breakdown=1,065).
Ingest-mined: 1,989 inserted / 0 skipped-duplicate / 490 audit-failed / 12
symbols touched. Pre n_patterns=14,812 -> post n_patterns=16,801.

**Independently verified before logging (M-054), not taken on the console
paste alone:**
- Arithmetic ties out both directions: 1,989 inserted + 490 audit-failed =
  2,479 = mine-patterns' own candidate count exactly (nothing silently
  dropped between the two pipeline stages). 14,812 + 1,989 = 16,801 matches
  the log's own post-count exactly.
- `staging_ingest_mined.db` real file check: 103.4MB, mtime 20:22:45.
  Initially looked wrong (predates the 21:13:41 "Ingest-mined complete" log
  line) -- traced the full log timeline before accepting it: the actual
  1,989-row insert completed by ~20:22:45 (staging's `load_full_catalog()`
  at 20:24:48 already shows 16,801 patterns present), and the 48-minute
  gap after that was the POST-batch walk-forward report computation only
  (read-only against the loaded data, writes the report file, not the DB)
  -- not a sign the insert didn't happen.
- Live catalog (`072326catalog.db`) confirmed genuinely untouched: real
  mtime 2026-07-22 10:30:10 (yesterday's promote), unchanged by today's
  run since `--promote` was correctly not passed. `Created` timestamp
  being today (20:22:11) is just the daily filename-rollover copy, not a
  content change -- same pattern already seen with 072126->072226->072326.

**WO-P300-E5.004 Part A fired for real in production, first time:** log
line confirms it directly -- `M-079 pre-batch: reconstructed from
topk_cache for 072326catalog.db (14812 patterns, WO-P300-E5.004 Part A)
-- skipped full DTW rescore`. Real wall time 20:22:53->20:24:47 = ~114s,
consistent with last session's PEH-verified 130.0s measurement on the
same-size catalog. This is the actual payoff of that WO: a real
`ingest-mined` run after a promote hit exactly the cold "pre" cache
scenario this was built for, and it reconstructed instead of falling
into a multi-hour rescore or requiring `--confirm-full-rescore`.

**490 audit failures, all expected, not a bug:** 9 are the standard
first-anchor-of-symbol window-too-early case (BWA/CW/DNN/IP/JBL/LBTYK/
MRCY/PWR/TEX, all anchored ~2021-08-1x, window reaches before
`MINE_MIN_ANCHOR_DATE`). The remaining ~481 are real `(symbol,
anchor_date)` catalog collisions, almost entirely CPSS (~250) and TECK
(~230) -- both symbols' mined history heavily overlaps windows already
in the live catalog from earlier sessions. `mine_audit.py`'s dedup check
(discussed earlier this session) caught every one of them correctly --
0 skipped-duplicate at the DB layer means the audit gate is doing 100%
of the dedup work here, upstream of the insert.

**NOT promoted.** Staging at `models\staging_ingest_mined.db` (16,801
patterns, real, confirmed above). Both walk-forward reports written:
`outputs\reports\eval\walkforward_072326catalog_default_20260723_202448.txt`
(pre) and `outputs\reports\eval\walkforward_staging_ingest_mined_default_
20260723_211341.txt` (post). Promote command is sitting ready
(`python cli.py ingest-mined --promote "...staging_ingest_mined.db"`) but
not run -- that's Tony's explicit, separate call per standing practice,
not something this session does on its own. 14/14 mined XLSX files
archived to `E:\AI-Agent-Learning-Hub_BackupFiles\Jul26BULKPattern.zip`
and cleared from `data\bulk\mine\` (2 of 14 hit "already in zip" on the
write but still deleted from the source dir correctly -- CPSS and TECK,
the same two symbols with most of the audit collisions above, likely
re-mined from a file already archived in an earlier batch; not
investigated further, non-blocking).

**Waiting on Tony: review both walk-forward reports (BUY precision / PASS
accuracy pre vs. post), then promote or hold.**


---

## 2026-07-23 (5th, Sonnet) -- APPENDED OUT OF ORDER (filesystem MCP edit tool still down; see prior entries' tooling note)

**Promoted -- live catalog now 16,801 patterns / 351 symbols.** Tony ran
the promote command directly (exit 0, ~32.5 min wall time). Independently
verified before logging (M-054), not taken on the pasted table alone:

- Both new files checked directly on disk: `072326catalog.db` real size
  109,969,408 bytes / mtime 23:43:46 -- exact match to the pasted table.
  `072326catalog.db.bak` real size 96,956,416 bytes -- exact match to the
  pre-promote live file's own size (confirmed independently earlier this
  session), AND its mtime (2026-07-22 10:30:10) matches the pre-promote
  live file's mtime exactly too -- genuine content-preserving backup, not
  a fresh/different file standing in for one.
- `staging_ingest_mined.db` confirmed gone from `models\` via a real
  directory listing -- atomic promote behaved as designed (staging
  consumed, not left behind).
- Arithmetic cross-checks: pattern_bars delta 39,780 = 1,989 x 20 exactly
  (`BULK_WINDOW_LENGTH`); forward_labels delta 9,945 = 1,989 x 5 exactly
  (5 horizons); topk_cache delta 39,780 matches pattern_bars delta exactly
  -- consistent with `TOP_K_MATCHES=20` per new pattern, no degenerate-
  corpus pids in this particular batch (the known 6 degenerate pids are
  all 2021-08-10-anchored, none of today's batch anchors that early).

**Catalog state going forward: 16,801 patterns / 351 symbols / 594
source_files.** `P_300_preflight_status.json` is now stale as of this
promote -- flag for next INIT's Step 1A/5b, re-run `P_300_Preflight.bat`
before trusting it. This is also now the second real production
`ingest-mined --promote` since WO-P300-E5.004 Part A went live -- the
next cold-"pre"-cache `ingest-mined` run (i.e. the next one after this)
is the one that will actually exercise Part A's reconstruction path
against TODAY's new 16,801-pattern baseline; today's own reconstruction
ran against the prior 14,812 baseline, logged in the entry above.





---

**>>> 2026-08-04 (Sonnet) -- APPENDED OUT OF ORDER (filesystem MCP edit tool timed out mid-session, ~4min stall, same relay-failure family as git/python -c; switched to windows-mcp:FileSystem append rather than retry or risk a full-file rewrite on a 102KB file without a safe partial-edit tool):**

**WO-P300-E5.002 and WO-P300-E5.005 -- both CLOSED.** Fresh session,
INIT'd this chat, wrote none of the underlying code or the 2026-07-30
completion-gate test. Independent review performed against real source,
not the ledger's own prior claims (M-054):

- **E5.002:** re-read `catalog_merge_pipeline.py`'s `promote_staging_to_live()`
  directly -- computes `new_pids`, derives `expected_delta`, calls
  `verify_and_promote()`, raises on failure. Matches the WO's claim
  exactly. Confirmed via `grep` across the whole `python/` tree that
  `promote_staging_to_live()` has exactly 2 real call sites
  (`cli_commands/bulk_promote.py`'s `merge-research-catalog --promote`
  and `ingest-mined --promote`), both routing through this one fixed
  function -- no second, unverified promote path exists anywhere.
- **E5.005:** builds on the 2026-07-29 independent review already on
  file. Confirmed the auto-promote call chain end-to-end via direct
  source read: `P_300_RunBulkAddPattern.ps1` -> `promote-gate` (exit
  code only, confirmed decide-only, never calls `promote_staging_to_live()`
  itself) -> on PROMOTE, `ingest-mined --promote` -> the same single
  verified function. Exactly one path mutates the live catalog.
- **Fresh PEH re-run, all 5 relevant test files** (`Agentic-Hub-Governance\verify\run_this.py`,
  Tony ran it, pasted full output): `test_verify_ingestion.py`,
  `test_walkforward_report_io.py`, `test_promote_gate.py`,
  `test_promote_marker_io.py`, `test_cli_registry_inventory.py` --
  **ALL 5 PASSED, exit 0.** Not trusting the 2026-07-30 transcript
  alone -- this is an independent re-confirmation, matching the
  precedent the 2026-07-29 E5.005 review already set for this exact
  closure.
- **Completion Gate checklist backfilled into both WO files** (neither
  had one on file; E5.005 predates the rule requiring it at OWNER_DONE
  time, backfilling now is the honest close-out). Caller Propagation
  and Imperative Sweep boxes both checked with named evidence, not
  assumed clean.

**Self-caught mid-session:** this session's own INIT read the
project-attached SIP (v3.3) instead of the live file on disk (v3.5,
Step 0.6 -- promote-marker HALT check -- added 2026-07-28). M-015
violation, caught and corrected same session before it caused any real
gap (checked `P_300_promote_marker.json` retroactively: absent, no
HALT owed). Session header format corrected going forward:
`P_300 [Day, Month DD, YYYY] [HH:MM] ET`, no `--` separator.

**Minor flagged, not fixed this session:** `CLAUDE.md`'s "Current SIP:
v3.3" note (2026-06-18) is now stale -- real version is v3.5. One-line
fix, not done here (out of this session's requested scope), logged so
it surfaces next time someone's in that file. `verify_ingestion.py`
still carries 3 copies of a stale docstring claim
(`check_topk_cache=True` passed by `promote_staging_to_live()` -- it
isn't) -- already logged in WO-P300-E5.002, cosmetic, unfixed.
`p300-project-context` SKILL doesn't yet name `P_300_promote_marker.json`
in Critical Paths -- SIP already covers the HALT, so this is a
nice-to-have.

**Both WOs' full evidence trail (Completion Gate + Independent Review
sections) is in the WO files themselves**, not just here.


---

**>>> 2026-08-04, later same day (Sonnet) -- APPENDED OUT OF ORDER (same
filesystem MCP timeout as the entry above -- tool still not retried):**

**Real production incident, resolved same session.** The 12:03 BulkAddPattern
batch promoted cleanly to live (`080426catalog.db`, 175.3 MB, `.bak` matches
prior live size exactly -- confirmed on disk before touching anything else)
but `archive-mined` failed on all 20 files: `E:\` (MINE_ARCHIVE_DIR) hit
`[Errno 28] No space left on device` -- 0.00 GB free out of ~931 GB used.
Not a P_300 bug -- root cause was Windows File History / Macrium Reflect
disk images consuming the drive (P_300's own `AI-Agent-Learning-Hub_
BackupFiles` folder was only ~183MB of the total). Tony freed space himself
(682.82 GB free after) and removed the corrupt 994-byte zip stub the failed
run left behind.

**Archived via PEH** (`Agentic-Hub-Governance\verify\run_this.py`, calling
`utilities.archive_mined_file.run_archive()` directly per file, same
function `archive-mined --xlsx` calls): **20 / 20 archived, exit 0.**
`E:\AI-Agent-Learning-Hub_BackupFiles\Aug26BULKPattern.zip` confirmed on
disk, 6.9 MB. `data\bulk\mine\` confirmed empty afterward. Tickers: AIQ,
ASTS, BBAI, BBBY, ENPH, EXP, FLNC, GGAL, HRZN, IREN, JMIA, KEY, OCSL, PAVE,
POOL, PSEC, RKLB, RKT, RY, VUZI.

**Self-caught mid-session:** attempted a `python.exe -m py_compile` sanity
check via `windows-mcp:PowerShell` earlier the same session (verifying the
`verify_ingestion.py` docstring fix) -- hung the full 4-min ceiling, exact
M-030 failure. Did not retry; verified the edit by re-reading the file
directly instead. No repeat of that mistake on this archive task -- went
straight to PEH.

**Not yet done:** `P_300_Preflight.bat` re-run (the script's own closing
instruction, operator-run) -- INIT will read stale catalog counts (23,365/
369, dated 2026-08-03) until that happens. `CLAUDE.md`/SIP v3.3->v3.5 and
`verify_ingestion.py`'s 3 stale docstrings were fixed earlier this session
(see prior entry).

---

**>>> 2026-08-05 (Sonnet) -- WO-P300-E5.007 BUILT: Chaikin permanent-skip filter wired at both call sites:**

**EDVMF classified and added.** Web-verified (Bloomberg/CNBC/StockTitan):
OTCQX:EDVMF, primary listings LSE:EDV and TSX:EDV -- Endeavour Mining plc.
Same Class 2 shape as CDPYF/CNSWF. Added to `data\reference\chaikin_skip_list.csv`
(5 rows -> 6), resolving the WO's one deliberately-unconfirmed entry.

**Scope decision (WO's "still open" item):** filter at both call sites,
duplicated ~15-line read+filter block per script rather than a new shared
.ps1 module -- the CSV stays the single source of truth for the list
itself; only the trivial read/filter code is duplicated, matching the
existing per-script hardcoded-constant convention ($LOG, $PROMPT_TEMPLATE
aren't shared today either).

**Files changed (3, all plan-gated, approved before build):**
- `data\reference\chaikin_skip_list.csv` -- +1 row (EDVMF).
- `P_300_RunChaikinBatch.ps1` (25 -> 42 lines) -- `$SKIP_LIST_CSV` constant,
  filter block right after `$actionable` derivation, `[SKIP] <symbol> --
  <reason>` visible per skip (hard requirement per WO), refined the
  "nothing to run" message to distinguish "no BUY/WATCH at all" from
  "all BUY/WATCH were on the skip list" -- the WO's silent-narrowing
  concern applies to this message too, not just the skip itself.
- `P_300_RunAllDailyEvals.ps1` (~103 -> ~122 lines) -- identical block at
  its inline Chaikin chain's equivalent insertion point, plus
  `Add-Content -Path $LOG` for each skip line (this script is already
  building that log; the standalone script only reads it, so no
  Add-Content there).

**Verified before calling this done:**
- Full file re-read after each write, compared against intended content
  (M-110) -- no truncation, correct order, both files complete.
- `[System.Management.Automation.Language.Parser]::ParseFile()` on both
  .ps1 files -- 0 parse errors each (PowerShell's ast.parse() equivalent).
- Real execution of the filter block against the live CSV with a mixed
  fake symbol list (AAPL, XYLD, EDVMF, MSFT, CDPYF) -- correctly narrowed
  to AAPL/MSFT, printed 3 named `[SKIP]` lines with real reasons pulled
  from the CSV, skip count matched. Not just syntax-valid -- confirmed
  logically correct against real data (M-110's full standard: parse,
  then run).

**Not touched (explicitly out of scope per WO):** `chaikin_batch_prompt.txt`
ETF-route bug, XYLD/EDVMF stub-section cleanup in existing vault notes --
both listed under WO-P300-E5.007's "OPEN, NOT PART OF THIS WO," awaiting
separate go-ahead.

**Next real-world proof:** first live DailyEval or standalone Chaikin
batch run that includes a skip-list symbol in its BUY/WATCH set --
confirms the `[SKIP]` line fires in production, not just in this
session's synthetic test. WO-P300-E5.007 not marked CLOSED here --
this session wrote the code (WO_COMPLETION_GATE: needs a fresh-session
independent review before closure, same standard as E5.002/E5.005).
