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

OneDrive: call `config.get_onedrive_root()` (reads `HKCU\Environment\OneDrive`
via `winreg` at call time) — never hardcode the drive letter, and never use
`os.environ["OneDrive"]` either. Confirmed live 2026-09-19 (WO-P020-E1.019):
a script launched via `Start-Process` (this project's standard execution
pattern) sees `os.environ.get("OneDrive")` as `None` even though the
registry value is set — standard Windows behavior, a child process only
inherits what its parent had at creation time, and OneDrive's client sets
this key post-logon. The registry is always current regardless of process
lineage; `get_onedrive_root()` reads it directly and falls back to the
last-known `D:\OneDrive` only if that read itself fails.

---

## Run a Script

Two CLI entry points, not one — `cli.py` is auth-only (`--project` flag);
`P_020_Trade_Manager.py` is the real one for `balance`, `positions`,
`init-db`, `verify`, trade-import, and `close-expired-options`. Check which
one before writing a command for Tony to paste (confirmed live 2026-08-20,
WO-P020-E1.016 — `cli.py balance` does not exist).

```powershell
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\database\application\paper_import.py" --commit
```

Always redirect stderr or errors are silent:
```powershell
& "C:\Users\Trader\.conda\envs\p140\python.exe" script.py > out.txt 2> err.txt
```

---

## Valid Trading Systems

Authoritative source is the `systems` table in `P_020_trades.db` (`trades.system`
is an FK to `systems.system_id`) — query `SELECT system_id FROM systems WHERE
active=1` rather than trusting a hardcoded list, which drifts. The list this
file used to carry here (`P_115` / `P_116` / `P_117` / `P_118` / `P_910` /
`P_920` / `SNT` / `Day` / `TOS_Import`) was found stale 2026-08-29 — missing
`P_300` and `P_010`, both live with real trade counts — and removed in favor
of this pointer (matches the same fix already applied in the
p020-project-context skill).

`TOS_Import` = unmatched fallthrough only.

---

## Database Rules

- Scope: AJZ account (...6348), Jan 1 2026 forward
- Pre-2026 data (Oct 2024–Dec 2025, 324 rows): leave alone unless Tony says otherwise
- Dedup: `schwab_transaction_id` for Schwab pulls; `(account_id, symbol, date, entry_price, source)` for paper
- Never silently drop orphaned sells — flag in audit log
- All reporting queries use `v_trade_summary` view, not raw `trades` table
- Tag columns: `trades.reason` (WHY) and `trades.signal_strength` (SIG) — TEXT, nullable
- Expiration columns (WO-P020-E1.018, 2026-09-15): `trades.expiration_date` (DATE) and
  `trades.settlement_price` (REAL) — captured at entry-parse time for options, used by
  `domain/expiration_closer.py` to auto-close 0DTE cash-settled positions that never get
  a closing transaction. Cash-settled roots allowlisted in `config.CASH_SETTLED_OPTION_ROOTS`
  (currently `{"NDXP"}` only — never broadened without Tony's explicit confirmation, an
  equity/ETF option looks identical in Schwab's payload but is assignable, not cash-settled)
- Pydantic models moved out of `schemas.py` (deleted, was over the 300-line cap) into
  `schemas_trade.py` (Account/TradingSystem/Trade/Exit/SpreadLeg/TradeParams),
  `schemas_tracker.py` (TrackerEntry/TrackerLookup), `schemas_ops.py` (LastRunFile/Order) —
  2026-09-19, WO-P020-E1.018 Follow-Up. Import from the specific file, not `schemas`.

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

Full table (17 rows as of 2026-09-19) lives in the p020-project-context skill
— kept there only, not duplicated here, so there's one source of truth instead
of two drifting copies (this table was 6 rows and 11 fixes behind before
2026-09-19). Skim it at session start via the skill; don't re-derive from
memory.

---

## Key Architecture Notes

- Tracker `Traded` column must NOT gate matching — the trade file itself is proof of execution
- Matching uses ±3-day date window, not exact date only
- `TrackerLookup.get()` tries exact date, then walks ±1/2/3 days
- Config key is `DATABASE_FILE` (not `DB_PATH`)
- Python path depth from `python\database\`: use `Path(__file__).resolve().parents[2]` for project root

---

*Last updated: 2026-09-19 -- OneDrive guidance corrected (registry via
get_onedrive_root(), not os.environ, WO-P020-E1.019); CLI entry-point split
noted; Valid Trading Systems pointer replaces a stale hardcoded list;
expiration_date/settlement_price + schemas.py split added to Database
Rules; Bugs Fixed table replaced with a pointer to the skill's fuller,
currently-maintained table. Prior: 2026-06-18.*
