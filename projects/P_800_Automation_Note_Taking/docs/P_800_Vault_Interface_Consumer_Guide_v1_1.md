# P_800 Vault Interface — Consumer Guide
**Version:** 1.1  
**Date:** 2026-05-23  
**Owner:** P_800 Automation_NoteTaking  
**Audience:** P_115, P_300, P_020, P_400 — any project writing to the Obsidian vault

---

## What This Is

P_800 exposes a single public function — `write_to_vault()` — that any project calls
to write a structured note into the Obsidian trading journal. P_800 handles file naming,
YAML frontmatter formatting, folder routing, and schema validation. The calling project
supplies the data. That is all.

---

## How to Call It

```python
from shared_resources.python_utils.vault_interface import write_to_vault

written = write_to_vault("P115", data_dict, overwrite=False)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `schema_key` | `str` | Yes | Which schema to validate against. See Schema Keys below. |
| `data` | `dict` | Yes | Field names and values for this record. See field tables below. |
| `overwrite` | `bool` | No | Default `False`. Pass `True` to replace an existing note. |

### Return value
`True` if the note was written. `False` if the note already existed and `overwrite=False`.

---

## Schema Keys

| Key | Project | Record type |
|-----|---------|-------------|
| `"P115"` | P_115 Buy The Dip | One trade evaluation |
| `"P300"` | P_300 VantagePoint | One signal report |
| `"P020"` | P_020 AJZ Strategies | One closed trade |
| `"P400"` | P_400 Trade Management | One trade lifecycle entry |
| `"KB"` | Any project | Knowledge base article |

---

## P_115 Field Reference

**Required fields:** `date`, `symbol`  
All other fields are optional and default to `None` if omitted.

| Field | Type | Values / Notes |
|-------|------|---------------|
| `date` | `str` \| `date` | ISO format: `"2026-05-23"` |
| `symbol` | `str` | Ticker symbol. No special characters. |
| `signal_source` | `str` | Always `"P_115"` — P_800 sets this automatically |
| `step1_verdict` | `str` | `BUY` \| `ASYM` \| `PASS` |
| `pattern_type` | `str` | Cup & Handle, Flat Base, Double Bottom, High Handle |
| `breakout_verdict` | `str` | Free text |
| `breakout_volume_multiple` | `float` | e.g. `4.07` |
| `distribution_day_count` | `int` | |
| `follow_through_day` | `str` | `Y` \| `N` \| `--` |
| `market_direction` | `str` | P_010 risk_mode value: `FULL` \| `HALF` \| `OFF` |
| `rs_vs_spy` | `float` | Relative strength vs SPY |
| `fundamentals_tier` | `int` | `0`–`4` (V110: adjusted, may be rounded from decimal) |
| `analysis_tier` | `int` | `1`–`4` |
| `candle_tier` | `int` | `0`–`3` |
| `setup_score` | `int` | `0`–`4` |
| `liquidity_tier` | `int` | `1`–`4` |
| `traded` | `str` | `"Y"` \| `"N"` — defaults to `"N"` |
| `entry_price` | `float` | |
| `tp_level` | `float` | |
| `sl_level` | `float` | |
| `stop_level` | `float` | |
| `risk_pct` | `float` | e.g. `1.5` (not `0.015`) |
| `account_balance` | `float` | |
| `outcome` | `str` | `TP Hit` \| `SL Hit` \| `Manual` \| `Pending` |
| `recheck_status` | `str` | |
| `simulation_notes` | `str` | Full SimulationNotes string — options format or plain text |
| `comments` | `str` | Free text — Eddie Z notes, chart observations, etc. |
| `why_code` | `str` | P_020 WHY vocabulary tag |
| `sig_code` | `str` | P_020 SIG vocabulary tag |

> **`market_direction` source:** Pass the `risk_mode` value read from
> `P_010_RiskConfig.json` at session start — `FULL`, `HALF`, or `OFF`.
> Do not pass trading mode labels (CORRECTION, STANDARD, HOT MARKET) —
> those are derived display names, not the stored value.

---

## P_300 Field Reference

**Required fields:** `date`, `ticker`

| Field | Type | Notes |
|-------|------|-------|
| `date` | `str` \| `date` | ISO format |
| `ticker` | `str` | |
| `signal` | `str` | `BUY` \| `SELL` \| `PASS` |
| `signal_horizon` | `int` | Days |
| `h5_win_rate` … `h20_win_rate` | `float` | Win rate at each horizon |
| `h5_mean_ret` … `h20_mean_ret` | `float` | Mean return at each horizon |
| `h5_z_score` … `h20_z_score` | `float` | Z-score at each horizon |
| `h5_class` … `h20_class` | `str` | Classification at each horizon |
| `top_analog_1/2/3` | `str` | Top analog tickers |
| `top_comp_dist_1` | `float` | Composite distance score |
| `n_matches` | `int` | Number of pattern matches |

---

## Call Patterns

### Single evaluation (P_115 standard — one record per signal)

```python
from shared_resources.python_utils.vault_interface import write_to_vault

data = {
    "date": "2026-05-27",
    "symbol": "AAPL",
    "step1_verdict": "BUY",
    "pattern_type": "Cup & Handle",
    "fundamentals_tier": 4,
    "analysis_tier": 3,
    "candle_tier": 2,
    "setup_score": 3,
    "market_direction": "FULL",   # risk_mode from P_010_RiskConfig.json
    "traded": "N",
    "comments": "Eddie Z Cup & Handle; strong volume on breakout",
}

written = write_to_vault("P115", data)
```

### Batch — multiple records in one session (non-buy analysis)

```python
records = [
    {"date": "2026-05-27", "symbol": "MSFT", "step1_verdict": "PASS", ...},
    {"date": "2026-05-27", "symbol": "NVDA", "step1_verdict": "ASYM", ...},
    {"date": "2026-05-27", "symbol": "AMD",  "step1_verdict": "PASS", ...},
]

for record in records:
    write_to_vault("P115", record)
```

There is no batch call — `write_to_vault()` is called once per record. Call it as many
times as needed in a session. Each call is independent.

---

## File Naming and Location

P_800 handles this automatically. Callers do not specify filenames or paths.

| Project | Output folder | File name format |
|---------|--------------|-----------------|
| P_115 | `trading_journal/TradeManagement/P115/` | `YYYY-MM-DD_SYMBOL.md` |
| P_300 | `trading_journal/TradeManagement/P300/` | `YYYY-MM-DD_TICKER.md` |
| P_020 | `trading_journal/TradeManagement/P020/` | `YYYY-MM-DD_SYMBOL.md` |
| P_400 | `trading_journal/TradeManagement/P400/` | `YYYY-MM-DD_TICKER.md` |
| KB | `trading_journal/KnowledgeBase/` | `YYYY-MM-DD_TITLE-SLUG.md` |

If a file for that date + symbol already exists and `overwrite=False` (the default),
the call returns `False` and nothing is written. Pass `overwrite=True` to replace it.

---

## Rules for Callers

1. **Never construct file paths.** Call `write_to_vault()` and let P_800 route the note.
2. **Never write directly to `trading_journal/`.** All writes go through the interface.
3. **Dates must be ISO strings or Python `date` objects.** `"2026-05-23"` not `"05/23/2026"`.
4. **Symbols must be clean ticker strings.** No brackets, slashes, or special characters.
5. **`signal_source` is set by P_800 automatically.** Do not pass it — it will be overwritten.
6. **`market_direction` = P_010 risk_mode.** Pass `FULL`, `HALF`, or `OFF` — not trading mode labels.
7. **Omit fields you don't have.** Do not pass `None` explicitly — just leave the key out.
   The schema defaults handle it.

---

## Error Handling

`write_to_vault()` raises a `ValueError` if schema validation fails. Wrap in try/except
when calling from automated loops:

```python
try:
    write_to_vault("P115", data)
except ValueError as e:
    log.error("Vault write failed for %s: %s", data.get("symbol"), e)
```

---

## Questions / Changes

All interface changes (new fields, new schema keys, new output folders) are made in P_800.
Do not modify `vault_interface.py` or `schemas.py` from a calling project.
Raise the change request in a P_800 session.
