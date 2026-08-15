# P_800 Task Queue

**File created:** 2026-07-24. P_800 had no `tasks/` folder before this --
this is the first entry, and it effectively starts the WO-P000-E8.001
working-state-doc rollout for P_800 (that WO's hub-wide rollout to
P_115/P_400/P_020/P_805/P_010/P_800 is still PENDING; P_300 was the
pilot). Format follows the P_300 pattern: newest dated session entry at
the top, reference sections below.

---

**>>> 2026-08-12 WO-P800-E4.004 remaining 4 Bases files fixed + p800-project-context skill created:**

Prior session (P_400, same day) found and fixed 2 of 6: `P400_Trades.base`,
`P020_Performance.base` -- top-level `filter:`/`conditions:`/`conjunction:`
keys are fabricated, not real Obsidian Bases schema; the plugin silently
ignored them and every base rendered the entire vault unfiltered. This
session fixed the remaining 4: `P300_Signals.base`, `P115_Evaluations.base`,
`Open_Positions.base`, `KB_Articles.base`. Converted to real syntax
(`filters:` plural, `and`/`or` expression lists, `properties:` for display
names, `views[].order`/`sort`). Each archived before edit
(`{name}.bak_2026-08-12`).

`P300_Signals.base` and `P115_Evaluations.base` had a compound defect --
fabricated schema AND still pointed at the pre-rename `TradeManagement/P300`
and `TradeManagement/P115` paths (never got WO-P800-E3.003's pass). Both
confirmed dead on disk; new `file.inFolder("TradeOrderManagement/<x>")`
target confirmed live: P300 582 files, P115 1,484 files. `P300_Signals.base`
kept its already-valid view-level WATCH-signal filter untouched, only added
top-level folder scoping (global+view filters AND together per spec).

`KB_Articles.base` -- straightforward folder-path fix, `KnowledgeBase`
confirmed live at 99 files.

`Open_Positions.base` -- different shape, no folder path. Filters on
`lifecycle_status`/`traded`/`outcome` properties with an OR/AND nest;
converted `outcome isEmpty` to `outcome.isEmpty()` method-call syntax. This
one is the least-verified of the six -- the `.isEmpty()` pattern hasn't been
confirmed live anywhere else in this WO. Flagged in the WO for Tony to
spot-check first.

**Also created `p800-project-context` SKILL** --
`.claude\skills\p800-project-context\SKILL.md`, 197 lines, UTF8-no-BOM/LF.
First always-loaded context layer for P_800; gap flagged by Tony at session
start as part of why the fabricated-schema bug sat undetected since
creation. Documents the TradeManagement-vs-TradeOrderManagement path
confusion, the real vs. fabricated Bases syntax (as Anti-Pattern #1/#2), the
EC-004 Pydantic `extra="forbid"` lesson, and P_800's ownership boundary.
Written to disk only -- Tony still needs to add it live via Customize ->
Skills (Protocol E).

**Process miss, self-caught:** `WO-P800-E4.004.md` was overwritten directly
without archiving first, breaking Archive-before-modify. Backfilled
`WO-P800-E4.004_backup_2026-08-12.md` from the pre-edit version still held in
session context (not from disk, since the original was already gone) --
noted here since it's a process gap, not a clean archive-then-edit.

**Not done this session:**
- Live row-count verification in Obsidian for all 4 newly-fixed bases (Tony)
- P_300 Ack on `P300_Signals.base`, P_115 Ack on `P115_Evaluations.base`
- `.isEmpty()` syntax spot-check on `Open_Positions.base` specifically
- Independent Review (separate session, per WO_COMPLETION_GATE)
- Skill added live in the app (disk write only, per Protocol E)
- Sweep of P_300/P_115 skill files for the same fabricated-schema description
  (WO's own Next Session Prep #4, not yet done)

---

**>>> 2026-07-25 WO-P800-E3.003 P_800-side complete (vault rename TradeManagement -> TradeOrderManagement):**

Tony approved P_800's piece only. Archived `obsidian_writers\config.py` ->
`config_backup_2026-07-25_WO-P800-E3.003.py`, then updated all 5
VAULT_FOLDER_MAP entries (P115/P300/P400/P400_PAPER/P020) from
`TradeManagement/...` to `TradeOrderManagement/...`. Merged vault folders via
`robocopy /E /MOVE` (P115 1483+2, P300 404, P400 191+1 merged cleanly into
existing `_pre_cutover_archive` with zero collisions, P020 202, `_archive\P020_pre_tradeid_fix` 190).
Post-move count reconciled exactly: 2473 files moved, 0 lost, old
`TradeManagement\` left as empty shell. Bases (.base) files grepped clean
beforehand -- no hardcoded path, no changes needed.

**Not done this session (deferred, outside P_800 boundary):** P_400's
`python\config.py` (BOOK_DIR/PAPER_BOOK_DIR still point at old path) and
`python\tests\test_p400_known_bugs.py` (assertion needs to flip); P_300's
`daily_evaluate_pipeline.py` line 437 (signal_source_link still hardcodes
old path). WO-P800-E3.003 updated with a "Still Open" list (items 1-3) and
Acks: P_400 pending, P_300 pending, P_115/P_020 N/A. **Until P_400's config.py
is fixed, P_400 is reading/writing against a dead folder** -- this should be
the first thing done in the next P_400 session. Same for P_300's next signal
write. Full detail in WO-P800-E3.003.md.

Also not done (flagged only, no approval sought): P_800's own test files
still reference old path (`smoke_test_pbf_2026_01_21.py`, `test_p115_write.py`,
`test_signal_v2_e2e.py`), chaikin_enrichment test fixtures, and Section 7.1 of
P_800_SYSTEM_DOCUMENTATION.md (folder tree stale, plus it wrongly still lists a
`TradeManagement\signals\` legacy folder that doesn't actually exist on disk).

---

**>>> 2026-07-24 (Opus) WO-P800-E3.002 CLOSED (independent review) + WO-P400-E3.011 P_800 Ack + stale-doc corrections:**

**WO-P800-E3.002 OWNER_DONE -> CLOSED.** Independent review session -- this
chat did not write any of the E3.002 code (built 2026-07-21), which is what
satisfies WO_COMPLETION_GATE.md's Independent Review Requirement. Every
Acceptance Criterion re-verified against live disk, not against the WO's own
claims: `vault_schemas.py` `P020Record.trade_id` present; `filename_builder.py`
`_get_identifier()` P020 branch appends `trade_id` with symbol-only fallback;
`test_filename_builder.py` 5 tests present; P_020's `vault_mapper.py` trade_id
passthrough + `_to_str()` helper present; `test_p020_vault_export.py` 8 tests;
`TradeManagement/P020` 202 files (201 notes + `.keep`), every filename on the
`SYMBOL_TRADEID` pattern, zero stragglers; `_archive/P020_pre_tradeid_fix/`
exactly 190 files including the POWL/VSAT/GOOG collision names; and
`P020_Performance.base` filter confirmed excluding the archive folder. No gaps
between claim and disk.

**WO-P400-E3.011 (Owner P_400, Affects P_800) -- P_800 Ack confirmed against
live code.** `"APPROVED_WITH_SEVERE_WARNING": "BUY"` verified present in
`obsidian_writers\config.py`, positioned after `APPROVED_WITH_CAUTION`, dict
block syntactically intact, CHANGELOG v2.5 present. Stale `PENDING` status
header corrected. One item genuinely still open and not closable from here:
live re-verification on the next `APPROVED_WITH_SEVERE_WARNING` record
(expect `write_route=BUY`, no VERDICT_MAP warning in the log).

**config.py line-ending cleanup done.** The 7 CRLF lines flagged during the
Ack (v2.5 changelog block + the adjacent `APPROVED_WITH_CAUTION` line)
normalized to LF -- file now 0 CRLF, 137 lines, no BOM, VERDICT_MAP verified
byte-intact after the write. Stale "Pending P_800 Ack" in the v2.5 changelog
updated to reflect the 2026-07-24 Ack. Same root pattern as WO-P400-E2.019's
2026-07-21 normalization: whatever tool makes these edits still writes CRLF.
Not fixed at the source -- recurrence expected.

**Stale roadmap corrected (caught at INIT, not reported by anything).**
`P_800_Interface_Arch_Part2` still showed 5E/5F/5H as unstarted session
placeholders while all three have been live in production. Corrected against
real vault state rather than from memory: 5E live since 2026-05-18 (earliest
P300 vault note; 403 notes), 5H live since 2026-06-08 (earliest P400 vault
note; 190 notes + `paper/` routing per WO-P400-E2.019), 5F done 2026-07-21
(201 notes). **Worth noting for future sessions:** the date carried in session
context said "late May 2026" for both 5E and 5H -- disk says 5H is early June.
Disk won, per the standing rule. 5G (KB Templater + Web Clipper) is now the
only Phase 5 item genuinely still open.

`P_800_SYSTEM_DOCUMENTATION.md`: Section 0 phase-progress line corrected to
match; Section 7.2's `obsidian_writers` listing gained `test_filename_builder.py`
and `domain\signal_schemas.py`, both present on disk but undocumented.
536 -> 538 lines, Last Updated 2026-07-24.

**Not done, deliberately:**
- System doc left at **v4.1** despite content changes. A version bump plus a
  Section 0 entry is a doc-governance call for Tony, not taken unilaterally.
- `config.py` **not syntax-checked by real execution.** Inline python through
  the MCP bridge wedges it (M-030 / peh-handoff). The edit touched only line
  endings and docstring text with VERDICT_MAP verified intact, so risk is low,
  but a PEH `run_this.py` covering `import obsidian_writers.config` plus the
  three test files was offered and not staged.

---

## Current State

**Files edited this session (2026-08-12)** (all archived before modify
except the WO backfill noted above; all written UTF8-no-BOM / LF-only, all
mtime/BOM/CRLF-verified after write):

| File | Change | Archive |
|---|---|---|
| `.claude\skills\p800-project-context\SKILL.md` | New file, 197 lines | n/a (new file) |
| `trading_journal\Bases\P300_Signals.base` | Fabricated schema -> real, folder path fixed | `P300_Signals.base.bak_2026-08-12` |
| `trading_journal\Bases\P115_Evaluations.base` | Fabricated schema -> real, folder path fixed | `P115_Evaluations.base.bak_2026-08-12` |
| `trading_journal\Bases\Open_Positions.base` | Fabricated schema -> real (property filter) | `Open_Positions.base.bak_2026-08-12` |
| `trading_journal\Bases\KB_Articles.base` | Fabricated schema -> real | `KB_Articles.base.bak_2026-08-12` |
| `work_orders\WO-P800-E4.004.md` | Scope table updated, all 6 marked fixed | `WO-P800-E4.004_backup_2026-08-12.md` (backfilled, see process-miss note above) |

**Vault state, confirmed live this session:** P300 582 · P115 1,484 ·
KnowledgeBase 99 (via `TradeOrderManagement\<x>` / `KnowledgeBase\` file
counts). P400 and P020 counts not reverified this session -- last known
(2026-07-25): P400 190 (+1 paper), P020 202. Bases 6/6 files now real schema
(all six converted as of this session; row-count live-verify in the Obsidian
app itself still outstanding -- see Open Items).

**Account/posture:** not pulled this session.

---

## Open Items

1. **WO-P800-E4.004 live row-count verification -- DONE 2026-08-12.**
   Tony confirmed via screenshots: P400_Trades 405, P300_Signals 187,
   P115_Evaluations 1,485 (1 off the 1,484 disk count -- drift, not a bug),
   Open_Positions 6 (card view, `.isEmpty()` syntax confirmed working).
   KB_Articles not screenshotted -- same proven pattern, lower risk.
2. **WO-P800-E4.004 -- P_300 and P_115 Acks still needed** on their
   respective `.base` fixes, per WO_COMPLETION_GATE caller propagation.
3. **Open_Positions empty `stop_price`/`target_1`/`account_id` -- NOT a bug
   (Tony, 2026-08-12).** P_115 no longer provides those fields -- ownership
   moved to P_400. Filter/schema confirmed correct in the screenshot; the
   empty cells are P_115 records correctly showing no data for fields it
   doesn't own. `Open_Positions.base` mixes both sources (`source: P115` /
   `source: P400`) by design, so this is expected on any P115-sourced card.
   No WO needed.
4. **`p800-project-context` SKILL** -- written to disk, not yet added live
   in the app (Customize -> Skills). Won't auto-load until Tony does this.
5. **Sweep P_300/P_115 skill files** for the same fabricated-Bases-schema
   description (WO-P800-E4.004 Next Session Prep #4, carried over).
6. **WO-P400-E3.011 live re-verification** -- next `APPROVED_WITH_SEVERE_WARNING`
   record must show `write_route=BUY` and no VERDICT_MAP warning. Only real
   gate left on that WO.
7. **WO-P800-E3.003 (PENDING)** -- rename `TradeManagement` -> `TradeOrderManagement`
   hub-wide. Needs Tony's sign-off on approach before any file moves. Reverses
   the direction WO-P400-E2.012 concluded (deliberately, not a reopened defect).
8. **Phase 5G** -- KB Templater template + Web Clipper config. Only Phase 5
   item still open. Also Open Item #4 in Interface Arch Part 2.
9. **Six `*_backup_*.py` files sitting inside the canonical `obsidian_writers`
   package folder** from the 07-21 edits. Harmless unless imported, but they
   don't belong in a live package. Proposed: move to an `_archive\` subfolder.
   Flagged to Tony, not actioned.
10. **System doc version bump** -- v4.1 with 2026-07-24 content changes; also
    now stale re: Bases fix (Section 5/7.1 caveat added via p800-project-context
    SKILL, not yet corrected in the doc itself). Tony's call.
11. **PEH syntax check on `config.py`** -- offered, not staged.
12. **Source of the recurring CRLF edits** -- normalized twice now (E2.019, E3.011)
    without identifying the tool doing it. Third occurrence should trigger a real
    investigation rather than another cleanup.

---

## Working-State Doc Retention (WO-P000-E8.001)

Capped at ~500 lines / ~100KB for the dated-session-log portion above. When it
crosses that, oldest entries move to `tasks/todo_archive.md` (full text
preserved, nothing deleted). Sections below the log are reference material, not
session history -- not subject to the cap.

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (architect)
- **Update trigger:** Protocol F2 -- every session where code changed, a
  validation ran, or project state moved. Not skippable when state changed.
- **Loaded by:** P_800 SIP at session start.

---

**End of P_800 Task Queue**