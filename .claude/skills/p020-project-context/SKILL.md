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
| CLI entry points | TWO, not one -- `cli.py` (auth only, `--project` flag)
  vs. `P_020_Trade_Manager.py` (`balance`, `positions`, `init-db`, `verify`,
  trade-import commands -- `cmd_balance()` calls
  `application.account_commands.run_balance_command()`). Confirmed live
  2026-08-20 after handing Tony a `cli.py balance` command that doesn't
  exist (WO-P020-E1.016). Check which one before writing any CLI command
  for Tony to paste.
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

**Known drift, not yet fixed:** this table's Tracker Dashboard path uses `F:\OneDrive\...`
while `config.py`'s `TRACKER_DASHBOARD` constant uses `D:\OneDrive\...`. One of these is
wrong. Flagged 2026-08-09, not yet root-caused — check `os.environ["OneDrive"]` on the
actual machine before trusting either literal.

---

## Valid Trading Systems

Authoritative source is the `systems` table in `P_020_trades.db` (`trades.system`
is an FK to `systems.system_id`) -- query `SELECT system_id FROM systems WHERE
active=1` rather than trusting a hardcoded list here, which drifts. This list
was found stale 2026-08-29 (missing `P_300`, `P_010` -- both live with real
trade counts, confirmed via the table itself, WO-P010-E2.001 follow-up) and
the enumeration was removed in favor of this pointer.

**Known case mismatch (flagged 2026-08-29, not yet fixed):** `systems` table
PK is `Day` (mixed case) but 7 live `trades` rows store `DAY` (all caps). Not
currently enforced (FK doesn't appear active), but would break if
`PRAGMA foreign_keys` were ever turned on.

`TOS_Import` = unmatched fallthrough only.

**Hub-wide Attribution Standard (WO-P000-E22.001, added 2026-09-06).**
Every trade record needs a Signal Source ID (this section) and a new
`confidence_tier` column (CONFIRMED/INFERRED/UNRESOLVED) -- not yet added
to `trades`, tracked in **WO-P000-E24.001** along with a resolver
priority reorder (P_820 override stays on top, unchanged; P_400 vault
cuts over from shadow to live; ThinkLog extends to the live account;
Tracker demoted). Also tracked there: the OIL/P_116 live-data fix from
WO-P000-E23.001's registry cleanup. Registry corrections from that same
cleanup: `P_910`/`P_920` are P_115 buckets (Relative Strength / EOD scan),
not generic systems; `P_110`/`P_105`/`P_120`/`P_210` added to this table
since they previously had no `system_id` at all despite needing one.

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

## System Assignment (API pulls vs. paper)

Live Schwab-API pulls (`account_id=AJZ6348`) do NOT get `system` from the API --
`domain/system_resolver.py` resolves it by priority: (1) vault -- if a P_400/P_115
vault note covers that symbol/date, its system tag wins (`source="vault"`); (2)
tracker -- `TrackerLookup` matches `P_115_118_TrackerDashboard_V2.xlsx` by symbol +
closest date in-window (`source="tracker"`); (3) default fallthrough to `TOS_Import`
(`source="default"`) if neither matches. When vault and tracker both resolve and
disagree, `system_resolver.py` logs it (`agree`/mismatch counters) -- check there
first if a symbol looks mistagged.

Paper trades skip this resolver entirely -- `paper_import.py` reads `system` directly
from the ThinkLog tag at CSV-import time, defaulting to `TOS_Import` if untagged.

IRA9885 also skips this resolver entirely (WO-P020-E1.015, 2026-08-22) --
`application/system_attribution.py`'s `run_full_attribution()` checks
`account_id == 'IRA9885'` and skips `apply_system_names()`, going straight to
ThinkLog override then P_820. No Tracker/vault detour, since neither has
meaningful IRA coverage.

ThinkLog note format for IRA (Tony, 2026-08-22): no traceable system ->
`[INV][SIG] free text` (system=`INV`). Traceable system -> put the real
system in the WHY bracket, `INV` moves to a parenthetical in the free text:
`[P_117][A] (INV) free text` (system=`P_117`, `INV` is context only).
Both are standard two-bracket lines -- no parser change for either form.

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
| SKILL.md Code Delivery said "Always `Start-Sleep 3` before `Get-Content`" -- this is the exact anti-pattern that stalled the relay for the full ~4-min MCP ceiling; contradicted the fix WO-P020-E1.012 landed the same week in the system doc and SIP, but nobody swept this skill file | `Start-Sleep` never goes inside an MCP call; `Get-Content` runs in a separate call, no sleep (WO-P020-E1.012) |
| SKILL.md Schwab Auth said the token file was "written by `python\api\P_020_Schwab_Auth.py`" -- that script was already retired (see `_RETIRED_P_020_Schwab_Auth.py`) in favor of `cli.py auth`, per WO-P020-E1.010 Scope item 4. This skill was never swept when the retirement shipped, so it pointed at dead code | Corrected to `cli.py auth --project ALL`, the shared login module's actual entry point |
| P_020 and P_400 share one Schwab app registration -- separate logins for each project (the design WO-P020-E1.010 originally specified) silently revoke each other's token, confirmed live 2026-08-09. `P_020_Schwab_Auth.bat` still called `--project P_020` alone, which would have kept breaking P_400 every time Tony double-clicked it | Bat updated to `cli.py auth --project ALL` -- one login, propagated to every registered project, verified byte-identical before success is reported (WO-P020-E1.010 SCOPE AMENDMENT) |
| `Bases/P020_Performance.base` filtered on `TradeManagement/P020` -- WO-P800-E3.003 (2026-07-25) renamed the vault namespace hub-wide to `TradeOrderManagement/*`; `TradeManagement` no longer exists at all. Not a substring-overmatch risk as previously documented below -- the path was entirely dead, zero rows returned for 17 days, unnoticed | Path corrected to `TradeOrderManagement/P020` (WO-P400-E6.001, 2026-08-11). Superseded next day, see row below. |
| `Bases/P020_Performance.base`'s entire schema was invalid, not just its path -- `filter:`/`conditions:`/`field:`/`operator:`/`value:`/`conjunction:` are not real Obsidian Bases keys (confirmed against `help.obsidian.md/bases/syntax`). The plugin silently ignored the whole filter block; the base rendered every file in the vault (3,002 results), not just P020's folder, regardless of what path string sat inside the dead filter. The prior day's path fix (row above) edited a block that was never functional. Found live 2026-08-12 (WO-P400-E6.001 follow-up) verifying Scope item 1 by reading the raw file via `obsidian_get_file_contents`, not trusting the rendered UI | Rewritten in real syntax: top-level `filters: {and: [file.inFolder("TradeOrderManagement/P020")]}`, `properties:` block for column display names, `views: [{type: table, order: [...], sort: [{property: close_date, direction: DESC}]}]`. `file.inFolder()` is recursive by design (matches sub-folders), so no separate handling needed for any P020 archive nesting. Live-verified in Obsidian: 3,002 -> 201 results, correctly sorted by `close_date` descending |
| `P_020_AccountParser.bat` invoked `P_020_TOS_Parser_v2.3.py` -- WO-P020-E1.002 (2026-07-26) had already confirmed v2.3 was dead/non-live and v2.4 was the real parser, but the batch runner itself was never swept. v2.3's `match_entries_exits()` recomputes `potential_exits` fresh per entry from the full unfiltered exits list -- no cross-entry consumption tracking -- so two entries opened close together on the same symbol can both attach the *same* SOLD transaction as their exit, double-counting realized P&L. Confirmed via code trace, not runtime (v2.3 is being retired from the runner, not patched) | Bat now calls `P_020_TOS_Parser_v2.4.py`, which replaced entry/exit matching with a single chronological pass over a shared long_book/short_book ledger -- structurally cannot double-count, an exit txn is popped from the book once. Verified: `test_v24_no_sibling_double_exit` (2 sibling entries, only the correct one closes) + `test_accountparser_bat_points_at_v24` (SOURCE guard on the bat file), both in `test_p020_known_bugs.py`. WO-P020-E1.013 |

---

## Vault Export

- `P020_Performance.base` -- as of 2026-08-12 uses real Obsidian Bases syntax
  (`filters: {and: [file.inFolder("TradeOrderManagement/P020")]}`). Prior
  versions of this file used a fabricated schema (`filter:`/`conditions:`/
  `field:`/`operator:`/`value:`) that isn't valid Bases YAML at all -- the
  plugin silently ignored it and rendered the whole vault, regardless of
  what path string sat inside. See Bugs Fixed table above for the full
  incident. `file.inFolder()` is recursive by design, covering any nested
  archive subfolder under the live path automatically -- the old
  substring-overmatch concern doesn't apply to the real function.
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
- Token Manager: `...\python\api\P_020_Schwab_Token_Manager.py` — project-level, this is the real working chain (read-only pre-flight check; does not issue tokens)
- Token file: `...\config\P_020_schwab_token.json` (written by `cli.py auth`, via `shared_resources\python_utils\schwab_auth.run_auth()` -- NOT by the retired `P_020_Schwab_Auth.py`, see `_RETIRED_P_020_Schwab_Auth.py`)
- **P_020 and P_400 share ONE Schwab app registration.** A login for either project revokes the other's token at the registration level, regardless of separate token files (confirmed live 2026-08-09, WO-P020-E1.010). Standard reauth is therefore `cli.py auth --project ALL` -- one browser login, propagated + byte-verified into every registered project's token file. `--project P_020` / `--project P_400` alone are retained for targeted reauth only and will break the other project's token if used without a follow-up ALL.
- Re-auth: double-click `P_020_Schwab_Auth.bat` (project root) -- now runs `--project ALL`. Auto-opens browser, captures callback via UIAutomation, no copy-paste.
- Weekly cadence: reauth once before the Saturday weekly update covers both projects for the documented 7-day refresh-token window -- IF Schwab keeps the refresh token stable across refreshes. Unconfirmed as of 2026-08-09; check by comparing `refresh_token` in both projects' token files after each has refreshed at least once (see WO-P020-E1.010 OPEN section).
- `AI-Agent-Learning-Hub\integrations\schwab_api\` does NOT exist — built 3/14/26 as Phase 2A shared-infra plan, abandoned same day when Phase 3 SQLite pivot happened, deleted 6/21/26. Never recreate this path or treat it as canonical if referenced in old chats/docs.

---

## Code Delivery

- Direct-write tools (`filesystem:write_file`, or `windows-mcp:FileSystem` mode=write
  for append) are the STANDARD path for any file write on Windows -- content passes as a
  tool parameter, never through a PowerShell command string. No sandbox build step, no
  base64, no chunking, no cross-machine hash comparison for the normal case
  (WO-P000-E15.001, 2026-08-09). Validate on Windows: compile with p140 under
  `-W error::SyntaxWarning` before declaring a file good -- syntax-only checking is
  insufficient (unchanged from prior guidance).
- Sandbox-build + base64 + SHA-256-compare is a FALLBACK ONLY, for a payload too large
  for a single tool call. Not the default. If reaching for it, first check whether the
  content simply fits in one `filesystem:write_file` call -- direct write has been proven
  to ~200 lines / 10KB in a single call, which covers nearly this project's entire
  300-line hard limit.
- `Start-Process -WindowStyle Hidden` with `-RedirectStandardOutput`/`-RedirectStandardError` to
  uniquely timestamped files (`$ts = Get-Date -Format "HHmmss"`) — never `Start-Job`, never
  `-NoNewWindow` (WO-P020-E1.012)
- `Get-Content` on the output file in a SEPARATE MCP call. NEVER `Start-Sleep` inside an MCP
  call — it stalls the relay for the full ~4-min ceiling (WO-P020-E1.012)
- Inline `python -c "..."` through the PowerShell MCP relay has stalled the full 4-minute
  ceiling twice (2026-08-09, unrelated calls). `Start-Process` invocations of a script file
  have not shown this failure. Prefer writing a small script file and running it via
  `Start-Process` over an inline `-c` one-liner when a call seems likely to be slow.
- Tracker Dashboard (drive letter TBD, see Canonical Paths note above): Windows-MCP PowerShell only — not accessible via filesystem MCP

---

*Skill version: 2.9 | Updated: 2026-09-06 | Added Hub-wide Attribution
Standard pointer (WO-P000-E22.001) to Valid Trading Systems: new
`confidence_tier` column and resolver reorder tracked in WO-P000-E24.001;
OIL/P_116 live-data fix tracked there too, inherited from WO-P000-E23.001's
registry cleanup. Registry corrections folded in from that same session:
P_910/P_920 are P_115 buckets (Relative Strength/EOD scan), not generic
systems; P_110/P_105/P_120/P_210 added to db_seeder.py's systems seed list
and both VALID_SYSTEMS sets, having previously had no system_id at all.
Prior: v2.8 (2026-08-12) | `Bases/P020_Performance.base` was
found to use an entirely fabricated Bases schema, not just a stale path --
`filter:`/`conditions:`/`field:`/`operator:` are not real Obsidian Bases keys,
so the filter block was silently ignored by the plugin regardless of the path
string inside it (yesterday's WO-P400-E6.001 path fix never actually took
effect). Rewritten in real syntax (`filters:`/`file.inFolder()`), live-verified
3,002 -> 201 results. Vault Export section and Bugs table corrected; added
System Assignment section (vault -> tracker -> TOS_Import default priority via
`system_resolver.py`, not documented anywhere prior). Prior: v2.7 (2026-08-11)
Bases path corrected to `TradeOrderManagement/P020` (WO-P400-E6.001); new Bugs
table row. Prior: v2.6 (2026-08-09) Schwab Auth section corrected: token file
is written by `cli.py auth` (retired script was stale info, not just a stale caller);
documented the shared-app-registration finding and `--project ALL` as the standard
reauth path; `P_020_Schwab_Auth.bat` updated to match (WO-P020-E1.010 SCOPE AMENDMENT).
Code Delivery rewritten to name direct-write tools as the standard transport, sandbox
+base64 demoted to oversized-payload fallback (WO-P000-E15.001). Added inline `python -c`
relay-stall observation. Flagged unresolved F:/D: drive-letter mismatch in Tracker
Dashboard path. Two new Bugs Fixed entries. Prior: v2.5 (2026-08-09) fixed stale
Start-Sleep line; v2.4 (2026-07-21) added trade_id str-cast bug, Vault Export section.*
