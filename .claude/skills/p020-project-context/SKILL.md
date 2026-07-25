---
name: p020-project-context
description: >
  P_020 AJZ Strategies Performance Analysis System — project-specific operating rules,
  critical paths, and anti-patterns. Load this skill at the start of ANY session
  involving P_020 work. Triggers on any reference to P_020, trade database, Schwab
  pull, weekly update, tracker matching, ThinkLog tags, or AJZ Strategies trading
  automation. Always read this BEFORE writing any code or referencing any file path
  for this project.
---

# P_020 Project Context

## CRITICAL: Folder Name

```
P_020_AJZStrategies_PerformanceAnalysisSystem
```
WRONG: `P_020_AJZStrategiesPerformanceAnalysisSystem` (missing underscore before Performance)
Never type from memory. Copy from here.

---

## Canonical Paths

| Reference | Path |
|---|---|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem` |
| SQLite DB | `...\data\database\P_020_trades.db` |
| Domain layer | `...\python\database\domain\` |
| Infrastructure layer | `...\python\database\infrastructure\` |
| Application layer | `...\python\database\application\` |
| TOS exports (paper) | `...\data\tos_exports\paper\` |
| API pulls | `...\data\api_pulls\live\` |
| Last run tracker | `...\data\api_pulls\P_020_last_run.json` |
| Schwab config | `...\config\P_020_schwab_config.json` |
| Schwab token | `...\config\P_020_schwab_token.json` |
| Weekly runner | `...\P_020_Weekly_Update.bat` |
| ThinkLog parser | `...\python\database\domain\thinklog_parser.py` |
| ThinkLog reader | `...\python\database\infrastructure\thinklog_reader.py` |
| Paper import | `...\python\database\application\paper_import.py` |
| Options Log | `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx` |
| Stock Log | `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx` |
| Tracker Dashboard | `F:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx` |
| Vocabulary source | `docs\P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md` Section 9.5 |
| Python exe | `C:\Users\Trader\.conda\envs\p140\python.exe` |

OneDrive: `Path(os.environ["OneDrive"])` — never hardcode drive letter.
Config key: `DATABASE_FILE` (not `DB_PATH`).
Python path depth from `python\database\`: `Path(__file__).resolve().parents[2]` = project root.

---

## Valid Trading Systems

Only these values are valid for `trades.system`. Never empty, never outside this list.

`P_115` · `P_116` · `P_117` · `P_118` · `P_910` · `P_920` · `SNT` · `Day` · `TOS_Import`

`TOS_Import` = unmatched fallthrough only.

---

## ThinkLog Tag Format

Tags live in TOS ThinkLog CSV export — NOT in the Account Statement CSV (order comments are stripped on export, verified 2026-04-28).

```
MMDD: [WHY] [SIG] free text
```

TOS ThinkLog CSV is 4-line blocks separated by blank lines:
```
HEADER LINE
M/D/YY HH:MM:SS
BODY (first line contains tags)
Symbol: XXX
```

Vocabulary is **open** — parser never validates WHY/SIG. Canonical vocabulary: `SESSION_INITIALIZATION_PROMPT_v2_9.md`.
Join to trades on Symbol + Date. Multiple entries for same (symbol, date) concatenated with ` | ` separator (LIFO).

DB columns: `trades.reason` (WHY) · `trades.signal_strength` (SIG) · `trades.notes` (free text) — all TEXT, nullable.
Tag parsing runs only in `paper_import.py` for `account_id='PAPER'`. Live account (...6348) leaves tag columns NULL.

---

## Database Rules

- Scope: AJZ (...6348), Jan 1 2026 forward
- Pre-2026 data (Oct 2024–Dec 2025, 324 rows): leave alone unless Tony says otherwise
- Dedup: `schwab_transaction_id` for Schwab pulls; `(account_id, symbol, date, entry_price, source)` for paper
- Orphaned sells: flag in audit log, never drop silently
- Tracker `Traded` column must NOT gate matching — trade file is proof of execution
- Matching: ±3-day date window; `TrackerLookup.get()` tries exact date then walks ±1/2/3 days
- All reporting queries use `v_trade_summary` view, not raw `trades` table

---

## Bugs Fixed — Never Re-Introduce

| Bug | Fix |
|---|---|
| Exit matching by `underlying_symbol` only → 2025 exits attached to 2026 positions | Key by `full_symbol`, `exit_date >= entry_date`, FIFO consume |
| SNT missing from `_VALID_SYSTEMS` → silent fallthrough to TOS_Import | SNT in `_VALID_SYSTEMS` |
| Tracker matcher first-match instead of closest-date | Closest-date match |
| `schwab_balance_pull.py` reading wrong config | `get_client()` from Token Manager with `get_account_hash(last4)` |
| ThinkLog parser validating closed vocabulary | Parser accepts any tag string |
| Order comments assumed to survive TOS CSV export | They don't — tags are ThinkLog-only |
| SKILL.md claimed hub-level `integrations\schwab_api\` was canonical Token Manager location | It was dead code from an abandoned 3/14/26 plan — folder deleted 6/21/26; real chain is project-level `python\api\` |
| `exit_allocator.py` orphaned exits (entry outside current pull batch, e.g. entry from a prior week) were logged then silently dropped — `schwab_mapper.map_pull_file()` discarded them after the warning | `map_pull_file()` now returns orphans; `import_command._resolve_orphans_against_db()` matches against `db_reader.get_open_trade_for_symbol()` (oldest open/partial trade, FIFO) and attaches via `trade_writer.attach_orphan_exit()` |
| `generate_dashboard.py` headline KPIs (closed count, open count, win rate, expectancy, best/worst) fed the `SYSTEM_ORDER`-filtered/sorted systems list, silently excluding any trade on a system not in the 7-name display list (e.g. TOS_Import) | `compute_kpis()` now takes the unfiltered `raw_systems` list; the filtered/sorted list stays scoped to the per-system breakdown table only |
| `vault_mapper.build_vault_payload()` passed `trade_id` through as raw int -- P_800's `P020Record.trade_id` is `Optional[str]`, every `--commit` write failed Pydantic validation (201/201, 0 files touched, caught before any write) | Cast with a `_to_str()` helper (None-safe, mirrors existing `_to_int()`) before returning the payload |

---

## Vault Export

- `P020_Performance.base` filters on `file.folder contains
  "TradeManagement/P020"` -- a **substring** match, not exact. Any
  archive/cleanup subfolder nested under `TradeManagement/P020`
  still matches and shows stale duplicates in the Base. Archive
  outside that path, e.g. `TradeManagement/_archive/P020_.../`.
- Old filename pattern (`SYMBOL.md`) and new trade_id-disambiguated
  pattern (`SYMBOL_TRADEID.md`, added WO-P800-E3.002) don't collide.
  Re-running `write_to_obsidian.py --commit` after a filename-scheme
  change does not overwrite old-scheme notes -- it leaves them as
  orphaned duplicates. Check for this after any filename_builder.py
  change on P_800's side.

---

## Schwab Auth

- Flow: `schwab.auth.client_from_manual_flow()` — never build URL separately (CSRF mismatch)
- Callback: `https://127.0.0.1` no port
- Codes expire ~30s — paste fast
- Token Manager: `...\python\api\P_020_Schwab_Token_Manager.py` — project-level, this is the real working chain
- Token file: `...\config\P_020_schwab_token.json` (written by `...\python\api\P_020_Schwab_Auth.py`)
- Re-auth: double-click `P_020_Schwab_Auth.bat` (project root) — auto-opens browser, captures callback via UIAutomation, no copy-paste
- `AI-Agent-Learning-Hub\integrations\schwab_api\` does NOT exist — built 3/14/26 as Phase 2A shared-infra plan, abandoned same day when Phase 3 SQLite pivot happened, deleted 6/21/26. Never recreate this path or treat it as canonical if referenced in old chats/docs.

---

## Code Delivery

- Run via Windows-MCP first; fallback = single CMD one-liner with full paths
- Always redirect stderr: `-RedirectStandardError "C:\Temp\err.txt"`
- Always `Start-Sleep 3` before `Get-Content`
- File writes: Python script, never PowerShell string replacement (corrupts UTF-8)
- Tracker Dashboard (F: drive): Windows-MCP PowerShell only — not accessible via filesystem MCP

---

*Skill version: 2.4 | Updated: 2026-07-21 | Added trade_id str-cast bug (WO-P800-E3.002) to bug registry; added Vault Export section (Base folder-filter substring trap, filename-scheme migration leaves orphans)*
