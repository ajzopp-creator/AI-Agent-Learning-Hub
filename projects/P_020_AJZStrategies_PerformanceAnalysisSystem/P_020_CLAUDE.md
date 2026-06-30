# CLAUDE.md — P_020 Project Memory
# Save to: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\CLAUDE.md
# Layers ON TOP of global C:\Users\Trader\.claude\CLAUDE.md. Project-specific only.
# AJZ Strategies Performance Analysis System.

## Folder Name — copy verbatim, never type from memory

RIGHT: P_020_AJZStrategies_PerformanceAnalysisSystem
WRONG: P_020_AJZStrategiesPerformanceAnalysisSystem
(Underscore between AJZStrategies and PerformanceAnalysisSystem.)

## Canonical Paths — use exactly, never reconstruct

Project root: ...\projects\P_020_AJZStrategies_PerformanceAnalysisSystem
- Python layers: python\database\{domain,infrastructure,application}\
- SQLite DB (verbatim):
  ...\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db
- API pulls: data\api_pulls\live\   | Paper exports: data\tos_exports\paper\
- Audit logs: audit_logs\           | Schwab config: config\P_020_schwab_config.json
- Last run tracker: data\api_pulls\P_020_last_run.json
- Weekly runner: P_020_Weekly_Update.bat   | Desktop launcher: Launch_P_020.bat

- Options Log (live): D:\OneDrive\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx
- Stock Log (live):   D:\OneDrive\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx
- Tracker Dashboard:  D:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx
  (Tony's file — he maintains it. Treat as read-only unless Tony says otherwise.)

## Valid `system` Column Values — ONLY these, never empty

P_115 Buy The Dip | P_116 Options Income Launchpad | P_117 External recs |
P_118 Eddie Z Breakouts | P_910 | P_920 | SNT Sunday Night Trader |
Day day trades | TOS_Import default for unmatched only.

## Database Rules

- Active scope: AJZ account (...6348), Jan 1 2026 forward.
- Pre-2026: 324 TOS_Import trades (Oct 2024-Dec 2025) — leave alone unless told.
- account_id: AJZ live contains '6348'; Paper = 'PAPER'; Inherited IRA contains '9885' (not traded).
- Dedup: schwab_transaction_id for Schwab; (account_id,symbol,date,entry_price,source) for paper.
- Orphaned sells: flag in audit log, never silently drop.
- Tables: trades, exits, accounts, systems, account_balances. Report via view v_trade_summary.
- Tag columns: trades.reason and trades.signal_strength (TEXT, indexed, nullable).

## ThinkLog Tags

- Format, first line of ThinkLog body: MMDD: [WHY] [SIG] free text
- Tags live in the TOS ThinkLog CSV, NOT the order comment field — TOS does
  not pass order comments into the Account Statement CSV (verified 2026-04-28).
  Join trades to ThinkLog on Symbol + Date.
- Vocabulary is OPEN. The parser must accept any [WHY]/[SIG] string — never
  validate against a closed list. Canonical vocab: SESSION_INITIALIZATION_PROMPT_v2_7.md.
- Tag parsing runs only in paper_import.py (account_id='PAPER'). Live trades leave tags NULL.

## Bugs Already Fixed — never re-introduce

- Exit matching by underlying_symbol only -> key by full_symbol, enforce
  exit_date >= entry_date, FIFO consume with a consumed-set.
- SNT missing from _VALID_SYSTEMS -> SNT is valid, do not normalize to TOS_Import.
- Tracker matcher first-match -> use closest-date match (same symbol, different systems/dates).
- schwab_balance_pull reading wrong config -> use get_client() from
  P_020_Schwab_Token_Manager with get_account_hash(last4).
- Parser validating closed vocab -> accept any tag string.
- Assuming Account Statement CSV keeps order comments -> it does not.

## Schwab Auth

- Manual flow only: schwab.auth.client_from_manual_flow().
- Portal redirect is https://127.0.0.1 with NO port — let client_from_manual_flow()
  own the entire auth URL, or CSRF state mismatches.
- Auth codes expire ~30s. Credentials cache: credentials_cache.json.
- Token Manager: AI-Agent-Learning-Hub\integrations\schwab_api\ — shared, never project-local.

## Running Code in the Code Tab (differs from Desktop)

- You have a real shell here — run python directly:
  C:\Users\Trader\.conda\envs\p140\python.exe <script.py>
  No Windows-MCP, no stdout/stderr redirect dance, no Start-Sleep needed.
- Python patch/edit scripts: write a .py file and run it. Never use PowerShell
  string replacement on source — it corrupts UTF-8.
- Batch (.bat) files: write as ASCII, not UTF-8.
- Filenames: underscores only, never spaces.

## Roles

- Tony: PM, trading domain expert, tester, ThinkLog vocab owner, business calls.
- Claude: all Python, debugging, file writes (except the F: drive Tracker Dashboard).

## Not Done Yet

SNVXX money-market filter in ingest | schwab_positions.py (open positions) |
Excel Power Query view layer | six AI-review stats CSVs | HTML perf dashboard
(in progress) | wire HTML gen into analyze command | token-expiry detection in
weekly bat | v_trade_summary exposing reason + signal_strength.
