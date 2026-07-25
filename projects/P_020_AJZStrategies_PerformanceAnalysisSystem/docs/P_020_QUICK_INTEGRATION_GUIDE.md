# P_020 Integration - Quick Visual Guide

## 🎯 Where P_020 Goes

```
C:\Users\Trader\
│
├── Documents\
│   └── AJZStrategiesLLC\
│       └── 2026_Operations\
│           ├── P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx  ← LIVE LOGS (DON'T MOVE)
│           └── P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx    ← LIVE LOGS (DON'T MOVE)
│
└── AI-Agent-Learning-Hub\
    │
    ├── projects\
    │   ├── P_300_Vantage_Point_Pattern_Recognition\
    │   ├── P_110_TradetheBounce_OIL\
    │   ├── P_010_Market_Posture_Weekly_Forecasts\
    │   │
    │   └── P_020_AJZStrategies_PerformanceAnalysisSystem\  ← ADD THIS!
    │       ├── python\parsers\
    │       │   └── P_020_TOS_Parser_v2.py
    │       ├── data\
    │       │   ├── tos_exports\live\      ← TOS exports here
    │       │   ├── tos_exports\paper\
    │       │   └── processed\live\        ← Parser outputs here
    │       ├── tracking_logs\
    │       │   ├── live\                  → Points to AJZ folder
    │       │   └── paper\                 ← Paper logs here
    │       └── docs\
    │
    ├── shared_resources\
    ├── integrations\
    └── docs\
```

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     LIVE ACCOUNT WORKFLOW                    │
└─────────────────────────────────────────────────────────────┘

1. ThinkorSwim
   │
   └─> Export CSV
       │
       └─> Save to: AI-Agent-Learning-Hub\projects\P_020_...\data\tos_exports\live\
           │
           └─> Run Parser: P_020_TOS_Parser_v2.py
               │
               └─> Output: data\processed\live\*_IMPORT.csv
                   │
                   └─> Copy/Paste into: C:\...\AJZStrategiesLLC\2026_Operations\P_020_*_Log.xlsx


┌─────────────────────────────────────────────────────────────┐
│                     PAPER ACCOUNT WORKFLOW                   │
└─────────────────────────────────────────────────────────────┘

1. ThinkorSwim (Paper)
   │
   └─> Export CSV
       │
       └─> Save to: AI-Agent-Learning-Hub\projects\P_020_...\data\tos_exports\paper\
           │
           └─> Run Parser: P_020_TOS_Parser_v2.py
               │
               └─> Output: data\processed\paper\*_IMPORT.csv
                   │
                   └─> Copy/Paste into: tracking_logs\paper\D_020_*_Log.xlsx
```

---

## 📋 3 Ways to Set Up

### **Option 1: PowerShell Script (Fastest)**
```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub
.\P_020_Setup_Script.ps1
```
**Result:** All folders created automatically in 2 seconds

### **Option 2: Extract .tar.gz (Easy)**
```
1. Right-click P_020_AJZStrategies_PerformanceAnalysisSystem.tar.gz
2. Extract Here
3. Move extracted folder to: AI-Agent-Learning-Hub\projects\
```
**Result:** Complete structure with files in place

### **Option 3: Manual (Most Control)**
```
1. Create folders manually (see structure above)
2. Copy P_020_TOS_Parser_v2.py to python\parsers\
3. Copy docs to docs\
```
**Result:** You control every step

---

## ✅ Quick Test

```powershell
# Navigate to parser
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers

# Test with paper account
python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\paper\test.csv

# Check output
dir ..\..\data\processed\paper\
```

**If you see `*_OPTIONS_IMPORT.csv` and `*_STOCKS_IMPORT.csv` → SUCCESS!** ✅

---

## 🔑 Key Paths to Remember

**Parser:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers\P_020_TOS_Parser_v2.py
```

**Live Logs (External):**
```
C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
```

**Paper Logs (Internal):**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\tracking_logs\paper\
```

---

## 🚨 Common Mistakes to Avoid

❌ **Don't put P_020 at root level**
```
WRONG: C:\Users\Trader\AI-Agent-Learning-Hub\P_020_...
RIGHT: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_...
```

❌ **Don't move live Excel logs**
```
WRONG: Move to P_020 project folder
RIGHT: Keep at C:\...\AJZStrategiesLLC\2026_Operations\
```

❌ **Don't mix live and paper exports**
```
WRONG: Both in same tos_exports\ folder
RIGHT: Separate live\ and paper\ subfolders
```

❌ **Don't use shared_resources**
```
P_020 is independent - has its own python\ and data\ folders
```

---

## 📞 Need Help?

**Parser not working?**
- Check you're in correct folder: `...\python\parsers\`
- Verify Python installed: `python --version`
- Check file path in command

**Can't find folders?**
- Verify setup script ran: Check for `projects\P_020_...` folder
- Or manually create folders per structure above

**Import failing in Excel?**
- Verify CSV columns match Excel columns
- Check for empty rows at top of CSV
- Backup Excel file before paste

---

*This is a QUICK REFERENCE - see P_020_SETUP_GUIDE_INTEGRATED.md for complete details*