# CLAUDE.md — P_020 AJZ Strategies Performance Analysis System

Inherits hub-level rules from `AI-Agent-Learning-Hub/CLAUDE.md`. This file adds P_020-specific context.

---

## Canonical Paths

| Reference | Path |
|---|---|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem` |
| SQLite DB | `...\data\database\P_020_trades.db` |
| Python scripts | `...\python\database\` |
| Domain layer | `...\python\database\domain\` |
| Infrastructure layer | `...\python\database\infrastructure\` |
| Application layer | `...\python\database\application\` |
| API pulls | `...\data\api_pulls\live\` |
| TOS exports (paper) | `...\data\tos_exports\paper\` |
| Last run tracker | `...\data\api_pulls\P_020_last_run.json` |
| Schwab config | `...\config\P_020_schwab_config.json` |
| Weekly runner | `...\P_020_Weekly_Update.bat` |
| Options Log | `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx` |
| Stock Log | `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx` |
| Tracker Dashboard | `D:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx` |

**Never reconstruct paths from memory. Copy from this table.**

OneDrive path: `Path(os.environ["OneDrive"])` — never hardcode drive letter.

---

## Run a Script

```powershell
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\database\application\paper_import.py" --commit
```

Always redirect stderr or errors are silent:
```powershell
& "C:\Users\Trader\.conda\envs\p140\python.exe" script.py > out.txt 2> err.txt
```

---

## Valid Trading Systems

Only these values are valid for the `system` column. Never use anything else. Never leave it empty.

`P_115` · `P_116` · `P_117` · `P_118` · `P_910` · `P_920` · `SNT` · `Day` · `TOS_Import`

`TOS_Import` = unmatched fallthrough only.

---

## Database Rules

- Scope: AJZ account (...6348), Jan 1 2026 forward
- Pre-2026 data (Oct 2024–Dec 2025, 324 rows): leave alone unless Tony says otherwise
- Dedup: `schwab_transaction_id` for Schwab pulls; `(account_id, symbol, date, entry_price, source)` for paper
- Never silently drop orphaned sells — flag in audit log
- All reporting queries use `v_trade_summary` view, not raw `trades` table
- Tag columns: `trades.reason` (WHY) and `trades.signal_strength` (SIG) — TEXT, nullable

---

## ThinkLog Tag Format

Tags live in the TOS ThinkLog CSV export — NOT in the Account Statement CSV (order comments are stripped on export).

```
MMDD: [WHY] [SIG] free text
```

TOS ThinkLog CSV is 4-line blocks separated by blank lines:
```
HEADER LINE
M/D/YY HH:MM:SS
BODY (free text, first line contains tags)
Symbol: XXX
```

Parser joins to trades on Symbol + Date. Vocabulary is **open** — never validate WHY/SIG against a closed list.

---

## Bugs Fixed — Never Re-Introduce

| Bug | Fix |
|---|---|
| Exit matching by `underlying_symbol` only — 2025 exits attached to 2026 positions | Key by `full_symbol`, enforce `exit_date >= entry_date`, FIFO consume |
| SNT missing from `_VALID_SYSTEMS` — silently fell through to TOS_Import | SNT is in `_VALID_SYSTEMS` |
| Tracker matcher returning first match, not closest date | Use closest-date match |
| `schwab_balance_pull.py` reading wrong config | Use `get_client()` from Token Manager with `get_account_hash(last4)` |
| ThinkLog parser validating against closed vocabulary | Parser accepts any tag string |
| Assumed order comments survive TOS CSV export — they don't | Tags are ThinkLog-only |

---

## Key Architecture Notes

- Tracker `Traded` column must NOT gate matching — the trade file itself is proof of execution
- Matching uses ±3-day date window, not exact date only
- `TrackerLookup.get()` tries exact date, then walks ±1/2/3 days
- Config key is `DATABASE_FILE` (not `DB_PATH`)
- Python path depth from `python\database\`: use `Path(__file__).resolve().parents[2]` for project root

---

*Last updated: 2026-06-18*
