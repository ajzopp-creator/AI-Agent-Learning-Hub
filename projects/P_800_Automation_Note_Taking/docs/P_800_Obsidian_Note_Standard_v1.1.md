# P_800 Obsidian Note Standard
**File:** `projects/P_800_Automation_Note_Taking/docs/P_800_Obsidian_Note_Standard.md`
**Version:** 1.1
**Date:** 2026-05-31
**Author:** Anthony Zoppi (review) / Claude (drafting)
**Status:** DRAFT — Pending implementation approval

---

## Purpose

This document defines the normalized note structure that every trading system
(P_115, P_300, and all future systems) must produce when writing to the
Obsidian vault via the P_800 Hub interface. It replaces ad-hoc per-system
conventions and eliminates the ambiguities and gaps identified on 2026-05-31.

All code changes required to implement this standard are specified in
Section 6. No code is to be written until the operator explicitly approves
implementation.

---

## 1. Current State and Identified Gaps

### 1.1 Systems Currently Writing to the Vault

| System | Folder | Schema | Notes active as of 2026-05-31 |
|--------|--------|--------|-------------------------------|
| P_300 | `TradeManagement/P300/` | `P300Record` | ~60 notes (2026-05-21 to present) |
| P_115 | `TradeManagement/P115/` | `P115Record` | 500+ notes (2024-12-18 to present) |

P_020, P_400, and KB schemas are defined in `schemas.py` but no live notes
exist yet.

### 1.2 Gap Inventory

**Gap 1 — Filename collision on re-run (critical)**
`filename_builder.py` constructs filenames as `YYYY-MM-DD_TICKER.md` using
the `date` field from the sending schema. The `date` field contains the
*signal date* (the VP grid export date for P_300; the evaluation date for
P_115). When the same signal is re-evaluated on a different calendar day,
the filename is unchanged and `vault_writer.py` silently overwrites the
prior note (`overwrite=True` is the hardcoded default). The re-run that
produced the overwrite leaves no trace in the vault.

*Observed instance:* ROST signal date 2026-05-29, re-run on 2026-05-31
→ `2026-05-29_ROST.md` overwritten silently. The Obsidian P300_Signals
base showed the note as 2026-05-29 with no indication of the 2026-05-31
re-run.

**Gap 2 — No run provenance in the note**
No field records when the pipeline actually ran. `generated_dt` exists on
`P300Record` but is `Optional[str]` with no enforced format, is populated
as `null` in every note examined on disk, and is not surfaced in the note
body. There is no equivalent field on `P115Record`. A note cannot answer
"when was this last written and by which pipeline run?"

**Gap 3 — No note version counter**
Notes are overwritten without tracking how many times that has occurred.
A note claiming to be current may be a first write or a tenth overwrite
with no way to distinguish.

**Gap 4 — No normalized verdict field across systems**
P_300 uses `signal: BUY | WATCH | PASS`. P_115 uses `step1_verdict:
BUY | ASYM | PASS`. No shared field name; no shared vocabulary. A Dataview
query for "all BUY signals this week across all systems" requires knowing
both field names and reconciling `ASYM` with `WATCH`. This will worsen as
P_400 and others come online.

**Gap 5 — `signal_date` vs `date` vs `anchor_date` ambiguity**
`P300Record` carries both `date` and `anchor_date`, both set to the VP
grid export date. It is not clear from the schema which is the signal date
and which is the pattern anchor. `P115Record` has only `date`. Neither
schema has a field explicitly named `signal_date` to make the intent
unambiguous.

**Gap 6 — `h5_win_rate` double-division bug in `write_signal_to_obsidian.py`
(resolved — fix pending)**
Root cause identified 2026-05-31. The P_300 report stores `win_rate` as a
decimal fraction (0.800 = 80%). `write_signal_to_obsidian.py` line 57
divides by 100 again, producing 0.008 in frontmatter. The note body shows
the correct 80.0% because display formatting uses `wr * 100` separately.
The same double-division bug affects `h5_mean_ret` (line 58):
`float(mr.rstrip('%')) / 100` — the report value has no `%` suffix so
`rstrip('%')` is a silent no-op, and dividing +4.81 by 100 produces 0.0481
in frontmatter instead of 4.81.

*Fix identified (not yet applied):*
- Line 57: `h_win_rate = wr` (remove `/ 100`)
- Line 58: `h_mean_ret = float(mr.lstrip('+'))` (strip leading `+`, no division)

Also on line 98: `overwrite=False` is hardcoded, causing re-runs to be
silently skipped when a note already exists. This will be corrected as part
of the full standard implementation (Decision 6 below).

**Gap 7 — No overwrite policy documented**
`vault_writer.write_note()` accepts `overwrite: bool = True`. There is no
documented policy for when overwrite should be True vs False, and no
calling code passes consistent values. The current default silently
destroys prior data with no record of what was lost.

**Gap 8 — Schema versions are static constants, never incremented**
`SCHEMA_VERSIONS` in `config.py` lists all schemas at `"1.0"`. This value
is written into every note's `schema_version` frontmatter field. Because
the value never changes, it provides no version signal when schema fields
are added or changed. There is no changelog tracking which version added
which fields.

**Gap 9 — No `written_by` attribution**
Notes carry `source: P300` or `source: P115`, which identifies the schema
family. No field records the specific pipeline module or batch run that
wrote the note. When multiple systems write to the same note (e.g., P_300
writes a signal, P_400 later appends a trade outcome), there is no audit
trail of who wrote what.

**Gap 10 — No verdict history; classification changes are undetectable**
A signal that classifies as WATCH on run 1, WATCH on run 2, and BUY on
run 3 leaves no record of the progression. The final note shows only
`verdict: BUY`. There is no way to query "signals that required multiple
runs to reach BUY" or "how many re-evaluations before conviction formed."
This is a signal quality indicator with direct trading relevance.

---

## 2. Design Decisions

### Decision 1 — Filename key is `signal_date`, not `run_date`
One canonical note per signal per symbol. The filename `YYYY-MM-DD_TICKER.md`
uses the date the signal applies to (the VP grid date for P_300, the eval
date for P_115). A re-run of the same signal on a later day overwrites the
same file. The frontmatter records the run date, increments the version
counter, and appends to the verdict history, providing full provenance
without vault proliferation.

*Rejected alternative:* `run_date` in filename → one new file per run →
vault fills with duplicates of the same signal with no clear canonical note.

### Decision 2 — Normalized `verdict` field added to all schemas
Every schema exposes a top-level `verdict` field using the shared
vocabulary: `BUY | WATCH | PASS`. Each system maps its own classification
to this field before calling `write_to_vault()`. P_115 maps `ASYM → WATCH`.
P_300 passes its `signal` value directly (vocabulary already matches).
Dataview queries target `verdict` exclusively for cross-system queries.

### Decision 3 — `signal_date` and `run_date` are explicit distinct fields
`signal_date` = the date the signal applies to. Used in filename
construction. `run_date` = the calendar date the pipeline wrote this note.
Stored in frontmatter only; never used in filename. Both fields are
required (not optional) on all schemas.

### Decision 4 — `note_version` auto-incremented on every overwrite
When `write_note()` overwrites an existing file, it reads the prior
`note_version` from the existing frontmatter and writes `note_version + 1`.
First write = `note_version: 1`. This counter is the primary audit signal
for "has this note been updated and how many times?"

### Decision 5 — `written_by` records the source module string
Each calling system passes a `written_by` string identifying the specific
pipeline module that produced the write (e.g.,
`"P_300/daily_evaluate_pipeline"`, `"P_115/tracker_writer"`). This is
written verbatim to frontmatter. P_800 does not validate the string — the
sending system owns its own identity.

### Decision 6 — Overwrite policy is always True; `verdict_history` carries
the full classification record
Every re-run of the same signal_date + ticker overwrites the existing note.
The prior classification is not lost — it is appended to `verdict_history`
before the new content is written. See Section 3.3 for the structure.

*Rejected alternative:* `prior_verdict` single field → only the immediately
preceding verdict is preserved. Three runs (WATCH → WATCH → BUY) would lose
the first WATCH. `verdict_history` retains the complete progression.

### Decision 7 — Obsidian is signal and context only; position tracking
lives in P_020
A single P_300 signal can spawn multiple concurrent position legs (e.g.,
3 option contracts, sell 2 at target 1, hold 1 for target 2, add stock
while waiting). Obsidian notes do not track individual legs. The vault note
represents the signal and its classification history. P_020 (sourced from
Schwab transactions) is the authoritative system of record for entries,
exits, quantities, and realized P&L. When P_020 is wired to P_800, a
`p020_realized_R` and `p020_outcome` field will be added to the signal note
as optional post-close fields, linking signal quality to realized outcome
without duplicating position-level data.

---

## 3. Normalized Note Specification

### 3.1 Filename Convention
```
<signal_date>_<TICKER>.md
```
- `signal_date` in `YYYY-MM-DD` format
- `TICKER` uppercase, spaces replaced with underscores
- Example: `2026-05-29_ROST.md`

This convention is unchanged from the current implementation. The change is
that `signal_date` is now an explicit required field in every schema rather
than inferred from the ambiguous `date` field.

### 3.2 Required Frontmatter Fields (All Schemas)

These fields must appear in every vault note regardless of source system.
They are written by P_800 from the normalized record. The sending system is
responsible for populating them correctly before calling `write_to_vault()`.

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Schema family: `P300`, `P115`, `P020`, `P400`, `KB` |
| `schema_version` | string | Schema version at time of write, e.g. `"2.0"` |
| `signal_date` | YYYY-MM-DD | The date the signal applies to; used in filename |
| `run_date` | YYYY-MM-DD | The calendar date the pipeline ran |
| `run_ts` | ISO 8601 | Full datetime of pipeline run, e.g. `2026-05-31T12:44:00` |
| `ticker` | string | Uppercase symbol |
| `verdict` | string | Normalized: `BUY`, `WATCH`, or `PASS` |
| `written_by` | string | Source module, e.g. `P_300/daily_evaluate_pipeline` |
| `note_version` | integer | Increments on every overwrite; first write = 1 |
| `verdict_history` | list | Ordered list of prior verdicts; empty on first write |

### 3.3 `verdict_history` Structure

`verdict_history` is a YAML list. Each entry is written by `vault_writer.py`
immediately before overwriting an existing note. The entry records the
verdict that is about to be replaced, the run date that produced it, and
the note version at that time. The list grows by one entry on each
overwrite.

**First write (note_version: 1):**
```yaml
verdict: WATCH
verdict_history: []
note_version: 1
run_date: 2026-05-29
run_ts: 2026-05-29T14:22:00
```

**Second run, same verdict (note_version: 2):**
```yaml
verdict: WATCH
verdict_history:
  - {verdict: WATCH, run_date: 2026-05-29, note_version: 1}
note_version: 2
run_date: 2026-05-30
run_ts: 2026-05-30T09:15:00
```

**Third run, verdict changes to BUY (note_version: 3):**
```yaml
verdict: BUY
verdict_history:
  - {verdict: WATCH, run_date: 2026-05-29, note_version: 1}
  - {verdict: WATCH, run_date: 2026-05-30, note_version: 2}
note_version: 3
run_date: 2026-05-31
run_ts: 2026-05-31T12:44:00
```

`vault_writer.py` is solely responsible for reading the existing
`verdict_history`, appending the current entry, and passing the updated
list to `frontmatter_builder.py`. The sending system never touches
`verdict_history` directly.

### 3.4 System-Specific Frontmatter Fields

Fields beyond the required set are system-specific and follow no
cross-system contract. P_300 retains its per-horizon stats (`h5_win_rate`,
`h5_mean_ret`, etc.). P_115 retains its scoring fields. These are queryable
within a single system's folder but are not guaranteed to exist in
cross-system queries.

### 3.5 Note Body Convention

The note body (below the closing `---`) is owned by the sending system.
P_800 does not validate or normalize body content. The body must begin with
a level-1 heading in the format:

```
# TICKER - VERDICT (source)
```

Example: `# ROST - BUY (P_300)`

---

## 4. Dataview Query Catalog

Once this standard is implemented, the following queries are available.
All queries assume notes have been written under this standard. Notes
written before implementation (existing ~600 notes) will not have the
required fields and will be excluded from results until backfilled.

### 4.1 All BUY signals this week, any system
```dataview
TABLE signal_date, source, written_by, run_date
FROM "TradeManagement"
WHERE verdict = "BUY"
  AND signal_date >= date(today) - dur(7 days)
SORT signal_date DESC
```

### 4.2 All signals for a specific ticker, all time
```dataview
TABLE signal_date, source, verdict, note_version, run_date
FROM "TradeManagement"
WHERE ticker = "ROST"
SORT signal_date DESC
```

### 4.3 Signals that required multiple runs to reach conviction
```dataview
TABLE signal_date, ticker, source, note_version, verdict, verdict_history
FROM "TradeManagement"
WHERE verdict = "BUY"
  AND note_version > 1
SORT note_version DESC
```
Returns signals where the final BUY took more than one run to develop.
Signals with high `note_version` had slower-developing conviction and
may warrant additional scrutiny.

### 4.4 All signals that changed classification on re-run
```dataview
TABLE signal_date, ticker, source, note_version, verdict
FROM "TradeManagement"
WHERE note_version > 1
  AND verdict != verdict_history[0].verdict
SORT run_date DESC
```
Note: `verdict_history[0]` accesses the most recent prior entry (the
immediately preceding verdict). This query shows every note where the
current verdict differs from the previous run's verdict.

### 4.5 Signals that went WATCH → WATCH → BUY (slow build)
```dataview
TABLE signal_date, ticker, note_version, run_date
FROM "TradeManagement"
WHERE verdict = "BUY"
  AND note_version >= 3
  AND verdict_history[0].verdict = "WATCH"
  AND verdict_history[1].verdict = "WATCH"
SORT signal_date DESC
```
This identifies the specific pattern from the design discussion: a signal
that held WATCH for two runs before upgrading to BUY. These are the weakest
conviction BUY signals in the vault.

### 4.6 P_300 BUY signals with win rate above threshold at h=5
```dataview
TABLE signal_date, ticker, h5_win_rate, h5_mean_ret, verdict
FROM "TradeManagement/P300"
WHERE verdict = "BUY"
  AND h5_win_rate >= 0.70
SORT signal_date DESC
```
Requires Gap 6 fix (`write_signal_to_obsidian.py` lines 57–58) to be
applied first. Valid once `h5_win_rate` stores a true decimal fraction
(0.70 = 70%).

### 4.7 Same ticker evaluated by both P_300 and P_115
```dataview
TABLE signal_date, source, verdict
FROM "TradeManagement"
WHERE ticker = "NVDA"
SORT signal_date DESC, source ASC
```

### 4.8 Weekly signal summary — count by verdict and system
```dataview
TABLE rows.source AS Systems, length(rows) AS Count
FROM "TradeManagement"
WHERE signal_date >= date(today) - dur(7 days)
GROUP BY verdict
SORT verdict ASC
```

### 4.9 P_300 signals linked to P_020 outcomes (future — post P_020 wiring)
```dataview
TABLE signal_date, verdict, note_version, p020_realized_R, p020_outcome
FROM "TradeManagement/P300"
WHERE verdict = "BUY"
  AND p020_realized_R != null
SORT signal_date DESC
```
This query becomes available once P_020 is wired to P_800 and the
`p020_realized_R` / `p020_outcome` fields are added to `P300Record` as
optional post-close fields.

---

## 5. Verdict Mapping by System

| System | Native field | Native value | Maps to `verdict` |
|--------|-------------|--------------|-------------------|
| P_300 | `signal` | `BUY` | `BUY` |
| P_300 | `signal` | `WATCH` | `WATCH` |
| P_300 | `signal` | `PASS` | `PASS` |
| P_115 | `step1_verdict` | `BUY` | `BUY` |
| P_115 | `step1_verdict` | `ASYM` | `WATCH` |
| P_115 | `step1_verdict` | `PASS` | `PASS` |
| P_020 | `outcome` | TBD | TBD — confirm when P_020 wired |
| P_400 | `council_verdict` | `Approve` | `BUY` |
| P_400 | `council_verdict` | `Approve with Caution` | `WATCH` |
| P_400 | `council_verdict` | `Block` | `PASS` |

---

## 6. Implementation Scope

When approved, the following files require changes. No files are to be
written until the operator gives explicit approval.

### 6.1 P_800 Package Files

| File | Change summary | Est. lines |
|------|---------------|------------|
| `obsidian_writers/schemas.py` | Add `signal_date`, `run_date`, `run_ts`, `verdict`, `written_by`, `note_version`, `verdict_history` to base; apply verdict mapping; retain `date` as deprecated optional | ~190 |
| `obsidian_writers/config.py` | Bump `SCHEMA_VERSIONS` to `"2.0"`; add `VERDICT_MAP` constant | ~45 |
| `obsidian_writers/domain/filename_builder.py` | Use `signal_date` field instead of `date` for filename construction | ~60 |
| `obsidian_writers/domain/frontmatter_builder.py` | Emit required fields in defined order; serialize `verdict_history` list correctly | ~75 |
| `obsidian_writers/infrastructure/vault_writer.py` | Add `_read_existing_frontmatter()` and `_build_history_entry()` helpers; read prior verdict + history before overwrite; pass updated history to builder | ~110 |
| `obsidian_writers/application/write_handler.py` | Inject `run_date`, `run_ts`, `written_by` into data dict before validate step | ~65 |

### 6.2 Sending-System Files

| File | Change summary |
|------|---------------|
| `P_300/python/write_signal_to_obsidian.py` | Fix lines 57–58 (win_rate double-division bug); fix line 98 (overwrite=False → True); populate `signal_date`, `run_date`, `run_ts`, `written_by`, `verdict` |
| `P_115/tracker_writer.py` (future) | Populate required fields; map `step1_verdict` to `verdict` using `VERDICT_MAP` from P_800 config |

### 6.3 Line Count Summary

Total P_800 package: ~545 lines across 6 files. No single file exceeds the
300-line standard. `vault_writer.py` is the largest net change at ~110 lines.

---

## 7. What This Standard Does NOT Address

**Historical note backfill:** Existing notes in `TradeManagement/P300/`
(~60 notes) and `TradeManagement/P115/` (500+ notes) do not have
`signal_date`, `run_date`, `verdict`, `note_version`, or `verdict_history`
fields. Cross-system queries will only return notes written after this
standard is implemented. Backfilling is a separate task, lower priority
than forward implementation.

**Append mode for multi-system notes:** If P_300 writes a note and P_400
later needs to add trade outcome data to the same note, the current
overwrite model would destroy P_300's content. This scenario requires an
append mode with field-level merge logic. It is not in scope here and will
be designed when P_400 is built.

**Vault folder structure:** The current `TradeManagement/P300/`,
`TradeManagement/P115/` etc. structure is unchanged by this standard.

**Intraday re-evaluations:** If a future system evaluates the same symbol
multiple times in a single day against the same signal date, the
signal_date + ticker key will collide. That system must append a sequence
number to the filename. This standard does not define that convention.

---

## 8. Open Questions Before Implementation

**Q1 — P_300 `signal` field retention after `verdict` is added**
After `verdict` is introduced, the existing `signal` field on `P300Record`
becomes redundant (it carries the same value with the same vocabulary).
Recommendation: retain `signal` in schema v2.0 for backward compatibility
with any existing queries that reference it; remove in schema v3.0 with
a documented migration window. Requires operator confirmation.

**Q2 — P_115 `written_by` string**
The P_115 tracker writer does not yet exist as a Python module. The
`written_by` value cannot be finalized until the module is named.
Placeholder: `"P_115/tracker_writer"`. Confirm before implementation.

**Q3 — Gap 6 fix timing**
The `write_signal_to_obsidian.py` lines 57–58 bug is isolated, low-risk,
and independent of the full standard implementation. It can be fixed now
(two lines changed) or held for the combined implementation pass.
Requires operator decision.

---

## Changelog

### v1.1 — 2026-05-31
- **Decision 7 added:** Obsidian is signal and context only; P_020 is
  system of record for position tracking. Multi-leg trade scenario
  (options + stock, partial closes) explicitly scoped out of this standard.
  Future `p020_realized_R` / `p020_outcome` link fields defined.
- **Gap 10 added:** No verdict history; classification changes undetectable.
- **Decision 6 revised:** `prior_verdict` single-field approach replaced
  with `verdict_history` list. Full progression (WATCH → WATCH → BUY)
  preserved on every overwrite. Rationale: one-level-back insufficient
  when signal conviction develops across multiple runs.
- **Section 3.3 added:** `verdict_history` structure with three-state
  example showing first write, same-verdict re-run, and verdict change.
- **Section 4 expanded:** Queries 4.3–4.5 rewritten to use
  `verdict_history`; new query 4.5 for slow-build WATCH → WATCH → BUY
  pattern; query 4.9 added for future P_020 outcome linking.
- **Gap 6 root cause identified:** `write_signal_to_obsidian.py` double-
  division bug on lines 57–58; silent overwrite bug on line 98. Fix
  specified, not yet applied.
- **Section 6 expanded:** `vault_writer.py` scope increased to include
  `_read_existing_frontmatter()` and `_build_history_entry()` helpers;
  line count estimates updated.
- **Open Questions revised:** Q1 added (signal field retention); Q3 added
  (Gap 6 fix timing).
- Author: Claude (drafting) / Anthony Zoppi (review pending)

### v1.0 — 2026-05-31
- Initial draft. 9 gaps, 6 decisions, normalized note spec, Dataview query
  catalog, verdict mapping, implementation scope, open questions.
- Author: Claude (drafting) / Anthony Zoppi (review pending)

---

**End of P_800 Obsidian Note Standard v1.1**
