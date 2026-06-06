# P_020 Enhanced Workflow - README

## 🎉 **New Features!**

### **REQ-020126_01: Auto-Match System Names** ✅
Parser output now automatically matches trades against your Tracker Dashboard to fill in correct System names (P_115, P_116, P_117, P_118, P_300) instead of defaulting everything to "TOS_Import".

### **REQ-020207_01: Auto-Import to Excel** ✅
New Python script automatically imports parsed CSV data to Excel logs while preserving formulas in calculated columns.

---

## 📦 **New Files**

### **1. P_020_Trade_Import_Enhanced.py**
**Location:** `python/parsers/`

**What it does:**
- Reads parser output CSV files (`*_OPTIONS_IMPORT.csv`, `*_STOCKS_IMPORT.csv`)
- Automatically matches Symbol + Date against Tracker Dashboard
- Fills System column with matched system (P_115/116/117/118/300)
- Imports data to Excel logs
- Preserves formulas in calculated columns (Gain/Loss, ROI, etc.)

**How to use:**
```bash
cd python/parsers
python P_020_Trade_Import_Enhanced.py
```

Then choose from menu:
1. Options → Paper Log
2. Options → Live Log
3. Stocks → Paper Log
4. Stocks → Live Log
5. Import ALL → Paper
6. Import ALL → Live
7. Reload Tracker Dashboard
0. Exit

### **2. P_020_Test_Full_Workflow.bat** (TESTING ONLY)
**Location:** Project root

**What it does:**
- Runs P_020_TOS_Parser_v2.py first
- Then runs P_020_Trade_Import_Enhanced.py
- Complete end-to-end workflow

**How to use:**
```batch
P_020_Test_Full_Workflow.bat "C:\path\to\your\TOS_AccountStatement.csv"
```

**Note:** This is for TESTING only! After testing complete, we'll merge into single production batch file.

---

## 🧪 **Testing Checklist**

### **Phase 1: Test Parser + Import Separately**

#### **Step 1: Test Parser (Existing)**
```batch
cd python\parsers
python P_020_TOS_Parser_v2.py "C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\YOUR_FILE.csv"
```

**Verify:**
- [ ] CSV files created in correct folder (live or paper)
- [ ] Options CSV has 20 columns
- [ ] Stocks CSV has 26 columns
- [ ] System column still shows "TOS_Import" (not matched yet)

#### **Step 2: Test Import Script (New)**
```batch
cd python\parsers
python P_020_Trade_Import_Enhanced.py
```

**Choose option from menu and verify:**
- [ ] Tracker Dashboard loads successfully
- [ ] System names are matched (shows count: "Matched X/Y trades")
- [ ] Excel file opens and imports data
- [ ] Formulas still calculate correctly
- [ ] System column shows matched names (P_115, P_118, etc.)
- [ ] Trades without matches show "TOS_Import"

### **Phase 2: Test Full Workflow Batch File**

#### **Run Complete Workflow**
```batch
P_020_Test_Full_Workflow.bat "C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\YOUR_FILE.csv"
```

**Verify:**
- [ ] Parser runs successfully
- [ ] Import script runs automatically
- [ ] Can choose which logs to import
- [ ] System names are matched correctly
- [ ] Excel formulas preserved
- [ ] No errors in console output

### **Phase 3: Edge Case Testing**

#### **Test Error Handling**
- [ ] Run with Tracker Dashboard file missing (should warn, continue with "TOS_Import")
- [ ] Run with Excel file open (should show error, ask to close Excel)
- [ ] Run with missing CSV file (should show error)
- [ ] Import same file twice (should overwrite cleanly)

#### **Test System Matching**
- [ ] Trade that's in Tracker → Should match system name
- [ ] Trade NOT in Tracker → Should stay "TOS_Import"
- [ ] Trade with date mismatch → Should stay "TOS_Import"
- [ ] Trade with symbol mismatch → Should stay "TOS_Import"

#### **Test Formula Preservation**
- [ ] Options: Column Q (Gain/Loss) still has formula
- [ ] Stocks: Column Q (Gain/Loss) still has formula
- [ ] Stocks: Column R (ROI) still has formula
- [ ] All formulas calculate correctly after import

---

## 📊 **Tracker Dashboard Requirements**

The auto-matching feature requires your Tracker Dashboard to have these columns:

**Required Columns:**
- **Symbol/Buy**: Stock or option symbol (e.g., "QBTS", "AAPL")
- **Date/Buy Date**: Date of trade entry
- **Signal Source**: System name (P_115, P_116, P_117, P_118, P_300)

**Example Tracker Dashboard:**
```
| Buy  | Date       | Signal Source |
|------|------------|---------------|
| QBTS | 1/2/2026   | P_118         |
| AAPL | 1/3/2026   | P_115         |
| TSLA | 1/5/2026   | P_300         |
```

**File Location:**
```
C:\Users\Trader\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TtrackerDashboard_V2.xlsx
```

---

## 🚀 **After Testing Complete**

Once you've tested and verified everything works:

1. **Report Results**
   - Any errors encountered?
   - System matching accuracy?
   - Formula preservation working?
   - Any edge cases found?

2. **Merge into Production**
   - Create single `P_020_AccountParser_v2.2.bat` file
   - Combines parser + import into one command
   - Remove test batch file
   - Update documentation

3. **Update Status**
   - REQ-020126_01: Move from "Approved" → "Testing"
   - REQ-020207_01: Move from "In Progress" → "Testing"
   - After successful testing → "Completed"

---

## 🔧 **Installation Requirements**

### **Python Libraries**
```bash
pip install openpyxl pandas
```

### **File Locations**
All files must be in correct locations:

**Parser:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers\P_020_TOS_Parser_v2.py
```

**Import Script:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers\P_020_Trade_Import_Enhanced.py
```

**Test Batch File:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\P_020_Test_Full_Workflow.bat
```

**Tracker Dashboard:**
```
C:\Users\Trader\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TtrackerDashboard_V2.xlsx
```

---

## ⚠️ **Important Notes**

### **Before Running:**
1. **Backup your Excel logs!** Always backup before testing new import functionality.
2. **Close Excel!** Excel files must be closed before import script runs.
3. **Check Tracker Dashboard** - Make sure it's up to date with recent trades.

### **During Testing:**
1. **Test on Paper account first!** Use paper account logs for initial testing.
2. **Verify each step** - Don't skip verification steps in testing checklist.
3. **Note any issues** - Document errors, warnings, or unexpected behavior.

### **After Testing:**
1. **Keep test batch file** until production merge is complete.
2. **Document results** - Share what worked and what didn't.
3. **Suggest improvements** - Any features or fixes needed?

---

## 📞 **Need Help?**

### **Common Issues:**

**"Tracker Dashboard not found"**
```
Check path: C:\Users\Trader\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TtrackerDashboard_V2.xlsx
If missing → System names will default to "TOS_Import"
```

**"Could not save workbook"**
```
Excel file is open! Close Excel and try again.
```

**"No OPTIONS CSV found"**
```
Parser didn't create output file. Check parser errors.
Make sure you ran parser first!
```

**"Matched 0/14 trades"**
```
Trades not in Tracker Dashboard, or dates don't match.
This is OK - trades will stay as "TOS_Import"
You can update manually in Excel.
```

---

## 🎯 **Success Criteria**

Testing is successful when:

✅ Parser creates CSV files correctly  
✅ Import script loads Tracker Dashboard  
✅ System names are matched for trades in Tracker  
✅ Unmatched trades default to "TOS_Import"  
✅ Excel formulas preserved and calculating  
✅ No data loss or corruption  
✅ Can run workflow repeatedly without errors  
✅ Works for both paper and live accounts  
✅ Works for both options and stocks  

---

*Version: 2.2 (Test)*  
*Date: 2026-02-07*  
*Status: Testing*  
*Author: Anthony (AJZ Strategies LLC)*
