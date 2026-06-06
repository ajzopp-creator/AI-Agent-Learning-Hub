# P_020 - QUICK FIX INSTRUCTIONS

## 🔧 **Here's What To Do:**

---

## **STEP 1: Run the Diagnostic Script**

```batch
P_020_Diagnostic.bat
```

**This will show you:**
- What folders exist
- What files are where
- What's missing or wrong

**Copy ALL the output and send it to me** (or just tell me what it says)

---

## **STEP 2: Use the Fixed Batch File**

```batch
P_020_Test_Full_Workflow_FIXED.bat Paper
```

**This new version:**
- ✅ Shows more debug info
- ✅ Lists all files it finds
- ✅ Better error messages
- ✅ More reliable file detection

---

## **STEP 3: If It Still Crashes**

Copy the error text from the command window and send it to me.

---

## 📂 **Quick Folder Check:**

### **Where files SHOULD be:**

```
data\tos_exports\paper\
  └── D_020_2026-02-07_AccountStatement.csv  ← TOS export (no _IMPORT!)

data\processed\paper\
  ├── D_020_*_OPTIONS_IMPORT.csv             ← Parser output
  └── D_020_*_STOCKS_IMPORT.csv              ← Parser output

data\
  ├── D_020_2026_AJZ_Strategies_Options_Log_V1.xlsx
  └── D_020_2026__AJZ_Strategies_Stock_Log_V1.xlsx
```

### **Common Problem:**

**Files are in wrong folders!**

```
❌ WRONG: data\tos_exports\paper\D_020_*_IMPORT.csv
          (Parser output in TOS export folder!)

✅ RIGHT: data\tos_exports\paper\D_020_*_AccountStatement.csv
          (TOS export - no _IMPORT in name)
```

**Fix:** Move `*_IMPORT.csv` files from `tos_exports` to `processed`

---

## 🎯 **Two New Files to Help:**

### **1. P_020_Diagnostic.bat** ⭐
- Shows what's in your folders
- Identifies missing files
- Helps debug issues
- **Run this first!**

### **2. P_020_Test_Full_Workflow_FIXED.bat** ⭐
- Better error handling
- More debug output
- Shows which files it finds
- Easier to troubleshoot
- **Use this instead of v2!**

---

## 💡 **Most Likely Issue:**

You probably have parser output files (`*_IMPORT.csv`) mixed with TOS export files.

**Quick fix:**
1. Look in `data\tos_exports\paper\`
2. Find files with `_IMPORT` in the name
3. Move them to `data\processed\paper\`
4. Run the FIXED batch file

---

**Download these 2 new files and let me know what happens!** 🚀
