# P_115 TOS Parser v2.0 - User Guide

## Overview
Automated parser that extracts trades from ThinkorSwim (TOS) Account Statement CSV files and formats them ready to paste directly into your P_115 Stock and Options trading logs.

**No more manual data entry!** 🎉

---

## What It Does

### Input:
ThinkorSwim Account Statement CSV export (the file with one giant DESCRIPTION column containing everything)

### Output:
Two clean CSV files ready to paste into Excel:
1. `*_OPTIONS_IMPORT.csv` → Paste into `P115__Paper_Options_Log_v2.xlsx`
2. `*_STOCKS_IMPORT.csv` → Paste into `P_115__Paper_Stock_Log-V4.xlsx`

---

## Features

✅ **Parses the "One Field" Problem**: Extracts all trade details from TOS's packed DESCRIPTION field  
✅ **Auto-Detects Trade Type**: Separates stock trades from option trades  
✅ **Matches Entries & Exits**: Automatically pairs BOT trades with SOLD trades  
✅ **Calculates Hold Time**: Computes # of Days between entry and exit  
✅ **Tracks Commissions**: Sums all fees (commissions + misc fees)  
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
python P_115_TOS_Parser_v2.py <your_tos_file.csv>
```

**Example:**
```bash
python P_115_TOS_Parser_v2.py 2026-01-28_AJZ_Strategies_YTD_AccountStatement.csv
```

### Step 3: Review Output
The parser creates two files:
```
2026-01-28_AJZ_Strategies_YTD_AccountStatement_OPTIONS_IMPORT.csv
2026-01-28_AJZ_Strategies_YTD_AccountStatement_STOCKS_IMPORT.csv
```

### Step 4: Paste into Excel
1. Open the `_OPTIONS_IMPORT.csv` file
2. Select all rows (Ctrl+A)
3. Copy (Ctrl+C)
4. Open `P115__Paper_Options_Log_v2.xlsx`
5. Go to the next empty row (after your last trade)
6. Paste (Ctrl+V)

**Repeat for stocks file → Stock log**

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

## What the Parser Does NOT Do

❌ **Does not calculate P&L** - Your Excel formulas handle this  
❌ **Does not assign trading system** - Defaults to "TOS_Import", you update manually  
❌ **Does not handle partial exits** - Only captures first exit (Exit #1)  
❌ **Does not parse complex corporate actions** - Focuses on BOT/SOLD trades only  

---

## Example Output

### Input (TOS DESCRIPTION field):
```
BOT +2 QBTS 100 16 JAN 26 27 CALL @2.32 CBOE
SOLD -2 QBTS 100 16 JAN 26 27 CALL @3.14 NASDAQ
```

### Output (Options Log format):
```csv
Symbol,System,Trade Type,Long,Trade Date,Entry Price,Contracts,Exit #1,# Exited,Exit Date,# of Days,Comm.
QBTS,TOS_Import,CALL,Long,1/2/26,2.32,2.0,3.14,2.0,1/5/26,3.0,2.65
```

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

---

## Advanced Usage

### Custom System Assignment
After importing, update the "System" column:
- P_115 → Buy The Dip entries
- P_116 → Options Income Launchpad
- P_117 → External recommendations
- P_118 → Eddie Z Breakouts
- P_300 → VantagePoint signals

### Handling Multiple Exits
The parser only captures Exit #1. For trades with multiple exits:
1. Import as-is
2. Manually add Exit #2 data in Excel
3. Excel formulas will auto-calculate totals

---

## File Locations (Recommended)

### In Your P_115 Project Structure:
```
P_115_BuytheDipTradingSystem/
├── python/parsers/
│   └── P_115_TOS_Parser_v2.py          ← Place parser here
├── data/tos_exports/account_statements/
│   └── 2026-01-28_*.csv                ← TOS exports here
├── data/processed/
│   ├── *_OPTIONS_IMPORT.csv            ← Outputs go here
│   └── *_STOCKS_IMPORT.csv
└── tracking_logs/paper_trading/
    ├── P115__Paper_Options_Log_v2.xlsx ← Import into these
    └── P_115__Paper_Stock_Log-V4.xlsx
```

---

## Success Metrics

From your test run:
- ✅ **167 transactions** loaded
- ✅ **44 option trades** parsed
- ✅ **11 stock trades** parsed
- ✅ **26 complete positions** created
- ✅ **22 option imports** ready
- ✅ **4 stock imports** ready

---

## Version History

### v2.0 (2026-01-28)
- Complete rewrite for P_115 project integration
- Maps directly to Excel log columns
- Auto-matches entries with exits
- Separate outputs for stocks and options
- Handles TOS CSV format with 3 header rows

### v1.0 (Original)
- Basic XML/CSV parsing
- Generic output format

---

## Support

**Issues?** Check these first:
1. Python 3.8+ installed?
2. pandas and numpy installed?
3. TOS file is a CSV (not XLS or XLSX)?
4. File path is correct?

**Still stuck?** Review the "Troubleshooting" section above.

---

## Future Enhancements

Planned features:
- [ ] GUI interface (drag & drop)
- [ ] Auto-detect trading system based on patterns
- [ ] Direct Excel integration (no copy/paste)
- [ ] Handle partial exits automatically
- [ ] Integration with daily workflow automation

---

*Last Updated: 2026-01-28*  
*Version: 2.0*  
*Author: Anthony (AJZ Strategies)*
