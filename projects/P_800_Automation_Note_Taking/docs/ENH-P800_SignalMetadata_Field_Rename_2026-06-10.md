# ENH-P800 -- Rename `p115_`-prefixed SignalMetadata fields to producer-neutral names

**Type:** Enhancement proposal (P_300 -> P_800)
**Originator:** P_300 (Claude, architect) -- 2026-06-10
**Owner (proposed):** P_800 (owns the shared signal contract + the v2.0 schema spec)
**For P_800 to:** convert into a Work Order
**Relates to:** `docs/P_115_P400_SIGNAL_PACKET_SCHEMA_v2_0.md`; WO-P800-E2.002 (schema relocation to shared_resources)

---

## WHY

The shared `SignalMetadata` model names two fields with a `p115_` prefix:

`shared_resources/python_utils/signal_schemas.py`, lines 37-41:
```
class SignalMetadata(BaseModel):
    p115_session_date: str       # YYYY-MM-DD of generating P_115 session
    p115_chart_timeframe: str    # 1D | 4H | 1H | etc
    signal_source_link: str      # path to upstream P_115/P_300 .md (audit)
```

The prefix is a P_115 origin artifact -- Buy The Dip was the first producer on the
signal contract, and the field names were never generalized when the schema unified to
v2.0 across P_115 **and** P_300. The model is shared by both packet versions
(`P400SignalRecord` v1.0, `SignalV2` v2.0) and by every producer.

**Effect, observed in a live P_300 packet:**
```
"signal_metadata": {
    "p115_session_date": "2026-06-08",                                   <- a P_300 eval date
    "p115_chart_timeframe": "1D",
    "signal_source_link": "trading_journal/TradeManagement/P300/2026-06-08_CALM.md"  <- P300
}
```
Right data, key names that lie about the owner. The schema comment ("generating P_115
session") is also wrong for a P_300 packet.

**Redundant on top of misleading:** the packet already carries a top-level
`signal_source: str  # P_115 | P_300 | manual` field that identifies the producer
correctly. The `p115_` prefix duplicates that intent -- incorrectly.

---

## WHY P_800 SCOPE (and why now)

- The schema lives at `shared_resources/python_utils/signal_schemas.py`, moved there under
  WO-P800-E2.002. P_800 owns the contract and the spec doc. Producers (P_115, P_300) must
  not unilaterally rename a shared field -- it is a versioned contract change.
- **P_400's consumer reader is not built yet.** A hub-wide grep (2026-06-10) for both field
  names found no P_400 file -- consistent with the open todo "P_400 builds the JSON reader
  (E1 consumer side) -- REMAINING." Renaming now costs **zero consumer migration**: P_400
  builds against the corrected names from day one. Once P_400's reader ships keyed to
  `p115_*`, the rename gets more expensive and risks a live consumer.

---

## RECOMMENDED DESIGN (for P_800 to spec into the WO)

1. **Rename in `signal_schemas.py` `SignalMetadata`:**
   - `p115_session_date` -> `session_date`
   - `p115_chart_timeframe` -> `chart_timeframe`
   - leave `signal_source_link` as-is (already neutral)
   - drop "P_115" from the field comments.

2. **Bump the spec doc** `docs/P_115_P400_SIGNAL_PACKET_SCHEMA_v2_0.md` -- the field names
   are normative there. (-> v2.1, or an in-place documented rename.) Same for the Consumer
   Guide if it lists the metadata keys.

3. **Versioning call (P_800's):** this is a breaking field rename. Because v1.0 is retired
   and no v2 consumer is live, a coordinated rename across producers **without** a packet
   version bump is the cheaper path. If P_800 prefers a clean break, bump v2.0 -> v2.1 and
   have producers stamp it. P_800 decides.

4. **Update producers in the same WO** (one file per commit):
   - `projects/P_300/python/infrastructure/signal_emitter.py` lines 103-104 -- two dict
     keys, trivial.
   - `projects/P_115/python/domain/signal_builder.py` + `projects/P_115/python/schemas.py`.

5. **Update P_800's own test** `python/tests/test_signal_v2_e2e.py` assertions.

---

## BLAST RADIUS (live files -- verified by hub grep 2026-06-10)

| File | Role | Owner |
|------|------|-------|
| `shared_resources/python_utils/signal_schemas.py` | rename the two fields | P_800 |
| `projects/P_115/python/domain/signal_builder.py` | producer write | P_115 |
| `projects/P_115/python/schemas.py` | producer schema | P_115 |
| `projects/P_300/python/infrastructure/signal_emitter.py` | producer write (2 keys) | P_300 |
| `projects/P_800/python/tests/test_signal_v2_e2e.py` | test assertions | P_800 |
| `projects/P_800/docs/P_115_P400_SIGNAL_PACKET_SCHEMA_v2_0.md` | spec doc | P_800 |

**No P_400 consumer file** -- reader not built; zero migration cost now.

**Vestigial / do NOT migrate:**
- `projects/P_300/python/schemas_signal_packet.py` -- already flagged for removal
  (Enhancement 1 routes via the Hub interface; file is unused). Delete per the existing
  Backlog item; do not rename.
- All `projects/P_800/python/_archive/**` copies -- archived, dead.
- `projects/P_115/test4.py`, `test5.py` -- scratch tests (also E2.003 sys.path in-scope).

---

## VERIFY (eventual WO -- OWNER_DONE gate)

- `from shared_resources.python_utils.signal_schemas import SignalV2` imports clean via the
  editable install (eager execution) in a fresh p140 interpreter.
- A P_300 daily-evaluate BUY emits a packet whose `signal_metadata` has `session_date` /
  `chart_timeframe` (no `p115_`), and it passes P_800 validation.
- A P_115 emit produces the same neutral keys.
- `test_signal_v2_e2e.py` passes against the renamed fields.
- Spec doc + Consumer Guide reflect the new names.
- Completion Gate (WO-P000-E3.001) satisfied: downstream producers notified, no contract
  drift left undocumented.

---

## OUT OF SCOPE

- `signal_source_link` -- already neutral, untouched.
- Any change to top-level packet fields, validators, or asset_class logic.
- Removal of vestigial `schemas_signal_packet.py` -- separate Backlog item; noted here, not
  bundled.

---

**End of ENH-P800 -- SignalMetadata field rename**
