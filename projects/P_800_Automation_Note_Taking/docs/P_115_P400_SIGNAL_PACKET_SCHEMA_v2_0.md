# P_115 → P_400 Signal Packet Schema v2.0

**Purpose:** Unified machine-readable signal handoff from all trading systems (P_115, P_300, future) to P_400 order management. Supports both stocks and options in a single schema.

**Format:** JSON  
**Location:** Obsidian vault, `trading_journal/TradeOrderManagement/signals/YYYY-MM-DD_SYMBOL_v2.0.json`  
**Owner:** P_800  
**Status:** Active (dual-emit compat window: 2 weeks from deployment)  
**Last Updated:** 2026-06-05

---

## Locked Design Decisions

1. **Single unified schema** — optional/null fields for stock vs options variants
2. **Flat signals/ folder** — signal_source field is authoritative (no per-source subfolders)
3. **Reject malformed packets** — no repair logic; producer responsible for valid data
4. **Dual-read compat window** — 2 weeks: emit both v1.0 (legacy) + v2.0 (new), then v2.0 only

---

## Core Schema Definition

```json
{
  "signal_id": "string (UUID or P115-YYYY-MM-DD-SYMBOL-SEQ)",
  "signal_timestamp": "ISO-8601 datetime (UTC)",
  "signal_source": "string (P_115 | P_300 | future)",
  "strategy": "string (dip_buy | breakout | mean_reversion | etc)",
  "symbol": "string (uppercase ticker)",
  "asset_class": "string (stock | option)",
  "guideline_entry": "number (price or premium)",
  "guideline_stop": "number (price or premium)",
  "guideline_target": "number (price, strike, or premium)",
  "signal_horizon": "string (e.g., ''3-5 days'', ''1-2 weeks'')",
  "confidence_level": "enum (HIGH | MEDIUM | LOW)",
  "position_size": "number (shares for stock, contracts for options)",
  "expiration_date": "string (YYYY-MM-DD, required for options, null for stocks)",
  "strike_price": "number (options only, null for stocks)",
  "underlying_price": "number (options context, null for stocks)",
  "option_type": "string (call | put, options only)",
  "context": {
    "atm_at_signal": "number (ATR at signal time, optional)",
    "close_at_signal": "number (close price at signal generation)",
    "trailing_volume_30d": "number (shares/day or contracts/day)",
    "signal_rationale": "string (free-text thesis summary)"
  },
  "signal_metadata": {
    "session_date": "YYYY-MM-DD",
    "chart_timeframe": "string (1D | 4H | 1H | etc)",
    "signal_source_link": "string (path to upstream P_115 or P_300 .md file)"
  }
}
```

---

## Compat Window & Cutover (2 Weeks)

### Week 1–2: Dual-Emit Active

**Producers:** Write both v1.0 and v2.0 JSON to signals/ folder
- Filenames: `YYYY-MM-DD_SYMBOL_signal.json` (v1.0) + `YYYY-MM-DD_SYMBOL_v2.0.json` (v2.0)

**Consumers:** P_400 reads v2.0 JSON files

### Week 3+: JSON-Only v2.0

1. Set `CUTOVER_DATE` in config.py (e.g., "2026-06-19")
2. Dual-emit disabled
3. Only v2.0 files written
4. Manual cleanup: delete all `YYYY-MM-DD_SYMBOL_signal.json` (v1.0) files
5. P_400 removes legacy v1.0 reader

---

**Status:** Ready for implementation  
**Owner:** P_800  
**Last Updated:** 2026-06-05