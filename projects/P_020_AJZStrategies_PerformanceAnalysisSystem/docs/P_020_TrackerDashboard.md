# P_020 — Tracker Dashboard
**File:** P_020_TrackerDashboard.md
**Location:** C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_TrackerDashboard\
**Created:** April 13, 2026
**Version:** v1.0 (Draft)
**Status:** DRAFT — Pending Tony's Review & Edits
**Next Review:** TBD

---

## 1. Project Overview

### 1.1 Purpose

P_020 is a **read-only performance dashboard** that ingests the unified 27-column trade tracker and surfaces actionable visibility into open paper trades, live positions, and historical outcomes. The primary use case is **stop price monitoring** — ensuring every open or simulated trade has a defined stop level that can be reviewed at a glance without opening the raw tracker.

P_020 does **not** generate signals, score tickers, or replace any strategy workflow. It is a reporting layer only.

### 1.2 Scope

**What P_020 Covers:**
- Import pipeline from 27-column tracker (Excel or CSV)
- Stop price display and alert thresholds for open/paper trades
- Position summary: entry, target, stop, R:R, status
- Strategy-level performance summary (win rate, avg R:R by source)
- Data quality flags (missing stops, incomplete rows)

**What P_020 Does NOT Cover:**
- Signal generation or scoring (→ P_115, P_116, P_117, P_118)
- Position sizing calculations (→ STEP 2 workflow)
- Options chain analysis (→ STEP 3 workflow)
- Account balance management (→ P_000)
- Market posture (→ P_010)

### 1.3 Project Details

| Field | Value |
|---|---|
| Start Date | April 2026 |
| Current Status | Draft / Planning |
| Primary AI Engine | Claude.ai |
| Primary Platform | Python + Excel or standalone HTML dashboard |
| Project Location | C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_TrackerDashboard\ |
| Depends On | Tracker_Log_Schema_v9_4_0_1.md (27-column schema) |
| Related Projects | P_000 (parameters), P_010 (posture), P_115/116/117/118 (signal sources) |

---

## 2. Stop Price Architecture

### 2.1 Background

The 27-column tracker schema includes two stop-related columns:

| Col # | Column Name | Definition |
|---|---|---|
| **20** | **SLLevel** | ATR-based calculated stop loss (output of STEP 2 formula) |
| **21** | **StopLevel** | Technical/chart-based hard stop (analyst-set key support level) |

Prior to P_020, StopLevel was defined as "same as SLLevel in current implementation." With P_020, these columns are **formally differentiated** and both must be populated on all BUY and ASYM rows before dashboard import.

### 2.2 Stop Price Hierarchy

The import pipeline applies this priority logic when resolving a stop price for display:

```
IF StopLevel != "--"
    → USE StopLevel   (chart-based, precision stop)
ELSE IF SLLevel != "--"
    → USE SLLevel     (ATR fallback, acceptable substitute)
ELSE
    → FLAG as INCOMPLETE  (data quality issue — row shown in red)
```

### 2.3 Column Population Rules (Effective Immediately)

Applies to all STEP 2 outputs for BUY and ASYM verdicts:

| Column | Required? | Source | Notes |
|---|---|---|---|
| **EntryPrice** | YES | STEP 2 output | Simulated or actual entry |
| **TPLevel** | YES | STEP 2 output | T1 target price |
| **SLLevel** | YES | STEP 2 formula | Entry − (ATR × multiplier) |
| **StopLevel** | YES | Analyst decision | Chart support / key technical level |
| **RiskPct** | YES | STEP 2 calculation | Capital deployed / account balance |

**Rule:** Neither SLLevel nor StopLevel may remain `--` on any BUY or ASYM row after STEP 2.

**Exception:** `No Signal` rows — both columns remain `--` (correct, expected).

### 2.4 Divergence Between StopLevel and SLLevel

When StopLevel and SLLevel differ, the dashboard shows **both** and flags the gap:

```
Stop Display Example:
  Chart Stop:  $47.20  (StopLevel — hard floor, technical key level)
  ATR Stop:    $46.85  (SLLevel — formula-based)
  Gap:         $0.35   [< $1.00 = NORMAL | > $1.00 = FLAG FOR REVIEW]
```

If the gap exceeds $1.00 (or 2% of entry, whichever is smaller), the dashboard highlights the row for Tony's review. This catches cases where the ATR stop and the chart stop are misaligned — a potential sign that the setup's risk parameters need adjustment.

---

## 3. Import Pipeline

### 3.1 Source File

| Parameter | Value |
|---|---|
| Source | 27-column tracker (Excel .xlsx or .csv export) |
| Sheet | Unified log (all strategies in one table) |
| Header Row | Row 1 (column names) |
| Date Format | M/D/YYYY |
| Delimiter | Tab (if CSV) |

### 3.2 Column Mapping (27-Column → Dashboard)

The import maps these columns from the tracker schema:

| Dashboard Field | Source Column | Col # | Notes |
|---|---|---|---|
| Date | Date | 1 | Parse as date |
| Ticker | Symbol | 2 | Uppercase |
| Strategy | SignalSource | 3 | P_115/116/117/118 |
| Verdict | Step1Verdict | 4 | BUY/ASYM/No Signal |
| Pattern | PatternType | 5 | Per strategy rules |
| Market | MarketDirection | 10 | From P_010 risk_mode |
| Fund | FundamentalsTier | 12 | 0–4 |
| Anal | AnalysisTier | 13 | 1–4 |
| Traded | Traded | 17 | Y/N/P |
| Entry | EntryPrice | 18 | Price |
| Target | TPLevel | 19 | T1 price |
| ATR Stop | SLLevel | 20 | Formula stop |
| **Chart Stop** | **StopLevel** | **21** | **Key technical level** |
| Risk% | RiskPct | 22 | % of account |
| Balance | AccountBalance | 23 | Risk basis |
| Outcome | Outcome | 24 | Pending/TP Hit/SL Hit |
| Notes | SimulationNotes | 26 | Sizing detail |
| Comments | Comments | 27 | Source / context |

### 3.3 Filtering Rules at Import

The pipeline applies these filters to build the dashboard views:

```python
# Open / Active positions (primary view)
open_trades = df[
    (df['Outcome'] == 'Pending') &
    (df['Step1Verdict'].isin(['BUY', 'ASYM'])) &
    (df['Traded'].isin(['Y', 'N', 'P']))
]

# Paper trades only
paper_trades = df[
    (df['Traded'] == 'N') &
    (df['Outcome'] == 'Pending')
]

# Completed trades (for performance view)
closed_trades = df[
    df['Outcome'].isin(['TP Hit', 'SL Hit', 'Partial Close', 'Expired'])
]

# Data quality flags
missing_stops = df[
    (df['Step1Verdict'].isin(['BUY', 'ASYM'])) &
    (df['StopLevel'] == '--') &
    (df['SLLevel'] == '--')
]
```

### 3.4 Derived Calculations at Import

The pipeline calculates these fields (not stored in tracker, computed on load):

| Field | Formula | Notes |
|---|---|---|
| R:R Planned | (TPLevel − EntryPrice) / (EntryPrice − StopLevel) | Uses StopLevel first, SLLevel fallback |
| Distance to Stop % | (EntryPrice − StopLevel) / EntryPrice × 100 | How far from entry to stop |
| Distance to Target % | (TPLevel − EntryPrice) / EntryPrice × 100 | How far from entry to T1 |
| Stop Source | "Chart" if StopLevel != "--", else "ATR" | Flags which stop is active |
| Stop Gap | abs(StopLevel − SLLevel) | Alert if > $1.00 or > 2% entry |

---

## 4. Dashboard Views

### 4.1 View 1: Open Positions Monitor (Primary)

Displays all Pending trades (Traded = Y, N, or P) with full stop visibility.

**Columns Shown:**
```
Date | Ticker | Strategy | Verdict | Entry | Target | Chart Stop | ATR Stop |
Stop Source | R:R Planned | Risk% | Outcome | Notes
```

**Color Coding:**
- 🟢 Green row — BUY, Chart Stop populated, R:R ≥ 2:1
- 🟡 Yellow row — ASYM, or Stop Source = "ATR" (no chart stop set)
- 🔴 Red row — Stop missing entirely (data quality flag)

### 4.2 View 2: Paper Trade Tracker

Paper trades only (Traded = N, Outcome = Pending). Same columns as View 1 with additional "Days Open" field (today − Date).

**Use Case:** Morning review — scan all open simulated trades for stop proximity before market open.

### 4.3 View 3: Performance Summary

Closed trades summary by strategy.

```
Strategy  | Total | Wins | Losses | Win% | Avg R:R | Notes
P_115     |   --  |  --  |   --   |  --% |   --    |
P_116     |   --  |  --  |   --   |  --% |   --    |
P_117     |   --  |  --  |   --   |  --% |   --    |
P_118     |   --  |  --  |   --   |  --% |   --    |
TOTAL     |   --  |  --  |   --   |  --% |   --    |
```

Win = Outcome contains "TP Hit"
Loss = Outcome contains "SL Hit"

### 4.4 View 4: Data Quality Report

Flags rows that violate data integrity rules before they corrupt the dashboard.

| Flag | Condition | Action |
|---|---|---|
| MISSING STOP | BUY/ASYM row, both SLLevel and StopLevel = "--" | Block from dashboard until fixed |
| MISSING ENTRY | BUY/ASYM row, EntryPrice = "--" | Flag but show row |
| MISSING TARGET | BUY/ASYM row, TPLevel = "--" | Flag but show row |
| POOR R:R | Calculated R:R < 2.0 | Highlight yellow |
| STOP GAP | abs(StopLevel − SLLevel) > $1.00 | Highlight for review |
| ORPHAN ROW | Step1Verdict = BUY but Traded = "--" | Flag as incomplete |

---

## 5. File Structure

```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_TrackerDashboard\
│
├── P_020_TrackerDashboard.md          ← This document
├── config\
│   └── P_020_Config.json              ← Dashboard config (paths, thresholds)
├── src\
│   ├── P_020_import_pipeline.py       ← Reads tracker, applies filters, computes derived fields
│   ├── P_020_dashboard.py             ← Renders dashboard views
│   └── P_020_data_quality.py          ← Data quality checks and flags
├── output\
│   └── P_020_Dashboard_[DATE].html    ← Daily snapshot export (optional)
└── logs\
    └── P_020_import_log.txt           ← Import errors and warnings
```

---

## 6. Configuration

### P_020_Config.json (Template)

```json
{
  "version": "1.0",
  "last_updated": "2026-04-13",

  "source": {
    "tracker_path": "C:\\Users\\Trader\\[PATH_TO_TRACKER.xlsx]",
    "sheet_name": "Trades",
    "header_row": 1,
    "date_column": "Date",
    "date_format": "M/D/YYYY"
  },

  "stop_price": {
    "primary_column": "StopLevel",
    "fallback_column": "SLLevel",
    "gap_alert_dollars": 1.00,
    "gap_alert_pct": 0.02
  },

  "thresholds": {
    "min_rr_ratio": 2.0,
    "warn_days_open": 20,
    "max_days_open": 45
  },

  "display": {
    "open_trades_view": true,
    "paper_trades_view": true,
    "performance_summary": true,
    "data_quality_report": true
  }
}
```

---

## 7. Implementation Phases

### Phase 1 — Stop Price Enforcement (Immediate)
- Claude populates both SLLevel and StopLevel on every STEP 2 output
- No tool changes required — workflow discipline only
- Target: All new BUY/ASYM rows from today forward

### Phase 2 — Import Pipeline (Next Build)
- Python script reads tracker, applies column mapping, computes derived fields
- Outputs clean DataFrame for dashboard or simple console report
- Target: First working version within current quarter

### Phase 3 — Dashboard UI (After Pipeline Validated)
- HTML or Excel pivot-style views for the four dashboard sections
- Daily snapshot export option
- Target: Q2–Q3 2026

---

## 8. Critical Rules

1. **StopLevel ≠ SLLevel** — they serve different purposes. Chart stop is set by analyst judgment; ATR stop is formula output. Never conflate.
2. **Dashboard is read-only** — it never modifies the tracker. All edits go through the normal STEP 1/2/3 workflow.
3. **Missing stop = data quality error** — not a display formatting choice. Rows without any stop are blocked from the open positions view until corrected.
4. **27-column schema is NOT extended by P_020** — all derived fields (R:R, Stop Source, Gap) are computed at import time and never written back to the tracker.
5. **Paper trade stop = same discipline as live trade** — there is no relaxed standard for simulated entries. If it would get a stop in a live trade, it gets a stop as a paper trade.

---

## 9. Version History

| Version | Date | Notes |
|---|---|---|
| v1.0 | 4/13/2026 | Initial draft — stop price architecture, import pipeline, four dashboard views |

---

*End of P_020_TrackerDashboard.md*
