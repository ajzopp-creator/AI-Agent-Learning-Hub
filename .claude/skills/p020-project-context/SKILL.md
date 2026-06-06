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
## AJZ Strategies Performance Analysis System

---

## Purpose

Lock in the critical paths, rules, and patterns for P_020 so Claude never:
- Uses the wrong folder name or DB path
- Invents paths from memory instead of reading them here
- Re-introduces bugs that have already been fixed
- Gives Tony a code block to run manually when Windows-MCP can run it directly

---

## CRITICAL: Folder Name (Gets Wrong Every Session)

The correct project folder name is:

```
P_020_AJZStrategies_PerformanceAnalysisSystem
```

**Note the underscore between AJZStrategies and PerformanceAnalysisSystem.**

WRONG: `P_020_AJZStrategiesPerformanceAnalysisSystem`
RIGHT: `P_020_AJZStrategies_PerformanceAnalysisSystem`

Never type this from memory. Always copy from this file.

---

## Canonical Path Registry

Use these exact paths. Never guess, never reconstruct from memory.

| Reference | Path |
|---|---|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem` |
| Python scripts | `...\python\database\` |
| Domain layer | `...\python\database\domain\` |
| Infrastructure layer | `...\python\database\infrastructure\` |
| Application layer | `...\python\database\application\` |
| SQLite database | `...\data\database\P_020_trades.db` |
| API pulls | `...\data\api_pulls\live\` |
| Audit logs | `...\audit_logs\` |
| Python executable | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Options Log (live) | `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx` |
| Stock Log (live) | `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx` |
| Tracker Dashboard | `F:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx` |
| Schwab config | `...\config\P_020_schwab_config.json` |
| Last run tracker | `...\data\api_pulls\P_020_last_run.json` |
| Weekly batch runner | `...\P_020_Weekly_Update.bat` |
| Desktop launcher | `Launch_P_020.bat` on Desktop |
| ThinkLog parser | `...\python\database\domain\thinklog_parser.py` |
| Session init prompt | `SESSION_INITIALIZATION_PROMPT_v2_7.md` (vocabulary source of truth) |

**Full DB path (use verbatim):**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db
```

---

## Valid Trading Systems

These are the ONLY valid values for the `system` column in the `trades` table:

| System ID | Description |
|---|---|
| P_115 | Buy The Dip |
| P_116 | Options Income Launchpad |
| P_117 | External recommendations |
| P_118 | Eddie Z Breakouts |
| P_910 | Additional system |
| P_920 | Additional system |
| SNT | Sunday Night Trader / BigTrends email subscription |
| Day | Day trades |
| TOS_Import | Default — unmatched trades only |

Never use any value outside this list. Never return an empty system column.

---

## ThinkLog Tag Format

Every ThinkLog note starts with a one-line tag header:

```
MMDD: [WHY] [SIG] free text
```

- `MMDD` — month/day of trade entry (e.g. `0421`)
- `[WHY]` — reason code (e.g. `[SNT]`, `[BTD]`, `[IFFY]`, `[LEARN]`, `[CROWDED]`)
- `[SIG]` — signal strength code (e.g. `[A]`, `[B]`, `[C]`, `[X]`)
- `free text` — everything after the last bracket is free-form notes

**Vocabulary is open.** The parser does NOT validate `WHY` or `SIG` against a closed list. The canonical vocabulary lives in `SESSION_INITIALIZATION_PROMPT_v2_7.md` and can evolve without code changes. Tony defines and maintains the vocabulary; Claude reads it.

**Parser behavior (`domain/thinklog_parser.py`):**
- Extracts `date_token`, `reason`, `signal_strength`, `notes`, `raw`
- Returns `None` for any missing field — never raises on malformed input
- Normalizes tag values to uppercase
- Backward compatible: notes without tags parse cleanly with `None` tags and full line as `notes`

**DB storage (`trades` table):**
- `reason` TEXT — maps to `[WHY]` bracket
- `signal_strength` TEXT — maps to `[SIG]` bracket
- `notes` TEXT — free-text portion of the line; appends rather than overwrites

**Ingestion scope:**
- ThinkLog tag parsing runs only inside `paper_import.py` — paper account (`account_id='PAPER'`)
- Live account trades (`account_id` contains '6348') leave tag columns NULL

**Filtering pattern:**
```sql
SELECT system, reason, COUNT(*), AVG(realized_pnl)
FROM v_trade_summary
WHERE account_id = 'PAPER' AND reason IS NOT NULL
GROUP BY system, reason;
```

---

## Database Rules

- **Scope:** AJZ account (...6348), Jan 1, 2026 forward — this is the active trading scope
- **Pre-2026 data:** 324 TOS_Import trades exist from Oct 2024 – Dec 2025. Leave them alone unless Tony explicitly says otherwise.
- **Dedup:** Use `schwab_transaction_id` — never insert a duplicate
- **Orphaned sells:** Flag in audit log, never silently drop
- **account_id formats:** AJZ live = contains '6348'; Paper = 'PAPER'; Inherited IRA = contains '9885' (not traded)
- **Tables:** `trades`, `exits`, `accounts`, `systems`, `account_balances`
- **View:** `v_trade_summary` — use for all reporting queries
- **Tag columns:** `trades.reason` and `trades.signal_strength` (added 2026-04-21 migration) — both TEXT, indexed, nullable

---

## Windows-MCP Reliable Patterns

**Multi-line Python script:**
```powershell
$script = @"
[python code here]
"@
$script | Out-File -FilePath "C:\Temp\script.py" -Encoding UTF8
Start-Process -FilePath "C:\Users\Trader\.conda\envs\p140\python.exe" -ArgumentList "C:\Temp\script.py" -Wait -NoNewWindow -RedirectStandardOutput "C:\Temp\out.txt" -RedirectStandardError "C:\Temp\err.txt"
Start-Sleep -Seconds 3
Get-Content "C:\Temp\out.txt"
Get-Content "C:\Temp\err.txt"
```

**Key rules:**
- Always redirect both stdout AND stderr — errors are silent without `-RedirectStandardError`
- Always `Start-Sleep 3` before `Get-Content` or output files appear empty
- Python patch scripts: use a Python script, NOT PowerShell string replacement (PowerShell corrupts UTF-8)
- Batch files: `-Encoding ASCII` not UTF8
- Tracker Dashboard (F: drive): NOT accessible via filesystem MCP — Windows-MCP PowerShell only
- Obsidian ThinkLog vault: access via `obsidian` MCP tools, not raw filesystem

---

## Code Delivery Rules

- Always attempt to run code via Windows-MCP before giving Tony a block to paste
- If Windows-MCP is unresponsive, give Tony a single CMD one-liner with the full path spelled out — never a multi-line code block to paste manually
- Complete code blocks only — no partial snippets
- Minimal comments
- Brief high-level explanation BEFORE the code
- Test command + expected output AFTER the code
- Never use spaces in filenames — underscores only
- All code targets the p140 conda environment
- Max 300 lines per file, 50 lines per function — enforced by Hub standard

---

## Bugs Already Fixed — Never Re-Introduce

These are documented in Section 6 of the System Documentation. Do NOT repeat them.

| Bug | Fix |
|---|---|
| `schwab_mapper.py` exit matching by `underlying_symbol` only — caused 2025 exits attaching to 2026 positions | Key by `full_symbol`, enforce `exit_date >= entry_date`, consume FIFO, use consumed-set |
| `tracker_reader.py` — SNT not in `_VALID_SYSTEMS` caused silent normalization to TOS_Import | SNT added to `_VALID_SYSTEMS` |
| Tracker matcher returning first-match instead of closest-date match | Use closest-date match — same symbol can appear from different systems on different dates |
| `schwab_balance_pull.py` reading from wrong config file | Use `get_client()` from `P_020_Schwab_Token_Manager` with `get_account_hash(last4)` lookup |
| ThinkLog parser validating against closed vocabulary | Parser MUST accept any tag string — vocabulary is open and evolves separately |

---

## Schwab Auth Rules

- Manual flow required: `schwab.auth.client_from_manual_flow()`
- Schwab portal uses `https://127.0.0.1` without port — conflicts with schwab-py redirect server
- Auth URL must be owned entirely by `client_from_manual_flow()` — building URL separately causes CSRF state mismatch
- Authorization codes expire ~30 seconds — copy-paste must be fast
- Credentials cached in `credentials_cache.json` after first auth
- Token Manager lives at: `AI-Agent-Learning-Hub\integrations\schwab_api\`
- Schwab API is shared infrastructure — never project-specific

---

## Weekly Workflow (Current State)

`P_020_Weekly_Update.bat` chains:
1. `schwab_balance_pull.py` — pulls account balances
2. Import (Schwab API → SQLite)
3. Analyze / export CSVs

One-click Monday morning. Zero manual steps for 2026 AJZ data.

**Paper workflow (starting 2026-04-27 Monday wipe):**
1. Wipe paper account in TOS
2. Export fresh account statement
3. Every paper trade ThinkLog entry uses tag format: `MMDD: [WHY] [SIG] free text`
4. `paper_import.py` parses tags and populates `reason`, `signal_strength`, `notes` in `trades` table
5. Filter paper analysis by reason to compare setups

---

## What Is NOT Done Yet

- SNVXX filter in ingest pipeline (money market sweeps inserting as trades — low urgency)
- Phase 2C: `schwab_positions.py` — open positions + balance snapshot
- Phase 3D: Excel Power Query view layer
- Phase 3E: Stats export CSVs for AI analysis (summary_by_system, equity_curve, r_distribution, monthly_summary, open_positions, drawdown)
- Phase 4: HTML performance dashboard (IN PROGRESS — built against six AI review CSVs)
- Wire HTML generator into `analyze` command for auto-regeneration
- Token expiry detection in `P_020_Weekly_Update.bat`
- `v_trade_summary` view update to expose `reason` and `signal_strength`

---

## Tony's Role vs Claude's Role

- Tony: Project manager, trading domain expert, tester, business decisions, ThinkLog vocabulary definition
- Claude: All Python implementation, debugging, technical documentation, file writes, tag parsing logic
- Files (except Tracker Dashboard): Claude's responsibility to write directly to machine
- Tracker Dashboard: Tony's file on F: drive — Claude cannot write it
- ThinkLog vocabulary: Tony defines in `SESSION_INITIALIZATION_PROMPT_v2_7.md`; parser never validates

---

*Project: P_020 AJZ Strategies Performance Analysis System*
*Skill version: 1.3*
*Created: 2026-03-28*
*Last updated: 2026-04-21 — ThinkLog tag format, open vocabulary, reason + signal_strength columns*
*Maintained by: Anthony Zoppi / Claude*
