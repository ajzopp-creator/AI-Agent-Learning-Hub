# P_020 AJZ Strategies Performance Analysis System
## Project Plan v4.0 — SQLite Data Layer Architecture
**Updated:** March 14, 2026
**Owner:** Tony (AJZ Strategies LLC)
**Environment:** p140 conda (`C:\Users\Trader\.conda\envs\p140\python.exe`)

---

## 🎯 PROJECT MISSION

Automate weekly trading performance tracking for AJZ Strategies LLC — eliminating manual data entry, ensuring accuracy, and freeing time for golf and fishing. Trade data flows from the Schwab API into a local SQLite database (the single source of truth), with Excel serving as a live view layer rather than the data store.

**Original approach (v1):** Parse TOS CSV exports → paste into Excel manually
**v3 approach:** Schwab API → CSV → paste into Excel
**v4 approach (current):** Schwab API → SQLite (master record) → Excel via Power Query (view only)

---

## ✅ PHASE 1 — COMPLETE (January–February 2026)

| Deliverable | Status | Notes |
|---|---|---|
| TOS Parser v2.1 | ✅ Complete | Archived — superseded by API approach |
| P_020_AccountParser.bat | ✅ Complete | Archived |
| Excel Master Templates (Options + Stock) | ✅ Complete | Retained as view layer in new architecture |
| Auto-Match System Names (REQ-020126_01) | ✅ Complete | Logic carried to Phase 3 DB ingestion |
| Formula Preservation on Import (REQ-020207_01) | ✅ Complete | No longer needed when Excel is a view |
| p140 Environment Standardization | ✅ Complete | Permanent standard |
| ClaudeCleanShutdown.bat | ✅ Complete | Permanent |

---

## 🔵 PHASE 2 — SCHWAB API INTEGRATION
**Target:** March 2026
**Status:** In Progress

Phase 2 focus is authentication and raw data retrieval only. Data written to flat files for now — Phase 3 wires it into SQLite.

### 2A — OAuth Authentication
**Blocker was:** Callback URL propagation (resolved ~Feb 25)
**Status:** Ready to test / may be complete

**Deliverables:**
- `python/infrastructure/schwab_auth.py` — OAuth 2.0 browser flow, saves tokens
- `python/infrastructure/schwab_token_manager.py` — auto-refresh (30-min access / 7-day refresh)
- `config/P_020_schwab_config.json` — secure local credential store (gitignored)

**Acceptance:**
- [ ] Browser auth flow completes without error
- [ ] Access token and refresh token saved to config file
- [ ] Token refresh works before expiry

---

### 2B — Trade History Pull
**Depends on:** 2A

**Deliverables:**
- `python/infrastructure/schwab_trade_pull.py` — pulls `/trader/v1/accounts/{acct}/transactions`
- Supports date range + incremental pull (since last run)
- Outputs raw JSON to `data/api_pulls/live/` for audit trail
- Also outputs interim CSV (same format as TOS parser output) as fallback

**Carried-forward requirements applied here:**
- REQ-020221_01: Filter to TRD transactions only
- REQ-020221_02: Detect orphaned sells (no matching buy in window)
- REQ-020221_04: 10-minute same-symbol buy consolidation

**Acceptance:**
- [ ] YTD pull matches TOS parser output for same date range
- [ ] Non-TRD transactions excluded and counted in audit
- [ ] Orphaned sells flagged, not silently dropped

---

### 2C — Positions & Balances Pull
**Depends on:** 2A

**Deliverables:**
- `python/infrastructure/schwab_positions.py`
- Outputs console summary + CSV to `data/api_pulls/live/`

**Acceptance:**
- [ ] Current open positions match Schwab platform display
- [ ] Account balance and buying power retrieved correctly

---

## 🟢 PHASE 3 — SQLITE DATA LAYER (NEW)
**Target:** April 2026
**Status:** Planned

**Mission:** Replace Excel as the data store. SQLite becomes the single source of truth. Excel becomes a read-only view layer populated by Power Query. This unlocks reliable performance analysis, prevents data entry errors forever, and makes AI-assisted trade review simple.

---

### 3A — Database Schema & Creation

**Database file location:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategiesPerformanceAnalysisSystem\
    data\database\P_020_trades.db
```

**Schema — 4 tables + 1 view:**

#### Table: `accounts`
Seed data — defines which accounts are tracked.

| Column | Type | Notes |
|---|---|---|
| account_id | TEXT PK | 'AJZ6348', 'PAPER' |
| account_name | TEXT | 'AJZ Strategies LLC Live', 'Paper Account' |
| account_type | TEXT | 'live', 'paper' |
| broker | TEXT | 'schwab' |
| created_at | DATETIME | auto |

---

#### Table: `systems`
Seed data — defines valid trading systems.

| Column | Type | Notes |
|---|---|---|
| system_id | TEXT PK | 'P_115', 'P_116', 'P_117', 'P_118', 'P_300', 'P_910', 'P_920', 'Day', 'TOS_Import' |
| system_name | TEXT | Human-readable name |
| description | TEXT | Brief description of the system |
| active | INTEGER | 1 = active, 0 = retired |

---

#### Table: `trades`
One row per position opened. This is the primary entity.

| Column | Type | Notes |
|---|---|---|
| trade_id | INTEGER PK AUTO | Surrogate key |
| account_id | TEXT FK | → accounts |
| system | TEXT FK | → systems |
| underlying_symbol | TEXT | 'QBTS', 'AAPL', etc. |
| asset_type | TEXT | 'stock', 'call', 'put', 'spread' |
| direction | TEXT | 'long', 'short' |
| open_date | DATE | Entry date (date only) |
| open_datetime | DATETIME | Entry datetime if available from API |
| qty | REAL | Shares or contracts at entry |
| entry_price | REAL | Per share or per contract |
| stop_price | REAL | For R calculation — null if not set |
| risk_amount | REAL | Dollar risk: (entry - stop) × qty × multiplier |
| total_commissions | REAL | All commissions for full round trip |
| status | TEXT | 'open', 'partial', 'closed' |
| tags | TEXT | Free text — comma-separated labels |
| notes | TEXT | Trade journal / comments |
| source | TEXT | 'schwab_api', 'tos_import', 'manual' |
| schwab_transaction_id | TEXT | Schwab's internal ID for dedup |
| created_at | DATETIME | auto |
| updated_at | DATETIME | auto-updated on change |

---

#### Table: `exits`
One row per partial or full exit. Normalized — supports 1, 2, or 3 exits per trade without schema changes.

| Column | Type | Notes |
|---|---|---|
| exit_id | INTEGER PK AUTO | Surrogate key |
| trade_id | INTEGER FK | → trades |
| exit_number | INTEGER | 1, 2, 3 |
| exit_date | DATE | Date of this exit |
| exit_datetime | DATETIME | Datetime if available |
| qty_exited | REAL | Shares/contracts closed at this exit |
| exit_price | REAL | Per share or per contract |
| exit_commissions | REAL | Commissions for this exit leg only |
| exit_pnl | REAL | (exit_price − entry_price) × qty_exited × multiplier |
| hold_days | INTEGER | exit_date − open_date |
| created_at | DATETIME | auto |

**Why normalized?**
The flat schema approach (Exit #1, Exit #2, Exit #3 columns in one row) hits a wall every time a new exit type is needed. The exits table handles 1, 2, 3, or 10 exits per trade with zero schema changes.

---

#### View: `v_trade_summary`
Computed rollup of trades + exits. Used by all reporting and by Excel Power Query import. No stored data — always calculated live.

```sql
CREATE VIEW v_trade_summary AS
SELECT
    t.trade_id,
    t.account_id,
    t.system,
    t.underlying_symbol,
    t.asset_type,
    t.direction,
    t.open_date,
    t.qty,
    t.entry_price,
    t.stop_price,
    t.risk_amount,
    t.total_commissions,
    t.status,
    t.tags,
    t.notes,
    t.source,

    -- Aggregated exit data
    COALESCE(SUM(e.exit_pnl), 0.0)      AS realized_pnl,
    COALESCE(SUM(e.qty_exited), 0)       AS qty_closed,
    t.qty - COALESCE(SUM(e.qty_exited), 0) AS qty_remaining,
    MAX(e.exit_date)                      AS last_exit_date,
    MAX(e.hold_days)                      AS max_hold_days,

    -- Exit prices (for Excel log compatibility)
    MAX(CASE WHEN e.exit_number = 1 THEN e.exit_price END)    AS exit_1_price,
    MAX(CASE WHEN e.exit_number = 1 THEN e.qty_exited END)    AS exit_1_qty,
    MAX(CASE WHEN e.exit_number = 1 THEN e.exit_date END)     AS exit_1_date,
    MAX(CASE WHEN e.exit_number = 1 THEN e.hold_days END)     AS exit_1_hold_days,
    MAX(CASE WHEN e.exit_number = 2 THEN e.exit_price END)    AS exit_2_price,
    MAX(CASE WHEN e.exit_number = 2 THEN e.qty_exited END)    AS exit_2_qty,
    MAX(CASE WHEN e.exit_number = 2 THEN e.exit_date END)     AS exit_2_date,
    MAX(CASE WHEN e.exit_number = 2 THEN e.hold_days END)     AS exit_2_hold_days,
    MAX(CASE WHEN e.exit_number = 3 THEN e.exit_price END)    AS exit_3_price,
    MAX(CASE WHEN e.exit_number = 3 THEN e.qty_exited END)    AS exit_3_qty,
    MAX(CASE WHEN e.exit_number = 3 THEN e.exit_date END)     AS exit_3_date,
    MAX(CASE WHEN e.exit_number = 3 THEN e.hold_days END)     AS exit_3_hold_days,

    -- R calculation (requires stop_price set)
    CASE
        WHEN t.risk_amount IS NOT NULL AND t.risk_amount != 0
        THEN ROUND(COALESCE(SUM(e.exit_pnl), 0.0) / t.risk_amount, 2)
        ELSE NULL
    END AS realized_R,

    -- Outcome
    CASE
        WHEN t.status = 'open'                             THEN 'OPEN'
        WHEN COALESCE(SUM(e.exit_pnl), 0.0) > 0           THEN 'WIN'
        WHEN COALESCE(SUM(e.exit_pnl), 0.0) < 0           THEN 'LOSS'
        ELSE 'SCRATCH'
    END AS outcome

FROM trades t
LEFT JOIN exits e ON t.trade_id = e.trade_id
GROUP BY t.trade_id;
```

---

### 3B — Python Database Infrastructure

Follows the p140 Hub architecture standard (domain / infrastructure / application layers).

**File plan (all under `python/`):**

| File | Layer | Purpose | Est. Lines |
|---|---|---|---|
| `config.py` | Config | All paths, constants, column lists | ~60 |
| `schemas.py` | Schema | Pydantic models for Trade, Exit, Account, System | ~80 |
| `domain/trade_logic.py` | Domain | R calculation, pnl calc, status logic, consolidation rules | ~120 |
| `domain/matcher.py` | Domain | Tracker Dashboard symbol+date matching | ~80 |
| `infrastructure/db_client.py` | Infra | SQLite connection, create tables, seed data | ~150 |
| `infrastructure/db_writer.py` | Infra | Insert/update trades and exits, dedup logic | ~150 |
| `infrastructure/db_reader.py` | Infra | Query helpers — by account, by system, by date range | ~120 |
| `infrastructure/tracker_reader.py` | Infra | Read Tracker Dashboard Excel → lookup dict | ~80 |
| `infrastructure/csv_exporter.py` | Infra | Export v_trade_summary → CSV for Excel Power Query | ~80 |
| `application/ingest_pipeline.py` | App | Orchestrates: API pull → parse → match → write to DB | ~150 |
| `application/stats_export.py` | App | Per-system summary, equity curve, R-dist → CSV for AI | ~120 |
| `cli.py` | CLI | Command-line entry point (ingest, export, stats) | ~80 |
| `P_020_Weekly_Update.bat` | Runner | One-click weekly runner | ~20 |
| `requirements.txt` | Deps | schwab-py, pandas, openpyxl, pydantic | ~10 |

**Total:** ~1,300 lines across 14 files. Well within Hub standards.

---

### 3C — Schwab API → SQLite Ingestion

Modify Phase 2B output to write directly to SQLite instead of (or in addition to) CSV.

**Ingestion flow:**
```
Schwab API pull (Phase 2B)
    ↓
Filter: TRD only (REQ-020221_01)
    ↓
Consolidate: 10-min same-symbol buys (REQ-020221_04)
    ↓
Detect: Orphaned sells (REQ-020221_02)
    ↓
Match: Tracker Dashboard → System name (REQ-020126_01)
    ↓
Dedup: Check schwab_transaction_id — skip if already in DB
    ↓
Write: trades table + exits table
    ↓
Update: last_run.json with today's date
    ↓
Audit log: full processing summary (REQ-020221_03)
```

**Deduplication rule:**
Before writing any transaction, check if `schwab_transaction_id` already exists in the `trades` table. If yes — skip and note in audit log. This makes it safe to run the weekly update more than once without creating duplicates.

---

### 3D — Excel as a View Layer

Replace manual copy/paste with a Power Query connection to the export CSV.

**How it works:**
1. Python exports `v_trade_summary` → `data/exports/P_020_options_export.csv` and `P_020_stocks_export.csv`
2. Excel Options Log and Stock Log connect to these CSVs via Power Query (Data → Get Data → From File → From CSV)
3. Refresh = click "Refresh All" in Excel — takes 3 seconds
4. Dashboard formulas and charts remain unchanged — they point to the imported Power Query table

**Formula columns:** Since P&L is now calculated in SQLite (`exit_pnl`, `realized_pnl`, `realized_R`), the Excel formulas become redundant — but can be kept for cross-validation during transition.

**Transition plan:**
- Phase 3 runs SQLite and Excel in parallel for 2 weeks
- Verify totals match between old manual entries and new DB values
- Once validated, Excel manual entry stops permanently

---

### 3E — Stats Export for AI Analysis

A dedicated export command that produces clean summary tables optimized for AI performance review.

**Export files (saved to `data/exports/ai_review/`):**

| File | Contents |
|---|---|
| `summary_by_system.csv` | Win rate, avg R, profit factor, expectancy per system |
| `equity_curve.csv` | Cumulative P&L by date (all systems + per system) |
| `r_distribution.csv` | R-multiple distribution table (for Kelly / position sizing) |
| `monthly_summary.csv` | Month-by-month P&L, win rate, trade count |
| `open_positions.csv` | All trades with status='open' — current exposure |
| `drawdown.csv` | Rolling max drawdown by date |

**Usage:** Feed these CSVs directly to Claude for performance reviews. No manual formatting. No copying from Excel.

---

## 🟡 PHASE 4 — PERFORMANCE ANALYSIS & REPORTING (~May 2026+)

*Unchanged from v3 — depends on Phase 3 data being clean and complete.*

- System comparison: P_115 vs P_116 vs P_117 vs P_118 vs P_300
- Win rate trends over time
- Risk metrics: Sharpe ratio, max drawdown, profit factor
- Time-based analysis: monthly, weekly, by market regime
- Automated performance reports (HTML dashboard — dark trading terminal aesthetic)

---

## 📋 COMPLETE REQUIREMENTS TRACKER

| Req ID | Description | Status | Target |
|---|---|---|---|
| 020126_01 | Auto-match Tracker Dashboard → System column | ✅ Complete | Carries to 3C ingestion |
| 020207_01 | Excel import with formula preservation | ✅ Complete | Superseded by SQLite view approach |
| 020221_01 | Filter to TRD transactions only | 🔄 Phase 2B + 3C | Schwab API v1.0 |
| 020221_02 | Orphaned transaction detection | 🔄 Phase 2B + 3C | Schwab API v1.0 |
| 020221_03 | Consolidated audit log | 🔄 Phase 2B + 3C | Schwab API v1.0 |
| 020221_04 | 10-minute buy consolidation window | 🔄 Phase 2B + 3C | Schwab API v1.0 |
| 020221_05 | Audit log cross-reference (dedup) | 🔄 Phase 3C | Handled by schwab_transaction_id dedup |
| 020224_01 | Schwab OAuth 2.0 auth + token management | 📋 Phase 2A | In progress |
| 020224_02 | Schwab trade history pull | 📋 Phase 2B | Planned |
| 020224_03 | Schwab positions + balances | 📋 Phase 2C | Planned |
| 020224_04 | Weekly one-click automation | 📋 Phase 3 | P_020_Weekly_Update.bat |
| NEW-01 | SQLite canonical schema | 📋 Phase 3A | New |
| NEW-02 | Python DB infrastructure layer | 📋 Phase 3B | New |
| NEW-03 | Schwab → SQLite ingestion pipeline | 📋 Phase 3C | New |
| NEW-04 | Excel Power Query view layer | 📋 Phase 3D | New |
| NEW-05 | Stats export CSV for AI analysis | 📋 Phase 3E | New |

---

## 📁 UPDATED FILE STRUCTURE

```
P_020_AJZStrategiesPerformanceAnalysisSystem\
│
├── python\
│   ├── parsers\                    [ARCHIVED — TOS parser]
│   ├── schwab_api\                 [PHASE 2 — active]
│   │   ├── infrastructure\
│   │   │   ├── schwab_auth.py
│   │   │   └── schwab_token_manager.py
│   │   └── schwab_trade_pull.py
│   │
│   └── database\                   [PHASE 3 — NEW]
│       ├── config.py
│       ├── schemas.py
│       ├── domain\
│       │   ├── trade_logic.py
│       │   └── matcher.py
│       ├── infrastructure\
│       │   ├── db_client.py
│       │   ├── db_writer.py
│       │   ├── db_reader.py
│       │   ├── tracker_reader.py
│       │   └── csv_exporter.py
│       ├── application\
│       │   ├── ingest_pipeline.py
│       │   └── stats_export.py
│       ├── cli.py
│       └── requirements.txt
│
├── data\
│   ├── tos_exports\                [ARCHIVED]
│   ├── processed\                  [ARCHIVED]
│   ├── api_pulls\                  [PHASE 2 output]
│   │   ├── live\
│   │   └── paper\
│   ├── database\                   [PHASE 3 — NEW]
│   │   └── P_020_trades.db         ← SINGLE SOURCE OF TRUTH
│   └── exports\                    [PHASE 3 — NEW]
│       ├── P_020_options_export.csv   ← Power Query source
│       ├── P_020_stocks_export.csv    ← Power Query source
│       └── ai_review\
│           ├── summary_by_system.csv
│           ├── equity_curve.csv
│           ├── r_distribution.csv
│           ├── monthly_summary.csv
│           ├── open_positions.csv
│           └── drawdown.csv
│
├── config\                         [gitignored]
│   └── P_020_schwab_config.json
│
├── tracking_logs\
│   ├── live\   → C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
│   └── paper\
│
├── audit_logs\
│   └── P_020_Weekly_Audit_YYYYMMDD.txt
│
├── P_020_Weekly_Update.bat         ← ONE-CLICK RUNNER
└── docs\
    └── P_020_PROJECT_PLAN_v4.md    ← THIS FILE
```

---

## ⏱️ REALISTIC TIMELINE

| Phase | Target Date | Status |
|---|---|---|
| Phase 1 — TOS Parser + Excel Templates | Jan–Feb 2026 | ✅ Complete |
| Phase 2A — Schwab Auth | Mar 2026 | ⏳ In progress |
| Phase 2B — Trade History Pull | Mar 2026 | 📋 Planned |
| Phase 2C — Positions Pull | Mar 2026 | 📋 Planned |
| Phase 3A — SQLite Schema + Creation Script | Apr 2026 | 📋 Planned |
| Phase 3B — Python DB Infrastructure | Apr 2026 | 📋 Planned |
| Phase 3C — Ingestion Pipeline (API → SQLite) | Apr 2026 | 📋 Planned |
| Phase 3D — Excel Power Query View | Apr 2026 | 📋 Planned |
| Phase 3E — Stats Export for AI | Apr 2026 | 📋 Planned |
| Phase 4 — Performance Analysis | May 2026+ | 📋 Planned |

---

## 🎯 SUCCESS DEFINITION

**We're done when:**
- Monday morning = one click → SQLite updated, Excel refreshes automatically
- Zero manual data entry — ever
- Performance review = drop AI export CSVs into Claude, get analysis
- More time for golf and fishing ⛳🎣

---

## 📌 KEY DESIGN DECISIONS

| Decision | Choice | Rationale |
|---|---|---|
| Database | SQLite | Local, file-based, no server admin, works with Python and Excel ODBC |
| Schema style | Normalized (trades + exits tables) | Supports unlimited exits without schema changes |
| Excel role | View only (Power Query) | Dashboard formulas untouched; no copy/paste ever |
| Dedup strategy | schwab_transaction_id | Safe to re-run weekly update without creating duplicates |
| R calculation | (exit_pnl / risk_amount) | risk_amount set at trade entry using 1.5% rule + stop price |
| Stats export | CSV files | Simple, AI-readable, no special tooling required |
| Architecture | p140 Hub standard (domain/infra/app layers) | Consistent with all other Hub projects |

---

*Version: 4.0*
*Updated: March 14, 2026*
*Status: Active — Plan Approved*
*Next Action: Confirm Phase 2A Schwab auth status, then begin Phase 3A schema creation*
