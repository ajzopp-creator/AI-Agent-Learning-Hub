# P_020 TOS Parser v2.1 - User Guide
# Update 02/07/2026 -Use the batch file at project root:
```batch
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem
P_020_AccountParser YOUR_FILENAME.csv
```

## Overview
Automated parser that extracts trades from ThinkorSwim (TOS) Account Statement CSV files and formats them ready to paste directly into your P_020 Stock and Options trading logs.

**No more manual data entry!** 🎉

---

## 🔑 **Understanding P_ vs D_ Designation**

### **Critical Naming Convention:**

#### **P_** = **PRODUCTION** (Live Trading)
- **Tested and approved** for live trading
- Contains real money trades
- Production-ready scripts and files
- Fully validated and verified
- **Example:** P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx

#### **D_** = **DEVELOPMENT** (Paper Trading/Sandbox)
- **Experimental and in development**
- Paper trading / demo account
- Not approved for live use
- Testing and validation phase
- **Example:** D_020__Paper_Options_Log_v2.xlsx

**This applies to ALL project files, scripts, folders, and spreadsheets!**

---

## What It Does

### Input:
ThinkorSwim Account Statement CSV export (the file with one giant DESCRIPTION column containing everything).

**File naming:**
- **Live Account exports:** Start with `P_020`
- **Paper Account exports:** Start with `D_020`

### Output:
Two clean CSV files ready to paste into Excel:
1. `*_OPTIONS_IMPORT.csv` → Paste into appropriate Options Log
2. `*_STOCKS_IMPORT.csv` → Paste into appropriate Stock Log

---

## Target Excel Logs

### **LIVE ACCOUNT (Production):**
**Location:** `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\`

**Files:**
- `P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx` ← Options imports here
- `P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx` ← Stock imports here

**Note:** These files track **real money** trades for AJZ Strategies LLC

### **PAPER ACCOUNT (Development):**
**Location:** `[Project folder]/tracking_logs/paper/`

**Files:**
- `D_020__Paper_Options_Log_v2.xlsx` ← Paper options imports here
- `D_020__Paper_Stock_Log-V2.xlsx` ← Paper stock imports here

**Note:** These files track **simulated** trades for testing strategies

---

## Features

✅ **Parses the "One Field" Problem**: Extracts all trade details from TOS's packed DESCRIPTION field  
✅ **Auto-Detects Trade Type**: Separates stock trades from option trades  
✅ **Handles Multiple Fills**: Aggregates split fills with same REF # (e.g., 2+2=4 contracts)  
✅ **Matches Entries & Exits**: Automatically pairs BOT trades with SOLD trades  
✅ **Captures Partial Exits**: Handles Exit #1 and Exit #2 (up to 2 partial exits)  
✅ **Calculates Hold Time**: Computes # of Days between entry and each exit  
✅ **Tracks Commissions**: Sums ALL fees correctly (commissions + misc fees, including multiple fills)  
✅ **Excel-Ready Format**: Columns match your spreadsheet exactly  

---

## Installation

### Prerequisites:
```bash
python 3.8+
pandas
numpy
```

### Install Dependencies:
```bash
pip install pandas numpy
```

---

## Usage

### Step 1: Export from ThinkorSwim
1. In TOS, go to **Monitor → Account Statement**
2. Set date range (e.g., "Year to Date")
3. Click **Export** → Save as CSV

### Step 2: Run the Parser
```bash
python P_020_TOS_Parser_v2.py <your_tos_file.csv>
```

**Example (Live Account):**
```bash
python P_020_TOS_Parser_v2.py P_020_2026-01-28_AJZ_Strategies_YTD_AccountStatement.csv
```

**Example (Paper Account):**
```bash
python P_020_TOS_Parser_v2.py D_020_2026-01-28_Paper_AccountStatement.csv
```

### Step 3: Review Output
The parser creates two files:
```
P_020_2026-01-28_AJZ_Strategies_YTD_AccountStatement_OPTIONS_IMPORT.csv
P_020_2026-01-28_AJZ_Strategies_YTD_AccountStatement_STOCKS_IMPORT.csv
```

### Step 4: Paste into Excel

#### **For LIVE Account:**
1. Open the `_OPTIONS_IMPORT.csv` file
2. Select all rows (Ctrl+A)
3. Copy (Ctrl+C)
4. Open `P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx`
   - Location: `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\`
5. Go to the next empty row (after your last trade)
6. Paste (Ctrl+V)

**Repeat for stocks file → Stock log**

#### **For PAPER Account:**
1. Follow same process but paste into `D_020__Paper_Options_Log_v2.xlsx` and `D_020__Paper_Stock_Log-V2.xlsx`

---

## Output Format

### Options Output (20 columns):
```
Symbol | System | Trade Type | Long | Trade Date | Entry Price | Contracts |
Exit #1 | # Exited | Exit Date | # of Days | Exit #2 | # Exited2 |
Exit Date3 | # of Days4 | Comm. | Gain/Loss | Trade Comments |
Exit #1 Gain | Exit #2 Gain
```

### Stock Output (26 columns):
```
Symbol | System | Long/Short | Trade Date | Entry Price | Shares |
Exit #1 | # Exited | Exit Date | # of Days | Exit #2 | # Exited2 |
Exit Date3 | # of Days4 | Comm. | Gain/Loss | ROI | Trade Comments |
Exit #1 Gain | Exit #2 Gain | Total Gain | Total ROI % | R:R Ratio |
Win/Loss | Strategy Notes | Review Status
```

---

## Important: How Multiple Fills Are Handled

### **Same REF # = Same Order, Multiple Fills**

When TOS executes an order in multiple fills, **each fill has its own commission**:

```
Example: QBTS Order
REF #1005039452515 (ENTRY ORDER - 2 FILLS):
  Fill 1: 1/2/26  BOT +2 contracts  Misc: $0.02 + Comm: $1.30 = $1.32
  Fill 2: 1/2/26  BOT +2 contracts  Misc: $0.02 + Comm: $1.30 = $1.32
  ────────────────────────────────────────────────────────────
  TOTAL: 4 contracts, Fees: $2.64 ✓

Parser Logic:
  1. Groups both rows by REF # → 4 contracts
  2. Sums both commissions → $1.32 + $1.32 = $2.64 ✓
  3. Creates single entry: 4 contracts @ $2.32, Fees: $2.64
```

**Key Point:** Same REF # means same order but separate executions. **Each execution has fees!**

---

## Example: Complete Trade with Partial Exits

### Input (TOS CSV):
```
1/2/26  REF #1005039452515  BOT +2 QBTS @ $2.32  Fees: $1.32  [Fill 1]
1/2/26  REF #1005039452515  BOT +2 QBTS @ $2.32  Fees: $1.32  [Fill 2]
1/5/26  REF #1005039452517  SOLD -2 QBTS @ $3.14  Fees: $1.33  [Exit 1]
1/6/26  REF #1005059369160  SOLD -2 QBTS @ $4.20  Fees: $1.33  [Exit 2]
```

### Output (Options Log format):
```csv
Symbol,System,Trade Type,Long,Trade Date,Entry Price,Contracts,Exit #1,# Exited,Exit Date,# of Days,Exit #2,# Exited2,Exit Date3,# of Days4,Comm.
QBTS,TOS_Import,CALL,Long,1/2/26,2.32,4.0,3.14,2.0,1/5/26,3.0,4.20,2.0,1/6/26,4.0,5.30
```

### Commission Breakdown:
```
Entry (2 fills):  $2.64  ($1.32 + $1.32)
Exit #1:          $1.33
Exit #2:          $1.33
─────────────────────────
TOTAL:            $5.30 ✓
```

---

## What the Parser Does NOT Do

❌ **Does not calculate P&L** - Your Excel formulas handle this  
❌ **Does not assign trading system** - Defaults to "TOS_Import", you update manually to:
   - P_115 (Buy The Dip)
   - P_116 (Options Income Launchpad)
   - P_117 (External recommendations)
   - P_118 (Eddie Z Breakouts)
   - P_300 (VantagePoint signals)  
❌ **Does not handle 3+ exits** - Only captures Exit #1 and Exit #2  
❌ **Does not parse complex corporate actions** - Focuses on BOT/SOLD trades only  

---

## Troubleshooting

### "Could not find CSV header row"
**Problem**: TOS export format changed  
**Solution**: Open CSV, find line starting with "DATE,TIME,TYPE", note line number, update `csv_start` logic

### "Unparsed: 112"
**Normal**: TOS exports include non-trade transactions (fees, dividends, adjustments)  
**Action**: Ignore - parser only extracts BOT/SOLD trades

### "No option trades to export"
**Check**: Did you trade options in this period?  
**Verify**: Look at raw TOS CSV - are there lines with "CALL" or "PUT"?

### Date Format Warning
**Message**: "Could not infer format..."  
**Status**: Safe to ignore - parser handles it automatically

### Commission Mismatch
**Problem**: "My Schwab.com shows different commission"  
**Explanation**: 
- Schwab might show partial totals (entry + exit #1 only)
- Parser includes ALL fees for complete P&L
- Parser shows: Entry + Exit #1 + Exit #2 = Complete round-trip cost
- This is correct for Excel calculations

---

## Advanced Usage

### Custom System Assignment
After importing, update the "System" column:
- **P_115** → Buy The Dip entries
- **P_116** → Options Income Launchpad
- **P_117** → External recommendations
- **P_118** → Eddie Z Breakouts
- **P_300** → VantagePoint signals

### Handling 3+ Exits
The parser captures Exit #1 and Exit #2. For trades with more exits:
1. Import as-is
2. Manually add Exit #3+ data in Excel
3. Excel formulas will auto-calculate totals

---

## Project Folder Structure

```
P_020_AJZStrategies_PerformanceAnalysisSystem/
├── python/parsers/
│   └── P_020_TOS_Parser_v2.py          ← Parser script
├── data/
│   ├── tos_exports/
│   │   ├── live/                       ← P_020 TOS exports
│   │   └── paper/                      ← D_020 TOS exports
│   └── processed/
│       ├── live/                       ← P_020 import files
│       └── paper/                      ← D_020 import files
├── tracking_logs/
│   ├── live/                           → Links to C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
│   └── paper/
│       ├── D_020__Paper_Options_Log_v2.xlsx
│       └── D_020__Paper_Stock_Log-V2.xlsx
└── docs/
    └── P_020_TOS_Parser_README.md     ← This file
```

**Note:** Live account logs (P_020_*) are maintained in AJZ Strategies LLC business folder

---

## Version History

### v2.1 (2026-01-31) - CURRENT
**Major Fixes:**
- ✅ **CRITICAL FIX:** Corrected commission calculation for multiple fills
  - Now correctly sums fees for each fill (e.g., $1.32 + $1.32 = $2.64)
  - Previous version incorrectly counted commission only once
- ✅ Added Exit #2 capture (handles partial exits properly)
- ✅ Fixed floating point precision (clean 2-decimal numbers)
- ✅ Updated to P_020 naming convention
- ✅ Added P_ vs D_ designation documentation
- ✅ Enhanced error handling for REF # grouping

### v2.0 (2026-01-28)
- Complete rewrite for P_020 project integration
- Maps directly to Excel log columns
- Auto-matches entries with exits
- Separate outputs for stocks and options
- Handles TOS CSV format with 3 header rows

### v1.0 (Original)
- Basic XML/CSV parsing
- Generic output format

---

## Success Metrics

From test runs:
- ✅ **167 transactions** loaded
- ✅ **44 option trades** parsed
- ✅ **11 stock trades** parsed
- ✅ **26 complete positions** created
- ✅ **22 option imports** ready
- ✅ **4 stock imports** ready
- ✅ **Multiple fills aggregated correctly** (QBTS: 2+2=4 contracts ✓)
- ✅ **Partial exits captured** (Exit #1 and Exit #2 ✓)
- ✅ **Commission calculations accurate** ($2.64 entry + $1.33 + $1.33 = $5.30 ✓)

---

## Support

**Issues?** Check these first:
1. Python 3.8+ installed?
2. pandas and numpy installed?
3. TOS file is a CSV (not XLS or XLSX)?
4. File path is correct?
5. Using correct log file (P_020 for live, D_020 for paper)?

**Still stuck?** Review the "Troubleshooting" section above.

---

## Future Enhancements (Phase 2 & 3)

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

## Critical Reminders

### ⚠️ **ALWAYS Verify:**
1. **P_ vs D_** - Are you using the correct files for your account type?
2. **Commission totals** - Parser includes ALL fees (multiple fills + all exits)
3. **System assignment** - Update from "TOS_Import" to actual system (P_115/116/117/118/300)
4. **Date ranges** - Make sure TOS export covers your intended period

### ✅ **Best Practices:**
1. **Backup first** - Always backup Excel logs before pasting new data
2. **Review before paste** - Check output CSVs for accuracy
3. **Update System column** - Don't leave as "TOS_Import"
4. **Document edge cases** - Note any unusual trades for future improvements
5. **Keep raw TOS files** - Store original exports for audit trail

---

*Last Updated: 2026-01-31*  
*Version: 2.1*  
*Author: Anthony (AJZ Strategies LLC)*  
*Status: Production Ready*
