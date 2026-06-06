# P_020 Project Naming Update Checklist

## ✅ Correct Project Name
**`P_020_AJZStrategies_PerformanceAnalysisSystem`**

### Naming Convention:
- P_020 = Project identifier
- AJZStrategies = Company name component
- PerformanceAnalysisSystem = Descriptive component
- Underscores separate ALL components

---

## 📋 Files/Folders That Need Renaming

### 1. Main Project Folder
**Current (if exists):**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\
```

**Should Be:**
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\
```

**Action:** Rename the folder if it already exists

---

### 2. Documentation Files to Update

#### ✅ Already Updated:
- [x] P_020_PROJECT_PLAN.md

#### ⏳ Need to Update:
- [ ] P_020_Future_Enhancements_Tracker.md (no project name in it, OK)
- [ ] P_020_QUICK_INTEGRATION_GUIDE.md (check for path references)
- [ ] P_020_TOS_Parser_README.md (check for path references)
- [ ] REQ_020126_01_Auto_Fill_System_Names.md (no project name, OK)
- [ ] P_020_SETUP_GUIDE_INTEGRATED.md (check for path references)

---

### 3. Path References in Documentation

**Search and Replace Pattern:**
```
OLD: P_020_AJZStrategies_PerformanceAnalysisSystem
NEW: P_020_AJZStrategies_PerformanceAnalysisSystem
```

**Files to Check:**
1. P_020_QUICK_INTEGRATION_GUIDE.md
2. P_020_SETUP_GUIDE_INTEGRATED.md
3. Any batch files (.bat)
4. Any PowerShell scripts (.ps1)
5. Python parser file (P_020_TOS_Parser_v2.py) if it has hardcoded paths

---

### 4. Configuration Files

**If you have a config file (like P_020_config.json):**
Update all path references to use the new name.

---

### 5. Batch File / Script Updates

**P_020_AccountParser.bat** - Update paths if they reference the folder name
**P_020_Setup_Script.ps1** - Update folder creation to use new name

---

## 🔄 Step-by-Step Renaming Process

### Step 1: Backup Everything
```powershell
# Create backup of entire project
Copy-Item "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_*" `
          "C:\Users\Trader\Desktop\P_020_BACKUP_$(Get-Date -Format 'yyyyMMdd')" `
          -Recurse
```

### Step 2: Rename Main Folder
```powershell
# Close all open files in VSCode and Excel first!

# Navigate to projects folder
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\

# Rename the folder
Rename-Item "P_020_AJZStrategies_PerformanceAnalysisSystem" `
            "P_020_AJZStrategies_PerformanceAnalysisSystem"
```

### Step 3: Update Documentation
Use find-and-replace in each document:
- Open in VSCode
- Ctrl+H (Find and Replace)
- Find: `P_020_AJZStrategies_PerformanceAnalysisSystem`
- Replace: `P_020_AJZStrategies_PerformanceAnalysisSystem`
- Replace All

### Step 4: Test Everything
```powershell
# Navigate to renamed folder
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem

# Test batch file
P_020_AccountParser.bat

# Test parser directly
cd python\parsers
python P_020_TOS_Parser_v2.py --help
```

### Step 5: Update Git (if using version control)
```bash
git mv P_020_AJZStrategies_PerformanceAnalysisSystem P_020_AJZStrategies_PerformanceAnalysisSystem
git commit -m "Rename project to correct underscore convention"
```

---

## 📝 Verification Checklist

After renaming, verify:
- [ ] Folder name is correct
- [ ] Batch file runs successfully
- [ ] Parser can be found and executed
- [ ] All paths in documentation are updated
- [ ] No broken links in README files
- [ ] Config files (if any) have correct paths
- [ ] Test parsing works end-to-end

---

## ⚠️ Important Notes

### Why This Matters:
1. **Consistency**: All P_020 files/folders follow same naming pattern
2. **Automation**: Future scripts will expect consistent naming
3. **Documentation**: Easier to find and reference
4. **Professional**: Clean, organized project structure

### Windows Path Considerations:
- Avoid spaces in folder names ✅ (already correct)
- Use underscores for word separation ✅ (now correct)
- Keep under 260 character total path length ✅
- Consistent capitalization ✅

---

## 🎯 Next Steps

1. **Review this checklist**
2. **Decide when to rename** (before or after course project?)
3. **Create backup**
4. **Execute rename**
5. **Test thoroughly**

**Recommendation:** Do the rename NOW (before starting course project) to avoid confusion later.

---

*Created: 2026-02-14*  
*Status: Pending Execution*  
*Impact: Low risk, high organizational benefit*
