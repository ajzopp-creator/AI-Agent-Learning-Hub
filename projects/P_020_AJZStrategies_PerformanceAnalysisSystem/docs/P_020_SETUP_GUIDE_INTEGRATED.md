# P_020 TOS Parser v2.1 - Setup Guide
## Integrated into AI-Agent-Learning-Hub

---

## ðŸ" **Your Project Location:**

```
C:\Users\Trader\AI-Agent-Learning-Hub\
â""â"€â"€ projects\
    P_020_AJZStrategies_PerformanceAnalysisSystem\\  â† YOUR NEW PROJECT
```

---

## ðŸš€ **Quick Setup (3 Steps):**

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
  â"œâ"€â"€ python\parsers\
  â"œâ"€â"€ data\tos_exports\live\
  â"œâ"€â"€ data\tos_exports\paper\
  â"œâ"€â"€ data\processed\live\
  â"œâ"€â"€ data\processed\paper\
  â"œâ"€â"€ tracking_logs\live\
  â"œâ"€â"€ tracking_logs\paper\
  â""â"€â"€ docs\
```

### **Step 2: Place Files**
```
Copy to project root:
  - P_020_AccountParser.bat           [EASY RUNNER - USE THIS!]

Copy to python\parsers\:
  - P_020_TOS_Parser_v2.py

Copy to docs\:
  - P_020_TOS_Parser_README.md
  - P_020_Folder_Structure.md
```

### **Step 3: Test with Paper Account**

**âœ… EASIEST - Use Batch File:**
```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\
P_020_AccountParser D_020_test.csv
```

**Advanced - Direct Python:**
```powershell
cd python\parsers
python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\paper\D_020_test.csv
```

---

## ðŸ"‚ **Complete Folder Structure:**

```
C:\Users\Trader\AI-Agent-Learning-Hub\
â""â"€â"€ projects\
    â""â"€â"€ P_020_AJZStrategies_PerformanceAnalysisSystem\P_020_AJZStrategies_PerformanceAnalysisSystem\
        â"‚
        â"œâ"€â"€ P_020_AccountParser.bat             [âœ… EASY RUNNER!]
        â"‚
        â"œâ"€â"€ python\
        â"‚   â""â"€â"€ parsers\
        â"‚       â""â"€â"€ P_020_TOS_Parser_v2.py          [THE PARSER]
        â"‚
        â"œâ"€â"€ data\
        â"‚   â"œâ"€â"€ tos_exports\
        â"‚   â"‚   â"œâ"€â"€ live\                           [P_020 TOS exports here]
        â"‚   â"‚   â"‚   â""â"€â"€ P_020_YYYY-MM-DD_*.csv
        â"‚   â"‚   â""â"€â"€ paper\                          [D_020 TOS exports here]
        â"‚   â"‚       â""â"€â"€ D_020_YYYY-MM-DD_*.csv
        â"‚
        â"‚   â""â"€â"€ processed\
        â"‚       â"œâ"€â"€ live\                           [P_020 import files]
        â"‚       â"‚   â"œâ"€â"€ *_OPTIONS_IMPORT.csv
        â"‚       â"‚   â""â"€â"€ *_STOCKS_IMPORT.csv
        â"‚       â""â"€â"€ paper\                          [D_020 import files]
        â"‚           â"œâ"€â"€ *_OPTIONS_IMPORT.csv
        â"‚           â""â"€â"€ *_STOCKS_IMPORT.csv
        â"‚
        â"œâ"€â"€ tracking_logs\
        â"‚   â"œâ"€â"€ live\                               â†' LINKS TO EXTERNAL
        â"‚   â"‚   â"‚                                   C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
        â"‚   â"‚   â"œâ"€â"€ P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx
        â"‚   â"‚   â""â"€â"€ P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx
        â"‚   â"‚
        â"‚   â""â"€â"€ paper\                              [Paper trading logs]
        â"‚       â"œâ"€â"€ D_020__Paper_Options_Log_v2.xlsx
        â"‚       â""â"€â"€ D_020__Paper_Stock_Log-V2.xlsx
        â"‚
        â""â"€â"€ docs\
            â"œâ"€â"€ P_020_TOS_Parser_README.md         [User guide]
            â""â"€â"€ P_020_Folder_Structure.md          [This file]
```

---

## ðŸ"„ **Typical Workflow:**

### **For LIVE Account (Production):**

**âœ… EASIEST METHOD - Use Batch File:**
```batch
1. Export from TOS
   â†' Save to: data\tos_exports\live\
   â†' Example: P_020_2026-01-31_AJZ_Strategies_YTD_AccountStatement.csv

2. Run Parser (from project root)
   cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\
   P_020_AccountParser P_020_2026-01-31_AJZ_Strategies_YTD_AccountStatement.csv

3. Output automatically goes to:
   data\processed\live\
   
4. Open CSV, copy all, paste into:
   C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx
   âš ï¸ Use "Paste Special â†' Values" to preserve formulas!

5. Update "System" column from "TOS_Import" to actual system (P_115/116/117/118/300)
6. Verify calculations
```

**Advanced: Manual Python Command**
```powershell
cd python\parsers
python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\live\P_020_2026-01-31_*.csv
```

---

### **For PAPER Account (Development):**

**âœ… EASIEST METHOD - Use Batch File:**
```batch
1. Export from TOS
   â†' Save to: data\tos_exports\paper\
   â†' Example: D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv

2. Run Parser (from project root)
   cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\
   P_020_AccountParser D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv

3. Output automatically goes to:
   data\processed\paper\

4. Open CSV, copy all, paste into:
   tracking_logs\paper\D_020__Paper_Options_Log_v2.xlsx
   âš ï¸ Use "Paste Special â†' Values" to preserve formulas!

5. Update "System" column from "TOS_Import" to actual system
6. Verify calculations
```

**Advanced: Manual Python Command**
```powershell
cd python\parsers
python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\paper\D_020_*.csv
```

---

## ðŸ"' **Key Path References:**

### **Batch Runner (Recommended):**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\P_020_AccountParser.bat
```

### **Parser Location:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers\P_020_TOS_Parser_v2.py
```

### **Live Account Logs (External - AJZ Strategies LLC):**
```
C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\
â"œâ"€â"€ P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx
â""â"€â"€ P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx
```

### **Paper Account Logs (Inside Project):**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\tracking_logs\paper\
â"œâ"€â"€ D_020__Paper_Options_Log_v2.xlsx
â""â"€â"€ D_020__Paper_Stock_Log-V2.xlsx
```

---

## ðŸ"— **Integration with AI-Agent-Learning-Hub:**

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
â""â"€â"€ workflows\
    â""â"€â"€ P_020_weekly_parser.py  â† Phase 2 automation can go here
```

---

## ðŸ"‹ **P_ vs D_ Naming Convention:**

**Applies to ALL projects in AI-Agent-Learning-Hub:**

- **P_** = **PRODUCTION** (tested, approved, live)
  - P_020 = Performance Analysis (this project)
  - P_010 = Market Posture Forecasts
  - P_300 = Vantage Point Pattern Recognition

- **D_** = **DEVELOPMENT** (experimental, paper trading)
  - D_020 = Paper trading version of P_020
  - D_130 = Trade the Bounce OIL (in development)

---

## âœ… **Verification Checklist:**

After setup, verify these paths exist:
- [ ] `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\`
- [ ] `...\P_020_AccountParser.bat` âœ… [NEW!]
- [ ] `...\python\parsers\P_020_TOS_Parser_v2.py`
- [ ] `...\data\tos_exports\live\` (folder exists)
- [ ] `...\data\tos_exports\paper\` (folder exists)
- [ ] `...\tracking_logs\paper\` (folder exists)
- [ ] `...\docs\P_020_TOS_Parser_README.md`

External paths still exist:
- [ ] `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx`
- [ ] `C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx`

---

## ðŸš¨ **Important Notes:**

### **DO NOT:**
âŒ Move live Excel logs into project folder (they stay in AJZ folder)  
âŒ Mix P_020 with other projects (P_300, D_130, P_010)  
âŒ Share resources with other projects (P_020 is independent)  
âŒ Delete TOS exports after processing (keep for audit)
âŒ Use filenames with SPACES (causes batch file issues - use underscores)

### **ALWAYS:**
âœ… Backup Excel logs before pasting new data  
âœ… Keep TOS exports in correct live/ or paper/ folder  
âœ… Use P_ prefix for live, D_ for paper  
âœ… Verify parser output before Excel import  
âœ… Update "System" column after import
âœ… Use filenames without spaces (e.g., AJZ_Strategies not "AJZ Strategies")

---

## ðŸ"„ **Phase 2 & 3 Roadmap:**

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

## ðŸ"ž **Quick Reference:**

**âœ… EASIEST - Use Batch File (from project root):**
```batch
P_020_AccountParser YOUR_FILENAME.csv
```

**Advanced - Manual Python Command:**
```powershell
CD to: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\parsers
python P_020_TOS_Parser_v2.py ..\..\data\tos_exports\live\YOUR_FILE.csv
```

**Output Location:**
```
data\processed\live\YOUR_FILE_OPTIONS_IMPORT.csv
data\processed\live\YOUR_FILE_STOCKS_IMPORT.csv
```

---

*Last Updated: 2026-02-07*  
*Version: 2.1.1*  
*Status: Production Ready*  
*Integrated into: AI-Agent-Learning-Hub*
