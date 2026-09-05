# P_300 Task Queue

## 2026-09-04 (2nd) -- F2 State Change: Chaikin MCP Pull (14 symbols, 1 failed, 0 no-coverage)
RunChaikinBatch.ps1 -Schema P300 hit the headless-bridge failure again
(exited 1, 0/14 notes updated) for SARK, ABM, CFG, CIFR, CRUS, FHN, FISV,
HUT, IREN, KEY, PNC, RIVN, SYNA, VRT. Pulled all 14 via docs/processes/
chaikin_mcp_pull.md, this session's own claude-in-chrome MCP tools.

**Updated (13):** ABM Neutral, CFG Neutral, CIFR Very Bearish, CRUS
Neutral+, FHN Neutral+, FISV Neutral, HUT Bearish, IREN Neutral, KEY
Bearish, PNC Neutral+, RIVN Very Bearish, SYNA Neutral, VRT Neutral. All
13 vault notes confirmed with real ## Chaikin Power Gauge sections,
mtimes 10:20:34-10:27:52, sequential, ratings cross-checked against the
raw page text before writing. 9 of 13 hit the known page-load race on
first read (blank/N/A) -- resolved on retry per runbook step 3 every
time.

**Failed (1):** SARK (Investment Managers Series Trust II - Tradr 1X
Short Innovation Daily ETF) -- "Oops! Something went wrong. Please try
again later."

**CORRECTION (same day, Tony's screenshot):** this was NOT an engine
error. SARK is an ETF; `/pgr/stock/SARK` (the URL this runbook always
uses) throws "Oops!" for ETF tickers -- the correct path is
`/pgr/etf/SARK`, which loads cleanly: Rating None, "This ETF is
unrated", ETF Group Global Inverse Equity, Holdings 0. Same shape as
the existing XYLD/BITX/CRPT/CLIX skip-list entries. The 2026-08-28 and
2026-09-03 "Oops!" failures were the identical misdiagnosis, not two
separate recurrences -- one root cause, caught late. Added to
chaikin_skip_list.csv this session. `docs/processes/chaikin_mcp_pull.md`
also gained a step: try `/pgr/etf/{TICKER}` before reporting Failed on
any `/pgr/stock/{TICKER}` "Oops!" response.

**No-coverage:** SARK confirmed genuine (ETF, unrated, see correction
above) -- all 14 resolved to a real rating or SARK's no-coverage.

**Chart Is King divergence flagged (disclosure, not override):** of this
batch's 5 BUY signals (CIFR, CRUS, HUT, RIVN, VRT), 3 landed
Bearish/Very Bearish on Chaikin -- CIFR (BUY, Very Bearish: high LT
debt-equity, high price-to-book), HUT (BUY, Bearish: high debt-equity,
high price-to-sales), RIVN (BUY, Very Bearish: high price-to-book, very
negative expert activity/short interest). All three are richly-valued,
high-debt growth names (bitcoin-mining infrastructure + EV) where the
pattern read is bullish and the fundamentals/expert-activity read is
bearish. CRUS and VRT (also BUY) landed Neutral+/Neutral -- no conflict.

---

## 2026-09-04 -- F2 State Change: WO-P300-E5.009 + WO-P300-E5.010 both CLOSED, independent review
Fresh session (INIT only, wrote none of the code under review). Tony's
instruction: "do Both."

**E5.009 (SIP Step 1B):** verified live -- SIP file read in full (v3.6,
Step 1B present verbatim), byte-scanned both edited files myself
(CR=0/LF=205 on the SIP, CR=0 on the archive -- matches the WO's own
post-write claim, not just trusted). Re-ran Step 1B's actual check logic
against TODAY's real files, not the 08-29 demo: todo.md fires (756 lines
> 500), lessons.md silent (37 entries/54.5KB, under cap since the 08-31
archive pass). No discrepancies. CLOSED.

**E5.010 (h5 timing finding):** both report files matched the WO's
numbers verbatim. Found one stale claim -- the two `run_this_P300_
20260831_*` PEH scripts weren't in `verify\` as stated, swept into
`verify\_archive\_stale_uninspected_20260902\` by an unrelated cleanup;
content intact, corrected in the WO rather than treated as a blocker.
Confirmed `signal_classifier.py`'s 08-31 mtime predates this WO's own
scripts by over an hour (the already-logged M-119/M-120 smoke-test fix,
not scope creep). Decided the CLAUDE.md question the WO left open --
added an `outputs\reports\ledger\` row to Canonical Paths. Staged a new
PEH script (`run_this_P300_20260904_095904.py`) to independently
recompute the complete-case panel (not just copy the WO's numbers) and
spot-check one row against `buy_ledger.db` raw values -- Tony ran it,
PASS, all five horizons matched inside tolerance, DE/2026-06-02 spot-check
confirmed the M-020/M-120 x100 scaling is actually correct against a real
row. CLOSED. No change to `signal_classifier.py`'s tiebreak -- WO's own
recommendation (re-check against a second market window first) stands.

Both WO files updated in place with Independent Review sections;
CLAUDE.md Canonical Paths gained one row. No production code touched by
this review session.

Open P_300 work orders after this: E5.001 (PENDING, import-linter,
unstarted) only.

---

## 2026-09-03 -- F2 State Change: Chaikin MCP Pull (13 symbols, 1 failed, 0 no-coverage)
RunChaikinBatch.ps1 -Schema P300 hit the headless-bridge failure again
(exited 1, 0/13 notes updated) for ARRY, FRT, LFCR, MFC, RDDT, RDN, RY,
SARK, SEDG, SLF, SLM, VST, WMT. Session was logged out of Chaikin's own
site at first navigate (login page returned for ARRY) -- paused per the
runbook, Tony logged back in, re-navigate succeeded immediately after.
Pulled all 13 via docs/processes/chaikin_mcp_pull.md, this session's own
claude-in-chrome MCP tools.

**Updated (12):** ARRY Neutral+, FRT Bearish, LFCR Neutral, MFC Very
Bullish, RDDT Neutral, RDN Neutral, RY Neutral+, SEDG Neutral+, SLF
Bullish, SLM Neutral-, VST Very Bearish, WMT Bearish. No page-load races
this batch -- all 12 returned full data on the first get_page_text after
login. Final sweep: all 12 LastWriteTime timestamps cluster
15:15:15-15:17:59, all 12 contain "## Chaikin Power Gauge", all 12
ratings cross-checked against the raw page text before writing.

**Failed (1):** SARK (Investment Managers Series Trust II - Tradr 1X
Short Innovation Daily ETF) -- page returned "Oops! Something went
wrong. Please try again later." on two separate attempts, same failure
shape as 2026-08-28's TSLY (leveraged/theme single-instrument ETF, Power
Gauge engine erroring, not the standard no-coverage shell). Not retried
a third time. Note untouched.

**No-coverage:** none this batch -- all 13 resolved to either a real
rating or the TSLY-shaped engine error above.

---

**>>> 2026-08-29, Gap analysis -- Citadel "Cross-Regime Bayesian Optimization" infographic + Apodex-promoted "Regime-Adaptive" article checked against real P_300 architecture, no build:**

Tony uploaded a Citadel Research infographic (7-principle Bayesian-optimization/ML-ensemble framework for regime-robust equity signals) and asked for a gap analysis against P_300's real architecture, then asked to also check a KnowledgeBase article (`2026-08-29_How Quants Use AI to Build Regime-Adaptive Trading Strategies (Complete Guide).md`, an Apodex-tool promotional piece describing HMM/MS-GARCH regime detection) against the same analysis.

Neither applies to P_300 directly -- P_300 is DTW nearest-neighbor pattern matching, not a trained/optimized model, so there's no hyperparameter space, no ensemble, and (per NFR-1) no place for a stochastic search or a fitted latent-state model in the decision path. The one principle that does bear on P_300 -- regime-robustness matters more than peak-regime performance -- was already tested and decided in WO-P300-E5.006 (real 6.67pp spread, routed to sizing, not the matcher). Both new sources independently land on the same placement (regime state throttles position size, not signal generation) by different technical routes, which strengthens rather than changes that call. One candidate idea surfaced, not built: an entropy-based "suppress trading when the regime read is ambiguous" circuit breaker, worth keeping in mind if WO-P010-E2.001 gets picked up.

Full transcription + point-by-point comparison in `docs/P_300_Regime_Robustness_Gap_Analysis_2026-08-29.md`.

---
**>>> 2026-08-29, Claude in Chrome scheduled shortcuts investigated for Chaikin automation and ruled out -- do not re-investigate:**

Tony asked whether the extension's native Schedule feature (Once/Daily/Weekly/etc, found in Create shortcut) could replace the broken claude -p --chrome headless bridge. Tested live, twice, with real fires: the scheduler is real and does fire fully unattended (proven with a one-time test shortcut that ran on its own and correctly reported SPY's Power Gauge rating). But a second test confirmed it has zero filesystem/export capability -- Claude's own words: "there is no file-writing, download, or export tool available to me." It can read a page unattended; it can never write the vault note.

Conclusion: closed dead end, same shape as the earlier chaikin_reader.py Playwright dead end. Full test detail and evidence in WO-P300-E4.009.md's POST-CLOSURE ADDENDUM (2026-08-29). The session-driven claude-in-chrome MCP pull (chaikin_mcp_pull.md) stays the mechanism -- that session carries filesystem/Obsidian tools the extension alone never will.

---
**>>> 2026-08-29, WO-P300-E5.009 OWNER_DONE -- SIP Step 1B (working-state size reminder) built, not yet independently reviewed:**

Added SIP Step 1B (v3.6) between Step 1A and Step 2: reads tasks/todo.md and tasks/lessons.md via windows-mcp:FileSystem (no Python), prints a one-line archive-pass-due reminder when over the WO-P000-E8.001 caps (todo.md >500 lines/>100KB; lessons.md >40 entries/>70KB), silent otherwise. Retention rule on the SIPs own changelog was being violated (three live entries, v3.5/v3.4/v3.3, against its stated two-version rule) -- fixed as part of this build: v3.4 and v3.3 moved to docs/P_300_SIP_CHANGELOG_ARCHIVE.md.

Demonstrated against real numbers, not synthetic: both live P_300 files fire right now (todo.md 595 lines/77.1KB; lessons.md 42 entries/58.2KB) -- confirms this WOs own premise, files were already over cap. Silent branch demonstrated against two real cross-project files under cap (P_400 todo.md 66 lines/3.4KB; P_000 lessons.md 5 entries/5.8KB), since no live P_300 file was available under cap to show it. Full numbers and Completion Gate in WO-P300-E5.009.md.

SKILL checklist line proposed via propose_skills, not yet clicked by Tony.

WO status: PENDING -> OWNER_DONE. Per WO_COMPLETION_GATE.md, the building session cannot self-close -- needs a fresh-session Independent Review before CLOSED.

---

**>>> 2026-08-29, WO-P300-E4.009 CLOSED -- loud detection proven (9/9), but found the automated Chaikin path is currently broken 100% of the time, not intermittently:**

Reviewed RunChaikinBatch.ps1 (Hub root) against live code and live data. Loud detection (Tee-Object, 16-phrase list, empty-output check, red banner, failure log) works exactly as designed -- read chaikin_failures.log in full, 9 real automated-batch failures 2026-08-21 through 2026-08-28, every one correctly caught, zero silent misses.

New finding: all 9 of those failures have the identical cause (claude -p --chrome falling back to a stateless WebFetch, no browser tool available, 403 on Chaikin) -- the automated headless path has not worked once in 8 days, worse than this WO's prior "occasionally flaky" history. Swept the vault (44 notes, 08-20 through 08-27): 36/38 actionable notes since the failures started DO have a real Chaikin section anyway, confirming the manual chaikin_mcp_pull.md runbook is covering the gap most days. Two misses, both already-diagnosed non-issues, not new: 2026-08-27_TSLY (Chaikin errors on this ETF type) and 2026-08-26_BRK_A (CORRECTED -- Tony flagged this was already investigated 08-27, missed on first pass of this review, logged as M-116: BRK_A/BRK_B fail to resolve under the underscore ticker format, but retried with Chaikin's period format, BRK.B has real data while BRK.A is confirmed genuine no-coverage, verified three times. Nothing further needed on BRK_A itself.

One backlog item surfaced, not built (Tony's call): decide whether to keep RunChaikinBatch auto-firing daily inside RunAllDailyEvals now that it reliably just writes a failure-log entry, or gate it off until the headless bridge is revisited. Separate, smaller open item already on file (not new): whether _last_prompt.txt's ticker resolution should auto-map dual-class tickers to Chaikin's period format so a future BRK.B-shaped case is not caught by hand.

WO status: OWNER_DONE -> CLOSED, full Completion Gate filled against real evidence. Independent Review section appended to the WO file.

---
**>>> 2026-08-29, WO-P300-E5.006 CLOSED -- independent review complete, same day, fresh session:**

Reviewed all four deliverables from the OWNER_DONE session against real files, not the WO prose: pre-registered context files match printed results exactly (no post-hoc changes to buckets/bar/floor); 08-26 walk-forward report line count (221,996) confirmed directly; both SPY/QQQ 10yr grids (data\reference\) independently re-verified at 2,514 bars each, 2016-08-29..2026-08-28, via a new PEH script using openpyxl directly rather than the production reader under review; swept every file under python\ for mtimes since 2026-08-27 and found zero production-code changes, confirming the WO Completion Gate claim.

Closed both open reviewer decisions the WO flagged: added a data\reference\ row to CLAUDE.md Canonical Paths (documentation gap, no judgment call); M-114 promotion to SKILL/SIP proposed to Tony separately via the skills UI (skill-file edits do not take effect from disk), not blocking closure.

WO status: OWNER_DONE -> CLOSED. Independent Review section added to the WO file with the full checklist. Script + context + .done at verify\run_this_P300_20260829_105337.*.

Next in queue: WO-P300-E4.009 review, then the WO-P300-E5.009 build (Tony set this order, 2026-08-29). WO-P010-E2.001 stays parked for a P_010 session -- P_010 owns it, P_400 is Affects only (correction logged as M-115).

---
**>>> 2026-08-21, direction locked (Tony: "do it") -- Chaikin MCP pull formalized as a runbook, not left as one-off manual steps:**

New file: `docs\processes\chaikin_mcp_pull.md` (v1.0) -- documents today's proven method (session-driven `claude-in-chrome` MCP pull, replacing `claude -p --chrome`) as a repeatable procedure: read `_last_prompt.txt` for the resolved candidate list, pull each symbol from `/pgr/stock/{TICKER}`, retry-before-no-coverage on empty reads, write + verify per symbol, report in three buckets. Logged to WO-P300-E4.009.

**Scope, deliberately:** this is session-driven, not unattended -- still needs a human to open a chat and invoke it. True unattended automation (extension-native scheduling, or a properly tested headless MCP config) was explicitly deferred, not built -- two candidates named in the WO entry, neither tested, given this WO's whole history is built on burned headless-behavior assumptions.

**Not done:** `p300-project-context` skill's "Pairs With" table should list this new runbook alongside `evaluate_trade.md`/`add_pattern.md` -- skill file edits don't take effect from disk (Protocol E, system-doc-initializer), Tony needs to add it via Customize -> Skills in-app.

---
**>>> 2026-08-21, real fix landed (Tony + Sonnet) -- all 8 Chaikin ratings actually written, via a different mechanism than the CLI pipeline entirely:**

Root cause fully isolated (see prior entry): `claude -p --chrome` (headless CLI-to-extension bridge) is broken; the extension itself, Tony's Chaikin login, and interactive `claude --chrome` all work fine. Rather than keep chasing the headless bridge, used this chat session's own `claude-in-chrome` MCP tools -- a completely separate connection path, no CLI subprocess, no native-messaging bridge -- to navigate directly and pull real data.

**First attempt hit a real, expected wall:** navigating to a new domain (chaikinanalytics.com) from this session returned "Permission denied by user" -- the extension is in "Ask before acting" mode, requiring a live approval click per new site. Tony triggered that approval himself in his own side panel (tested on SPY, worked). Confirmed the approval is a **browser-level allowlist, not per-conversation** -- this session's next navigate to the same domain went through with no prompt.

**All 8 symbols pulled and written directly to the vault notes** (AGCO, CBOE, CLSK, GLPI, GPK, MSCI, RIOT, YUM) -- real Power Gauge ratings, full Quick Stats blocks, real summary paragraphs, matching the existing prompt template's exact format (`chaikin_prompt_template.txt`, corrected navigation to `/pgr/stock/{TICKER}`, not `/20-factors` -- the latter was this session's own first mistake, missing the Quick Stats block entirely). One transient empty-page read on CBOE (page hadn't finished rendering) -- retried rather than misreported as no-coverage; second read was real.

**Independently verified, all 8, after writing:** every note has a real `## Chaikin Power Gauge` section, `LastWriteTime` matches the write, ratings spot-checked against the page text pulled (Neutral/Neutral+/Bearish/Bearish/Neutral-/Neutral/Bearish/Very Bearish for AGCO/CBOE/CLSK/GLPI/GPK/MSCI/RIOT/YUM respectively). This is the actual objective -- not infrastructure, not a detector, real Chaikin data on real notes.

**Not yet decided:** whether the *automated* pipeline (unattended DailyEval runs) should be rearchitected around an MCP-connected session doing this directly, replacing `claude -p --chrome` outright, rather than continuing to debug the headless bridge. Real option now proven to work manually; turning it into something that runs unattended is a separate design question, not started.

---
**>>> 2026-08-21, later same session (Tony + Sonnet) -- Clean A/B test isolates Chaikin failure to the headless CLI bridge specifically; extension and Chaikin auth both ruled out:**

Tony ran `/check-power-gauge` (a pre-existing Claude in Chrome shortcut) directly in the extension's side panel against a live Chaikin page (CIGI) -- worked perfectly, real rating returned, at the same time `RunChaikinBatch.ps1 -Schema P300` failed again with the same banner. Rules out Chaikin auth and extension health entirely; narrows the open question to the headless `claude -p --chrome` bridge specifically (matches WO-P300-E4.009's 08-10/08-13 open question, cleanest data point yet).

Possible real fix path surfaced, not investigated: Claude in Chrome shortcuts can be scheduled natively (Anthropic docs), entirely inside the extension, no CLI bridge involved. If parameterizable per-symbol, could replace `claude -p --chrome` as the mechanism outright. Architecture question -- needs Tony's call, not started.

Logged to WO-P300-E4.009.

---
**>>> 2026-08-21, real production confirmation (Sonnet + Tony) -- rebuilt Chaikin detector fired correctly on a genuine live failure; one encoding bug found and fixed:**

Tony re-ran `RunChaikinBatch.ps1 -Schema P300` standalone against the same 8 unfulfilled candidates (AGCO, CBOE, CLSK, GLPI, GPK, MSCI, RIOT, YUM). Real failure recurred (same underlying WebFetch/403 issue). Red banner fired. `chaikin_failures.log` got its first-ever real entry, full captured response text, correctly schema-tagged and timestamped.

**Independently verified, not taken on the banner alone:** all 8 vault notes checked directly -- zero have a `## Chaikin Power Gauge` section, all `LastWriteTime` predate this Chaikin attempt (unchanged since the original DailyEval write). Ground truth matches the banner and the log exactly. First real production round-trip on the rebuilt detector -- worked correctly on every count (fired when it should, log captured the real cause, no false signal).

**Bug found reading the log:** em dashes and similar characters came through as "ΓÇö" -- console active code page was 437 (OEM US) despite `[Console]::OutputEncoding` reporting UTF-8, mis-decoding claude's UTF-8 stdout. Same failure class as M-019/EC-069 (Python stdout vs cp1252), new instance. Fixed: `chcp 65001` added immediately before the `claude -p --chrome` call. 113 -> 120 lines, parse-clean. Not yet re-confirmed against a real run (next real Chaikin call, success or failure, will show clean characters or not) -- low-risk, cosmetic-only fix, didn't block logging this as done.

---
**>>> 2026-08-21, later same session (Sonnet) -- Chaikin loud-detection rebuilt in RunChaikinBatch.ps1 (Hub-root); legacy P_300_RunChaikinBatch.ps1 finally archived and retired:**

Per Tony's go-ahead: `RunChaikinBatch.ps1` (Hub-root, WO-P800-E4.001's deliverable) rebuilt with Tee-Object capture, the full contraction-aware failure-phrase list plus 5 new phrases for today's WebFetch/403 failure shape, empty-output check, red banner, and a new `shared_resources\chaikin_enrichment\chaikin_failures.log`. Also fixed a second regression found mid-rebuild: `$prompt` had reverted to positional-argument passing (the exact truncation bug fixed 2026-08-10) -- restored stdin piping. 43 -> 113 lines, 0 parse errors, tested against today's real failure text (6/16 patterns match, would have fired) and a synthetic success string (0 false positives).

Legacy project-local `P_300_RunChaikinBatch.ps1` -- the file WO-P800-E4.001 always intended to retire but never actually removed -- archived to `E:\AI-Agent-Learning-Hub_BackupFiles\P_300\P_300_ArchiveFiles.zip` (verified: zip entry present, byte-exact) and deleted from live, Tony's explicit instruction.

WO-P300-E4.009 and WO-P800-E4.001 both updated with dated entries describing the rebuild and the archive. Neither WO closed -- E4.009 still needs a real production run to confirm the rebuilt detector; E4.001 still blocked from CLOSED by the pre-existing Completion Gate gap flagged earlier this session.

---
**>>> 2026-08-21 (Sonnet) -- Real Chaikin batch failure occurred (11-symbol DailyEval, 0/8 Chaikin updated); WO-P300-E4.009's documented loud-detection mechanism confirmed ABSENT from the live code path -- superseded, undocumented, during the 08-12 schema-driven migration:**

**Real production run:** `P_300_RunAllDailyEvals.ps1`, anchor 2026-08-20, 11 symbols. All 11 evaluations completed. 8 BUY/WATCH candidates (AGCO, CBOE, CLSK, GLPI, GPK, MSCI, RIOT, YUM) fed to `RunChaikinBatch.ps1 -Schema P300`. Result: 0/8 notes updated. Claude's live console response (captured by Tony, not logged anywhere on disk): attempted WebFetch instead of the Chrome extension, hit 403 Forbidden on Chaikin ("no login session... not even a viewable login page"), correctly refused to proceed and explained why.

**Spot-verified (M-054):** `2026-08-20_YUM.md` -- no `## Chaikin Power Gauge` section, `LastWriteTime` 12:00:45 PM (before the Chaikin attempt) -- confirms a genuine miss, not a silent partial write.

**Finding -- WO-P300-E4.009's own "WHAT WAS BUILT" no longer matches production:** The WO documents Tee-Object output capture + failure-phrase text match + a distinct red banner + a `$LOG` failure line, built into `P_300_RunAllDailyEvals.ps1`'s *inline* Chaikin chain. That inline chain was replaced 2026-08-12 (WO-P800-E4.001 migration) with a call to the Hub-root `RunChaikinBatch.ps1 -Schema P300`, which has **no output capture, no phrase matching, no banner, and writes nothing to any log file** -- confirmed by reading the live script and `shared_resources\chaikin_enrichment\` (no log file exists in that folder). The new wrapper instead verifies success by checking real vault notes for a `## Chaikin Power Gauge` section post-run (arguably more reliable, evidence-based per M-054) and prints a summary count -- which DID accurately report "0/8 ... may be legitimate no-coverage, or a real miss, including auth failure -- check console output above" this run. So the failure was NOT silently missed, but the specific mechanism the WO promises (unmissable banner, named root cause, durable log line) does not exist today. Nobody updated WO-P300-E4.009 to reflect this when the 08-12 migration happened -- it still describes code that was quietly replaced.

**New failure shape, not on E4.009's original phrase list:** `claude -p $prompt --chrome` fell back to WebFetch and hit a 403, rather than a login wall or "extension not connected." Root cause of the fallback itself (why `--chrome` didn't force browser-tool use this run) not yet investigated.

**Not decided this session -- needs Tony's call:** (1) rebuild loud-banner/log capture on top of the new Hub-root call chain, or (2) formally accept the vault-note verification as E4.009's real fix and update the WO to describe it accurately instead of the retired inline-chain mechanism. Either way E4.009 stays OWNER_DONE, not touched, pending direction.

**Also this session:** WO-P800-E4.001 header corrected (was 9 days stale, still said "awaiting P_300 Ack" after that Ack completed 08-12) -- both notes it cited (CLIX, NSLR) re-spot-checked live, hold up. Found the WO is blocked from CLOSED for an unrelated reason: its Completion Gate checklist was never added at OWNER_DONE time (2026-07-24), and WO_COMPLETION_GATE.md's own Enforcement rule (added 07-29) forbids backfilling it now. Flagged in the WO itself, not resolved -- needs Tony's/P_000's call on how to handle the pre-existing gap.

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
Third pass: 2026-08-29, top-block entries dated before
2026-08-21 and appended (out-of-order) entries dated before
2026-08-23 archived, mechanically, via verify\run_this_P300_20260829_104500.py.
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

**>>> 2026-08-23 (Sonnet) -- Chaikin MCP pull run, 7/7 real candidates:**

**Trigger:** `RunChaikinBatch.ps1 -Schema P300` ran clean (LOOKBACK_DAYS
fix same session -- see below), resolved 7 candidates to `_last_prompt.txt`,
then the headless `claude -p --chrome` step hit its now-familiar failure
(HTTP 403 via WebFetch, no browser-automation tool in that subprocess --
logged to `chaikin_failures.log` 2026-08-23 19:02:19). Per WO-P300-E4.009's
08-21 direction, did not retry the headless bridge -- ran the session-driven
`chaikin_mcp_pull.md` runbook instead, this session's own `claude-in-chrome`
MCP tools.

**Pulled and verified, all 7:** ABEV (Neutral), LIN (Very Bearish), OI
(Very Bearish), POST (Very Bearish), SIGA (Neutral+), SLGN (Neutral), STLA
(Neutral). One page-load race (LIN first read: zero-width chars, N/A
rating, blank Quick Stats on a liquid large-cap -- second `get_page_text`
came back complete, per runbook step 3's known-race handling). Final sweep:
all 7 `LastWriteTime` timestamps cluster 19:18:50-19:20:55, all 7 contain
`## Chaikin Power Gauge`, all 7 ratings cross-checked against the raw page
text before writing -- not taken from the tool call succeeding alone.

**Real finding, not part of the runbook itself:** 3 of 4 BUYs (OI, POST)
plus the LIN WATCH landed Very Bearish on Chaikin -- a real pattern-vs-
fundamentals divergence, not noise. OI: ROE -94.6%, EPS growth -2.5%. POST:
very negative expert activity / analyst revisions. Flagged to Tony, not
acted on -- Chart Is King is his own standing rule, this is disclosure not
override.

**Separate same-run fix, logged here since it's what made the 7 resolvable
at all:** `shared_resources\chaikin_enrichment\config.py` `LOOKBACK_DAYS`
1 -> 3. The `RunAllDailyEvals.ps1` run immediately prior reported "No
BUY/WATCH candidates" while 7 real WATCH/BUY notes sat in the vault,
filename-dated 2026-08-21 (Friday anchor) against a Sunday `today` --
2 days outside the old 1-day window. Root cause: vault filenames use
`signal_date` (the anchor), not write date (`filename_builder.py`,
confirmed same mechanism for P115 -- both schemas share `_get_date_str()`,
no separate exposure, no separate action needed there). Confirmed safe to
widen: idempotency runs on `has_chaikin_section` per-note
(`candidate_filter.py`), not window size, so a wider window only means
scanning more files.


---

**>>> 2026-08-25 (Sonnet) -- APPENDED past End-of marker, consistent with recent practice -- Chaikin MCP pull run, 7/7 real candidates, headless bridge failure recurred:**

`P_300_RunAllDailyEvals.ps1` run, 8 symbols (CB, CPT, HIG, KNDI, LMND, STAG, VTRS, YELP), all 8 evaluations complete, 0 errors. 7 BUY/WATCH candidates fed to `RunChaikinBatch.ps1 -Schema P300` (CB, CPT, HIG, LMND, STAG, VTRS, YELP -- KNDI not actionable, excluded by the scanner's own filter, not this session).

Headless `claude -p --chrome` step failed again -- same recurring shape as every prior instance (WebFetch/403, no browser-automation tool in that subprocess). Logged to `chaikin_failures.log` 2026-08-25 12:23:19. Per WO-P300-E4.009's established direction, did not retry the headless bridge -- ran the session-driven `chaikin_mcp_pull.md` runbook instead, this session's own `claude-in-chrome` MCP tools.

**Pulled and verified, all 7:** CB (Neutral+), CPT (Neutral-), HIG (Neutral+), LMND (Neutral), STAG (Bearish), VTRS (Neutral+), YELP (Bullish). One page-load race on CB (first read: blank Quick Stats, N/A rating -- second `get_page_text` came back complete, per runbook step 3's known-race handling). Final sweep: all 7 `LastWriteTime` timestamps cluster 12:31:54-12:32:36, all 7 contain `## Chaikin Power Gauge`, all 7 ratings cross-checked against the raw page text before writing.

**No Chart Is King divergence flag this run** -- unlike 2026-08-23's OI/POST/LIN pattern-vs-fundamentals split, this batch's ratings don't show a comparable pattern-vs-fundamentals conflict worth surfacing.

**Tooling note:** `windows-mcp:PowerShell` and `windows-mcp:FileSystem` both hit a full 4-minute no-response stall mid-session (a plain `Get-Date` and a `mode=info` call, neither python.exe-related -- not M-030's specific pattern, a broader relay stall). Did not retry blind -- flagged to Tony, he confirmed the relay was back, retried once, succeeded immediately. No data loss; this F2 entry is being written on the recovered connection.


## 2026-08-26 -- F2 State Change: Chaikin MCP Pull (10 symbols)
RunChaikinBatch.ps1 -Schema P300 hit the headless-bridge failure again
(login wall detected, banner fired correctly, 0/10 notes updated) even
though the Chaikin website session itself was confirmed live (Tony's
screenshot, SPY page, logged in). Pulled all 10 via docs/processes/
chaikin_mcp_pull.md instead: AB, APP, CDNS, CDW, CLFD, GGAL, GT, KEEL,
SMG, VYX. All 10 vault notes (2026-08-25_*.md) confirmed with real
## Chaikin Power Gauge sections, mtimes 16:44:55-16:47:18, sequential.
APP/CDNS/CDW/GT/KEEL/VYX hit the page-load race on first read (empty/
placeholder), resolved on retry per runbook step 3. No no-coverage
symbols this batch -- all 10 had real Chaikin ratings. Ratings: AB
Neutral, APP Bearish, CDNS Neutral, CDW Bullish, CLFD Neutral, GGAL
Neutral, GT Very Bearish, KEEL Very Bearish, SMG Neutral, VYX Bullish.
This is another real production firing of WO-P300-E4.009's loud
detection (banner correctly caught the headless-bridge miss) -- see WO
file for running list.


## 2026-08-27 -- F2 State Change: Chaikin MCP Pull (8 symbols, headless bridge failed again)
RunChaikinBatch.ps1 -Schema P300 hit the headless-bridge failure again
(banner fired correctly, 0/8 notes updated) for BRK_A, BRK_B, DOMO, FFIV,
GNTX, OTIS, QCOM, XRX. Pulled all via docs/processes/chaikin_mcp_pull.md
instead, this session's own claude-in-chrome MCP tools.

**Real finding, not part of the runbook itself:** BRK_A / BRK_B (the
underscore-formatted dual-class tickers in _last_prompt.txt / the
resolved note paths) do not resolve on Chaikin's site as-is --
/pgr/stock/BRK_A loads a real page shell (Recently Viewed sidebar,
Quick Stats headers) but with no data (title "(BRK_A) N/A", Rating
None, "Power Gauge summary not available"), which reads exactly like
a genuine no-coverage case unless you know to suspect the ticker
format. Retried with the period format Chaikin actually uses --
BRK.A: confirmed real no-coverage (full Quick Stats populate, Rating
still None/"Power Gauge summary not available" -- Chaikin does not
rate the A-share). BRK.B: real Bullish rating, full data. So of the
two, only BRK_A is genuinely uncovered; BRK_B was one ticker-format
fix away from a false no-coverage report.

**Written (7):** BRK_B (Bullish), DOMO (Very Bullish), FFIV (Very
Bullish), GNTX (Neutral), OTIS (Very Bearish), QCOM (Neutral), XRX
(Bullish). All 7 vault notes confirmed with real ## Chaikin Power
Gauge sections, mtimes 15:16:01-15:16:52, sequential.

**Skipped, no-coverage (1):** BRK_A -- confirmed genuine (see above,
not a page-load race, not a runbook step-3 retry case).

**Open question, not resolved this session:** whether _last_prompt.txt's
ticker resolution (Python-side, upstream of this runbook) should map
dual-class tickers to Chaikin's period format before generating the
candidate list, so a future pull doesn't have to catch this by hand.
Not fixed -- flagged only.


## 2026-08-28 -- F2 State Change: Chaikin MCP Pull (5 symbols, headless bridge failed again)
RunChaikinBatch.ps1 -Schema P300 hit the same headless-bridge failure
(banner fired correctly, 0/5 notes updated) for BRK_A, RBA, TDC, TE,
TSLY. Pulled via the MCP runbook, this session's own claude-in-chrome
tools, same as every prior occurrence.

**Updated (3):** RBA Bearish, TDC Neutral+, TE Bearish (T1 Energy Inc.,
not TransAlta -- real ticker match confirmed on page). All 3 vault
notes confirmed with real ## Chaikin Power Gauge sections, mtimes
12:30:45-12:31:00, sequential.

**Skipped, no-coverage (1):** BRK_A -- not re-tested, already confirmed
genuine no-coverage yesterday (2026-08-27, period-format retry +
Tony's own screenshot both confirmed Rating None/unrated).

**Failed, real reason (1):** TSLY (Tidal Trust II - YieldMax TSLA
Option Income Strategy ETF) -- page loaded the sidebar/nav fine but the
main content area returned "Oops! Something went wrong. Please try
again later." on two separate attempts (reload + retry), not the usual
blank-placeholder race and not the standard no-coverage shell (Rating:
None + "Power Gauge summary not available" on an otherwise normal
page). This looks like Chaikin's Power Gauge engine erroring on this
specific instrument type (actively-managed single-stock options-income
ETF), not absence of coverage. Reported as Failed per the runbook's
three-bucket rule, not folded into no-coverage. Not retried a third
time. Note untouched.



## 2026-08-29 -- F2 State Change: WO-P300-E5.006 step 3 false blocker
## cleared; 214.5h rescore NOT required; SPY/QQQ grids need re-export
Tony challenged the 08-27/28 conclusion that step 3 needed a ~214.5h
uncached walk-forward run. Verified live: the eval already exists --
outputs\reports\eval\walkforward_staging_ingest_mined_default_
20260826_130212.txt covers all 44,399 patterns x 5 horizons (221,996
lines), written by the 08-26 promote's post-batch step; topk_cache on
082626catalog.db is current (887,712 rows, 1444 new + 42341 rechecked
per the 08-26 log). The prior session keyed only on the JSON cache
fingerprint (pre-batch, misses by design after every promote).

**Dropped:** checkpoint/resume plan (eval_checkpoint_io.py +
run_eval_loop.py changes) -- not built. P_300_RunEvalLoop_KeepAwake.bat
stays on disk, do NOT run it against the live catalog.

**Logged:** M-114 (lessons.md), CORRECTION 2026-08-29 appended to
WO-P300-E5.006 + Status header corrected.

**New small blocker:** the SPY/QQQ 10-yr grid files confirmed 08-27
are gone from disk (data\bulk\mine\ holds only 8 symbol files; no
copy under the project or E:\). Tony re-exporting to
data\reference\SPY_grid_10yr.xlsx / QQQ_grid_10yr.xlsx (Date, Close
Price, Medium Term Difference, Long Term Difference). Verify on disk
before writing the step 3 script.

**Next:** step 3 read-only PEH script -- join 08-26 report
(final_signal_class, chosen_horizon, is_chosen_horizon=True) to real
forward_labels outcome, tag anchor_date with VP-reconstructed
avg_posture from the two grids, bucket, check BUY win-rate spread
against the pre-registered 5pp bar. Pre-register buckets in the
context file before running.


## 2026-08-29 -- F2 State Change: WO-P300-E5.006 step 3 RUN -- over bar
PEH run PASS first try (run_this_P300_20260829_101500.py). BUY win rate
by P_010 regime: OFF 72.8% (n=9,491) / HALF 73.6% (n=1,310) / FULL
66.9% (n=7,738); spread 6.67pp vs pre-registered 5.0pp bar -> OVER.
Direction is opposite to current sizing (best BUY outcomes where P_400
halves risk). But base rate moves too (ALL: OFF 59.5% vs FULL 50.3%),
so BUY lift over baseline is actually larger in FULL (16.6pp vs
13.3pp). Full numbers + caveats in the WO. Grids re-exported to
data\reference\ (verified 2,514 bars each, 2016-08-29..2026-08-28).

**Decision owed by Tony (WO gate):** what, if anything, to do with an
over-bar result. Claude's recommendation: NO matcher/schema change (the
z-score gate already normalizes for regime baseline); the one worthwhile
follow-up is a step 4 read-only measurement -- same join, broken out by
calendar year and with mean/median return_pct and worst-decile return
per bucket -- to test whether the OFF-regime advantage survives
independence and magnitude checks before P_010/P_400 sizing policy is
even discussed. If it doesn't survive, close the WO with a documented
null-after-caveats. Not started.


## 2026-08-29 -- F2 State Change: WO-P300-E5.006 step 4 RUN -- analysis complete
PEH PASS first try (run_this_P300_20260829_103000.py). OFF-regime BUY
advantage holds in 5 of 6 years (2026 YTD reversed) and on every
magnitude measure (expectancy OFF +6.12% vs FULL +5.24%, p10 -6.87 vs
-7.28). But BUY lift over own-regime base rate is HIGHER in FULL every
year but 2021 -- the matcher's z-gate already handles regime. Full
tables in the WO. Recommendation logged: no P_300 build, close WO as
measured/no-build, hand the "OFF-mode size cut vs P_300 BUY
expectancy" question to P_010/P_400 as a candidate WO. Awaiting Tony's
decision on closure + whether to file the P_010/P_400 WO.


## 2026-08-29 -- F2 State Change: WO-P300-E5.006 -> OWNER_DONE; WO-P010-E2.001 filed
Tony's decision: no P_300 build. E5.006 set OWNER_DONE with Completion
Gate written at OWNER_DONE time (EC-005). Independent review owed from
a fresh session -> CLOSED; reviewer checklist is in the WO. Reviewer
open items: (1) add data\reference\ row to CLAUDE.md Canonical Paths
or decide not to; (2) consider promoting M-114 to SKILL/SIP.
Handoff WO filed: WO-P010-E2.001 (Owner P_010, Affects P_400/P_300,
PENDING, read-only questions only, no sizing change authorized).
Session closing; Tony switching to a Sonnet session next.


## 2026-08-29 -- F2 State Change: archive roll (3rd pass) DONE; WO-P300-E5.009 filed
PEH PASS first run (run_this_P300_20260829_104500.py). todo.md 1,240 ->
558 lines / 149KB -> 75KB (dated-log portion 283, cap 500); lessons.md
63 -> 40 entries / 75KB -> 57KB. 29 todo entries + 23 lessons (M-001..
M-041 range, M-015 kept as referenced) moved verbatim to the _archive
files; byte conservation checked (delta 928 = script's own headers).
Backups in tasks\_backup_20260829_archive_roll\ -- delete after the next
session confirms INIT reads clean. Script's SKILL reference path was
wrong (project .claude\skills\ -- real location is Hub-root
.claude\skills\); re-checked after the run: none of the 23 archived IDs
are cited in any SKILL.md, so the miss changed nothing. Correct path
recorded for E5.009. WO-P300-E5.009 (INIT size-check nudge, SIP Step
1B) filed PENDING to close E8.001's "who notices" gap.

**>>> 2026-08-31 (Sonnet) -- INIT through session close, dense day:**
INIT surfaced real drift from stale notes: E5.006/E4.009/E4.004 already
CLOSED (not open as last tracked), E5.009 already OWNER_DONE (SIP v3.6
built, not PENDING), LM Studio running with no model loaded. Diagnosed
the overnight BulkAddPattern batch mid-flight (not hung -- Step 4
promoting, per its own >1hr warning). Fixed two real staleness bugs:
CLAUDE.md's BUY z-gate line (documented z>0.0, live BUY_MIN_Z_SCORE has
been 1.0 since 06-28) and signal_classifier.py's smoke-test case 4
(fixture would have printed WATCH not the BUY it claimed, at the
current gate). 4th lessons.md archive pass (M-042/043/044/045/046/
047/048/051 moved, oldest-first, none referenced live) plus a real
duplicate-ID fix -- two unrelated lessons had both been numbered M-111;
the newer one (headless OAuth, 08-19) renamed to M-118, M-113's
cross-reference updated to match, M-112's correct M-111 reference
verified untouched. M-119 (Path.read_text() lacks newline= on p140's
3.12) and M-120 (a printed "matches known value" claim isn't a check
unless the code asserts it) added same day.

Catalog-growth question settled with data, not opinion: BUY precision
has been flat 70.0-70.4% since ~36K patterns despite 11K more added
since (chart run); root-caused the batch's 10hr Step 2 (vs. the usual
1.5-2hr) to MINE_MIN_ANCHOR_DATE's rolling 5-year window pushing
min_new_date back far enough to force near-full-corpus rescoring in
eval_incremental.py's _partition_unaffected -- confirmed 13 of 15
batch symbols were genuinely new, not redundant re-mining, so the
plateau reads as a DTW signal ceiling, not a coverage gap. CE_GATE
pointed to as the real next lever over more bulk-mining.

Ledger-fill hadn't run since 07-03 despite the DB being written to
daily -- run today (362/553 filled). h5 calibration gap (n=472,
75.5% pred vs 51.1% real, -0.75% avg) diagnosed as broad-based (worst
week 19.8%, worst 5 symbols 12.1% of total negative return, neither
close to a majority) rather than a bad stretch or bad names. Trajectory
check on the same 324 complete-case rows: -0.52% at h5 to +1.92% at
h20, same trades, five time points -- checked against market data
(S&P roughly flat June-July, not a rising tide) before trusting it.
Real evidence for a timing artifact in the classifier's shortest-
horizon tiebreak, not proof. Filed as **WO-P300-E5.010** (OWNER_DONE,
no build, re-check against a second market window before touching the
tiebreak) rather than acted on directly.

Overnight batch finished mid-session: promoted to
083026catalog.db, 44,399 -> 46,809 patterns / 460 -> 473 symbols,
18/18 mine files archived, total runtime 15:46:35 (Step 4 alone
5:16:18 -- same min_new_date mechanism as Step 2, not a new problem).

Open at session close: WO-P300-E5.010 and WO-P300-E5.009 both
OWNER_DONE awaiting independent review (fresh session, not this one).
WO-P300-E5.001 (import-linter) still PENDING, untouched. LM Studio
still has no model loaded. P_300_preflight_status.json is now stale
against the promoted catalog -- run P_300_Preflight.bat before next
INIT. p300-project-context skill's Step 1B checklist line is still an
unclicked propose_skills card, not live.

## 2026-08-31 -- F2 State Change: Chaikin MCP Pull (8 symbols, 2 no-coverage)
Automated RunChaikinBatch.ps1 failed as expected (headless bridge, E4.009
-- 0/10 via the CLI path). Pulled directly via claude-in-chrome MCP per
chaikin_mcp_pull.md: CME, FCNCA, JPM, LULU, PTON, SCHW, SPGI, WFC updated
(## Chaikin Power Gauge section appended, verified via LastWriteTime +
rating spot-check against what was extracted, not tool-call success
alone). LVMUY and TCEHY genuine no-coverage (Rating: None + "Power Gauge
summary not available" on retry, both OTC ADRs) -- no stub written,
matches the runbook's rule. Most symbols hit the known page-load race
(blank/N/A on first get_page_text) -- retried once per the runbook, real
data on the second read every time; only LVMUY/TCEHY stayed empty on
retry, confirming genuine no-coverage rather than a slow load. Two Chrome
browsers were connected with no way to distinguish them from deviceId
alone -- used switch_browser so Tony could pick by clicking Connect in
the actual window, rather than guessing.

## 2026-09-02 -- F2 State Change: Chaikin MCP Pull (7 symbols, 0 no-coverage)
RunChaikinBatch.ps1 -Schema P300 hit the headless-bridge failure again
(banner fired correctly, 0/7 notes updated) for LUMN, BWXT, CVE, GME,
HLX, HPQ, LTC. Pulled all 7 via docs/processes/chaikin_mcp_pull.md,
this session's own claude-in-chrome MCP tools -- the MCP relay itself
had stalled earlier same day (windows-mcp:FileSystem, filesystem:read_text_file,
and a plain Get-Date all timed out at 4 min back-to-back); did not retry
blind, waited for Tony to confirm the relay was back before proceeding.

**Written (7):** LUMN Neutral, BWXT Bearish, CVE Very Bullish, GME
Bearish, HLX Very Bullish, HPQ Very Bullish, LTC Neutral-. No page-load
races this batch -- all 7 returned full data on the first get_page_text.
Final sweep: all 7 LastWriteTime timestamps cluster 15:19:51-15:21:45,
all 7 contain "## Chaikin Power Gauge", all 7 ratings cross-checked
against the raw page text before writing.

**Chart Is King divergence flagged (Tony's rule, disclosure not
override):** GME's P_300 signal is BUY with z=+2.13 to +2.31 across
every horizon (h5-h20, 85% win rate each) -- about as strong a BUY as
this catalog produces -- while Chaikin rates it Bearish on very
negative expert activity (high short interest) and poor financial
metrics, despite very strong earnings performance. Pattern says buy,
fundamentals/expert-activity side says sell.

**Separate finding, not a Chaikin issue:** LTC Properties' note narrative
(LM Studio-generated) refers to the company as "Litecoin (LTC)" --
LTC Properties, Inc. is a health-care REIT; Litecoin is the
cryptocurrency with the same ticker. The narrator hallucinated the
wrong entity from the ticker alone. Doesn't touch the underlying
z-scores/win-rates (real math, unaffected), but the narrative text in
that note is wrong and should not be read as company context. Same
shape as the 2026-08-28 TE/TransAlta mismatch (M-116 family) --
ticker-to-entity confusion in generated text, not in the signal.
