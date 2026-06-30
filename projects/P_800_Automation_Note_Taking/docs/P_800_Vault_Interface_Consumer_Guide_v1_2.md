# P_800 Vault Interface — Consumer Guide
**Version:** 1.2
**Date:** 2026-06-07
**Owner:** P_800 Automation_NoteTaking
**Audience:** P_115, P_300, P_020, P_400 — any project writing to the vault

> **v1.2 change:** Documented the JSON signal-packet route (`P400SIG`, `SIGNAL_V2`)
> to `TradeOrderManagement/signals/`. v1.1 only covered markdown notes. The legacy
> v1.0 packet (`P400SIG`) and unified v2.0 packet (`SIGNAL_V2`) run in parallel
> during a 2–4 week dual-emit window, then `P400SIG` is retired at cutover.

---

## What This Is

P_800 exposes a single public function — `write_to_vault()` — that any project calls
to write into the Obsidian trading journal. P_800 handles file naming, formatting,
folder routing, and schema validation. The calling project supplies the data. That is all.

Two output kinds, selected automatically by the schema key:

- **Markdown notes** — `P115 | P300 | P020 | P400 | KB` → `TradeManagement/<x>/` (or `KnowledgeBase/`)
- **Raw JSON signal packets** — `P400SIG | SIGNAL_V2` → `TradeOrderManagement/signals/`

---

## How to Call It

```python
from shared_resources.python_utils.vault_interface import write_to_vault

written = write_to_vault("P115", data_dict, overwrite=False)        # md note
written = write_to_vault("SIGNAL_V2", packet_dict)                  # JSON packet
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schema_name` | `str` | Yes | Which schema to validate against. See Schema Keys. |
| `data` | `dict` | Yes | Field names and values for this record. |
| `body` | `str` | No | Markdown body appended below frontmatter. **md schemas only** — ignored for JSON packets. |
| `overwrite` | `bool` | No | Default `True`. Pass `False` to skip an existing file. |

### Return value
`True` if written. `False` if the file already existed and `overwrite=False`.

---

## Schema Keys

| Key | Project | Output | Destination |
|-----|---------|--------|-------------|
| `"P115"` | P_115 Buy The Dip | md note | `TradeManagement/P115/` |
| `"P300"` | P_300 VantagePoint | md note | `TradeManagement/P300/` |
| `"P020"` | P_020 AJZ Strategies | md note | `TradeManagement/P020/` |
| `"P400"` | P_400 Trade Management | md note | `TradeManagement/P400/` |
| `"KB"` | Any project | md note | `KnowledgeBase/` |
| `"P400SIG"` | P_115/P_300 → P_400 | JSON packet (legacy v1.0) | `TradeOrderManagement/signals/` |
| `"SIGNAL_V2"` | P_115/P_300 → P_400 | JSON packet (unified v2.0) | `TradeOrderManagement/signals/` |

---

## JSON Signal Packets — `SIGNAL_V2`

Unified machine-readable handoff from any trading system to P_400 order management.
One schema for both stocks and options; the variant is discriminated by `asset_class`.
Packets are raw JSON — no frontmatter, no verdict normalization, no provenance.

### Required fields (all packets)

| Field | Type | Notes |
|-------|------|-------|
| `signal_id` | `str` | e.g. `P300-2026-06-07-AAPL-001` |
| `signal_timestamp` | `str` | ISO 8601 UTC. Also supplies the filename date. |
| `signal_source` | `str` | `P_115` \| `P_300` \| `manual` |
| `strategy` | `str` | `dip_buy` \| `breakout` \| `mean_reversion` \| etc |
| `symbol` | `str` | Uppercase ticker |
| `asset_class` | `str` | `stock` \| `option` |
| `guideline_entry` | `float` | Price or premium. Must be > 0 and > `guideline_stop`. |
| `guideline_stop` | `float` | Must be > 0. |
| `guideline_target` | `float` | Must be > `guideline_entry`. |
| `signal_horizon` | `str` | e.g. `"3-5 days"` |
| `confidence_level` | `str` | `HIGH` \| `MEDIUM` \| `LOW` |
| `position_size` | `int` | Shares (stock) or contracts (option) |
| `context` | `obj` | See below |
| `signal_metadata` | `obj` | See below |

### Options-only fields (required when `asset_class = "option"`, must be null for stocks)

| Field | Type | Notes |
|-------|------|-------|
| `strike_price` | `float` | Required for options |
| `underlying_price` | `float` | Required for options |
| `option_type` | `str` | `call` \| `put` |
| `expiration_date` | `str` | `YYYY-MM-DD`, required for options |

### `context` sub-object

| Field | Type | Notes |
|-------|------|-------|
| `close_at_signal` | `float` | Close price at signal generation |
| `trailing_volume_30d` | `float` | Avg daily volume/contracts, 30d |
| `signal_rationale` | `str` | Short thesis |
| `atm_at_signal` | `float` | ATR(14) at signal — optional |

### `signal_metadata` sub-object

| Field | Type | Notes |
|-------|------|-------|
| `session_date` | `str` | `YYYY-MM-DD` of the generating session |
| `chart_timeframe` | `str` | `1D` \| `4H` \| `1H` \| etc |
| `signal_source_link` | `str` | Path to the upstream `.md` (audit) |

### Stock example

```python
write_to_vault("SIGNAL_V2", {
    "signal_id": "P300-2026-06-07-AAPL-001",
    "signal_timestamp": "2026-06-07T13:45:00Z",
    "signal_source": "P_300",
    "strategy": "breakout",
    "symbol": "AAPL",
    "asset_class": "stock",
    "guideline_entry": 195.50,
    "guideline_stop": 190.00,
    "guideline_target": 207.00,
    "signal_horizon": "3-5 days",
    "confidence_level": "HIGH",
    "position_size": 25,
    "context": {
        "close_at_signal": 194.80,
        "trailing_volume_30d": 52000000,
        "signal_rationale": "VP grid bullish; breakout over base",
    },
    "signal_metadata": {
        "session_date": "2026-06-07",
        "chart_timeframe": "1D",
        "signal_source_link": "TradeManagement/P300/2026-06-07_AAPL.md",
    },
})
```

For stocks, omit `strike_price` / `underlying_price` / `option_type` /
`expiration_date` — they default to null and validate correctly. For options,
set `asset_class="option"` and supply all four; validation rejects the packet otherwise.

### Filenames & dual-emit window

| Key | Filename | Status |
|-----|----------|--------|
| `P400SIG` | `YYYY-MM-DD_SYMBOL_signal.json` | Legacy v1.0 — retired at cutover |
| `SIGNAL_V2` | `YYYY-MM-DD_SYMBOL_v2.0.json` | Unified — going forward |

Both land in the flat `TradeOrderManagement/signals/` folder; `signal_source`
inside the packet is authoritative (no per-source subfolders). During the
2–4 week window, producers may emit both. After cutover (`CUTOVER_DATE` in P_400),
only `SIGNAL_V2` is written and legacy files are cleaned up.

---

## P_115 Field Reference (md note)

**Required:** `date`, `symbol`. All other fields optional, default to `None`.

| Field | Type | Values / Notes |
|-------|------|---------------|
| `date` | `str` \| `date` | ISO: `"2026-05-23"` |
| `symbol` | `str` | Ticker. No special characters. |
| `signal_source` | `str` | `"P_115"` — P_800 sets this automatically |
| `step1_verdict` | `str` | `BUY` \| `ASYM` \| `PASS` |
| `pattern_type` | `str` | Cup & Handle, Flat Base, Double Bottom, High Handle |
| `breakout_volume_multiple` | `float` | e.g. `4.07` |
| `distribution_day_count` | `int` | |
| `follow_through_day` | `str` | `Y` \| `N` \| `--` |
| `market_direction` | `str` | P_010 risk_mode: `FULL` \| `HALF` \| `OFF` |
| `rs_vs_spy` | `float` | Relative strength vs SPY |
| `fundamentals_tier` | `int` | `0`–`4` |
| `analysis_tier` | `int` | `1`–`4` |
| `candle_tier` | `int` | `0`–`3` |
| `setup_score` | `int` | `0`–`4` |
| `liquidity_tier` | `int` | `1`–`4` |
| `traded` | `str` | `"Y"` \| `"N"` — defaults to `"N"` |
| `entry_price` / `tp_level` / `sl_level` / `stop_level` | `float` | |
| `risk_pct` | `float` | e.g. `1.5` (not `0.015`) |
| `account_balance` | `float` | |
| `outcome` | `str` | `TP Hit` \| `SL Hit` \| `Manual` \| `Pending` |
| `simulation_notes` / `comments` | `str` | Free text |
| `why_code` / `sig_code` | `str` | P_020 vocabulary tags |

> **`market_direction`** = the `risk_mode` value from `P_010_RiskConfig.json`
> (`FULL`, `HALF`, `OFF`). Not the derived display labels (CORRECTION, STANDARD, HOT).

---

## P_300 Field Reference (md note)

**Required:** `date`, `ticker`.

| Field | Type | Notes |
|-------|------|-------|
| `date` | `str` \| `date` | ISO format |
| `ticker` | `str` | |
| `signal` | `str` | `BUY` \| `WATCH` \| `PASS` |
| `signal_horizon` | `int` | Days |
| `h5…h20_win_rate` / `_mean_ret` / `_z_score` / `_class` | mixed | Per-horizon stats |
| `top_analog_1/2/3` | `str` | Top analog tickers |
| `top_comp_dist_1` | `float` | Composite distance |
| `n_matches` | `int` | Pattern match count |

---

## File Naming and Location

P_800 handles this automatically. Callers never specify filenames or paths.

| Key | Folder | Filename |
|-----|--------|----------|
| P_115 | `TradeManagement/P115/` | `YYYY-MM-DD_SYMBOL.md` |
| P_300 | `TradeManagement/P300/` | `YYYY-MM-DD_TICKER.md` |
| P_020 | `TradeManagement/P020/` | `YYYY-MM-DD_SYMBOL.md` |
| P_400 | `TradeManagement/P400/` | `YYYY-MM-DD_TICKER.md` |
| KB | `KnowledgeBase/` | `YYYY-MM-DD_TITLE-SLUG.md` |
| P400SIG | `TradeOrderManagement/signals/` | `YYYY-MM-DD_SYMBOL_signal.json` |
| SIGNAL_V2 | `TradeOrderManagement/signals/` | `YYYY-MM-DD_SYMBOL_v2.0.json` |

---

## Rules for Callers

1. **Never construct file paths.** Call `write_to_vault()` and let P_800 route.
2. **Never write directly to the vault.** All writes go through the interface.
3. **Dates are ISO strings or `date` objects.** `"2026-05-23"`, not `"05/23/2026"`.
4. **Symbols are clean ticker strings.** No brackets, slashes, or special characters.
5. **md only:** `signal_source` is set by P_800 automatically — do not pass it.
6. **md only:** `market_direction` = P_010 risk_mode (`FULL` / `HALF` / `OFF`).
7. **Omit fields you don't have** — defaults handle them. Don't pass `None` explicitly.
8. **JSON packets reject on malformed data** — no repair. The producer owns valid data.

---

## Error Handling

`write_to_vault()` raises `ValueError` on schema validation failure and `OSError`
on disk failure. Wrap calls in automated loops:

```python
try:
    write_to_vault("SIGNAL_V2", packet)
except ValueError as e:
    log.error("Signal rejected for %s: %s", packet.get("symbol"), e)
```

---

## Questions / Changes

All interface changes (new fields, keys, folders) are made in P_800. Do not modify
`vault_interface.py` or `schemas.py` from a calling project. Raise the request in a
P_800 session.
