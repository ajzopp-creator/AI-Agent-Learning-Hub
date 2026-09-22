# P_300 Task Queue

## 2026-09-17 -- F2 State Change: Chaikin MCP Pull (4 symbols, 0 failed, 0 no-coverage)
RunChaikinBatch.ps1 -Schema P300 (Tony, standalone at Hub root) hit the same
headless-bridge failure for CW, GRPN, LAUR, LMT. Pulled all 4 via
docs/processes/chaikin_mcp_pull.md, this session's own claude-in-chrome MCP
tools.

**Updated (4):** CW Neutral, GRPN Bearish, LAUR Bearish, LMT Neutral. All 4
vault notes confirmed with real ## Chaikin Power Gauge sections via tail-read
immediately after each write. No page-load races, no ETF/skip-list symbols.

**Failed (0). No-coverage (0).**

## 2026-09-16 (2nd) -- P_300_RunAllDailyEvals.ps1 edited: pause added at Chaikin verification gate
Per Tony's direct instruction, following the same-day Chaikin MCP-pull entry
below: claude -p --chrome inside RunChaikinBatch.ps1 has now failed 7/7 runs
since 2026-09-04 (chaikin_failures.log). Edited
P_300_RunAllDailyEvals.ps1's Chaikin section -- when the post-run vault-file
check finds any symbol NOT written ($notWritten non-empty), the script now
prints a red PAUSED banner naming the symbols + the runbook path
(docs\processes\chaikin_mcp_pull.md) and blocks on Read-Host, instead of
logging a yellow warning and finishing silently. Did not touch the
Hub-root RunChaikinBatch.ps1 (shared across other projects/schemas --
out of scope for a P_300-only ask) or remove the `& $HUB_RUN_CHAIKIN`
call itself (still needed for the scan step that produces
_last_prompt.txt / the candidate list the MCP-pull runbook's step 1
reads). Single-file edit via filesystem:edit_file, ~15 lines added.
Note: this entry itself was lost to a windows-mcp relay timeout when
first logged 2026-09-16 (M-030-adjacent -- two consecutive different-type
tool calls timed out mid-session) -- backfilled 2026-09-17 once confirmed
missing from live disk. **Confirmed live** 2026-09-17: RunAllDailyEvals.ps1
was not run this session so the pause branch itself is still unexercised
end-to-end; next live daily-eval run with a real notWritten case is the
actual verification.

## 2026-09-16 -- F2 State Change: Chaikin MCP Pull (6 symbols, 0 failed, 0 no-coverage)
RunChaikinBatch.ps1 -Schema P300 hit the headless-bridge failure again (exited 1,
0/6 notes updated) for BB, CUBE, EXTR, GL, LTRX, LYB -- same claude -p --chrome
bridge failure logged in chaikin_failures.log on 09-04/09/10/11/14/15 (no browser
tool wired into that CLI session; WebFetch 403s on the JS-rendered page). Pulled
all 6 via docs/processes/chaikin_mcp_pull.md, this session's own claude-in-chrome
MCP tools.

**Updated (6):** BB Neutral+, CUBE Very Bearish, EXTR Neutral+, GL Neutral+, LTRX
Neutral+, LYB Neutral-. All 6 vault notes confirmed with real ## Chaikin Power
Gauge sections via tail-read immediately after each write. No page-load races,
no ETF/skip-list symbols in this batch.

**Failed (0). No-coverage (0).**

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

- **topk_cache/forward_labels join index (NEW, 2026-09-21)** -- `forward_labels` has no index covering `(pattern_instance_id, horizon_days)`. `tools/alphalens_ic_quantile.py`'s pooled join over ~936K topk_cache rows took ~4.5 min unindexed (Start-Process/detached, confirmed via M-057 pattern -- relay call itself timed out, process kept running server-side, real output landed after). An index would likely drop this to seconds. Not built this session -- schema-touching, not asked for at build time. Tony's call (2026-09-21): flagged, queue for whenever the next schema-touching work happens, or build standalone.
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




---

## 2026-09-10 -- F2 State Change: Chaikin MCP Pull (6 symbols, 6 updated, 0 no-coverage)
RunChaikinBatch.ps1 -Schema P300 hit the headless-bridge failure again
(exited 1, 0/6 notes updated) for AKAM, CDLX, GFS, GLW, KLAC, MSGS.
Session had expired to a login page on first navigate (AKAM) -- paused
per runbook step 2, Tony logged in manually, resumed. Pulled all 6 via
docs/processes/chaikin_mcp_pull.md, this session's own claude-in-chrome
MCP tools.

**Updated (6):** AKAM Very Bearish, CDLX Bearish, GFS Neutral+, GLW
Neutral, KLAC Neutral+, MSGS Bearish. All 6 vault notes
(2026-09-09_<SYMBOL>.md) confirmed with real ## Chaikin Power Gauge
sections, mtimes 17:42:17-17:43:16, sequential, ratings cross-checked
against the raw page text before writing. All 6 hit the known
page-load race on first read (empty get_page_text) -- resolved on
retry per runbook step 3 every time.

**No-coverage:** none.

**Chart Is King divergence flagged (disclosure, not override):** of
this batch's 3 BUY signals (CDLX, GFS, KLAC), CDLX (BUY, z=+1.208 h5)
landed Bearish on Chaikin -- financial metrics weak (high price-sales,
low cash flow) but very strong earnings, same pattern-vs-fundamentals
shape as prior divergences. GFS and KLAC (also BUY) landed Neutral+ --
no conflict. AKAM/GLW/MSGS (WATCH) not evaluated for divergence under
the established BUY-vs-Bearish definition. CDLX not yet checked
against P_400 -- open pending review, same status as the still-open
AEVA/CSIQ divergences from the 09-09 batch.


---

## 2026-09-10 (2nd) -- F2 State Change: archive roll (4th pass) DONE
WO-P000-E8.001 archive pass. todo.md was 927 lines/98.6KB (over the
500-line cap flagged at INIT). Archived the 2026-08-26 through
2026-09-09 dated log block (332 lines, oldest-first section only --
the pinned 09-03/09-04 entries at the top and the static
Current State / Stage / Backlog / Active / Maintenance sections were
left untouched, not part of this retention rule) to tasks/todo_archive.md
as a new "Fourth archive pass" section, inserted near the top per that
file's own newest-first convention (ahead of the existing
"Third archive pass -- 2026-08-29" section, now at line 353).

Integrity verified before/after: line-count split (564 + 332 + 31 = 927
original) confirmed exact; todo.md's first 5 and last 5 lines read back
unchanged; archive.md's original tail (2026-06-11 section) read back
unchanged; archived-block landed at archive.md line 15, byte counts
sane on both files (todo.md 595 lines/79.6KB, archive.md 1684
lines/247.3KB). No Python used -- windows-mcp:PowerShell array slicing
+ Set-Content only, per PEH's existing-file full-rewrite path (v1.8).

**Note:** archive.md already had two sections both labeled
"Third archive pass" (2026-08-29 and 2026-07-26) before this edit --
pre-existing numbering drift, not touched or renumbered here, flagging
it since this pass is labeled "Fourth" assuming the 08-29 one was
genuinely third.

Still over the 500-line cap (595) -- expected, matches the same
post-3rd-pass reading (595 lines, per WO-P300-E5.009's 08-29 demo).
Reminder will keep firing at INIT; non-blocking, same as before.


---

## 2026-09-10 (3rd) -- F2 State Change: archive roll (5th pass) DONE -- pre-08/01 cleanup
Tony asked to archive all entries prior to 08/01. Found the request
exposed a real miss from the 4th pass: a second, older log format
(`**>>> DATE ...**`, not `## DATE`) was sitting under a now-removed
"## Current State" header -- entries 2026-06-09 through 2026-07-08,
all pre-08/01, invisible to the `^## ` header search used for the 4th
pass. Archived to tasks/todo_archive.md as a new "Fifth archive pass"
section (130 lines, verified line-count split before/after: 250 keep +
130 archived + 241 keep = 621, +6 dropped vestigial lines [the orphaned
"## Current State" header and its surrounding blank/--- separators] =
627 original). Post-write header sweep confirms both remaining
`## `/`>>> ` blocks (08-21 through 08-29, and the two post-"End of"
entries at 08-23/08-25) are untouched and in original order.

**Real write failure hit and resolved mid-task:** first two write
attempts (PowerShell `Set-Content`, then a raw `[System.IO.File]::
WriteAllText`) both returned cleanly but silently did not land --
Durable signal check (line-count read-back) caught it both times, not
a clean-return assumption. Root cause found on the third attempt via
an explicit try/catch around a `StreamWriter` open: file was locked
("being used by another process") -- Tony had the doc open. Not a
relay stall (ping was fast throughout) -- a genuinely new failure
shape for this project, worth a peh-handoff addition if it recurs.
Closed by Tony, write succeeded immediately on retry, verified
(492 lines, 40.8KB, boundary content exact).

**todo.md now 492 lines/40.8KB -- back under the 500-line cap for the
first time since before the 3rd pass.**


---

## 2026-09-10 (4th) -- F2 State Change: WO-P300-E5.001 Batch 1 built -- PatternMetadata/MineCandidateRow relocated, schemas.py + schemas_pipeline_b.py split, PEH verification staged
Real import-linter audit (before writing any linter config) found 5
domain files importing infrastructure directly (PatternMetadata,
MineCandidateRow) -- a genuine, pre-existing CLAUDE.md rule violation,
confirmed deliberate via the classes' own docstrings, not accidental.
Tony flagged mid-plan that the fix (adding to schemas_pipeline_b.py/
schemas.py) would push both files further over the 300-line cap --
both were already over (433 and 422 lines) with no prior split plan
for schemas.py; schemas_pipeline_b.py had one already, in its own v1.2
DEBT NOTE, backlogged since 2026-05-20 and never executed until now.

**Built (WO-P000-E3.001 layer rules unchanged, this batch just moves
where types are defined):**
- NEW schemas_pipeline_b_bar.py (242 ln), schemas_pipeline_b_report.py
  (197 ln) -- executes schemas_pipeline_b.py's own debt-note split.
  PatternMetadata added to the bar file (same in-memory-only category
  as NormalizedBar/MatchResult).
- schemas_pipeline_b.py trimmed 433 -> 64 lines, kept as a re-export
  shim -- all 20 existing `from schemas_pipeline_b import X` call
  sites untouched.
- NEW schemas_vp_raw.py (115 ln), schemas_catalog_records.py (166 ln)
  -- new split for schemas.py, following the grouping its own
  docstring already named (INPUT / CATALOG ROW) but never executed.
  schemas_catalog_records.py imports DataOriginType back from
  schemas.py (partial circular import, resolved by import order --
  documented in both files' docstrings, do not reorder).
- schemas.py trimmed 422 -> 260 lines, kept as a re-export shim -- all
  11 existing `from schemas import X` call sites untouched.
- NEW schemas_mine.py (48 ln) for MineCandidateRow -- tried
  schemas_bulk.py first (closest topical fit), but the addition pushed
  it 281 -> 315 lines, over cap; reverted cleanly, built a dedicated
  file instead rather than trade one violation for another.
- infrastructure/catalog_reader.py (370 -> 356 ln) and
  infrastructure/mine_report_writer.py (164 -> 148 ln): class
  definitions removed, both now import from the new schema modules.
- 5 domain files (eval_incremental, eval_scoring, reconstruct_from_topk,
  topk_cache, mine_audit) + 2 more real callers the first sweep missed
  (infrastructure/eval_io.py, application/incremental_post_batch.py)
  + 6 test files under python/tests/ (also missed on the first sweep,
  caught by a second, wider one): import paths updated.

**Two self-caught mistakes, both fixed before calling this done:**
1. A PowerShell helper function's two-part edit (update one import,
   remove another) partially landed on topk_cache.py and mine_audit.py
   -- the update landed, the removal silently no-opped (a `` `r`n ``
   suffix on the match string that didn't line up), leaving the old
   infrastructure import present alongside the new one. Caught by a
   read-back verification sweep after the fact, not assumed clean from
   the "OK" the helper printed. Fixed directly, re-verified.
2. First cross-reference sweep only checked domain/infrastructure/
   application for the old import paths -- missed infrastructure/
   eval_io.py, application/incremental_post_batch.py, and all 6 files
   under python/tests/. Caught by a second, wider sweep across the
   entire project tree before considering this done, not after Tony
   found it.

**Verification staged, not yet run:** PEH script
`verify\run_this_P300_20260910_195500.py` + `_context.txt` -- compiles
every touched file under warnings-as-errors, imports every new/edited
module, confirms both re-export shims expose every original name, and
confirms PatternMetadata/MineCandidateRow each resolve to a single,
identical object across every import path (old and new). Could not run
it directly -- `python.exe` invocations via windows-mcp:PowerShell hit
the documented ~4-min subprocess ceiling on this file count; ping
confirmed the relay itself was fine, so per peh-handoff v1.10 this was
handed off rather than retried.

**Not yet done:** Tony runs the staged script and pastes output back.
Batch 2 (utilities/ -> utilities/ + tools/ split) not started --
separate go-ahead, per the original file plan.


---

## 2026-09-10 (5th) -- F2 State Change: WO-P300-E5.001 Batch 1 -- PASS, one production fix by Tony
run_this_P300_20260910_195500.py: PASS, all 5 phases clean (compile,
import, both shim-completeness checks, both identity checks).

Tony found and fixed a real bug in the handoff before reaching PASS:
schemas.py's bottom re-export section imported catalog-row names
eagerly (`from schemas_catalog_records import (...)`), which circular-
imports back when schemas_catalog_records is the FIRST of the two
touched (schemas_catalog_records's own top does `from schemas import
DataOriginType` -- reenters partially-initialized schemas_catalog_
records before any of its classes are defined). My design assumed
import order would always favor schemas.py first and documented that
as the mitigation instead of removing the dependency -- never verified
myself since the PEH handoff was needed precisely because I couldn't
run python directly. Fixed via PEP 562 module-level `__getattr__` on
schemas.py: catalog-row names resolve lazily on first access instead
of at import time, so the fix doesn't depend on which module gets
imported first, unlike the original ordering-based design. Verified by
reading the file back post-fix -- import importlib added at top,
_CATALOG_RECORD_NAMES frozenset correct, 281 lines. No test assertions
changed (Tony's own note, confirmed by the diff).

**WO-P300-E5.001 Batch 1 complete.** Batch 2 (utilities/ -> utilities/
+ tools/ split, 12 files) not started -- separate go-ahead per the
original file plan.


---

## 2026-09-10 (6th) -- F2 State Change: WO-P300-E5.001 Batch 2 built -- utilities/ split into utilities/ + tools/
9 diagnostic scripts moved (Move-Item, byte-identical, not retyped) out
of utilities/ into new tools/ package: catalog_summary, check_pattern,
ledger_calibration, preflight_status, vp_export_integrity_check,
loo_replay, feature_ablation, threshold_sweep, cap_sensitivity_audit.
utilities/ now holds only true leaves (db_connect, db_utils, 4x
archive_*_file, intelliscan_reader, inspect_pattern) -- confirmed by
exhaustive project-wide grep, zero remaining `utilities.<moved name>`
references anywhere (.py/.bat/.ps1).

Fixed: feature_ablation.py + threshold_sweep.py's internal loo_replay
self-imports (all three now in tools/), cli_commands/utility.py's 4 of
5 utilities imports (inspect_pattern stays, untouched),
P_300_Preflight.bat's preflight_status.py script path, and
tests/smoke_loo_replay.py's import + docstring reference -- caught by
the same exhaustive whole-project sweep pattern that caught Batch 1's
missed callers, run proactively this time before calling it done
rather than after.

**Verification staged:** verify\run_this_P300_20260910_203000.py +
_context.txt. Same PEH handoff reason as Batch 1 (python.exe via
windows-mcp:PowerShell hits the ~4-min ceiling on this file count).

**WO-P300-E5.001 Batches 1+2 both built.** Once Batch 2 verifies PASS,
both cleanup batches are done -- next real step per the WO's own
NEXT STEPS is step 2: write the actual import-linter config and run
the first real audit, now that the two known violation classes
(domain->infrastructure, utilities/'s bidirectional coupling) are
fixed rather than worked around.


---

## 2026-09-10 (7th) -- F2 State Change: WO-P300-E5.001 Batch 2 -- PASS, clean
run_this_P300_20260910_203000.py: PASS, all 4 phases clean, no fix
needed this time (unlike Batch 1's __getattr__ catch).

**Batches 1+2 both complete and verified.** utilities/ split into
utilities/ (true leaves) + tools/ (9 diagnostic scripts); domain->
infrastructure violations (PatternMetadata/MineCandidateRow) fixed;
schemas.py + schemas_pipeline_b.py both back under the 300-line cap.
Next per the WO's own NEXT STEPS: step 2, write the actual import-
linter config (domain/infrastructure/utilities/application/tools/
cli_commands layer order + the one documented exception, promote_
gate.py) and run the first real audit against the now-cleaned tree.


---

## 2026-09-10 (8th) -- F2 State Change: WO-P300-E5.001 step 2 -- import-linter config written, first real audit staged
python\.importlinter written. Layer order bottom-to-top: domain ->
utilities -> infrastructure -> (application | tools, independent
siblings) -> cli_commands. schemas*.py/config.py deliberately excluded
from root_packages (single-file modules, no __init__.py, every layer
allowed to import them freely by design). cli.py excluded too (nothing
imports it). promote_gate.py's cli_commands->domain/infrastructure
direct-import case is NOT a violation under a standard Layers contract
(higher layer can import any lower layer, not just the adjacent one)
-- no special exception needed after all, contrary to what the design
conversation assumed.

import-linter was not installed in p140 -- confirmed absent from
site-packages and requirements.txt. `pip install` via windows-mcp:
PowerShell hit the same subprocess-timeout class as direct python.exe
calls, so the install got folded into the PEH handoff script itself
rather than attempted separately.

**Staged, not yet run:** verify\run_this_P300_20260910_211500.py +
_context.txt -- installs import-linter, then runs the real
`lint-imports` for the first time ever against this codebase and
prints raw output, unfiltered. Context file is explicit that a
non-zero exit here isn't necessarily a script failure -- could be a
genuine violation Batches 1+2 missed (the useful case, the actual
point of this step), or a config mistake in .importlinter itself
(written from documentation, never test-run, since python.exe can't
be invoked directly this session).


---

## 2026-09-10 (9th) -- F2 State Change: WO-P300-E5.001 step 2 -- first audit attempt failed on invocation, not the contract; corrected and re-staged
run_this_P300_20260910_211500.py died at the version-check step --
`python -m importlinter` isn't valid (no __main__.py). pip install
itself succeeded; import-linter ships as standalone console-script
exes (import-linter.exe, lint-imports.exe) in p140\Scripts\, not a
-m-invokable module. Confirmed both exes present. The real lint-imports
run against .importlinter never started -- config itself still
unverified.

Corrected and re-staged: verify\run_this_P300_20260910_213000.py +
_context.txt -- calls lint-imports.exe directly by full path instead
of python -m importlinter.


---

## 2026-09-10 (10th) -- F2 State Change: WO-P300-E5.001 -- first real import-linter audit PASSES, contract holds
run_this_P300_20260910_213000.py: PASS. 91 files analyzed, 159
dependencies, "P_300 layered architecture" contract kept, 0 broken.
One harmless skip (not a violation): application/daily_evaluate_
pipeline_backup_2026-07-25_WO-P800-E3.003.py -- a stale backup file,
dots in the filename confuse import-linter's module-name parsing.
Minor housekeeping candidate, not acted on this session (not in scope).

Confirms Batches 1+2 actually fixed what they meant to -- the
domain->infrastructure violations and the utilities/ bidirectional
coupling were the only real breaks, and nothing else crept in across
today's work. Also caught (real, minor, in the verify script itself
not production code): a SyntaxWarning on an unescaped `\ ` in
run_this_P300_20260910_213000.py's own docstring -- harmless, script
completed anyway, not fixed (throwaway PEH file, not a WO deliverable).

**WO-P300-E5.001 status: all four of its own NEXT STEPS done** --
(1) prose contract + sign-off, (2) config + first real audit [PASS],
(3) triage findings [nothing to triage, clean pass], (4) file-level
plans presented before each batch's build. Ready for the fresh-session
independent review CLOSED requires -- not this session, it wrote the
code.


---

## 2026-09-10 (11th) -- F2 State Change: Hub-level rollout WO filed, referencing WO-P300-E5.001
Tony's read after WO-P300-E5.001's clean first audit: this pattern is
worth taking to Hub governance, not staying P_300-only. Filed
WO-P000-E30.001 (Agentic-Hub-Governance\work_orders\) -- PENDING,
assessment only, no project chosen yet. Directly cites WO-P300-
E5.001's own SCOPE NOTE, which explicitly deferred Hub-wide rollout as
"a separate, bigger conversation, not part of this WO" -- this is that
conversation. Candidate projects (P_010/020/110/115/120/200/400/800/
805/810/820) listed as unassessed, not pre-selected -- next step per
that WO is confirming which ones actually have a real layer split
worth enforcing before writing any contract for them.


---

## 2026-09-10 (12th) -- Session Review

**Session scope:** INIT, Chaikin MCP pull (6 symbols + 1 new divergence
flagged, CDLX), two todo.md archive passes (927 -> under 500 lines,
twice), WO-P300-E5.001 designed prose-first then fully built and
verified: Batch 1 (PatternMetadata/MineCandidateRow out of
infrastructure/, schemas.py + schemas_pipeline_b.py split under cap),
Batch 2 (utilities/ -> utilities/ + tools/), the actual `.importlinter`
config, and the first-ever real `lint-imports` audit -- PASS, 91
files, 159 dependencies, 0 breaks. Closed with WO-P000-E30.001 filed
(Hub-level rollout assessment, PENDING, no project chosen).

**Self-caught, not Tony-caught (in order):** two archive-pass entries
missed on the first structural read of todo.md (a second `>>> `-format
log section under a since-removed header); 8 real callers missed on
Batch 1's first cross-reference sweep, caught by a second wider one;
1 more missed the same way on Batch 2. One real write failure (file
lock, Word had todo.md open) and one compound-edit partial-landing bug
(PowerShell `.Replace()` helper) both caught by read-back verification
before being reported done, not after.

**Tony-caught:** the schemas.py <-> schemas_catalog_records.py
circular import (fixed via PEP 562 `__getattr__`, more robust than the
import-ordering design it replaced) and the `python -m importlinter`
invocation mistake (no `__main__.py`; fixed to call `lint-imports.exe`
directly) -- both on the first real PEH round-trip for each, one clean
fix apiece, no repeat failures.

**Lessons captured:** M-121 through M-124 added to tasks/lessons.md
(file-lock write failures, compound-edit partial-landing, console-
script `.exe` vs `-m` invocation, project-wide sweep scope for
relocations).

**Open at close:** WO-P300-E5.001 needs its fresh-session independent
review before CLOSED (this session built it, cannot review it). The
stale backup file `application/daily_evaluate_pipeline_backup_2026-
07-25_WO-P800-E3.003.py` (import-linter skip warning) is an unclaimed
minor cleanup candidate, not filed as its own WO. WO-P000-E30.001 has
no project chosen yet -- next real step lives there, not here.

todo.md ends this session at ~800 lines -- back over the 500-line cap
already; the two archive passes done today only bought partial
headroom against a single long session's own logging volume. Next
session's INIT will flag it again; expected, non-blocking, same as
every prior pass.

## 2026-09-11 -- Chaikin manual MCP pull (RunChaikinBatch.ps1 headless bridge failed, exit 1)
- RunChaikinBatch.ps1 -Schema P300 exited 1, 0/6 reported not updated: AMBA, EWBC, HST, LOGI, PENN, RDDT.
- Root cause confirmed NOT auth/session expiry -- live claude-in-chrome session loaded AMBA cleanly, Power Gauge data present, no login redirect. Consistent with the known headless `claude -p --chrome` bridge failure (chaikin_mcp_pull.md).
- Ran manual MCP pull per chaikin_mcp_pull.md v1.1 against `_last_prompt.txt` (modified 2026-09-11 10:52, confirmed same-day).
- Result: Updated 6/6, No-coverage 0, Failed 0. Ratings -- AMBA: Neutral, EWBC: Neutral, HST: Neutral+, LOGI: Neutral+, PENN: Bearish, RDDT: Neutral.
- One page-load race hit on EWBC and PENN (get_page_text empty on first read) -- resolved on retry per existing runbook step 3, no new issue.
- All 6 notes verified via Select-String "## Chaikin Power Gauge" post-write.


---

## 2026-09-14 -- F2 State Change: Chaikin manual MCP pull (17 symbols, 0 failed, 0 no-coverage)
RunChaikinBatch.ps1 -Schema P300 exited 1 again, 0/17 notes updated (headless
`claude -p --chrome` bridge failure, same known root cause). Verified against
real vault notes before treating the exit code as the whole story -- all 17
confirmed still missing a Chaikin section pre-pull (spot-checked AEVA).

Pulled all 17 via docs/processes/chaikin_mcp_pull.md, this session's own
claude-in-chrome MCP tools: AEVA, AVAV, CSCO, DKNG, DY, FOUR, GHC, IMDX,
INMD, IRM, LSCC, MCHP, OLED, POWL, RMBS, TREX, VISN.

**Updated (17/17):** AEVA Very Bearish, AVAV Neutral, CSCO Neutral+, DKNG
Bearish, DY Neutral+, FOUR Neutral, GHC Neutral, IMDX Neutral, INMD Neutral,
IRM Neutral+, LSCC Neutral, MCHP Neutral, OLED Bullish, POWL Neutral+, RMBS
Neutral+, TREX Neutral, VISN Neutral+. All 17 vault notes confirmed with
real ## Chaikin Power Gauge sections (file sizes grew ~1.1-1.5KB each,
consistent with a real append; VISN spot-checked in full, frontmatter and
existing sections untouched).

**Failed:** none. **No-coverage:** none.

5 of 17 hit the known page-load race on first `get_page_text` (blank/N/A):
AVAV, CSCO, DKNG, DY, FOUR -- all resolved clean on retry per runbook step 3,
no new issue, no skip-list additions needed.

**Chart Is King divergence flagged (disclosure, not override):** of this
batch's 12 BUY signals, 2 landed Bearish/Very Bearish on Chaikin -- AEVA
(BUY, Very Bearish: high LT debt-equity, high price-to-book) and DKNG (BUY,
Bearish: high LT debt-equity, high price-to-book). Same shape as the prior
CIFR/HUT/RIVN divergences (richly-valued/high-debt names where pattern read
is bullish and fundamentals read is bearish). Remaining 10 BUYs (AVAV, CSCO,
DY, FOUR, IMDX, LSCC, MCHP, POWL, RMBS, TREX) landed Neutral/Neutral+ --
no conflict. 4 WATCH signals (GHC, INMD, IRM, OLED) not part of the
divergence pattern (pattern is BUY vs Bearish/Very Bearish specifically);
OLED's Bullish Chaikin agrees directionally with its WATCH lean, no conflict.

- 2026-09-15: Chaikin batch (RunChaikinBatch.ps1 -Schema P300) failed again, 0/10 (chronic claude -p --chrome bridge issue). Pulled via chaikin_mcp_pull.md fallback instead -- claude-in-chrome MCP, session-driven. 10/10 updated, all verified (## Chaikin Power Gauge present, LastWriteTime confirmed): CAE, CARG, COLM, FLNT, HCSG, LBTYK, RBA, RGTI, SFIX, TTWO. Notes under trading_journal\TradeOrderManagement\P300\.
