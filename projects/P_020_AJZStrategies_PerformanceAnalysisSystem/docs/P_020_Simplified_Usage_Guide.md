# P_020 Simplified Workflow - Quick Usage Guide

## 🎯 **Super Simple Usage!**

---

## **Just Two Commands:**

### **For Live Account (P_020):**
```batch
P_020_Test_Full_Workflow.bat
```
**or**
```batch
P_020_Test_Full_Workflow.bat Live
```

**What it does:**
- ✅ Finds latest `P_020*.csv` in `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\`
- ✅ Runs parser
- ✅ Imports to live Excel logs
- ✅ Auto-matches System names
- ✅ Done!

---

### **For Paper Account (D_020):**
```batch
P_020_Test_Full_Workflow.bat Paper
```

**What it does:**
- ✅ Finds latest `D_020*.csv` in `data/tos_exports/paper/`
- ✅ Runs parser
- ✅ Imports to paper Excel logs
- ✅ Auto-matches System names
- ✅ Done!

---

## 📋 **Complete Weekly Workflow:**

### **Every Sunday Evening:**

**Step 1: Export from TOS**
```
ThinkorSwim → Monitor → Account Statement → YTD → Export
Save to appropriate folder (Live or Paper)
```

**Step 2: Run Workflow**
```batch
# Navigate to project
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem

# For Live account
P_020_Test_Full_Workflow.bat

# OR for Paper account
P_020_Test_Full_Workflow.bat Paper
```

**Step 3: Choose Import Option**
```
Menu appears:
[1] Options → Paper Log
[2] Options → Live Log
[3] Stocks → Paper Log
[4] Stocks → Live Log
[5] Import ALL → Paper
[6] Import ALL → Live

Choose appropriate option (e.g., "6" for live account imports both)
```

**Step 4: Verify in Excel**
```
- Open Excel logs
- Check System names filled in (P_115, P_116, P_117, P_118, P_300)
- Verify formulas calculating
- Done!
```

**Total Time: 2-3 minutes!** ⚡

---

## 🎊 **What Changed?**

### **Old Way (Co-Pilot Version):**
```batch
# Had to type full filename
P_020_Test_Full_Workflow.bat "P_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv"
```
❌ Long, annoying to type  
❌ Easy to make typos  
❌ Have to remember exact filename  

### **New Way (Your Improvement):**
```batch
# Just say "Paper" or nothing
P_020_Test_Full_Workflow.bat Paper    # Paper account
P_020_Test_Full_Workflow.bat          # Live account
```
✅ Super simple!  
✅ No typing filenames  
✅ Auto-finds latest file  
✅ Less error-prone  

---

## 📂 **How It Finds Files:**

### **Live Account (P_020):**
```
Looks in: C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
Finds:    P_020*.csv (most recent)
Example:  P_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
```

### **Paper Account (D_020):**
```
Looks in: [Project]/data/tos_exports/paper/
Finds:    D_020*.csv (most recent)
Example:  D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
```

**Always uses the most recent file!** (by date modified)

---

## ⚠️ **Important Notes:**

### **File Must Exist First:**
```
If you haven't exported from TOS yet, batch file will show:
"ERROR: No P_020*.csv files found"

Solution: Export from TOS first, then run batch file
```

### **Multiple TOS Exports:**
```
If you have multiple exports:
  P_020_2026-02-01_AccountStatement.csv
  P_020_2026-02-07_AccountStatement.csv  ← This one is used!

Batch file always uses the NEWEST one
```

### **Keep Old Exports:**
```
Don't delete old TOS export files!
Keep them for audit trail
Batch file automatically picks the newest
```

---

## 🚀 **Examples:**

### **Monday Morning - Live Account:**
```batch
# You exported from TOS on Sunday
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem
P_020_Test_Full_Workflow.bat

# Output:
# Account Type: Live
# File Prefix:  P_020
# Found latest file: P_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
# [Parser runs...]
# [Import runs...]
# Done!
```

### **Testing on Paper Account:**
```batch
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem
P_020_Test_Full_Workflow.bat Paper

# Output:
# Account Type: Paper
# File Prefix:  D_020
# Found latest file: D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
# [Parser runs...]
# [Import runs...]
# Done!
```

---

## ✅ **Testing Checklist:**

This weekend:

- [ ] Export TOS account statement (Paper account first)
- [ ] Save to correct folder (`data/tos_exports/paper/`)
- [ ] Run: `P_020_Test_Full_Workflow.bat Paper`
- [ ] Verify it finds the file
- [ ] Verify parser runs successfully
- [ ] Verify import matches System names
- [ ] Check Excel formulas work
- [ ] Repeat for Live account

---

## 🎯 **Bottom Line:**

**Before:** Had to type long filename  
**After:** Just type `Paper` or nothing  

**Simple. Fast. Clean.** ✨

---

*Version: 2.2 (Test)*  
*Date: 2026-02-07*  
*Author: Anthony (AJZ Strategies LLC)*
