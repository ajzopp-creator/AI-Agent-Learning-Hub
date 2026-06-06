# P_020 Folder Structure - TOS Exports vs Parser Outputs

## 🚨 **CRITICAL: Where Files Go**

---

## 📂 **Folder Structure:**

```
P_020_AJZStrategies_PerformanceAnalysisSystem\
│
├── data\
│   │
│   ├── tos_exports\                    ← TOS EXPORT FILES GO HERE
│   │   ├── live\
│   │   │   └── P_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv  ← TOS EXPORT (you put this here)
│   │   │
│   │   └── paper\
│   │       └── D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv  ← TOS EXPORT (you put this here)
│   │
│   ├── processed\                      ← PARSER OUTPUT FILES GO HERE (automatic)
│   │   ├── live\
│   │   │   ├── P_020_*_OPTIONS_IMPORT.csv  ← PARSER CREATES THIS
│   │   │   └── P_020_*_STOCKS_IMPORT.csv   ← PARSER CREATES THIS
│   │   │
│   │   └── paper\
│   │       ├── D_020_*_OPTIONS_IMPORT.csv  ← PARSER CREATES THIS
│   │       └── D_020_*_STOCKS_IMPORT.csv   ← PARSER CREATES THIS
│   │
│   ├── D_020_2026_AJZ_Strategies_Options_Log_V1.xlsx  ← PAPER EXCEL LOGS
│   └── D_020_2026__AJZ_Strategies_Stock_Log_V1.xlsx   ← PAPER EXCEL LOGS
│
└── python\parsers\
    ├── P_020_TOS_Parser_v2.py
    └── P_020_Trade_Import_Enhanced.py
```

---

## 🎯 **Key Points:**

### **1. TOS Export Files** ❌ **DO NOT HAVE "_IMPORT" IN NAME**
```
✅ CORRECT: D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
✅ CORRECT: P_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv

❌ WRONG: D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement_STOCKS_IMPORT.csv
❌ WRONG: D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement_OPTIONS_IMPORT.csv
          (These are PARSER OUTPUT, not TOS export!)
```

### **2. Parser Output Files** ✅ **ALWAYS HAVE "_IMPORT" IN NAME**
```
✅ Parser creates: *_OPTIONS_IMPORT.csv
✅ Parser creates: *_STOCKS_IMPORT.csv
```

### **3. Where You Save TOS Exports:**
```
Paper account:
Save to: data/tos_exports/paper/

Live account:
Save to: C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
```

---

## ⚠️ **Your Current Issue:**

### **What Happened:**
```
Batch file looked in: data/tos_exports/paper/
Found: D_020_2026-02-07-AJZ Stategies_YTD_AccountStatement_STOCKS_IMPORT.csv
                                                           ^^^^^^^^^^^^^^^^^^^^
                                                           This is PARSER OUTPUT!
```

**The parser tried to parse its own output → ERROR!**

### **Why This Happened:**
One of two reasons:
1. **TOS export file was saved to wrong folder** (saved to `processed/` instead of `tos_exports/`)
2. **Parser output files got mixed with TOS export files** somehow

---

## ✅ **How to Fix:**

### **Step 1: Check Your Folders**
```
Look in: data/tos_exports/paper/

Do you see files with "_IMPORT" in the name?
  - YES → Those shouldn't be there! Move them to processed/paper/
  - NO → Good! Now check if TOS export file is there
```

### **Step 2: Find Your TOS Export File**
```
TOS export file should be named like:
  D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv

NOT like:
  D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement_STOCKS_IMPORT.csv
```

### **Step 3: Move Files to Correct Locations**
```
TOS export (no _IMPORT) → data/tos_exports/paper/
Parser output (_IMPORT) → data/processed/paper/
```

---

## 📋 **Correct Workflow:**

### **Step 1: Export from TOS**
```
ThinkorSwim → Monitor → Account Statement → YTD → Export
Save as: D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
```

### **Step 2: Save to Correct Folder**
```
Paper account:
Save to: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\tos_exports\paper\

Live account:
Save to: C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
```

### **Step 3: Run Workflow**
```batch
P_020_Test_Full_Workflow.bat Paper
```

### **Step 4: Parser Runs Automatically**
```
Parser reads: data/tos_exports/paper/D_020_*_AccountStatement.csv
Parser creates:
  - data/processed/paper/D_020_*_OPTIONS_IMPORT.csv
  - data/processed/paper/D_020_*_STOCKS_IMPORT.csv
```

### **Step 5: Import Runs Automatically**
```
Import reads: data/processed/paper/D_020_*_IMPORT.csv
Import writes to: data/D_020_*_Log_V1.xlsx
```

---

## 🔍 **Quick Check:**

### **In data/tos_exports/paper/ you should see:**
```
D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv  ← TOS export (no _IMPORT)
```

### **In data/processed/paper/ you should see:**
```
D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement_OPTIONS_IMPORT.csv  ← Parser output
D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement_STOCKS_IMPORT.csv   ← Parser output
```

### **In data/ you should see:**
```
D_020_2026_AJZ_Strategies_Options_Log_V1.xlsx  ← Paper Excel log
D_020_2026__AJZ_Strategies_Stock_Log_V1.xlsx   ← Paper Excel log
```

---

## 💡 **Remember:**

**TOS Export:**
- ✅ You save manually
- ✅ Goes in `tos_exports/`
- ✅ No "_IMPORT" in name
- ✅ Parser reads this

**Parser Output:**
- ✅ Parser creates automatically
- ✅ Goes in `processed/`
- ✅ Has "_IMPORT" in name
- ✅ Import script reads this

**Don't mix them up!** 🚨

---

*Version: 2.2*  
*Date: 2026-02-07*  
*Status: Critical clarification*
