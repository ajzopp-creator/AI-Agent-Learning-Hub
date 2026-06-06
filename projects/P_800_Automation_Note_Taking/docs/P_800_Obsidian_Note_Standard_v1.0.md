# P_800 Obsidian Note Standard
**File:** `projects/P_800_Automation_Note_Taking/docs/P_800_Obsidian_Note_Standard.md`
**Version:** 1.0
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

**Gap 6 — `h5_win_rate` stored as decimal, displayed as percentage without
a schema-level marker**
`h5_win_rate: 0.008` appears in the ROST note frontmatter. The note body
shows `WR=80.0%`. These are inconsistent: `0.008` = 0.8%, not 80%.
The actual value being stored appears to be a raw count divided by top-K
(e.g., 8 wins out of 1000 comparisons?), not a true win rate fraction.
This is a data integrity issue that must be resolved before any Dataview
query against win rate will produce correct results. *Flagged here for
investigation; not in scope for this standard's initial implementation.*

**Gap 7 — No overwrite policy documented**
`vault_writer.write_note()` accepts `overwrite: bool = True`. There is no
documented policy for when overwrite should be True vs False, and no
calling code passes `overwrite=False` for any schema. The default silently
destroys prior data.

**Gap 8 — Schema versions are static constants, never incremented**
`SCHEMA_VERSIONS` in `config.py` lists all schemas at `"1.0"`. This value
is written into every note's `schema_version` frontmatter field. Because
the value never changes, it provides no version signal when schema fields
are added or changed. There is no changelog tracking which version added
which fields.

**Gap 9 — No `written_by` attribution**
Notes carry `source: P300` or `source: P115`, which identifies the schema
family. No field records the specific pipeline module or batch run that
wrote the note. When multiple systems could write to the same note
(e.g., P_300 writes a signal, P_400 later appends a trade outcome), there
is no audit trail of who wrote what.

---

## 2. Design Decisions

### Decision 1 — Filename key is `signal_date`, not `run_date`
One canonical note per signal per symbol. The filename `YYYY-MM-DD_TICKER.md`
uses the date the signal applies to (the VP grid date for P_300, the eval
date for P_115). A re-run of the same signal on a later day overwrites the
same file. The frontmatter records the run date and increments the version
counter, providing full provenance without vault proliferation.

*Rejected alternative:* `run_date` in filename → one new file per run →
vault fills with duplicates of the same signal with no clear canonical note.

### Decision 2 — Normalized `verdict` field added to all schemas
Every schema exposes a top-level `verdict` field using the shared
vocabulary: `BUY | WATCH | PASS`. Each system maps its own classification
to this field before calling `write_to_vault()`. P_115 maps `ASYM → WATCH`.
P_300 passes its `signal` value directly (vocabulary already matches).
Dataview queries target `verdict` exclusively.

### Decision 3 — `signal_date` and `run_date` are explicit distinct fields
`signal_date` = the date the signal applies to. Used in filename construction.
`run_date` = the calendar date the pipeline wrote this note. Stored in
frontmatter only; never used in filename. Both fields are required (not
optional) on all schemas.

### Decision 4 — `note_version` auto-incremented on every overwrite
When `write_note()` overwrites an existing file, it reads the prior
`note_version` from the existing frontmatter and writes `note_version + 1`.
First write = `note_version: 1`. This counter is the primary audit signal
for "has this note been updated?"

### Decision 5 — `written_by` records the source module string
Each calling system passes a `written_by` string (e.g., `"P_300/daily_evaluate_pipeline"`,
`"P_115/tracker_writer"`). This is written verbatim to frontmatter. It is
not validated by P_800 — the sending system owns its own identity string.

### Decision 6 — Overwrite policy is always True for same-signal re-runs
The policy is: if the signal_date + ticker match an existing note, overwrite.
If a future system needs to create multiple notes for the same signal (e.g.,
intraday re-evaluations), it must use a different filename key (e.g., append
a sequence number). This standard does not accommodate that case yet.

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
that `signal_date` is now an explicit field in every schema rather than
inferred from `date`.

### 3.2 Required Frontmatter Fields (All Schemas)

These fields must appear in every vault note regardless of source system.
They are written by P_800 from the normalized record. The sending system
is responsible for populating them correctly before calling `write_to_vault()`.

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Schema family: `P300`, `P115`, `P020`, `P400`, `KB` |
| `schema_version` | string | Schema version at time of write, e.g. `"2.0"` |
| `signal_date` | YYYY-MM-DD | The date the signal applies to |
| `run_date` | YYYY-MM-DD | The calendar date the pipeline ran |
| `run_ts` | ISO 8601 | Full datetime of pipeline run, e.g. `2026-05-31T12:44:00` |
| `ticker` | string | Uppercase symbol |
| `verdict` | string | Normalized: `BUY`, `WATCH`, or `PASS` |
| `written_by` | string | Source module path, e.g. `P_300/daily_evaluate_pipeline` |
| `note_version` | integer | Increments on every overwrite; first write = 1 |

### 3.3 System-Specific Frontmatter Fields

Fields beyond the required set are system-specific and follow no cross-system
contract. P_300 retains its per-horizon stats. P_115 retains its scoring
fields. These are queryable within a single system's folder but are not
guaranteed to exist in cross-system queries.

### 3.4 Note Body Convention

The note body (below the closing `---`) is owned by the sending system.
P_800 does not validate or normalize body content. The body must begin with
a level-1 heading: `# TICKER - VERDICT (source)`.

Example:
```
# ROST - BUY (P_300)
```

---

## 4. Dataview Query Capabilities Enabled by This Standard

Once this standard is implemented, the following Dataview queries become
possible across all systems writing to `TradeManagement/`.

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
This query answers the re-run question: if ROST was evaluated twice on the
same signal date, `note_version` will be 2 and `run_date` will show the
most recent run date.

### 4.3 Notes that have been re-run (overwritten at least once)
```dataview
TABLE signal_date, ticker, source, note_version, run_date
FROM "TradeManagement"
WHERE note_version > 1
SORT run_date DESC
```

### 4.4 P_300 BUY signals with win rate above threshold at h=5
```dataview
TABLE signal_date, ticker, h5_win_rate, h5_mean_ret, verdict
FROM "TradeManagement/P300"
WHERE verdict = "BUY"
  AND h5_win_rate >= 0.70
SORT signal_date DESC
```
Note: This query requires Gap 6 (win rate storage inconsistency) to be
resolved first. The query is valid once `h5_win_rate` reliably stores
a true decimal fraction (0.70 = 70%).

### 4.5 Same ticker evaluated by both P_300 and P_115
```dataview
TABLE signal_date, source, verdict
FROM "TradeManagement"
WHERE ticker = "NVDA"
SORT signal_date DESC, source ASC
```

### 4.6 P_300 signals where verdict shifted between runs
This requires `note_version > 1` and comparing the current `verdict` to
prior verdicts. Obsidian Dataview cannot query historical field values —
it only reads the current frontmatter. To answer "did this signal change
from PASS to BUY on re-run?", the prior verdict must be preserved in the
note body as a change log section. This is a body convention, not a
frontmatter requirement, and is left to the sending system to implement.

### 4.7 Weekly signal summary — count by verdict and system
```dataview
TABLE rows.source AS Systems, length(rows) AS Count
FROM "TradeManagement"
WHERE signal_date >= date(today) - dur(7 days)
GROUP BY verdict
SORT verdict ASC
```

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
| P_020 | `outcome` | `TP Hit` | mapped by caller — TBD |
| P_400 | `council_verdict` | `Approve` | `BUY` |
| P_400 | `council_verdict` | `Approve with Caution` | `WATCH` |
| P_400 | `council_verdict` | `Block` | `PASS` |

P_020 and P_400 mappings are preliminary and must be confirmed when those
systems are built out.

---

## 6. Implementation Scope

When approved, the following files require changes. No files are to be
written until the operator gives explicit approval.

| File | Change | Est. lines |
|------|--------|------------|
| `obsidian_writers/schemas.py` | Add `signal_date`, `run_date`, `run_ts`, `verdict`, `written_by`, `note_version` to base; apply verdict mapping; deprecate raw `date` field | ~180 |
| `obsidian_writers/config.py` | Bump `SCHEMA_VERSIONS` to `"2.0"` for all schemas; add `VERDICT_MAP` constant | ~40 |
| `obsidian_writers/domain/filename_builder.py` | Use `signal_date` field instead of `date` for filename construction | ~60 |
| `obsidian_writers/domain/frontmatter_builder.py` | Emit required fields in defined order; no structural changes to YAML logic | ~70 |
| `obsidian_writers/infrastructure/vault_writer.py` | Add `_read_note_version()` helper; increment `note_version` on overwrite | ~80 |
| `obsidian_writers/application/write_handler.py` | Pass `run_date`, `run_ts`, `written_by` into the data dict before validate step | ~60 |

Sending-system changes (not P_800 files):
| File | Change |
|------|--------|
| `P_300/.../daily_evaluate_pipeline.py` | Populate `signal_date`, `run_date`, `run_ts`, `written_by`, `verdict` before calling `write_to_vault()` |
| `P_115/.../tracker_writer.py` (future) | Same; map `step1_verdict` to `verdict` |

Total estimated new/changed lines across P_800 package: ~490 lines across
6 files. No file exceeds the 300-line standard; `schemas.py` is the largest
at ~180 lines.

---

## 7. What This Standard Does NOT Address

- **Gap 6 (win rate storage inconsistency):** The `h5_win_rate` value in
  existing P_300 notes appears to store a raw count, not a fraction. This
  must be investigated and corrected in P_300's report parser before any
  Dataview query against win rate will be reliable. This is a P_300 data
  issue, not a P_800 standard issue.

- **Historical note backfill:** Existing notes in `TradeManagement/P300/`
  and `TradeManagement/P115/` do not have `signal_date`, `run_date`,
  `verdict`, or `note_version` fields. Backfilling ~600 existing notes is
  possible but is a separate task. Until backfilled, cross-system queries
  will only return notes written after this standard is implemented.

- **Append vs overwrite for multi-system notes:** If a future workflow
  requires P_300 to write a note and P_400 to later append trade outcome
  to the same note, the current write_handler is overwrite-only. Append
  mode requires a separate design decision.

- **Vault folder structure:** The current `TradeManagement/P300/`,
  `TradeManagement/P115/` etc. structure is unchanged by this standard.

---

## 8. Open Questions Before Implementation

1. **Gap 6 resolution:** What is `h5_win_rate` actually storing? Compare
   the value in `2026-05-29_ROST.md` (`h5_win_rate: 0.008`) to the note
   body (`WR=80.0%`). These do not reconcile. Confirm the correct value
   and fix before implementing Dataview win-rate queries.

2. **P_115 `written_by` string:** The P_115 tracker writer does not yet
   exist as a Python module. Confirm the module name before finalizing
   the `written_by` convention for P_115.

3. **P_300 `signal` vs `verdict` field retention:** After adding `verdict`,
   should the existing `signal` field be retained in frontmatter for
   backward compatibility, or removed? Recommendation: retain during a
   transition period, then remove in schema v3.0.

---

## Changelog

### v1.0 — 2026-05-31
- Initial draft. Gap analysis (9 gaps), design decisions (6), normalized
  note spec, Dataview query catalog, verdict mapping table, implementation
  scope, open questions.
- Author: Claude (drafting) / Anthony Zoppi (review pending)

---

**End of P_800 Obsidian Note Standard v1.0**
