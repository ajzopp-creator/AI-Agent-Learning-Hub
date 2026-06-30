# P_020 AJZ Strategies Performance Analysis System — Master System Documentation
**Project ID:** P_020
**Version:** 2.0
**Last Updated:** 2026-03-14
**Maintained By:** Anthony Zoppi
**Status:** Active — Phase 3 (SQLite Data Layer)

---

## DOCUMENTATION DECISION PROTOCOL

### The Golden Rule
Always try to fit new content into this master document first.
Only create a separate file when one of the trigger conditions below is met.

### When to Add Directly to This Document
- Short content (under 1 page)
- Stable content that rarely changes
- Content specific to this project only
- Definitions, parameters, rules, checklists

### When to Create a Separate File
- Content exceeds 1 page of detail
- Updated frequently (e.g., daily/weekly logs)
- Shared or referenced across multiple projects
- Requires its own version history

---

## TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Database Design](#3-database-design)
4. [File Structure](#4-file-structure)
5. [AI Tools & Platforms](#5-ai-tools--platforms)
6. [Requirements](#6-requirements)
7. [Change Log](#7-change-log)
8. [Error Corrections Log](#8-error-corrections-log)
9. [AI Workflows & Processes](#9-ai-workflows--processes)
10. [Testing & Validation](#10-testing--validation)
11. [Daily Operations & Session Management](#11-daily-operations--session-management)
12. [Troubleshooting & Support](#12-troubleshooting--support)
13. [Appendices](#13-appendices)

---

## 1. PROJECT OVERVIEW

### 1.1 Purpose
**Objective:** Automate weekly trading performance tracking for AJZ Strategies LLC — eliminating
manual data entry, ensuring accuracy, and freeing time for golf and fishing.

Trade data flows from the Schwab API into a local SQLite database (single source of truth).
Excel serves as a read-only view layer populated by Power Query. Performance stats are exported
as CSVs for AI-assisted analysis.

**Problem Solved:** A manual 30-minute weekly workflow (export TOS CSV → parse → paste into
Excel → assign system names) replaced with a one-click Monday morning update taking ~3 minutes.

### 1.2 Architecture Evolution

| Version | Approach | Status |
|---|---|---|
| v1 | TOS CSV export → manual Excel paste | Retired |
| v3 | Schwab API → CSV → manual Excel paste | Retired |
| v4 (current) | Schwab API → SQLite → Excel via Power Query | Active |

### 1.3 Scope

**What This System Covers:**
- OAuth 2.0 authentication to Schwab API with auto token refresh
- Trade data retrieval with TRD-type filtering and 10-minute consolidation
- Orphaned transaction detection (sells with no matching buy in pull window)
- Auto-matching trades to system names via Tracker Dashboard lookup
- SQLite as the single source of truth for all trade data
- Excel as a view-only layer connected via Power Query
- Audit log generation for every weekly run
- Stats CSV exports optimized for AI performance review
- Three accounts: live trading (AJZ6348), IRA investing (IRA9885), paper (PAPER)

**What This System Does NOT Cover:**
- Real-time intraday signals or trade execution
- More than 3 partial exits per trade
- Complex corporate actions (splits, mergers)
- P&L calculation — computed in SQLite (exit_pnl, realized_pnl, realized_R)
- IRA options trading — IRA holds stocks and ETFs only

### 1.4 Project Details

| Field | Value |
|---|---|
| Start Date | January 2026 |
| Current Phase | Phase 3A/3B complete — Phase 3C next |
| Python Environment | p140 conda — C:\Users\Trader\.conda\envs\p140\python.exe |
| Project Folder | AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem |
| Database File | data\database\P_020_trades.db |
| Primary AI | Claude.ai (Anthropic) |

### 1.5 Accounts

| account_id | Name | Type | Notes |
|---|---|---|---|
| AJZ6348 | AJZ Strategies LLC | live | Active options + stock trading |
| IRA9885 | AJZ Strategies IRA | invest | Inherited IRA — stocks/ETFs only, 10-year distribution |
| PAPER | Paper Account | paper | Simulation — excluded from real P&L |

**IRA context:** Inherited IRA, 10-year distribution rule. Distribution start year derived
from earliest open_date in trades WHERE account_id = 'IRA9885'. Distribution window = 10 years
(stored in accounts.distribution_years).

### 1.6 Definitions & Acronyms

| Term | Definition |
|---|---|
| P_ | Production prefix — tested, approved, live money |
| D_ | Development prefix — paper trading / sandbox |
| TRD | Trade transaction type in Schwab API — the only type processed |
| Orphaned Transaction | A sell with no matching buy in the current pull window |
| TOS_Import | Default system name when no Tracker Dashboard match found |
| Formula Preservation | Protecting Excel formula columns during import |
| 10-min consolidation | Combining same-symbol buys within 10 minutes into one entry |
| realized_R | (realized_pnl / risk_amount) — risk-adjusted return |
| risk_amount | (entry_price - stop_price) × qty × multiplier, or 1.5% of position if no stop |
| v_trade_summary | SQLite computed view — trades JOIN exits, used by all exports |
| Power Query | Excel feature — connects to CSV exports, replaces manual paste |
| schwab_transaction_id | Schwab's unique transaction ID — used for deduplication |
| p140 | Conda environment standardized for P_020 and P_010 projects |

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Data Flow

```
[Schwab API]           [Tracker Dashboard]     [Account Params JSON]
     |                        |                         |
     └──────────────┬─────────┘──────────────┬──────────┘
                    ▼
          [ingest_pipeline.py]
          ┌─────────────────────────┐
          │  1. TRD filter          │
          │  2. 10-min consolidate  │
          │  3. Orphan detection    │
          │  4. Auto-match system   │
          │  5. Dedup check         │
          └───────────┬─────────────┘
                      │
          ┌───────────▼─────────────┐
          │   P_020_trades.db       │  ← SINGLE SOURCE OF TRUTH
          │   SQLite database       │
          └───────┬─────────┬───────┘
                  │         │
          ┌───────▼──┐  ┌───▼────────────┐
          │ CSV       │  │ Audit log      │
          │ exports   │  │ Weekly_Audit_  │
          └───┬───────┘  │ YYYYMMDD.txt   │
              │          └────────────────┘
     ┌────────┼──────────┐
     ▼        ▼          ▼
  Excel    Excel      AI review
  Options  Stocks     CSVs
  (Power   (Power     (equity,
  Query)   Query)     R-dist...)
```

### 2.2 Core Components

| Component | File | Responsibility |
|---|---|---|
| Authentication | schwab_auth.py | OAuth 2.0 browser flow, token save |
| Token Manager | schwab_token_manager.py | Auto-refresh (30-min access / 7-day refresh) |
| Trade Pull | schwab_trade_pull.py | Pull /transactions, output raw JSON |
| Ingest Pipeline | ingest_pipeline.py | Orchestrate: filter → consolidate → match → write |
| DB Client | db_client.py | SQLite connection, CREATE TABLE, CREATE VIEW |
| DB Seeder | db_seeder.py | Seed accounts (3 rows) and systems (9 rows) |
| DB Writer | db_writer.py | INSERT trades + exits, dedup protection |
| DB Reader | db_reader.py | Query by account, system, date range, status |
| Tracker Reader | tracker_reader.py | Load Tracker Dashboard → symbol+date lookup dict |
| CSV Exporter | csv_exporter.py | Export v_trade_summary → Power Query CSVs |
| Stats Export | stats_export.py | Per-system summary, equity curve, R-dist (Phase 3E) |
| CLI | cli.py | Command-line entry point (init-db, verify, ingest, export) |
| Weekly Runner | P_020_Weekly_Update.bat | One-click full pipeline |

### 2.3 Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Database | SQLite | Local, file-based, no server, works with Python + Excel ODBC |
| Schema style | Normalized (trades + exits) | Supports 1, 2, or 3+ exits without schema changes |
| Excel role | View only via Power Query | Dashboard formulas untouched; no copy/paste ever |
| R calculation default | 1.5% of position (from params) | Applied when no stop price logged |
| Dedup strategy | schwab_transaction_id UNIQUE | Safe to re-run without creating duplicates |
| Stats export | CSV files | Simple, AI-readable, no special tooling |
| Parameters | P_020_Account_Params.json | Business rules editable in Notepad, not hardcoded |
| IRA distribution years | accounts.distribution_years column | Data-driven, not hardcoded |
| IRA distribution start | MIN(open_date) WHERE account_id='IRA9885' | Derived from data |
| Architecture | p140 Hub standard (domain/infra/app) | Consistent with all Hub projects |

---

## 3. DATABASE DESIGN

### 3.1 Schema Overview

**Database file:** `data\database\P_020_trades.db`
**Tables:** accounts, systems, trades, exits
**Views:** v_trade_summary (computed — no stored data)

```
accounts ──────────────┐
  (3 rows)              │  FK: account_id
                        ▼
systems ───────────► trades ◄──────────────────────
  (9 rows)   FK:      (1 row           FK: trade_id
           system    per position)
                        │
                        ▼
                      exits
                    (1–3 rows
                    per trade)
                        │
                        ▼
                  v_trade_summary
                  (computed view —
                  trades JOIN exits)
```

### 3.2 Table: accounts

| Column | Type | Notes |
|---|---|---|
| account_id | TEXT PK | 'AJZ6348', 'IRA9885', 'PAPER' |
| account_name | TEXT | Human-readable name |
| account_type | TEXT | 'live', 'invest', 'paper' |
| broker | TEXT | 'schwab' |
| distribution_years | INTEGER | IRA distribution window — null for non-IRA |
| created_at | DATETIME | Auto |

### 3.3 Table: systems

| Column | Type | Notes |
|---|---|---|
| system_id | TEXT PK | 'P_115' through 'TOS_Import' |
| system_name | TEXT | Human-readable name |
| description | TEXT | Brief description |
| active | INTEGER | 1 = active, 0 = retired |

**Seeded systems:** P_115, P_116, P_117, P_118, P_300, P_910, P_920, Day, TOS_Import

### 3.4 Table: trades

One row per position opened. Primary entity — everything links to this.

| Column | Type | Notes |
|---|---|---|
| trade_id | INTEGER PK AUTO | Surrogate key |
| account_id | TEXT FK | → accounts |
| system | TEXT FK | → systems |
| underlying_symbol | TEXT | 'QBTS', 'AAPL', etc. |
| asset_type | TEXT | 'stock', 'etf', 'call', 'put', 'spread' |
| direction | TEXT | 'long', 'short' |
| open_date | DATE | Entry date |
| open_datetime | DATETIME | Entry datetime (from API) |
| qty | REAL | Shares or contracts |
| entry_price | REAL | Per share or contract |
| stop_price | REAL | For R calculation — null if not set |
| risk_amount | REAL | Computed: (entry-stop)×qty×mult, or 1.5% default |
| total_commissions | REAL | All commissions for full round trip |
| status | TEXT | 'open', 'partial', 'closed' |
| tags | TEXT | Comma-separated labels |
| notes | TEXT | Trade journal / comments |
| source | TEXT | 'schwab_api', 'tos_import', 'manual' |
| schwab_transaction_id | TEXT UNIQUE | Schwab's ID — dedup protection |
| created_at / updated_at | DATETIME | Auto |

### 3.5 Table: exits

One row per exit leg. Normalized — supports unlimited exits without schema changes.

| Column | Type | Notes |
|---|---|---|
| exit_id | INTEGER PK AUTO | Surrogate key |
| trade_id | INTEGER FK | → trades |
| exit_number | INTEGER | 1, 2, or 3 |
| exit_date | DATE | Date of this exit |
| exit_datetime | DATETIME | Datetime if available |
| qty_exited | REAL | Shares/contracts closed at this exit |
| exit_price | REAL | Per share or contract |
| exit_commissions | REAL | Commissions for this exit leg only |
| exit_pnl | REAL | (exit_price − entry_price) × qty_exited × multiplier |
| hold_days | INTEGER | exit_date − open_date |
| created_at | DATETIME | Auto |

**UNIQUE constraint:** (trade_id, exit_number) — prevents duplicate exit entries.

### 3.6 View: v_trade_summary

Computed rollup of trades + exits. This is what all exports and Power Query use.

**Key computed columns:**
- `realized_pnl` — SUM(exit_pnl) across all exits
- `qty_remaining` — qty − SUM(qty_exited)
- `realized_R` — realized_pnl / risk_amount (null if risk_amount = 0)
- `outcome` — 'WIN', 'LOSS', 'SCRATCH', or 'OPEN'
- `exit_1/2/3_price/qty/date/hold_days` — pivoted from exits table for Excel compatibility

### 3.7 Business Parameters

**File:** `config\P_020_Account_Params.json`
**Edit with:** Notepad — no code change required

```json
{
  "default_risk_pct": 0.015,
  "options_multiplier": 100,
  "consolidation_window_minutes": 10,
  "default_system_name": "TOS_Import"
}
```

**Rule:** Nothing is hardcoded. All business parameters come from this file or are derived
from data in the database. Code only hardcodes structural constants (file paths, column names).

---

## 4. FILE STRUCTURE

```
P_020_AJZStrategies_PerformanceAnalysisSystem\
│
├── config\
│   ├── P_020_Account_Params.json          ← Business parameters (edit in Notepad)
│   └── P_020_schwab_config.json           ← Schwab OAuth tokens (gitignored)
│
├── data\
│   ├── database\
│   │   └── P_020_trades.db                ← SINGLE SOURCE OF TRUTH
│   ├── api_pulls\
│   │   ├── live\                          ← Raw JSON from Schwab API
│   │   ├── paper\
│   │   └── P_020_last_run.json            ← Last pull date for incremental updates
│   └── exports\
│       ├── P_020_options_export.csv        ← Excel Power Query source
│       ├── P_020_stocks_export.csv         ← Excel Power Query source
│       └── ai_review\
│           ├── summary_by_system.csv
│           ├── equity_curve.csv
│           ├── r_distribution.csv
│           ├── monthly_summary.csv
│           ├── open_positions.csv
│           └── drawdown.csv
│
├── python\
│   ├── database\                          ← Phase 3 — ACTIVE
│   │   ├── config.py                      ← All paths and constants
│   │   ├── schemas.py                     ← Pydantic models
│   │   ├── cli.py                         ← Command-line entry point
│   │   ├── requirements.txt
│   │   ├── infrastructure\
│   │   │   ├── db_client.py               ← Connection, CREATE TABLE, CREATE VIEW
│   │   │   ├── db_seeder.py               ← Seed accounts and systems
│   │   │   ├── db_writer.py               ← INSERT trades + exits, dedup
│   │   │   ├── db_reader.py               ← Query helpers
│   │   │   ├── tracker_reader.py          ← Tracker Dashboard lookup
│   │   │   └── csv_exporter.py            ← Export to Power Query CSVs
│   │   ├── domain\                        ← Phase 3B — pending
│   │   │   ├── trade_logic.py
│   │   │   └── matcher.py
│   │   └── application\                   ← Phase 3C — pending
│   │       ├── ingest_pipeline.py
│   │       └── stats_export.py
│   ├── schwab_api\                        ← Phase 2 — complete
│   │   └── infrastructure\
│   │       ├── schwab_auth.py
│   │       └── schwab_token_manager.py
│   └── parsers\                           ← ARCHIVED (TOS parser)
│
├── audit_logs\
│   └── P_020_Weekly_Audit_YYYYMMDD.txt
│
├── P_020_Create_Database.bat              ← Phase 3A runner (run once)
├── P_020_Weekly_Update.bat                ← One-click weekly runner (Phase 3C)
│
└── docs\
    └── P_020_MASTER_SYSTEM_DOCUMENTATION_v1_0.md  ← THIS FILE
```

---

## 5. AI TOOLS & PLATFORMS

### 5.1 Tool Stack

| Tool | Role | Notes |
|---|---|---|
| Claude.ai | Development partner — Python, debugging, docs | Pro tier |
| Python | Core automation language | p140 conda env |
| SQLite | Trade data store | File-based, no server required |
| schwab-py | Schwab OAuth + API calls | Install in p140 |
| pandas | Data processing | Already in p140 |
| openpyxl | Tracker Dashboard Excel read | Already in p140 |
| pydantic | Schema validation | v2.x in p140 |
| Excel Power Query | Read-only view layer | Connects to CSV exports |
| ThinkorSwim | Paper account data (D_020 only) | Still used for paper trading |

### 5.2 Claude Behavior Rules

**Claude MUST:**
- Deliver complete, ready-to-run code blocks — no partial snippets
- Explain what the code does at a high level BEFORE showing the code
- Include a test command and expected output after each code block
- Use p140 conda environment path in all Python references
- Follow Hub architecture: config → schemas → domain → infra → application → cli
- Hard limit: 300 lines per file, 50 lines per function
- Fall back to 'TOS_Import' (never error out) when Tracker Dashboard match fails
- Never hardcode business parameters — always load from P_020_Account_Params.json
- Derive IRA distribution start from data, never hardcode year

**Claude MUST NOT:**
- Hardcode any business value that could change (risk %, multiplier, system names)
- Mix live (AJZ6348) and paper (PAPER) data in the same export
- Include IRA (IRA9885) in trading performance stats unless explicitly requested
- Assume the TOS parser approach — it is archived
- Break SQLite dedup protection (schwab_transaction_id UNIQUE constraint)

### 5.3 Prompt Library

**New Session Context Restore:**
```
P_020 AJZ Strategies Performance Analysis System — v4 SQLite architecture.
Current phase: [Phase 2A/2B/3A/3B/3C — fill in].
Last completed: [brief description].
Today's task: [brief description].
Python: p140 conda at C:\Users\Trader\.conda\envs\p140\python.exe
DB: data\database\P_020_trades.db
```

**Code Delivery Standard:**
```
Deliver complete working code block. Minimal comments. High-level explanation first.
Then: test command. Then: expected output. Save path included.
```

---

## 6. REQUIREMENTS

### 6.1 Requirements Matrix

| Req ID | Description | Status | Phase |
|---|---|---|---|
| 020126_01 | Auto-match Tracker Dashboard → System column | ✅ Complete | tracker_reader.py |
| 020207_01 | Excel import with formula preservation | ✅ Superseded | SQLite/Power Query replaces |
| 020221_01 | TRD transaction filter | 🔄 Phase 3C | ingest_pipeline.py |
| 020221_02 | Orphaned transaction detection | 🔄 Phase 3C | ingest_pipeline.py |
| 020221_03 | Consolidated audit log | 🔄 Phase 3C | ingest_pipeline.py |
| 020221_04 | 10-minute buy consolidation | 🔄 Phase 3C | ingest_pipeline.py |
| 020221_05 | Dedup / audit cross-reference | ✅ Handled | schwab_transaction_id UNIQUE |
| 020224_01 | Schwab OAuth auth + token mgmt | ✅ Complete | schwab_auth.py |
| 020224_02 | Schwab trade history pull | 🔄 Phase 2B | schwab_trade_pull.py |
| 020224_03 | Schwab positions + balances | 🔄 Phase 2C | schwab_positions.py |
| 020224_04 | Weekly one-click automation | 🔄 Phase 3C | P_020_Weekly_Update.bat |
| NEW-01 | SQLite canonical schema | ✅ Phase 3A | P_020_trades.db |
| NEW-02 | Python DB infrastructure layer | ✅ Phase 3B | infrastructure\ folder |
| NEW-03 | Schwab → SQLite ingestion pipeline | 🔄 Phase 3C | ingest_pipeline.py |
| NEW-04 | Excel Power Query view layer | 🔄 Phase 3D | csv_exporter.py + Excel |
| NEW-05 | Stats export CSVs for AI analysis | 🔄 Phase 3E | stats_export.py |

---

## 7. CHANGE LOG

### v2.0 — 2026-03-14 (This version)
**Major direction change — SQLite data layer introduced.**

- Retired TOS CSV parser approach entirely (archived, not deleted)
- Retired manual Excel paste workflow
- Introduced SQLite as single source of truth
- Excel demoted to view-only layer via Power Query
- Three accounts defined: AJZ6348 (live), IRA9885 (invest), PAPER (paper)
- IRA distribution_years stored in accounts table — derived from data, not hardcoded
- P_020_Account_Params.json introduced — all business parameters external
- Phase 3A complete: db_client.py, db_seeder.py, cli.py, P_020_Create_Database.bat
- Phase 3B complete: db_writer.py, db_reader.py, tracker_reader.py, csv_exporter.py
- v_trade_summary view built with R calculation, outcome, and pivoted exit columns

### v1.0 — 2026-02-27
- Initial master document — merged from 8 source documents
- Documented TOS parser v2.1 and Excel import workflow
- Schwab API integration roadmap established

### v2.1 (Parser) — 2026-01-31
- CRITICAL FIX: Commission calculation for multiple fills
- Added Exit #2 capture

---

## 8. ERROR CORRECTIONS LOG

*Errors are never deleted — only marked Resolved.*

### Error: Multiple Fill Commission Undercounting
- **Date:** 2026-01-31 | **Severity:** Critical | **Status:** Resolved
- **Wrong:** Parser counted commission once for multi-fill orders (e.g. $1.32 instead of $2.64)
- **Fix:** Sum all commissions per REF # group — released in TOS Parser v2.1
- **Verify:** QBTS trade Jan 2 2026 — entry commission should show $2.64

### Error: Python Environment Corruption
- **Date:** February 2026 | **Severity:** High | **Status:** Resolved
- **Wrong:** Root-level venv approach caused corruption; P_010 and P_020 scripts failed
- **Fix:** Standardized all projects on p140 conda env; ClaudeCleanShutdown.bat registered
- **Verify:** All scripts run without environment errors from p140 path

---


### Error: Exit Matching — Old Exits Attached to Wrong Entries (CRITICAL)
- **Date:** 2026-03-15 | **Severity:** Critical | **Status:** Resolved
- **Wrong:** `schwab_mapper.py _match_exits_to_entries()` keyed exit pool by `underlying_symbol` only with no date guard. 2025 AMD exits were attached to 2026 AMD entry, producing -$28,458 P&L instead of the correct +$626.
- **Root Cause:** No chronological check in exit-to-entry matching. Same symbol traded across multiple years caused cross-year exit contamination.
- **Fix:** Rewrote `_match_exits_to_entries()` — keyed by `full_symbol`, added `exit_date >= entry_date` guard, FIFO consumption, consumed-set dedup. Released 2026-03-15.
- **Verify:** AMD Jan 20 2026: entry $21.34 → exit $27.60 = +$626 WIN (confirmed vs Schwab transaction history)

### Error: SNT System Not Recognized — Normalized to TOS_Import
- **Date:** 2026-03-15 | **Severity:** Medium | **Status:** Resolved
- **Wrong:** `tracker_reader.py _normalize_signal()` hardcoded `_VALID_SYSTEMS` set excluded `SNT`. All SNT Tracker rows silently normalized to `TOS_Import`.
- **Fix:** Added `"SNT"` to `_VALID_SYSTEMS` in `tracker_reader.py`. Added SNT to `db_seeder.py` seed data so it survives `init-db`. Released 2026-03-15.
- **Verify:** `summary_by_system.csv` shows SNT as distinct system.

### Error: Tracker Matcher — First Match Wins Instead of Closest Date
- **Date:** 2026-03-15 | **Severity:** Medium | **Status:** Resolved
- **Wrong:** `domain/matcher.py match_system()` window search returned first match found within ±3 days. Same symbol in Tracker from multiple systems on nearby dates could match wrong system.
- **Root Cause (Tony-identified):** Same symbol legitimately appears in Tracker from different systems on different dates. First-match is wrong — closest date is correct.
- **Fix:** Window search now collects ALL matches within ±3 days and returns the one with smallest date offset. Released 2026-03-15.

### Error: schwab_balance_pull.py — Wrong Config File and Auth Method
- **Date:** 2026-03-15 | **Severity:** High | **Status:** Resolved
- **Wrong:** New `schwab_balance_pull.py` read `access_token` from `config/P_020_schwab_config.json` via raw `urllib`. That file contains only app credentials, not tokens. Tokens are managed by schwab-py at `integrations/schwab_api/credentials/P_020_schwab_config.json`.
- **Fix:** Rewrote to use `P_020_Schwab_Token_Manager.get_client()` which handles token loading and auto-refresh. Added `get_account_hash(last4)` to look up encrypted hash before calling `client.get_account()`. Released 2026-03-15.
- **Verify:** `python P_020_Trade_Manager.py balance --account AJZ` → $31,674.64 current / $31,660.33 start-of-day with auto token refresh confirmed.

---


### Error: Exit Matching — Old Exits Attached to Wrong Entries (CRITICAL)
- **Date:** 2026-03-15 | **Severity:** Critical | **Status:** Resolved
- **Wrong:** `schwab_mapper.py _match_exits_to_entries()` keyed exit pool by `underlying_symbol` only with no date guard. 2025 AMD exits were attached to 2026 AMD entry, producing -$28,458 P&L instead of the correct +$626.
- **Root Cause:** No chronological check in exit-to-entry matching. Same symbol traded across multiple years caused cross-year exit contamination.
- **Fix:** Rewrote `_match_exits_to_entries()` — keyed by `full_symbol`, added `exit_date >= entry_date` guard, FIFO consumption, consumed-set dedup. Released 2026-03-15.
- **Verify:** AMD Jan 20 2026: entry $21.34 → exit $27.60 = +$626 WIN (confirmed vs Schwab transaction history)

### Error: SNT System Not Recognized — Normalized to TOS_Import
- **Date:** 2026-03-15 | **Severity:** Medium | **Status:** Resolved
- **Wrong:** `tracker_reader.py _normalize_signal()` hardcoded `_VALID_SYSTEMS` set excluded `SNT`. All SNT Tracker rows silently normalized to `TOS_Import`.
- **Fix:** Added `"SNT"` to `_VALID_SYSTEMS` in `tracker_reader.py`. Added SNT to `db_seeder.py` seed data so it survives `init-db`. Released 2026-03-15.
- **Verify:** `summary_by_system.csv` shows SNT as distinct system.

### Error: Tracker Matcher — First Match Wins Instead of Closest Date
- **Date:** 2026-03-15 | **Severity:** Medium | **Status:** Resolved
- **Wrong:** `domain/matcher.py match_system()` window search returned first match found within ±3 days. Same symbol in Tracker from multiple systems on nearby dates could match wrong system.
- **Root Cause (Tony-identified):** Same symbol legitimately appears in Tracker from different systems on different dates. First-match is wrong — closest date is correct.
- **Fix:** Window search now collects ALL matches within ±3 days and returns the one with smallest date offset. Released 2026-03-15.

### Error: schwab_balance_pull.py — Wrong Config File and Auth Method
- **Date:** 2026-03-15 | **Severity:** High | **Status:** Resolved
- **Wrong:** New `schwab_balance_pull.py` read `access_token` from `config/P_020_schwab_config.json` via raw `urllib`. That file contains only app credentials, not tokens. Tokens are managed by schwab-py at `integrations/schwab_api/credentials/P_020_schwab_config.json`.
- **Fix:** Rewrote to use `P_020_Schwab_Token_Manager.get_client()` which handles token loading and auto-refresh. Added `get_account_hash(last4)` to look up encrypted hash before calling `client.get_account()`. Released 2026-03-15.
- **Verify:** `python P_020_Trade_Manager.py balance --account AJZ` → $31,674.64 current / $31,660.33 start-of-day with auto token refresh confirmed.

---


### Fix: P_020_Schwab_Auth.py -- Automated Browser Callback Capture
- **Date:** 2026-03-23 | **Severity:** High | **Status:** Resolved
- **Wrong:** Auth script used temp_url.txt with manual copy-paste of callback URL. 30-second expiry window made this unreliable -- stale URLs from previous attempts caused CSRF state mismatch errors.
- **Fix:** Rewrote P_020_Schwab_Auth.py to intercept schwab-py print() to capture the state parameter, open the browser automatically via webbrowser.open(), and poll all browser windows every second via UIAutomation until a callback URL with matching state is found. No copy-paste required -- Tony only logs in.
- **Verify:** Run P_020_Schwab_Auth.py -- browser opens automatically, callback captured, tokens saved without any manual URL handling.

### Fix: config.py -- Tracker Dashboard Path F: Drive to D: Drive
- **Date:** 2026-03-23 | **Severity:** High | **Status:** Resolved
- **Wrong:** TRACKER_DASHBOARD path in config.py pointed to F:\OneDrive\... -- OneDrive is mounted at D: not F:. All imports defaulted every trade to TOS_Import.
- **Fix:** Updated config.py TRACKER_DASHBOARD path to D:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx
- **Verify:** Run import -- log shows TrackerLookup loaded with 198+ entries, system matching > 0 trades matched.

### Fix: p140 Not on System PATH -- Wrong Python Interpreter Used
- **Date:** 2026-03-23 | **Severity:** High | **Status:** Resolved
- **Wrong:** p140 conda env was not on the Windows PATH. Typing python resolved to Python 3.14.3 (standalone install) which lacked pydantic and all P_020 dependencies. Caused ModuleNotFoundError on import command.
- **Fix:** Added C:\Users\Trader\.conda\envs\p140\ and C:\Users\Trader\.conda\envs\p140\Scripts\ to front of user PATH via registry (HKCU:\Environment). Updated Launch_P_020.bat to also SET PATH=p140 at top as belt-and-suspenders.
- **Verify:** Open new terminal, run python --version -- should show Python 3.12.x (p140).

### Fix: ingest_pipeline.py -- Invalid Escape Sequence in Docstring
- **Date:** 2026-03-23 | **Severity:** Low | **Status:** Resolved
- **Wrong:** Docstring in _write_audit_log() contained audit_logs\ with a backslash, producing SyntaxWarning on Python 3.12+.
- **Fix:** Changed backslash to forward slash in docstring string.
- **Verify:** No SyntaxWarning on import.

---

## 9. AI WORKFLOWS & PROCESSES

### 9.1 Weekly Trade Import — Target State (Phase 3C+)

**Trigger:** Monday morning
**Time Required:** ~3 minutes

1. Double-click `P_020_Weekly_Update.bat`
2. Token auto-refreshes
3. Pulls transactions since last run (from P_020_last_run.json)
4. TRD filter → 10-min consolidation → orphan detection → auto-match → dedup check
5. Writes to SQLite trades + exits tables
6. Exports Power Query CSVs (options + stocks)
7. Exports AI review CSVs
8. Generates audit log
9. Updates last_run.json
10. Open Excel → click Refresh All → done

**Decision gate after run:**
```
Audit log shows orphaned trades  → Check prior week's Excel log manually
Audit log shows unmatched trades → Update System column from TOS_Import
Audit log shows errors           → Check Schwab token, verify API connection
Audit log is clean               → Done ✅
```

### 9.2 Weekly Trade Import — Current State (Manual, pre-Phase 3C)

1. Run Schwab auth if token expired
2. Export TOS CSV (paper account only — live uses API when 2B complete)
3. Run TOS parser for paper account if needed
4. Manually paste into Excel logs
5. Update System column entries

### 9.3 New Session Startup

1. Open P_020 Claude Project (not default chat)
2. Confirm system doc context loaded
3. If context missing: paste New Session Context Restore prompt (Section 5.3)
4. Confirm p140 env path, current phase, last completed task
5. State today's task and begin

### 9.4 Performance Review / Monthly Review

**Trigger:** "monthly review" or first session of month
Tony runs:
```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py analyze --account AJZ6348
```
Outputs 6 CSVs to `data\exports\ai_review\`: summary_by_system, monthly_summary, equity_curve, r_distribution, open_positions, drawdown.

Tony pastes all six. Claude interprets in order: (1) P&L health vs prior month, (2) system win rate (flag <40%), (3) equity curve shape/drawdown >5%, (4) WHY/SIG analysis (FOMO/REVENGE cost, A vs X), (5) open positions (flag >30 days, missing stops), (6) data quality (untagged, bad R, SNVXX/SWPPX), (7) account parameters (flag if ±10% from $35K baseline; prompt sizing review), (8) 1-2 concrete observations + journal items.

Claude does NOT advise trades, interpret opens as signals, or fix data without instruction.

---

### 9.5 ThinkLog Tag Vocabulary (Canonical)

Format: `MMDD: [WHY] [SIG] optional free text` — WHY + SIG required. Vocabulary is open — parser never validates.

**WHY — System:** `BTD`=P_115 | `OIL`=P_116 | `EXT`=P_117 | `EZB`=P_118 | `VPT`=P_300 | `SNT`=BigTrends | `DAY`=intraday-flat

**WHY — Situation:** `ASYM`=near-miss BUY | `IFFY`=marginal | `LEARN`=educational | `CROWDED`=at-capacity | `FOMO`=honesty | `REVENGE`=loss-chase

**SIG:** `A`=high-conviction | `B`=standard-fired | `C`=marginal-feels-off | `X`=counter-signal

### 9.6 Session INIT Command Block

**Rule:** NEVER `Start-Process -NoNewWindow` (blocks MCP ~4 min). ALWAYS `Start-Job + cmd /c`.

```powershell
$job = Start-Job -ScriptBlock {
    cmd /c """C:\Users\Trader\.conda\envs\p140\python.exe"" ""C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\P_020_INIT.py"" > ""C:\Temp\init_out.txt"" 2>&1"
}
# Separate tool call — Start-Sleep 20; Get-Content "C:\Temp\init_out.txt"
```

Fallback: Tony pastes output of one-liner in Anaconda Prompt.
Script output fields: MARKET block, DB block, ACCOUNT block (THRESHOLD flag at ±10% of $35K; STALE flag >14d).

---

## 10. TESTING & VALIDATION

### 10.1 Phase 3A Validation — PASSED 2026-03-14

```
P_020 Database Verification
=============================================
  accounts                      3 rows
  systems                       9 rows
  trades                        0 rows
  exits                         0 rows
  v_trade_summary (view)        exists
=============================================
```

### 10.2 Known-Good Reference Examples

**Multi-fill commission (QBTS):**
- Input: REF #1005039452515 — 2 fills × $1.32 = $2.64 entry commission
- Expected: total_commissions = $5.30 (entry $2.64 + exit1 $1.33 + exit2 $1.33)

**Auto-match:**
- Input: QBTS trade on 2026-01-02 in Tracker with Signal Source = P_118
- Expected: system = 'P_118' (not 'TOS_Import')

**R calculation (no stop):**
- Input: AAPL entry $180.50, qty 100 shares, no stop set
- Expected: risk_amount = $180.50 × 100 × 0.015 = $270.75

### 10.3 Validation Checklist (Run at Session Start)

- [ ] p140 conda confirmed: C:\Users\Trader\.conda\envs\p140\python.exe
- [ ] DB file exists: data\database\P_020_trades.db
- [ ] Schwab config exists: config\P_020_schwab_config.json
- [ ] Params file exists: config\P_020_Account_Params.json
- [ ] Tracker Dashboard accessible at known path

### 10.4 Known Issues & Limitations

| ID | Description | Severity | Workaround |
|---|---|---|---|
| LIM-001 | 3+ exits not in original Excel schema | Low | SQLite exits table handles unlimited |
| LIM-002 | IRA account not yet pulling from API | Low | Manual entry for now |
| LIM-003 | Same-day same-symbol trades with different systems | Medium | Tracker reader uses first match |

---

## 11. DAILY OPERATIONS & SESSION MANAGEMENT

### 11.1 Parameter Registry

| Parameter | Value | Source | Next Review |
|---|---|---|---|
| Python executable | C:\Users\Trader\.conda\envs\p140\python.exe | config.py | 2026-06-01 |
| Database file | data\database\P_020_trades.db | config.py | N/A (auto) |
| Default risk % | 0.015 (1.5%) | P_020_Account_Params.json | As needed |
| Options multiplier | 100 | P_020_Account_Params.json | As needed |
| Consolidation window | 10 minutes | P_020_Account_Params.json | As needed |
| Default system name | TOS_Import | P_020_Account_Params.json | As needed |
| Schwab app name | AJZ-Strategies-P020 | developer.schwab.com | N/A |
| Schwab callback URL | https://127.0.0.1 | config.py | N/A (fixed) |
| IRA distribution years | 10 | accounts table (IRA9885) | N/A |
| IRA distribution start | MIN(open_date) WHERE acct=IRA9885 | Derived from data | N/A |
| Live Options log | AJZStrategiesLLC\2026_Operations\..._Options_Log_v1.xlsx | config.py | 2026-06-01 |
| Live Stock log | AJZStrategiesLLC\2026_Operations\..._Stock_Log_v1.xlsx | config.py | 2026-06-01 |
| Tracker Dashboard | P_115_TrackerAudit\P_115_118_TtrackerDashboard_V2.xlsx | config.py | 2026-06-01 |

### 11.2 Monthly Maintenance

| Task | Owner | Notes |
|---|---|---|
| Schwab refresh token renewal | Auto | Token Manager handles — verify running |
| Tracker Dashboard sync | Tony | Update when new systems added |
| Audit log archive | Tony | Move old logs out of audit_logs\ |
| Enhancement tracker review | Tony | Update priorities, close completed items |
| Params file review | Tony | Confirm risk %, multiplier still correct |

---

## 12. TROUBLESHOOTING & SUPPORT

### 12.1 Common Issues

**Claude gives unexpected code output:**
- Restate the specific rule from Section 5.2 being violated
- Show known-good example and ask Claude to match
- If persistent: start new session (system doc reloads)

**Schwab API returns 401 Unauthorized:**
- Run schwab_token_manager.py to auto-refresh
- If refresh token expired (7 days): re-run schwab_auth.py full flow

**Tracker Dashboard locked (PermissionError):**
- Close Tracker Dashboard in Excel
- Re-run script — falls back to TOS_Import for this run

**DB verify shows 0 accounts/systems:**
- Re-run P_020_Create_Database.bat
- init-db is safe to re-run (INSERT OR IGNORE protects seed data)

**Claude repeating a corrected error:**
- Check Section 8 for documented fix
- Paste the specific violated rule
- If recurs 2+ times: update Section 5.2 AI Behavior Rules

### 12.2 Escalation Path

| Level | Condition | Action |
|---|---|---|
| Self-resolve | Minor output format issue | Restate rule, show example |
| Session reset | Persistent drift or wrong logic | New session |
| Documentation update | Same error 2+ times | Add to Section 8 |
| System redesign | Fundamental logic failure | New enhancement request |

---

## 13. APPENDICES

### Appendix A: Phase Progress

| Phase | Description | Status | Completed |
|---|---|---|---|
| 1 | TOS Parser + Excel templates | ✅ Complete | Feb 2026 |
| 2A | Schwab OAuth authentication | ✅ Complete | Feb 2026 |
| 2B | Schwab trade history pull | 🔄 In progress | — |
| 2C | Schwab positions + balances | 📋 Planned | — |
| 3A | SQLite schema + creation script | ✅ Complete | Mar 14, 2026 |
| 3B | Python DB infrastructure layer | ✅ Complete | Mar 14, 2026 |
| 3C | Ingest pipeline (API → SQLite) | 📋 Next | — |
| 3D | Excel Power Query view | 📋 Planned | — |
| 3E | Stats export for AI analysis | 📋 Planned | — |
| 4 | Performance analysis + reporting | 📋 Planned | May 2026+ |

### Appendix B: Related Documents

| Document | Location | Purpose |
|---|---|---|
| P_020_PROJECT_PLAN_v4.md | docs\ | Full project plan with SQLite architecture |
| P_020_Future_Enhancements_Tracker.md | docs\ | All enhancement requests with status |
| P_020_COLLABORATION_FRAMEWORK.md | docs\ | Tony & Claude working agreement |
| P_020_TOS_Parser_README.md | docs\ | Archived — TOS parser v2.1 guide |

### Appendix C: Success Definition

**We're done when:**
- Monday morning = one click → SQLite updated, Excel refreshes in 3 seconds
- Zero manual data entry — ever
- Performance review = drop AI export CSVs into Claude, get analysis
- More time for golf and fishing ⛳🎣

---

**Document Classification:** Internal
**Document Owner:** Anthony Zoppi — AJZ Strategies LLC
**Version:** 2.0
**Last Updated:** 2026-03-14
**Next Review:** 2026-04-30