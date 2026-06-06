# P_020 TOS Parser v2.1 - Setup Guide
## Integrated into AI-Agent-Learning-Hub

---

## 📍 **Your Project Location:**

```
C:\Users\Trader\AI-Agent-Learning-Hub\
└── projects\
    └── P_020_AJZStrategies_PerformanceAnalysisSystem\  ← YOUR NEW PROJECT
```

---

## 🚀 **Quick Setup (3 Steps):**

### **Step 1: Create Folder Structure**

**Option A: Use PowerShell Script (Easiest)**
```powershell
# Open PowerShell
# Navigate to your hub
cd C:\Users\Trader\AI-Agent-Learning-Hub

# Run the setup script (provided)
.\P_020_Setup_Script.ps1
```

**Option B: Extract .tar.gz File**
1. Extract the `P_020_AJZStrategies_PerformanceAnalysisSystem.tar.gz` file
2. Move the extracted folder to: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\`

**Option C: Manual Folder Creation**
```
Create these folders manually:
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\
  ├── python\parsers\
  ├── data\tos_exports\live\
  ├── data\tos_exports\paper\
  ├── data\processed\live\
  ├── data\processed\paper\
  ├── tracking_logs\live\
  ├── tracking_logs\paper\
  └── docs\
```

### **Step 2: Place Files**
```
Copy to python\parsers\:
  - P_020_TOS_Parser_v2.py

Copy to docs\:
  - P_020_TOS_Parser_README.md
  - P_020_Folder_Structure.md
```

### **Step 3: Test with Paper Account**
```powershell
# Navigate to parser folder
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers

# Run parser on test file
python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\paper\D_020_test.csv
```

---

## 📂 **Complete Folder Structure:**

```
C:\Users\Trader\AI-Agent-Learning-Hub\
└── projects\
    └── P_020_AJZStrategies_PerformanceAnalysisSystem\
        │
        ├── python\
        │   └── parsers\
        │       └── P_020_TOS_Parser_v2.py          [THE PARSER]
        │
        ├── data\
        │   ├── tos_exports\
        │   │   ├── live\                           [P_020 TOS exports here]
        │   │   │   └── P_020_YYYY-MM-DD_*.csv
        │   │   └── paper\                          [D_020 TOS exports here]
        │   │       └── D_020_YYYY-MM-DD_*.csv
        │   │
        │   └── processed\
        │       ├── live\                           [P_020 import files]
        │       │   ├── *_OPTIONS_IMPORT.csv
        │       │   └── *_STOCKS_IMPORT.csv
        │       └── paper\                          [D_020 import files]
        │           ├── *_OPTIONS_IMPORT.csv
        │           └── *_STOCKS_IMPORT.csv
        │
        ├── tracking_logs\
        │   ├── live\                               → LINKS TO EXTERNAL
        │   │   │                                   C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
        │   │   ├── P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx
        │   │   └── P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx
        │   │
        │   └── paper\                              [Paper trading logs]
        │       ├── D_020__Paper_Options_Log_v2.xlsx
        │       └── D_020__Paper_Stock_Log-V2.xlsx
        │
        └── docs\
            ├── P_020_TOS_Parser_README.md         [User guide]
            └── P_020_Folder_Structure.md          [This file]
```

---

## 🔄 **Typical Workflow:**

### **For LIVE Account (Production):**
```
1. Export from TOS
   → Save to: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\tos_exports\live\

2. Run Parser
   cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers
   python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\live\P_020_2026-01-31_*.csv

3. Output goes to:
   ..\..\data\processed\live\
   
4. Open CSV, copy all, paste into:
   C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx

5. Update "System" column
6. Verify calculations
```

### **For PAPER Account (Development):**
```
1. Export from TOS
   → Save to: ...\data\tos_exports\paper\

2. Run Parser
   python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\paper\D_020_*.csv

3. Output goes to:
   ..\..\data\processed\paper\

4. Open CSV, copy all, paste into:
   ..\..\tracking_logs\paper\D_020__Paper_Options_Log_v2.xlsx

5. Update "System" column
6. Verify calculations
```

---

## 🔑 **Key Path References:**

### **Parser Location:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers\P_020_TOS_Parser_v2.py
```

### **Live Account Logs (External - AJZ Strategies LLC):**
```
C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
├── P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx
└── P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx
```

### **Paper Account Logs (Inside Project):**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\tracking_logs\paper\
├── D_020__Paper_Options_Log_v2.xlsx
└── D_020__Paper_Stock_Log-V2.xlsx
```

---

## 🔗 **Integration with AI-Agent-Learning-Hub:**

### **P_020 is INDEPENDENT:**
- Has its own `python/` folder (not using shared_resources)
- Has its own `data/` structure
- Unique to performance tracking
- Does NOT share with P_300, D_130, or P_010

### **Why Independent?**
- Different purpose (performance analysis vs. strategy testing)
- Different data sources (TOS account statements)
- Different outputs (trade logs vs. forecasts)
- Will have unique Phase 2 automation

### **Future Integration Points (Phase 2-3):**
When you build Phase 2 automation:
```
AI-Agent-Learning-Hub\integrations\automation\
└── workflows\
    └── P_020_weekly_parser.py  ← Phase 2 automation can go here
```

---

## 📋 **P_ vs D_ Naming Convention:**

**Applies to ALL projects in AI-Agent-Learning-Hub:**

- **P_** = **PRODUCTION** (tested, approved, live)
  - P_020 = Performance Analysis (this project)
  - P_010 = Market Posture Forecasts
  - P_300 = Vantage Point Pattern Recognition

- **D_** = **DEVELOPMENT** (experimental, paper trading)
  - D_020 = Paper trading version of P_020
  - D_130 = Trade the Bounce OIL (in development)

---

## ✅ **Verification Checklist:**

After setup, verify these paths exist:
- [ ] `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\`
- [ ] `...\python\parsers\P_020_TOS_Parser_v2.py`
- [ ] `...\data\tos_exports\live\` (folder exists)
- [ ] `...\data\tos_exports\paper\` (folder exists)
- [ ] `...\tracking_logs\paper\` (folder exists)
- [ ] `...\docs\P_020_TOS_Parser_README.md`

External paths still exist:
- [ ] `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx`
- [ ] `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx`

---

## 🚨 **Important Notes:**

### **DO NOT:**
❌ Move live Excel logs into project folder (they stay in AJZ folder)  
❌ Mix P_020 with other projects (P_300, D_130, P_010)  
❌ Share resources with other projects (P_020 is independent)  
❌ Delete TOS exports after processing (keep for audit)

### **ALWAYS:**
✅ Backup Excel logs before pasting new data  
✅ Keep TOS exports in correct live/ or paper/ folder  
✅ Use P_ prefix for live, D_ for paper  
✅ Verify parser output before Excel import  
✅ Update "System" column after import

---

## 🔄 **Phase 2 & 3 Roadmap:**

**Phase 2: Weekly Automation (~March 2026)**
- Auto-detect new TOS exports
- Run parser automatically
- Validate outputs
- Auto-update Excel (with backup)
- Email notifications

**Phase 3: Performance Analysis (~April 2026+)**
- System comparison (P_115/116/117/118/300)
- Win rate trends
- Risk metrics
- Weekly reports
- Actionable insights

---

## 📞 **Quick Reference:**

**Parser Location:**
```
CD to: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers
```

**Run Parser:**
```powershell
python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\live\YOUR_FILE.csv
```

**Output Location:**
```
..\..\data\processed\live\YOUR_FILE_OPTIONS_IMPORT.csv
..\..\data\processed\live\YOUR_FILE_STOCKS_IMPORT.csv
```

---

*Last Updated: 2026-01-31*  
*Version: 2.1*  
*Status: Production Ready*  
*Integrated into: AI-Agent-Learning-Hub*
