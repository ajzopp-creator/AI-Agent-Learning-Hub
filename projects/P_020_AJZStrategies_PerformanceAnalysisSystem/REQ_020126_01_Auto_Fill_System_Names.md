# REQ-020126_01: Auto-Fill Trading System Names

## The Problem We're Solving

**Right now:** When you run the parser, every trade gets labeled "TOS_Import" in the System column. Then you have to manually go through and change each one to the real system name (like P_115, P_118, etc.). This takes time and you might make mistakes.

**What we want:** The parser should automatically look up the correct system name and fill it in for you.

---

## How It Will Work (Simple Version)

### Step 1: Parser Looks at Your Trade
```
Your trade: QBTS bought on 1/2/2026
```

### Step 2: Parser Checks Your Tracker Dashboard
The parser opens this file:
```
C:\Users\Trader\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TtrackerDashboard_V2.xlsx
```

It looks for a matching trade:
- Same stock symbol (QBTS)
- Same date (1/2/2026)

### Step 3: Parser Copies the Signal Source
If it finds a match in your Tracker:
```
Tracker says: QBTS on 1/2/2026 → Signal Source is "P_118"
```

The parser copies "P_118" into your import file.

### Step 4: You Paste into Excel
Now when you paste into Excel, the System column already has "P_118" instead of "TOS_Import"!

---

## What Gets Matched?

The parser compares TWO things:

1. **Symbol** - The stock or option name (like QBTS, AAPL, etc.)
2. **Trade Date** - The day you bought it

**Both must match** for the parser to use the Signal Source from your Tracker.

---

## What If There's No Match?

If the parser can't find your trade in the Tracker Dashboard, it does what it does now:
- Fills in "TOS_Import" 
- You update it manually (just like before)

**Nothing breaks!** The parser keeps working even if:
- The Tracker file is missing
- The trade isn't in the Tracker yet
- The dates don't line up exactly

---

## Benefits

### Time Savings
- **Before:** 2-5 minutes updating System names after each import
- **After:** Already filled in correctly!

### Accuracy
- **Before:** Might type "P_155" instead of "P_115" by accident
- **After:** Copies exact text from your Tracker (no typos)

### Less Work
- **Before:** Open import file → Update 10-20 rows → Save → Open Excel → Paste
- **After:** Open import file → Open Excel → Paste (System already correct!)

---

## Example: Before vs After

### BEFORE (Current Way):
```csv
Symbol,System,Trade Date,Entry Price
QBTS,TOS_Import,1/2/26,2.32     ← You change to P_118
AAPL,TOS_Import,1/3/26,180.50   ← You change to P_115
TSLA,TOS_Import,1/3/26,245.00   ← You change to P_300
```

### AFTER (With Enhancement):
```csv
Symbol,System,Trade Date,Entry Price
QBTS,P_118,1/2/26,2.32          ← Already correct! ✓
AAPL,P_115,1/3/26,180.50        ← Already correct! ✓
TSLA,P_300,1/3/26,245.00        ← Already correct! ✓
```

---

## Technical Details (For Implementation)

### Files Involved:
1. **Input 1:** TOS Account Statement CSV (what you export from ThinkorSwim)
2. **Input 2:** Tracker Dashboard Excel file (your signal tracking spreadsheet)
3. **Output:** Import CSV files with System column auto-filled

### Required Changes:
1. Add code to read the Tracker Dashboard Excel file
2. Create a lookup function that matches Symbol + Date
3. Update the System column assignment logic
4. Add error handling if Tracker file is missing or locked

### Python Libraries Needed:
- `pandas` (already installed for parser)
- `openpyxl` (for reading Excel files - may need to install)

### Tracker File Requirements:
Your Tracker Dashboard must have these columns:
- **"Buy"** or **"Symbol"** - Contains stock/option symbol
- **"Date"** or **"Buy Date"** - Contains the trade date
- **"Signal Source"** - Contains the system name (P_115, P_118, etc.)

---

## What Could Go Wrong? (Edge Cases)

### Issue 1: Tracker File Not Found
**What happens:** Parser shows a warning message, continues with "TOS_Import" default  
**What you do:** Nothing - import works normally

### Issue 2: Date Formats Don't Match
**Example:** Tracker has "January 2, 2026" but TOS has "1/2/26"  
**Solution:** Parser converts both to same format before comparing

### Issue 3: Symbol Looks Different
**Example:** Tracker has "QBTS 100C" but TOS has "QBTS"  
**Solution:** Parser strips extra text and compares base symbol only

### Issue 4: Multiple Matches Found
**Example:** You bought QBTS twice on same day with different systems  
**Solution:** Parser uses the FIRST match it finds (or we pick newest one)

### Issue 5: Excel Has File Locked
**What happens:** Tracker Dashboard is open in Excel, parser can't read it  
**Solution:** Parser shows error message, continues with "TOS_Import" default

---

## Testing Plan (Before Going Live)

We'll test with:
- ✅ 10 trades that ARE in Tracker (should auto-fill correctly)
- ✅ 5 trades that are NOT in Tracker (should stay "TOS_Import")
- ✅ Tracker file missing (should still work with defaults)
- ✅ Tracker file open in Excel (should show error but keep working)
- ✅ Options trades with complex symbols
- ✅ Different date formats
- ✅ Both P_020 (live) and D_020 (paper) files

**Only deploy to production after all tests pass!**

---

## When Will This Be Ready?

**Status:** Requirement submitted 2/1/2026  
**Estimated time:** 2-3 hours to code + 1 hour to test  
**Target version:** P_020 v2.2  
**Planned release:** March 2026 (along with Phase 2 automation)

---

## Questions or Changes?

If you need changes to this requirement:
1. Update the "P_020_Future_Enhancements_Tracker.md" document
2. Note what changed and why
3. Update the date in that document

---

*Requirement ID: 020126_01*  
*Date Submitted: 2026-02-01*  
*Status: Proposed*  
*Written in: Plain English (9th grade level)*  
*Project: P_020 TOS Parser v2.x*
