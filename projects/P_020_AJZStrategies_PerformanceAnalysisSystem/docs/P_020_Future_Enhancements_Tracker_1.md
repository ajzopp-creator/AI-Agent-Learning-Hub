# P_020 Future Enhancements Tracker

## Purpose
This document tracks all enhancement requests for the P_020 AJZ Strategies Performance Analysis System. Each requirement is assigned a unique ID, documented, approved, and tracked through implementation.

**Note:** As of February 24, 2026, the TOS CSV parser has been retired in favor of direct Schwab API integration. All carried-forward enhancements are now targeted at the Schwab API build.

---

## Enhancement Request Table

| Req ID | Requirement Description | Date Submitted | Date Approved | Date Implemented | Status | Project Version |
|--------|------------------------|----------------|---------------|------------------|--------|-----------------|
| 020126_01 | Auto-match Tracker Dashboard signals to assign correct System instead of defaulting to "TOS_Import" | 2026-02-01 | 2026-02-07 | 2026-02-15 | ✅ Completed | P_020 v2.2 |
| 020207_01 | Excel import with formula preservation — protect formula columns on paste | 2026-02-07 | 2026-02-07 | 2026-02-15 | ✅ Completed | P_020 v2.2 |
| 020221_01 | Filter transactions to TRD type only (exclude non-trade rows) | 2026-02-21 | 2026-02-24 | - | 🔄 Carry to API | Schwab API v1.0 |
| 020221_02 | Orphaned transaction detection (sells with no matching buy in export window) | 2026-02-21 | 2026-02-24 | - | 🔄 Carry to API | Schwab API v1.0 |
| 020221_03 | Consolidated audit log for dropped/unmatched records | 2026-02-21 | 2026-02-24 | - | 🔄 Carry to API | Schwab API v1.0 |
| 020221_04 | 10-minute window consolidation for same-symbol buy orders | 2026-02-21 | 2026-02-24 | - | 🔄 Carry to API | Schwab API v1.0 |
| 020221_05 | Audit log cross-reference with Excel logs for weekly automation reconciliation | 2026-02-21 | 2026-02-24 | - | 🔄 Carry to API | Phase 3 |
| 020224_01 | Schwab OAuth 2.0 authentication + token management (30-min refresh, 7-day refresh token) | 2026-02-24 | 2026-02-24 | - | 📋 Planned | Schwab API v1.0 |
| 020224_02 | Schwab trade history pull — replace TOS CSV export entirely | 2026-02-24 | 2026-02-24 | - | 📋 Planned | Schwab API v1.0 |
| 020224_03 | Schwab positions + balances pull — real-time account snapshot | 2026-02-24 | 2026-02-24 | - | 📋 Planned | Schwab API v1.0 |
| 020224_04 | Weekly automated update — one-click full workflow (pull → match → append → audit) | 2026-02-24 | 2026-02-24 | - | 📋 Planned | Phase 3 |

---

## Status Definitions

- **📋 Planned**: Approved and scheduled for development
- **🔄 Carry to API**: Originally written for TOS parser, approved to carry forward to Schwab API build
- **🔵 In Progress**: Actively being developed
- **🧪 Testing**: Under validation/testing
- **✅ Completed**: Implemented and deployed to production
- **📦 Archived**: Was for retired TOS parser — no longer applicable
- **❌ Rejected**: Not approved for implementation

---

## Detailed Requirements

---

### ✅ REQ-020126_01: Auto-Match Trading System from Tracker Dashboard

**Status**: Completed — February 15, 2026  
**Priority**: Medium  
**Target Version**: P_020 v2.2  
**Implemented In**: `P_020_Trade_Import_Enhanced.py`

Reads Tracker Dashboard (`P_115_118_TtrackerDashboard_V2.xlsx`), matches Symbol + Trade Date to each parsed trade, and fills the System column automatically (P_115, P_116, P_117, P_118, P_300). Falls back to "TOS_Import" if no match found. Handles both "Symbol" and "Buy" column naming in the Tracker. Case-insensitive symbol matching.

---

### ✅ REQ-020207_01: Excel Import with Formula Preservation

**Status**: Completed — February 15, 2026  
**Priority**: High  
**Target Version**: P_020 v2.2  
**Implemented In**: `P_020_Trade_Import_Enhanced.py`

Protects formula columns during import so Excel calculations are not overwritten.

- **Options formula columns protected:** M, Q, U, W, Y, Z, AA
- **Stock formula columns protected:** J, N, P, Q, S, T
- Trade data columns written as values only

---

### 🔄 REQ-020221_01: Filter to TRD Transactions Only

**Status**: Carry to Schwab API v1.0  
**Priority**: High  
**Originally For**: TOS Parser v2.3 (retired)  
**Now Target**: Schwab API Trade Pull script

**What it does:** When pulling transactions from Schwab API, filter to trade-type transactions only. Exclude dividend payments, interest, fees, journal entries, and other non-trade rows that would otherwise clutter the import and cause parsing errors.

**Why it matters:** Prevents orphaned-looking records, reduces noise in audit log, makes matching cleaner.

---

### 🔄 REQ-020221_02: Orphaned Transaction Detection

**Status**: Carry to Schwab API v1.0  
**Priority**: High  
**Originally For**: TOS Parser v2.3 (retired)  
**Now Target**: Schwab API Trade Pull script

**What it does:** Detects sell transactions that have no matching buy within the pull window — meaning the position was opened before the date range being pulled. Flags these in the audit log rather than dropping them silently.

**Why it matters:** Critical for weekly automation — without this, sells from positions opened the prior week would appear as orphaned and be missed entirely.

**Example:**
```
DJT — Buy occurred 12/31/25, Sell appeared in 1/2/26 pull
Without detection: Sell is dropped silently
With detection: Audit log flags "DJT sell on 1/2/26 has no matching buy — check prior week"
```

---

### 🔄 REQ-020221_03: Consolidated Audit Log

**Status**: Carry to Schwab API v1.0  
**Priority**: Medium  
**Originally For**: TOS Parser v2.3 (retired)  
**Now Target**: Schwab API Trade Pull script + Weekly Automation

**What it does:** Every time a pull runs, generate a single audit log file (`P_020_Weekly_Audit_YYYYMMDD.txt`) that records:
- Total transactions pulled
- Transactions matched to Excel logs
- Transactions dropped (with reason)
- Orphaned transactions flagged
- System names auto-matched vs. left as default
- Any errors encountered

**Why it matters:** Single place to review anything that needs manual attention after automation runs.

---

### 🔄 REQ-020221_04: 10-Minute Buy Consolidation Window

**Status**: Carry to Schwab API v1.0  
**Priority**: Medium  
**Originally For**: TOS Parser v2.3 (retired)  
**Now Target**: Schwab API Trade Pull script

**What it does:** When two or more buy orders for the same symbol occur within 10 minutes of each other, consolidate them into a single position entry rather than creating separate rows.

**Why it matters:** Intraday scaling into a position (buying 2 lots at 9:32 AM and 2 more lots at 9:38 AM) should be treated as one position entry, not two separate trades.

**Rule:** Same Symbol + Same Direction (Buy) + Within 10 minutes = Consolidate into one entry, sum shares/contracts and fees.

---

### 🔄 REQ-020221_05: Audit Log Cross-Reference for Weekly Automation

**Status**: Carry to Phase 3  
**Priority**: Low (needed for full automation)  
**Originally For**: TOS Parser v2.3 (retired)  
**Now Target**: Phase 3 Weekly Automation

**What it does:** After weekly automation appends new trades to Excel, cross-reference the audit log against what's already in the Excel log to prevent duplicate entries. If a trade already exists in Excel (same Symbol + Date + Entry Price), skip it and note in audit log.

**Why it matters:** Protects against running the weekly update twice by accident and double-counting trades.

---

### 📋 REQ-020224_01: Schwab OAuth 2.0 Authentication + Token Management

**Status**: Planned — Target Feb 25, 2026  
**Priority**: Critical (blocks everything else)  
**Target Version**: Schwab API v1.0  
**Blocker**: Callback URL propagation — clears Feb 25 morning

**What it does:**
- Guides through one-time browser login to get authorization code
- Exchanges auth code for access token + refresh token
- Saves tokens securely to local config file
- Auto-refreshes access token before it expires (30-minute window)
- Handles refresh token renewal (7-day expiry)

**Files:**
- `P_020_Schwab_Auth.py` — Initial OAuth flow
- `P_020_Schwab_Token_Manager.py` — Ongoing token refresh
- `config\P_020_schwab_config.json` — Secure local credential store

**App Details:**
- App Name: AJZ-Strategies-P020
- Callback URL: `https://127.0.0.1`
- Portal: developer.schwab.com

---

### 📋 REQ-020224_02: Schwab Trade History Pull

**Status**: Planned — Target March 1–7, 2026  
**Priority**: High  
**Target Version**: Schwab API v1.0  
**Depends On**: REQ-020224_01 (auth)

**What it does:**
- Pulls transactions from Schwab API for a specified date range
- Applies TRD filter (REQ-020221_01)
- Applies 10-minute consolidation (REQ-020221_04)
- Detects orphaned transactions (REQ-020221_02)
- Runs auto-match against Tracker Dashboard (carries logic from REQ-020126_01)
- Outputs clean CSV in exact format Excel templates expect
- Generates audit log (REQ-020221_03)

**Schwab API Endpoint:** `GET /trader/v1/accounts/{accountNumber}/transactions`

**Replaces:** TOS CSV export + `P_020_TOS_Parser_v2.2.py` entirely

---

### 📋 REQ-020224_03: Schwab Positions + Balances Pull

**Status**: Planned — Target March 8–14, 2026  
**Priority**: Medium  
**Target Version**: Schwab API v1.0  
**Depends On**: REQ-020224_01 (auth)

**What it does:**
- Pulls current open positions from Schwab API
- Pulls account balance, buying power, cash available
- Outputs simple summary report (CSV or console)

**Schwab API Endpoints:**
- `GET /trader/v1/accounts/{accountNumber}/positions`
- `GET /trader/v1/accounts/{accountNumber}`

---

### 📋 REQ-020224_04: Weekly Automated Update (One-Click)

**Status**: Planned — Target March 15–31, 2026  
**Priority**: High  
**Target Version**: Phase 3  
**Depends On**: REQ-020224_01, REQ-020224_02

**What it does:**
Full one-click weekly workflow:
1. Refresh token (auto)
2. Pull transactions since last run date
3. Apply all filters and consolidations
4. Auto-match to Tracker Dashboard
5. Append to Excel logs (preserve formulas)
6. Generate audit log
7. Update last-run date tracker

**Files:**
- `P_020_Weekly_Update.py` — Master orchestration script
- `P_020_Weekly_Update.bat` — One-click runner
- `data\api_pulls\P_020_last_run.json` — Tracks last pull date for incremental updates

---

## Phase 4 Enhancements (Planned ~April 2026+)

- [ ] System comparison: P_115 vs P_116 vs P_117 vs P_118 vs P_300
- [ ] Win rate trends over time
- [ ] Risk metrics: Sharpe ratio, max drawdown, profit factor
- [ ] Time-based analysis: monthly, weekly, by market regime
- [ ] Weekly performance reports (auto-emailed)
- [ ] Actionable insights dashboard

---

## How to Submit New Enhancements

1. **Add a row** to the table above with:
   - Next sequential Req ID (format: YYMMDD_##)
   - Brief description
   - Today's date in "Date Submitted"
   - Leave other fields blank

2. **Create detailed section** below the table with:
   - Full requirement explanation (plain English)
   - Current behavior vs. desired behavior
   - Benefits and use cases
   - Technical considerations
   - Edge cases
   - Testing checklist

3. **Update status** as requirement moves through lifecycle

---

*Document Created: 2026-02-01*  
*Last Updated: 2026-02-24*  
*Owner: Anthony (AJZ Strategies LLC)*  
*Project: P_020 AJZ Strategies Performance Analysis System*
