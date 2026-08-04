# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What P_115 Is

P_115 is a systematic swing trading strategy that produces BUY / ASYM / PASS verdicts using a multi-tier scoring model (FundamentalsTier + AnalysisTier + CandleTier + SetupScore). It feeds trade signals downstream to P_400 (order management) via the P_800 vault interface.

Two distinct Python entry points exist:

- **Signal emitter** (`python/cli.py`) — emits a single SIGNAL_V2 packet for one trade thesis.
- **Tracker writer** (`python/tracker_writer.py`) — bulk-exports all rows from the Excel tracker to the Obsidian vault.

## Running the Code

```powershell
# Emit one signal (from python/ folder)
"C:\Users\Trader\.conda\envs\p140\python.exe" cli.py `
  --symbol AMTM --session-date 2026-06-03 `
  --timestamp 2026-06-03T14:23:00Z --strategy dip_buy `
  --entry 47.50 --stop 45.75 --target 52.00 `
  --horizon "3-5 days" --confidence HIGH `
  --close 47.75 --volume 1850000 `
  --rationale "Dip into 20-day MA after earnings" `
  --timeframe 1D --source-link "TradeOrderManagement/P_115/x.md" `
  --atm 1.85

# Bulk-export tracker to vault
python\run_tracker_writer.bat
# or directly:
"C:\Users\Trader\.conda\envs\p140\python.exe" python\tracker_writer.py
```

No tests exist yet — validation is done by running the emitter and confirming the written vault file.

## Architecture

```
cli.py
  └─ application/emit_signal.py        # orchestration only; owns no I/O
       ├─ domain/signal_builder.py     # pure dict construction; no I/O
       ├─ config.py                    # all constants/paths/enums
       └─ shared_resources.python_utils.vault_interface.write_to_vault()
                                       # P_800 owns all Obsidian file I/O

tracker_writer.py                      # standalone; reads Excel, calls write_to_vault()
```

**Key design rule:** P_115 never writes files directly. All vault I/O goes through `shared_resources.python_utils.vault_interface.write_to_vault(schema_name, data, overwrite)`. The `VAULT_SCHEMA` constant in `config.py` (`"SIGNAL_V2"`) is the authoritative schema name passed to that function.

**Signal packet flow:** `cli.py` args → `emit_signal()` computes `atr_adjusted_stop` (entry − 1×ATR) → `build_record()` assembles a plain dict → `write_to_vault()` writes to `trading_journal/TradeOrderManagement/signals/`.

**`schemas.py` status:** Contains legacy `P400SignalRecord` Pydantic models from v1.0. The active path (`signal_builder.py`) returns a plain dict that matches the SIGNAL_V2 schema directly — `schemas.py` is not used in the current emit path.

## Signal Fields

| Field | Notes |
|---|---|
| `confidence_level` | `HIGH` / `MEDIUM` / `LOW` only |
| `strategy` | `dip_buy`, `breakout`, `mean_reversion`, `support_bounce` |
| `signal_horizon` | Format: `"3-5 days"` or `"1-2 weeks"` |
| `symbol` | Uppercase, 1–6 chars, matches `^[A-Z][A-Z0-9.]{0,5}$` |
| `atr_adjusted_stop` | Computed automatically: `entry - atm_at_signal` |
| `intelliscan_support_1/2` | Optional structural stops; passed through to P_400 gate |
| `position_size` | Always `0` from P_115; P_400 sets final sizing |

## Data Files

- **Tracker:** `data/P_115_TrackerDashboard_V3.xlsx` — 27-column locked schema; do not alter column names.
- **TOS scripts:** `tos_scripts/` — ThinkScript (`.ts`) chart studies; not Python.
- **`config.py` has two `TRACKER_PATH` / `VAULT_SCHEMA` constants** — `tracker_writer.py` imports `TRACKER_PATH`, `COLUMN_MAP`, `REQUIRED_FIELDS`, and `WRITTEN_BY` from `config.py`. If those are missing, `tracker_writer.py` will fail on import.

## Session Initialization (Claude Desktop only)

At the start of any P_115 trading session, trigger the SIP by typing `INIT` or `P_115 INIT`. The full sequence is in `docs/SESSION_INITIALIZATION_PROMPT.md` (v3.4). It reads `P_010_RiskConfig.json` for current posture and `P_000_Account_Parameters_Current.md` for account parameters. Posture **must** be re-read fresh before every signal emission and before writing MarketDirection. P_115 performs NO position sizing -- STEP 2 is emit-only as of arch v1.3 (2026-07-24); P_400 owns sizing, R:R, options gates, and order formatting.

## Documentation Protocol

New content goes into `docs/P_115_System_Architecture.v1.0.md` first. Only create a separate file if the content exceeds one page, changes frequently, or is shared across projects. When creating a separate file, add a reference link in the architecture doc and name it `P_115_[Topic].v[X.X].md`.
