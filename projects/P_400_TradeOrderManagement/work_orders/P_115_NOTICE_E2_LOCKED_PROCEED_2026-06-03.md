# P_115 NOTICE: E2 Decisions LOCKED — Proceed with Signal Emitter Build

**From:** Anthony Zoppi  
**To:** P_115 (Signal Detection System)  
**Date:** 2026-06-03  
**Status:** READY TO BUILD — WO-P115-E1.001

---

## E2 Planning Finalized

All interface decisions are locked. You have a clear target for signal_emitter implementation.

### Locked Decisions Affecting P_115

1. **Schema:** Single unified v2_signal (same fields for all signals)
2. **Output Location:** TradeOrderManagement/signals/YYYY-MM-DD_SYMBOL_signal.json
3. **Error Responsibility:** P_115 must emit valid JSON. P_400 will reject malformed packets.
4. **Backwards Compat:** Your current TradeManagement/P_115/ output stays. New signals go to TradeOrderManagement/signals/ (JSON).

---

## Signal Emitter Spec (Unchanged from WO-P115-E1.001)

Build signal_emitter that:
1. Detects BUY signal (existing P_115 logic — no change)
2. Formats as P400SignalRecord dict
3. Calls write_to_vault("P400SIG", packet) to emit

### Call Pattern

\\\python
from vault_interface import write_to_vault

write_to_vault(
    schema_name="P400SIG",
    data={
        "signal_id": "P115-2026-06-03-AMTM-001",
        "signal_timestamp": "2026-06-03T14:23:00Z",
        "signal_source": "P_115",
        "strategy": "dip_buy",
        "symbol": "AMTM",
        "guideline_entry": 47.50,
        "guideline_stop": 45.75,
        "guideline_target": 52.00,
        "signal_horizon": "3-5 days",
        "confidence_level": "HIGH",
        "context": {
            "atm_at_signal": 1.85,
            "close_at_signal": 47.75,
            "trailing_volume_30d": 1850000,
            "signal_rationale": "Dip into 20-day MA after earnings"
        },
        "signal_metadata": {
            "p115_session_date": "2026-06-03",
            "p115_chart_timeframe": "1D",
            "signal_source_link": "TradeOrderManagement/P_115/2026-06-03_AMTM_P115.md"
        }
    },
    overwrite=True
)
\\\

**Reference:** WO-P115-E1.001.md (full spec + all required fields)  
**Schema Reference:** P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0.md (locked)

---

## Quality Requirements

P_400 will validate incoming JSON. Invalid packets are REJECTED (no repair, no skip).

Ensure:
- All required fields present
- Valid JSON syntax
- Correct field types (strings, numbers, dates)
- signal_source = "P_115" (hardcoded)

---

## Timeline

- **Next P_115 session:** Build + test signal_emitter
- **Live run:** 1-2 trading days (verify JSON files created correctly)
- **After validation:** E2 planning proceeds (P_400 JSON reader, P_115 STEP 2 removal)

---

## Questions?

See WO-P115-E1.001.md or ask Claude.

---

**Ready to build. Let's lock in the signal flow.**
