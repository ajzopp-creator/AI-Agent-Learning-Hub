# P_020 AJZ Strategies Performance Analysis System
## Project Plan v3.0 — ACCURATE CURRENT STATE
**Updated:** February 24, 2026  
**Owner:** Tony (AJZ Strategies LLC)  
**Environment:** p140 conda (`C:\Users\Trader\.conda\envs\p140\python.exe`)

---

## 🎯 PROJECT MISSION

Automate weekly trading performance tracking for AJZ Strategies LLC — eliminating manual data entry, ensuring accuracy, and freeing time for what matters (golf and fishing).

**Original approach:** Parse TOS CSV account statement exports → Excel  
**New approach:** Pull directly from Schwab API → Excel (automated weekly)

---

## ✅ PHASE 1 — COMPLETED (January–February 2026)

### Parser v2.1 — Production Ready ✅
- Processes TOS CSV exports (300+ transactions)
- Aggregates multiple fills, captures Exit #1 and Exit #2
- Handles both live (P_020) and paper (D_020) accounts
- **Status:** Production, working

### P_020_AccountParser.bat — Production Ready ✅
- Simplified batch interface, auto-detects live vs paper
- UTF-8 encoding fix applied
- **Status:** Production, working

### Excel Master Templates ✅
- **Options Log:** 27 columns, 3 exits supported
- **Stock Log:** 25 columns, 2 exits supported
- Formula columns identified and protected on import
- **Status:** Complete

### Auto-Match Trading System (REQ-020126_01) ✅
- Reads Tracker Dashboard → matches Symbol + Date → fills System column
- Falls back to "TOS_Import" if no match found
- Column detection handles both "Symbol" and "Buy" column naming
- **Status:** Coded and tested with real data

### Formula Preservation on Import ✅
- Options formula columns protected: M, Q, U, W, Y, Z, AA
- Stock formula columns protected: J, N, P, Q, S, T
- Paste Special → Values only for trade data columns
- **Status:** Working

### Environment Stabilization ✅
- All projects standardized on p140 conda environment
- P_010 batch files updated to use p140 (removed fragile root venv)
- ClaudeCleanShutdown.bat implemented and registered as Windows shutdown script
- **Status:** Complete

---

## 🚫 PHASE 1 — RETIRED

### TOS CSV Account Statement Processing
**Decision:** Retire in favor of Schwab API direct pull  
**Reason:** API eliminates manual export step entirely — cleaner, faster, automatable  
**Retained from this work:** Excel templates, formula protection logic, auto-matching logic  
**Files to archive (not delete):**
- `P_020_TOS_Parser_v2.py`
- `P_020_TOS_Parser_v2.2.py`
- `P_020_AccountParser.bat`
- `P_020_Trade_Import_Enhanced.py`

---

## ⚠️ HANGING ENHANCEMENTS — DECISION NEEDED

These were documented for Parser v2.3 but the parser is now being retired. Decide: **carry forward to API version** or **close as N/A**.

| Req ID | Description | Recommendation |
|--------|-------------|----------------|
| v2.3-01 | Filter to TRD transactions only | ✅ Carry forward — apply to API transaction filter |
| v2.3-02 | Position tracking for orphaned transactions | ✅ Carry forward — critical for weekly automation |
| v2.3-03 | Consolidated audit log for dropped records | ✅ Carry forward — needed for reconciliation |
| v2.3-04 | 10-minute window consolidation for same-symbol buys | ✅ Carry forward — still applies to API data |
| v2.3-05 | Cross-reference audit log with Excel for weekly automation | ✅ Carry forward — core to Phase 4 |

**Action:** Update Future Enhancements Tracker to reassign these from "Parser v2.3" to "Schwab API v1.0"

---

## 🔵 PHASE 2 — SCHWAB API INTEGRATION (Starting ~February 25, 2026)

### 2A — Authentication (Next Session — Feb 25)
**Blocker:** Callback URL correction propagating overnight (resolves Feb 25 morning)  
**Callback URL:** `https://127.0.0.1`  
**App:** AJZ-Strategies-P020 on developer.schwab.com  

**Deliverables:**
- `P_020_Schwab_Auth.py` — Full OAuth 2.0 flow, saves tokens to local config
- `P_020_Schwab_Token_Manager.py` — Auto-refresh (tokens expire 30 min, refresh tokens 7 days)
- `P_020_schwab_config.json` — Secure local credential store (gitignored)

**Test:** Successfully retrieve access token and refresh token

### 2B — Trade History Pull (Phase 2, Week 1)
**Goal:** Replace TOS CSV export entirely  
**Schwab API Endpoint:** `/trader/v1/accounts/{accountNumber}/transactions`  

**Deliverables:**
- `P_020_Schwab_Trade_Pull.py` — Pull transactions for date range
- Output: Same clean CSV format Excel templates already expect
- Apply v2.3 enhancements: TRD filter, 10-min window consolidation, orphan detection

**Test:** Pull YTD transactions, verify output matches what TOS parser produced

### 2C — Positions & Balances Pull (Phase 2, Week 2)
**Goal:** Real-time account snapshot  
**Schwab API Endpoints:**
- `/trader/v1/accounts/{accountNumber}/positions`
- `/trader/v1/accounts/{accountNumber}`

**Deliverables:**
- `P_020_Schwab_Positions.py` — Current open positions, account value, buying power
- Simple summary output (CSV or console report)

---

## 🟢 PHASE 3 — WEEKLY AUTOMATION (~March 2026)

**Goal:** Fully automated weekly workflow — zero manual steps

**Weekly flow:**
```
Monday Morning (or Friday EOD)
  ↓
P_020_Weekly_Update.bat  (one click)
  ↓
Token refresh (auto)
  ↓
Pull transactions since last run
  ↓
Apply TRD filter + 10-min consolidation
  ↓
Auto-match to Tracker Dashboard
  ↓
Append to Excel logs (preserve formulas)
  ↓
Generate audit log of any orphaned/unmatched trades
  ↓
Done. ✅
```

**Deliverables:**
- `P_020_Weekly_Update.py` — Master orchestration script
- `P_020_Weekly_Update.bat` — One-click runner
- Audit log: `P_020_Weekly_Audit_YYYYMMDD.txt`
- Last-run tracker: `P_020_last_run.json` (stores last pull date for incremental updates)

---

## 🔵 PHASE 4 — PERFORMANCE ANALYSIS (~April 2026+)

- System comparison: P_115 vs P_116 vs P_117 vs P_118 vs P_300
- Win rate trends over time
- Risk metrics: Sharpe ratio, max drawdown, profit factor
- Time-based analysis: monthly, weekly, by market regime
- Weekly performance reports

---

## 📋 UPDATED REQUIREMENTS TRACKER

| Req ID | Description | Status | Target |
|--------|-------------|--------|--------|
| 020126_01 | Auto-match Tracker Dashboard → System column | ✅ Complete | v2.2 |
| 020207_01 | Excel import with formula preservation | ✅ Complete | v2.2 |
| v2.3-01 | Filter to TRD transactions only | 🔄 Carry to API | Schwab v1.0 |
| v2.3-02 | Orphaned transaction detection | 🔄 Carry to API | Schwab v1.0 |
| v2.3-03 | Consolidated audit log | 🔄 Carry to API | Schwab v1.0 |
| v2.3-04 | 10-minute buy consolidation window | 🔄 Carry to API | Schwab v1.0 |
| v2.3-05 | Audit log cross-reference for automation | 🔄 Carry to API | Phase 3 |
| NEW-01 | Schwab OAuth 2.0 authentication + token management | 📋 Planned | Phase 2A |
| NEW-02 | Schwab trade history pull (replace TOS CSV) | 📋 Planned | Phase 2B |
| NEW-03 | Schwab positions + balances pull | 📋 Planned | Phase 2C |
| NEW-04 | Weekly automated update (one-click) | 📋 Planned | Phase 3 |

---

## 📁 FILE STRUCTURE GOING FORWARD

```
P_020_AJZStrategies_PerformanceAnalysisSystem\
│
├── python\
│   ├── parsers\              ← ARCHIVE (TOS parser retired)
│   │   ├── P_020_TOS_Parser_v2.py       [archived]
│   │   ├── P_020_TOS_Parser_v2.2.py     [archived]
│   │   └── P_020_Trade_Import_Enhanced.py [archived]
│   │
│   └── schwab_api\           ← NEW (active development)
│       ├── P_020_Schwab_Auth.py
│       ├── P_020_Schwab_Token_Manager.py
│       ├── P_020_Schwab_Trade_Pull.py
│       ├── P_020_Schwab_Positions.py
│       └── P_020_Weekly_Update.py
│
├── data\
│   ├── tos_exports\          ← ARCHIVE (no longer adding new files)
│   ├── processed\            ← ARCHIVE
│   └── api_pulls\            ← NEW
│       ├── live\
│       └── paper\
│
├── config\                   ← NEW (gitignored)
│   └── P_020_schwab_config.json
│
├── tracking_logs\
│   ├── live\                 → C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
│   └── paper\
│
├── audit_logs\               ← NEW
│   └── P_020_Weekly_Audit_YYYYMMDD.txt
│
└── docs\
    ├── P_020_PROJECT_PLAN_v3.md          ← THIS FILE
    ├── P_020_Future_Enhancements_Tracker.md
    └── [archived TOS docs]
```

---

## ⏱️ REALISTIC TIMELINE

| Phase | Target Date | Status |
|-------|-------------|--------|
| Phase 1 — TOS Parser + Excel Templates | Jan–Feb 2026 | ✅ Complete |
| Phase 2A — Schwab Auth | Feb 25, 2026 | ⏳ Waiting on URL propagation |
| Phase 2B — Trade History Pull | Mar 1–7, 2026 | 📋 Planned |
| Phase 2C — Positions Pull | Mar 8–14, 2026 | 📋 Planned |
| Phase 3 — Weekly Automation | Mar 15–31, 2026 | 📋 Planned |
| Phase 4 — Performance Analysis | April 2026+ | 📋 Planned |

---

## 🎯 SUCCESS DEFINITION

**We're done when:**
- Monday morning = one click → Excel logs updated automatically
- Zero manual TOS exports
- Zero manual copy/paste
- Zero manual system name updates
- Audit log flags anything that needs attention
- More time for golf and fishing ⛳🎣

---

*Version: 3.0*  
*Updated: February 24, 2026*  
*Status: Active*  
*Next Action: Feb 25 — Schwab OAuth test when callback URL propagates*
