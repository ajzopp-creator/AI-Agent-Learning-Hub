# P_800 NOTICE: E2 Decisions LOCKED

**From:** Anthony Zoppi  
**To:** P_800 (Vault Interface Owner)  
**Date:** 2026-06-03  
**Status:** FINAL DECISIONS — Ready for Implementation

---

## E2 Interface Decisions — ALL LOCKED

### 1. Signal Schema Versioning
**DECISION: A — Single Unified v2_signal**
- One schema for stocks + options
- Optional/null fields where not applicable
- Backwards compat: keep v1.0 notes readable, new signals in v2 only
- Future-proof for E3 options enhancements

### 2. Vault Folder Structure
**DECISION: A — Keep Flat**
- Location: TradeOrderManagement/signals/YYYY-MM-DD_SYMBOL_signal.json
- All sources (P_115, P_300, future) in same folder
- signal_source field in JSON is authoritative
- No separate P_115/ or P_300/ subfolders

### 3. Error Handling (Malformed Packets)
**DECISION: A — Reject**
- P_400 STEP 1 validates incoming signal packets
- If invalid: STOP, error message, do NOT proceed
- Producer responsibility: P_115/P_300 must emit valid JSON
- Principle: Error origin layer handles it

### 4. Backwards Compatibility (1,462 v1.0 Notes)
**DECISION: A — Dual-Read 2-4 Week Migration Window**
- E1→E2 transition: P_400 reads old v1.0 notes AND new v2 JSON signals
- Migration window: 2-4 weeks (you decide exact length)
- After cutover: P_400 reads JSON-only
- Ensures no signal loss, team has time to adapt

---

## P_800 Implementation Tasks (E2)

Based on locked decisions:

1. **Update obsidian_writers / write_handler**
   - Implement v2_signal Pydantic model (stocks + options fields)
   - Maintain backwards compatibility (read v1.0 notes during migration window)
   - Define optional/null field handling for stock-only signals

2. **Update signal schema documentation**
   - Create P_115_P400_SIGNAL_PACKET_SCHEMA_v2_0.md
   - Document all v2 fields
   - Include validation rules

3. **Update config.py**
   - SIGNALS_DIR remains: TradeOrderManagement/signals/
   - MIGRATION_WINDOW_END: [date 2-4 weeks from E2 start]
   - BACKWARDS_COMPAT_MODE: true during window, false after cutover

4. **Error handling in write_handler**
   - Validation on P400SIG packets before writing
   - Reject invalid → notify P_115/P_300 (method TBD)
   - Never repair or skip — always fail loudly

5. **Migration documentation**
   - How to archive old v1.0 notes (if needed)
   - Dual-read logic implementation notes
   - Cutover checklist for E2→E3 transition

---

## Timeline

- **Now:** Locked decisions confirmed ✅
- **Next:** P_115 builds signal_emitter (E1)
- **After E1 live run:** P_800 starts E2 implementation
- **E2 implementation:** ~1 week (v2_signal model, backwards compat logic, validation)
- **E2 cutover:** After P_400 JSON reader is live

---

## Questions / Confirmation Needed

1. Do locked decisions align with your vault architecture vision?
2. Any blockers to implementing v2_signal + backwards compat dual-read path?
3. How should invalid signal packets notify P_115/P_300 (email, Slack, log file, P_400 report)?
4. Confirm migration window length: 2 weeks? 3 weeks? 4 weeks?

---

**Ready to proceed. P_115 can now build signal_emitter. Awaiting your feedback on questions above.**
