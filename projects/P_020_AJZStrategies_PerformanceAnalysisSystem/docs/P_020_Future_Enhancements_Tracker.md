# P_020 Future Enhancements Tracker

## Purpose
This document tracks all enhancement requests for the P_020 TOS Parser system. Each requirement is assigned a unique ID, documented, approved, and tracked through implementation.

---

## Enhancement Request Table

| Req ID | Requirement Description | Date Submitted | Date Approved | Date Implemented | Status | Project Version |
|--------|------------------------|----------------|---------------|------------------|--------|-----------------|
| 020126_01 | Auto-match Tracker Dashboard signals to assign correct System instead of defaulting to "TOS_Import" | 2026-02-01 | 2026-02-07 | - | Approved | P_020 v2.2 |
| 020207_01 | Auto-import parsed CSV data to Excel logs while preserving formulas | 2026-02-07 | 2026-02-07 | - | In Progress | P_020 v2.2 |

---

## Status Definitions

- **Proposed**: New requirement submitted, awaiting review
- **Approved**: Requirement approved for development
- **In Progress**: Actively being developed
- **Testing**: Under validation/testing
- **Completed**: Implemented and deployed to production
- **Deferred**: Approved but delayed to future version
- **Rejected**: Not approved for implementation

---

## Detailed Requirements

### ðŸ“‹ REQ-020126_01: Auto-Match Trading System from Tracker Dashboard

**Status**: Approved  
**Priority**: Medium  
**Estimated Effort**: 2-3 hours development + 1 hour testing  
**Target Version**: P_020 v2.2

#### What It Does Now:
The parser currently sets all trades to "TOS_Import" in the System column. You have to manually change each trade to the correct system:
- P_115 (Buy The Dip)
- P_116 (Options Income Launchpad) 
- P_117 (External recommendations)
- P_118 (Eddie Z Breakouts)
- P_300 (VantagePoint signals)

#### What We Want:
The parser should automatically fill in the correct System by checking your Tracker Dashboard file.

#### How It Should Work:

1. **Read the Tracker File**
   - Location: `C:\Users\Trader\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TtrackerDashboard_V2.xlsx`
   - Look at two columns: "Buy" (the stock/option symbol) and "Date" (when you bought it)

2. **Match Trades**
   - Compare each trade in the parser output files (`*_OPTIONS_IMPORT.csv` and `*_STOCKS_IMPORT.csv`)
   - If the Symbol AND Trade Date match between Tracker Dashboard and import file â†’ Use the Signal Source from Tracker
   - If NO match found â†’ Leave as "TOS_Import"

3. **Fill in System Column**
   - When there's a match, copy the "Signal Source" from Tracker Dashboard into the "System" column
   - This eliminates manual data entry

#### Example:

**Tracker Dashboard has:**
```
Symbol: QBTS
Date: 1/2/2026
Signal Source: P_118
```

**Parser output before (current):**
```
Symbol: QBTS
Trade Date: 1/2/2026
System: TOS_Import  â† You have to manually change this
```

**Parser output after (with enhancement):**
```
Symbol: QBTS
Trade Date: 1/2/2026
System: P_118  â† Automatically filled in! âœ“
```

#### Benefits:
- âœ… Saves 2-5 minutes per import session
- âœ… Eliminates manual typing errors
- âœ… Ensures accurate system assignment
- âœ… Makes weekly imports faster

#### Technical Considerations:
- Need to handle date format matching (TOS uses M/D/YY, Tracker might use different format)
- Need to handle option symbols (might have spaces or special formatting)
- Should handle case-insensitive symbol matching (QBTS = qbts)
- What if one trade matches multiple tracker entries? (Use first match? Most recent?)

#### Edge Cases to Handle:
1. **No Tracker file found** â†’ Continue with "TOS_Import" default, show warning message
2. **Symbol found but date doesn't match** â†’ Leave as "TOS_Import"
3. **Date matches but symbol doesn't** â†’ Leave as "TOS_Import"
4. **Multiple matches** â†’ Use the most recent Signal Source
5. **Tracker Dashboard is open/locked by Excel** â†’ Show error, continue with defaults

#### Testing Checklist:
- [ ] Test with live account data (P_020 files)
- [ ] Test with paper account data (D_020 files)
- [ ] Test with no Tracker file present
- [ ] Test with missing columns in Tracker
- [ ] Test with multiple matching entries
- [ ] Verify date formats match correctly
- [ ] Verify option symbols match correctly
- [ ] Test with Tracker file locked by Excel

#### Dependencies:
- Requires `openpyxl` or `pandas` to read Excel files
- Tracker Dashboard must have consistent column names
- Tracker Dashboard location must be accessible from parser script

#### Documentation Updates Needed:
- Update README with new auto-matching feature
- Document required Tracker Dashboard format
- Add troubleshooting section for match failures
- Update "What the Parser Does NOT Do" section (remove manual system assignment)

---

### 📋 REQ-020207_01: Auto-Import to Excel with Formula Preservation

**Status**: In Progress  
**Priority**: High  
**Estimated Effort**: 2 hours development + 1 hour testing  
**Target Version**: P_020 v2.2

#### What It Does Now:
After parser creates CSV files, you must manually:
1. Open CSV in Excel
2. Copy all data (Ctrl+A, Ctrl+C)
3. Navigate to Excel log file
4. Paste Special → Values (Ctrl+Alt+V → V → Enter)
5. Be careful not to overwrite formula columns
6. Close CSV file
7. Verify formulas still work

#### What We Want:
Python script automatically imports CSV data to Excel while preserving formulas in calculated columns.

#### How It Should Work:

1. **Detect Parser Output Files**
   - Location: `data/processed/live/` or `data/processed/paper/`
   - Files: `*_OPTIONS_IMPORT.csv` and `*_STOCKS_IMPORT.csv`

2. **Open Target Excel Logs**
   - Paper Options: `tracking_logs/paper/D_020__Paper_Options_Log_v2.xlsx`
   - Paper Stocks: `tracking_logs/paper/D_020__Paper_Stock_Log-V2.xlsx`
   - Live Options: `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx`
   - Live Stocks: `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx`

3. **Import Data Safely**
   - Clear existing data in columns A-P and R (data columns)
   - **PRESERVE formulas in columns Q, S, T** (calculated columns)
   - Write CSV data row by row
   - Only write to data columns, skip formula columns
   - Save and close Excel file

4. **User Interface**
   - Menu-driven: Choose Options/Stocks, Paper/Live
   - Option to import all at once
   - Show progress and confirmation
   - Handle errors gracefully

#### Example:

**Before (Manual):**
```
1. Parser creates: 2026-01-31_..._OPTIONS_IMPORT.csv
2. You open CSV
3. Copy all → Paste Special Values to Excel
4. Hope you didn't overwrite formulas!
5. Time: 2-3 minutes per file
```

**After (Automated):**
```
1. Parser creates: 2026-01-31_..._OPTIONS_IMPORT.csv
2. Run: python trade_import.py
3. Select: "Import Options → Live"
4. Done! Formulas intact!
5. Time: 10 seconds
```

#### Benefits:
- ✅ Eliminates manual copy/paste (saves 5-10 minutes weekly)
- ✅ Prevents accidentally overwriting formulas
- ✅ Faster workflow (10 seconds vs 2-3 minutes)
- ✅ Reduces human error
- ✅ Can be automated in Phase 2

#### Technical Considerations:
- Requires Python libraries: `openpyxl`, `pandas`
- Must handle Excel file being open/locked (show error)
- Must validate CSV columns match Excel structure
- Should handle missing CSV files gracefully
- Compatible with existing Excel table structure

#### Edge Cases to Handle:
1. **Excel file is open** → Show error, ask user to close Excel
2. **CSV file not found** → Show error, list available files
3. **Column mismatch** → Show warning, attempt best-effort mapping
4. **More than 100 rows** → Truncate and warn (Excel table size limit)
5. **Formula columns missing** → Warn user, but still import data

#### Testing Checklist:
- [ ] Test with options data (paper account)
- [ ] Test with stocks data (paper account)  
- [ ] Test with options data (live account)
- [ ] Test with stocks data (live account)
- [ ] Verify formulas still calculate correctly after import
- [ ] Test with Excel file open (should show error message)
- [ ] Test with missing CSV file (should show error message)
- [ ] Test with >100 rows (should truncate at row 101)
- [ ] Import same file twice (should overwrite cleanly)
- [ ] Verify all 26 stock columns and 20 option columns work

#### Dependencies:
- Python 3.8+ installed
- `openpyxl` library: `pip install openpyxl`
- `pandas` library: `pip install pandas`
- Parser output must have consistent column names
- Excel logs must have standard table structure

#### Documentation Updates Needed:
- Add trade_import.py to python/parsers/ folder
- Update README with import workflow
- Document formula column preservation
- Add troubleshooting guide for import errors

---

## Phase 2 & 3 Enhancements (From Original README)

### Phase 2: Weekly Automation (Planned ~March 2026)
- [ ] Auto-detect new TOS CSV files (watch folder)
- [ ] Run parser automatically on schedule
- [ ] Validate outputs for anomalies
- [ ] Auto-append to Excel logs (with backup)
- [ ] Generate weekly summary report
- [ ] Email/alert notifications

### Phase 3: Performance Analysis (Planned ~April 2026+)
- [ ] System comparison (P_115 vs P_116 vs P_117 vs P_118 vs P_300)
- [ ] Win rate trends over time
- [ ] Risk metrics (Sharpe ratio, max drawdown, profit factor)
- [ ] Time-based analysis (monthly, weekly, by market regime)
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
   - Full requirement explanation (9th grade reading level)
   - Current behavior vs. desired behavior
   - Benefits and use cases
   - Technical considerations
   - Edge cases
   - Testing checklist

3. **Update status** as requirement moves through lifecycle

---

*Document Created: 2026-02-01*  
*Last Updated: 2026-02-07*  
*Owner: Anthony (AJZ Strategies LLC)*  
*Project: P_020 TOS Parser System*
