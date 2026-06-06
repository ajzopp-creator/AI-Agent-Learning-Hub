---
name: p020-project-context
description: >
  P_020 AJZ Strategies Performance Analysis System — project-specific operating rules,
  critical paths, and anti-patterns. Load this skill at the start of ANY session
  involving P_020 work. Triggers on any reference to P_020, trade database, Schwab
  pull, weekly update, tracker matching, or AJZ Strategies trading automation.
  Always read this BEFORE writing any code or referencing any file path for this project.
---
# Version 1.1  
# date 2026-05-01 : Added P_300 
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
| CLI entry point | `...\python\database\P_020_Trade_Manager.py` |
| Schwab Token Manager | `...\python\api\P_020_Schwab_Token_Manager.py` |
| All DB infrastructure scripts | `...\python\database\infrastructure\` |
| SQLite database | `...\data\database\P_020_trades.db` |
| Project config (app_key, accounts) | `...\config\P_020_schwab_config.json` |
| Schwab token file (schwab-py) | `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\schwab_api\credentials\P_020_schwab_config.json` |
| Schwab credentials cache | `C:\Users\Trader\AI-Agent-Learning-Hub\integrations\schwab_api\credentials\credentials_cache.json` |
| API pulls (AJZ live) | `...\data\api_pulls\ajz_strategies\` |
| Audit logs | `...\audit_logs\` |
| Python executable | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Options Log (live) | `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx` |
| Stock Log (live) | `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx` |
| Tracker Dashboard | `F:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx` |
| Last run tracker | `...\data\api_pulls\P_020_last_run.json` |
| Weekly batch runner | `...\P_020_Weekly_Update.bat` |
| Desktop launcher | `Launch_P_020.bat` on Desktop |

**Full DB path (use verbatim):**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db
```

---

## Schwab Path Chain — Read This Before Writing Any Schwab Code

There are TWO separate config concepts. Never confuse them:

| File | Location | Contains |
|---|---|---|
| Project config | `...\config\P_020_schwab_config.json` | `app_key`, `app_secret`, account definitions (last4, label, boa) |
| Schwab token file | `integrations\schwab_api\credentials\P_020_schwab_config.json` | OAuth token (managed by schwab-py, auto-refreshed) |
| Credentials cache | `integrations\schwab_api\credentials\credentials_cache.json` | `app_key` + `app_secret` used by Token Manager |

**The chain for all infrastructure scripts:**
```
schwab_balance_pull.py / schwab_positions.py / schwab_mapper.py
    |
    | _API_DIR = Path(__file__).resolve().parents[2] / "api"
    | (resolves to: python\api\ — for scripts 2 levels deep in python\database\infrastructure\)
    v
python\api\P_020_Schwab_Token_Manager.py
    |
    | reads from: integrations\schwab_api\credentials\
    v
Schwab API
```

**Rule for diagnostic scripts:** Never hardcode the Token Manager path. Always construct it relative to the project root:
```python
_PROJECT_ROOT = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem')
_API_DIR = _PROJECT_ROOT / 'python' / 'api'
if str(_API_DIR) not in sys.path:
    sys.path.insert(0, str(_API_DIR))
from P_020_Schwab_Token_Manager import get_client
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
| P_300 | Vantage Point Pattern Recognition |
| P_910 | Additional system |
| P_920 | Additional system |
| SNT | Sunday Night Trader / BigTrends email subscription |
| Day | Day trades |
| TOS_Import | Default — unmatched trades only |

Never use any value outside this list. Never return an empty system column.

---

## Database Rules

- **Scope:** AJZ account (...6348), Jan 1, 2026 forward — this is the active trading scope
- **Pre-2026 data:** TOS_Import trades exist from Oct 2024 – Dec 2025. Leave them alone unless Tony explicitly says otherwise.
- **Dedup:** Use `schwab_transaction_id` — never insert a duplicate
- **Orphaned sells:** Flag in audit log, never silently drop
- **account_id formats:** AJZ live = contains '6348'; Paper = 'PAPER'
- **Tables:** `trades`, `exits`, `accounts`, `systems`, `account_balances`
- **View:** `v_trade_summary` — use for all reporting queries

---

## Windows-MCP Reliable Patterns

**Write script to C:\Temp then run — most reliable pattern:**
```
Use FileSystem MCP to write script to C:\Temp\script.py
Then give Tony this CMD one-liner:
C:\Users\Trader\.conda\envs\p140\python.exe C:\Temp\script.py
```

**PowerShell with output capture (when MCP is responsive):**
```powershell
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
- Windows-MCP PowerShell consistently times out on Python execution — always use FileSystem write + CMD one-liner pattern instead

---

## Code Delivery Rules

- Always write scripts directly via FileSystem MCP — never paste code blocks for Tony to copy manually
- Windows-MCP times out on Python — use FileSystem MCP to write the file, then provide a single CMD one-liner
- Complete code blocks only — no partial snippets
- Minimal comments
- Brief high-level explanation BEFORE the code
- Test command + expected output AFTER the code
- Never use spaces in filenames — underscores only
- All code targets the p140 conda environment

---

## Bugs Already Fixed — Never Re-Introduce

| Bug | Fix |
|---|---|
| `schwab_mapper.py` exit matching by `underlying_symbol` only — caused 2025 exits attaching to 2026 positions | Key by `full_symbol`, enforce `exit_date >= entry_date`, consume FIFO, use consumed-set |
| `tracker_reader.py` — SNT not in `_VALID_SYSTEMS` caused silent normalization to TOS_Import | SNT added to `_VALID_SYSTEMS` |
| Tracker matcher returning first-match instead of closest-date match | Use closest-date match — same symbol can appear from different systems on different dates |
| `schwab_balance_pull.py` reading from wrong config file | Use `get_client()` from `P_020_Schwab_Token_Manager` with `get_account_hash(last4)` lookup |
| Diagnostic scripts using hardcoded wrong Token Manager path | Always construct from project root using `_PROJECT_ROOT / 'python' / 'api'` pattern |
| `schwab_positions.py` unrealized P&L always 0.00 | Schwab API has no `unrealizedProfitLoss` field — use `longOpenProfitLoss` / `shortOpenProfitLoss` — fixed 2026-04-07 |

---

## Schwab Auth Rules

- Token Manager lives at: `python\api\P_020_Schwab_Token_Manager.py` — INSIDE the project
- Credentials (token + cache) live at: `integrations\schwab_api\credentials\` — HUB level shared infrastructure
- Schwab portal callback URL: `https://127.0.0.1` (no port)
- Authorization codes expire ~30 seconds — copy-paste must be fast
- Re-auth required when token expires: run `P_020_Schwab_Auth.bat auth` from `integrations\schwab_api\`

---

## Weekly Workflow (Current State)

`P_020_Weekly_Update.bat` cd's to `python\database\` and chains:
1. `P_020_Trade_Manager.py balance --account AJZ` — pulls account balance
2. `P_020_Trade_Manager.py import --account AJZ` — imports trades from Schwab API to SQLite
3. `P_020_Trade_Manager.py analyze --account AJZ6348` — generates analysis CSVs

One-click Monday morning. Zero manual steps for 2026 AJZ data.

---

## What Is NOT Done Yet

- Phase 3D: Excel Power Query view layer
- Phase 3E: Stats export CSVs for AI analysis (summary_by_system, equity_curve, r_distribution, monthly_summary, open_positions, drawdown)
- Phase 4: HTML performance dashboard

---

## Tony's Role vs Claude's Role

- Tony: Project manager, trading domain expert, tester, business decisions
- Claude: All Python implementation, debugging, technical documentation, file writes
- Files (except Tracker Dashboard): Claude's responsibility to write directly to machine via MCP
- Tracker Dashboard: Tony's file on F: drive — Claude cannot write it

---

*Project: P_020 AJZ Strategies Performance Analysis System*
*Skill version: 1.2*
*Updated: 2026-04-07*
*Maintained by: Anthony Zoppi / Claude*
