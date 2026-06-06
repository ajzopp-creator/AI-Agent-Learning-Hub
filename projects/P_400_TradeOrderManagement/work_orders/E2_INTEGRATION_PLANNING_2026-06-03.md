# P_400 Enhancement 2 & Integration Planning

**Document:** E2 Roadmap + Integration Strategy  
**Version:** 1.0  
**Date:** 2026-06-03  
**From:** Claude (P_400 Coordinator)  
**Scope:** Architecture split (remove P_115 STEP 2), full JSON-only signal handoff, options signal integration

---

## Phase Timeline

**Phase E1 (Signal Emission) — IN PROGRESS**
- P_115 signal_emitter: build + test (next P_115 session)
- P_300 signal_emitter: build + test (parallel to P_115)
- P_400 JSON reader: build after P_115/P_300 ready
- Live run: 1-2 trading days (signal → JSON → P_400 order spec)
- Validation: end-to-end test (no inline chat fallback yet)

**Phase E2 (Architectural Split) — DESIGN, ready for build**
- Remove P_115 STEP 2 (no more .md output, JSON-only)
- Remove P_300 STEP 2 (same as P_115)
- P_400 reads JSON as sole upstream source (no chat fallback)
- P_800 finalizes schema versioning + vault structure
- Live validation: E2-mode trading (1+ week)

**Phase E3 (Enhancement + Options) — FUTURE**
- P_300 options signals → P_400 options order specs
- Complex order types (verticals, spreads, 1st-trgs-OCO)
- Vehicle selection (shares vs. call vs. vertical)
- Options-specific Council rules (IV crush, theta, delta)

---

## E2 Critical Path

**Dependencies (what must happen first):**

1. ✅ P_400 Architecture v1.0 finalized
2. ✅ P_800 signal infrastructure (E1) complete
3. ⏳ P_115 signal_emitter built + tested
4. ⏳ P_300 signal_emitter built + tested (parallel)
5. ⏳ P_400 JSON reader implementation
6. ⏳ 1-2 day live run (signals flowing, files created, P_400 reading)
7. 🔄 P_800 finalizes E2 interface decisions:
   - Schema versioning (v1_stock, v1_options, or single v2?)
   - Vault folder structure (signals/P_115 vs. signals/ flat?)
   - Error handling (malformed packets → reject/repair/skip?)
   - Backwards compatibility (dual-read path for old v1.0 notes vs. JSON-only going forward?)
8. 🔄 Remove P_115 STEP 2 (no more .md output)
9. 🔄 Remove P_300 STEP 2 (no more .md output)
10. ⏳ P_400 live validation in E2 mode (1+ week, JSON-only, no chat fallback)

---

## E2 Interface Decisions (P_800 to Decide)

### 1. Signal Schema Versioning

**Option A: Single Schema (Recommended)**
- v2_signal (unified for stocks + options)
- Stock signals include: strategy, entry/stop/target, confidence, horizon
- Options signals include: same + IV, delta, theta, contract_specs
- Backwards compat: keep v1 notes readable, new signals only in v2

**Option B: Dual Schema**
- v1_stock_signal (stock signals only)
- v1_option_signal (options signals only)
- Requires P_400 to detect + handle both
- More fragmented

**Option C: Versioned Paths**
- signals/v1/ (for backward compat v1.0 notes, readonly)
- signals/v2/ (new stocks + options signals)
- P_400 reads from v2 exclusively

**LOCKED DECISION: A** — Single unified v2_signal schema. Stock + options covered in one model, optional/null fields. Future-proof.

### 2. Vault Folder Structure

**Current (E1):** TradeOrderManagement/signals/YYYY-MM-DD_SYMBOL_signal.json (flat, all sources mixed)

**Option A: Keep Flat (Recommended)**
- Pro: Simple, glob patterns work for P_400 (read all signals/)
- Con: Cannot quickly isolate P_115 vs P_300 signals at filesystem level

**Option B: Separate by Source**
- signals/P_115/YYYY-MM-DD_SYMBOL_signal.json
- signals/P_300/YYYY-MM-DD_SYMBOL_signal.json
- Pro: Visual separation, source tracking at path level
- Con: P_400 glob pattern more complex, potential for missed signals

**LOCKED DECISION: A** — Keep flat. signal_source field in JSON is authoritative; path structure adds no value.

### 3. Error Handling & Validation

**Scenario:** P_115 emits malformed packet (missing required field, invalid JSON).

**Option A: Reject (Recommended)**
- P_400 STEP 1 validates file; if invalid, error message + do NOT proceed
- P_115 notified to fix and re-emit
- Pro: Prevents garbage orders
- Con: Requires human intervention

**Option B: Repair**
- P_400 fills missing fields with defaults or asks Tony
- Con: May produce incorrect orders if defaults are wrong

**Option C: Skip**
- P_400 skips malformed packets, continues
- Con: Silent failure — signals lost

**LOCKED DECISION: A** — Reject malformed packets. Error origin layer (P_115/P_300) handles it. Producer responsible for signal quality.

### 4. Backwards Compatibility (Existing 1,462 P_115 v1.0 Notes)

**Scenario:** 1,462 P_115 .md files written under schema v1.0 exist in TradeOrderManagement/P_115/. E2 removes P_115 STEP 2 output entirely (JSON-only going forward).

**Option A: Dual-Read Path (Recommended for Migration)**
- P_400 can read old v1.0 notes AND new v2 JSON signals for ~2-4 weeks
- Allows gradual transition
- After cutover window, P_400 reads JSON-only
- Pro: No signals lost, clean switchover
- Con: P_400 logic more complex temporarily

**Option B: JSON-Only Going Forward**
- E2 cutover: P_115 STEP 2 disabled, JSON-only from that point
- Existing 1,462 v1.0 notes archived (not deleted, not readable by P_400)
- Pro: Clean break, simpler P_400 logic
- Con: Historical records need archival strategy

**LOCKED DECISION: A** — Dual-read path 2-4 weeks (old v1.0 notes OR new v2 JSON), then JSON-only cutover. Ensures no signal loss, allows team to adapt.

---

## P_400 Implementation Checklist for E2

- [ ] Build P_400 STEP 1 JSON reader (parse signal file, extract fields, validate)
- [ ] Implement P_400 schema validation (required fields, type checking, range validation)
- [ ] Add error handling (malformed packets → stop + error message)
- [ ] (Optional) Dual-read logic: read old v1.0 notes OR new v2 JSON signals
- [ ] Test end-to-end: signal file → P_400 reconciliation → Council → order spec
- [ ] Update P_400 init prompt (remove any chat input fallback, JSON-only)
- [ ] Remove P_115 STEP 2 from P_400 init (no inline chat trigger)
- [ ] Documentation: P_400 v1.1 (E2 finalized)

---

## P_115 / P_300 Implementation Checklist for E2

**P_115:**
- [ ] Confirm signal_emitter working (signals flowing to signals/ folder)
- [ ] Live run validation (1-2 days, verify JSON format)
- [ ] Deactivate STEP 2 (.md output) after E1 validation
- [ ] Transition to JSON-only signal output

**P_300:**
- [ ] Same as P_115 (for stocks)
- [ ] Prepare options signal structure (if included in v2 schema)

---

## P_800 Implementation Checklist for E2

- [ ] Finalize schema versioning decision (v2 single vs. dual vs. versioned paths)
- [ ] Finalize vault folder structure decision
- [ ] Define error handling strategy (reject malformed → how to notify P_115?)
- [ ] Decide on backwards-compatibility window (dual-read 2-4 weeks? or JSON-only from cutover?)
- [ ] Update obsidian_writers / write_handler for E2 logic (if schema changes)
- [ ] Document E2 signal schema (updated version of P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0.md)

---

## Timeline Estimate

**E1 Completion (live run):** 1-2 weeks (P_115/P_300 builds + testing + validation)  
**E2 Interface Decisions:** ~3 days (P_800 confirms options above)  
**E2 Implementation:** ~1 week (P_400 JSON reader, P_115/P_300 STEP 2 removal, testing)  
**E2 Live Validation:** 1+ week (JSON-only mode, no fallback)  
**E2 Completion & Cutover:** ~2-3 weeks total from now  

---

## Next Immediate Actions

1. **P_115 builds signal_emitter** (WO-P115-E1.001) — next P_115 session
2. **P_300 builds signal_emitter** (WO-P300-E1.001) — parallel to P_115
3. **P_400 stands by** — ready to implement JSON reader once signals are flowing
4. **P_800 reviews E2 decision points** above and confirms answers (schema versioning, folder structure, error handling, backwards compat)

---

**Ready to proceed. Awaiting P_115 signal_emitter completion.**

