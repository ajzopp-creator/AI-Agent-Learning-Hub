# P_115 → P_400 Signal Packet Schema v1.0
**Purpose:** Structured machine-readable handoff from P_115 signal generation to P_400 order management  
**Format:** JSON  
**Location:** Obsidian vault, `TradeOrderManagement/signals/YYYY-MM-DD_SYMBOL_signal.json`  
**Last Updated:** 2026-06-02

---

## Schema Definition

```json
{
  "signal_id": "string (UUID or P115-YYYY-MM-DD-SYMBOL-SEQ)",
  "signal_timestamp": "ISO-8601 datetime (UTC)",
  "signal_source": "string (P_115 | P_300 | manual)",
  "strategy": "string (dip_buy | breakout | mean_reversion | support_bounce | etc)",
  "symbol": "string (uppercase ticker)",
  "guideline_entry": "number (price)",
  "guideline_stop": "number (price)",
  "guideline_target": "number (price)",
  "signal_horizon": "string (e.g., '3-5 days', '1-2 weeks')",
  "confidence_level": "enum (HIGH | MEDIUM | LOW)",
  "context": {
    "atm_at_signal": "number (ATR at signal time, optional)",
    "close_at_signal": "number (close price at signal generation)",
    "trailing_volume_30d": "number (shares/day)",
    "signal_rationale": "string (free-text summary of thesis)"
  },
  "signal_metadata": {
    "p115_session_date": "YYYY-MM-DD",
    "p115_chart_timeframe": "string (1D | 4H | 1H | etc)",
    "signal_source_link": "string (path to upstream P_115 or P_300 .md file)"
  }
}
```

---

## Field Definitions

| Field | Type | Required | Notes |
|---|---|---|---|
| signal_id | string | Yes | Unique identifier. Format: `P115-2026-06-02-AMTM-001` (system-generated) |
| signal_timestamp | ISO-8601 | Yes | UTC datetime when signal was generated |
| signal_source | enum | Yes | P_115 (stock), P_300 (options), manual (user entry) |
| strategy | enum | Yes | Trading strategy name (dip_buy, breakout, mean_reversion, etc) |
| symbol | string | Yes | Uppercase ticker (AMTM, SPY, etc) |
| guideline_entry | number | Yes | Recommended entry price from upstream thesis |
| guideline_stop | number | Yes | Recommended stop-loss from upstream thesis |
| guideline_target | number | Yes | Recommended profit target from upstream thesis |
| signal_horizon | string | Yes | Expected holding period (e.g., "3-5 days", "1-2 weeks") |
| confidence_level | enum | Yes | Signal quality: HIGH, MEDIUM, or LOW |
| context.atm_at_signal | number | No | ATR(14) at time of signal generation |
| context.close_at_signal | number | Yes | Close price at signal generation (audit trail) |
| context.trailing_volume_30d | number | Yes | Average daily volume, last 30 days |
| context.signal_rationale | string | Yes | One-sentence or short summary of thesis |
| signal_metadata.p115_session_date | date | Yes | YYYY-MM-DD of the P_115 session that generated the signal |
| signal_metadata.p115_chart_timeframe | string | Yes | Chart timeframe used in analysis (1D, 4H, 1H, etc) |
| signal_metadata.signal_source_link | string | Yes | Path to the upstream P_115 or P_300 .md file (audit linkage) |

---

## Sample File

**Filename:** `2026-06-02_AMTM_signal.json`  
**Location:** `TradeOrderManagement/signals/`

```json
{
  "signal_id": "P115-2026-06-02-AMTM-001",
  "signal_timestamp": "2026-06-02T14:23:00Z",
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
    "signal_rationale": "Dip into the 20-day moving average after earnings; 1.5x ATR stop; R:R 2.8:1"
  },
  "signal_metadata": {
    "p115_session_date": "2026-06-02",
    "p115_chart_timeframe": "1D",
    "signal_source_link": "TradeOrderManagement/P_115/2026-06-02_AMTM_P115.md"
  }
}
```

---

## File Location & Naming Convention

**Directory:** `<Obsidian vault root>/TradeOrderManagement/signals/`

**Filename format:** `YYYY-MM-DD_SYMBOL_signal.json`

Example: `2026-06-02_AMTM_signal.json`

---

## Integration Points

### P_115 Output (Enhancement 1)
P_115 STEP 1 (signal generation) writes this file after confirming the signal. The file is created by a new `signal_emitter.py` function that takes the thesis fields and exports JSON.

### P_400 Input (Enhancement 1)
P_400 STEP 1 (signal ingestion) reads the signal file instead of parsing inline chat. The reader parses JSON and maps fields to P_400's internal signal structure for reconciliation.

### Enhancement 2 (Future)
Once files are flowing reliably, P_115 can be split: STEP 1 generates the signal and writes the file. STEP 2 (order logic) is deleted, and P_400 reads the file as its exclusive input. This completes the architectural split recommended in the Process Evaluation doc.

---

## Validation Rules

- signal_id must be unique per session
- symbol must be a valid ticker
- guideline_entry > guideline_stop (long trades)
- guideline_target > guideline_entry (long trades)
- confidence_level must be one of {HIGH, MEDIUM, LOW}
- signal_horizon must match a recognizable duration pattern (e.g., "3-5 days")
- close_at_signal and atm_at_signal must match live price/ATR at signal_timestamp (audit check)

---

## Archival & Audit Trail

Every signal file is permanent. P_400 STEP 1 reads the file, stores the signal_source_link in the P_400 record, and logs the read. Later, during post-trade review, the signal_id and source_link allow tracing back to the original thesis, verdict, and live conditions at signal time. This creates an unbroken audit trail from generation to execution to closure.

---

**End of Signal Packet Schema v1.0**  
**Status:** Ready for implementation in P_115 Enhancement 1  
**Next Steps:** Build signal_emitter.py (P_115); build signal_reader.py (P_400)
