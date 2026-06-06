# P_020 TOS Parser System - Project Plan
## AI Fluency Course Integration

**Project Name:** P_020_AJZStrategies_PerformanceAnalysisSystem  
**Project Owner:** Tony (AJZ Strategies LLC)  
**Course:** AI Fluency: Framework & Foundations  
**Skill Level:** Novice Python, Novice VSCode  
**Total Estimated Time:** 12-15 hours (spread across multiple sessions)  
**Target Completion:** March 2026

---

## 🎯 Project Overview

**What We're Building:**
Transform the P_020 TOS Parser from a manual tool into a semi-automated system that eliminates tedious weekly data entry tasks, saving 26+ hours annually while reducing errors.

**Current State (v2.1 - COMPLETED ✅):**
- Parser successfully extracts trades from TOS CSV exports
- Handles 300+ transactions correctly
- Separates options and stocks
- Matches entries with exits
- Calculates commissions accurately
- **Status:** Production-ready, in weekly use

**Course Project Goal:**
Implement v2.2 with auto-matching enhancement + foundational Phase 2 components

---

## 📊 Project Scope for AI Fluency Course

### In Scope (Achievable in Course Timeline):
✅ **Milestone 1:** Auto-System Matching (REQ-020126_01) - v2.2  
✅ **Milestone 2:** Basic File Monitoring Foundation  
✅ **Milestone 3:** Enhanced Error Handling & Logging  
✅ **Milestone 4:** Comprehensive Testing & Documentation

### Out of Scope (Future Work):
❌ Full Phase 2 automation (scheduled tasks, auto-Excel updates)  
❌ Phase 3 performance analytics dashboard  
❌ Email notifications  
❌ Advanced Excel formula preservation

*These remain in the roadmap but are deferred beyond course timeline*

---

## 🗓️ Master Timeline

```
Week 1 (Feb 14-21):  Planning & Setup          [2 hours]
Week 2 (Feb 22-28):  Auto-Matching Dev         [4-5 hours]
Week 3 (Mar 1-7):    Testing & Refinement      [3-4 hours]
Week 4 (Mar 8-14):   Documentation & Polish    [2-3 hours]
════════════════════════════════════════════════════════
TOTAL:                                         [12-15 hours]
```

---

## 📋 MILESTONE 1: Auto-System Matching (v2.2)
**Priority:** HIGH  
**Status:** Approved for Development  
**Time Estimate:** 4-6 hours (development + testing)  
**Target:** Feb 22-28, 2026

### What It Does:
Automatically fills in the "System" column (P_115, P_116, P_117, P_118, P_300) by cross-referencing the Tracker Dashboard Excel file, eliminating manual updates for every trade.

### Success Criteria:
✅ Parser reads Tracker Dashboard Excel file  
✅ Matches Symbol + Trade Date correctly  
✅ Auto-fills System column when match found  
✅ Defaults to "TOS_Import" when no match  
✅ Handles all edge cases gracefully  
✅ Works with both live (P_020) and paper (D_020) accounts

### Tasks Breakdown:

#### Task 1.1: Environment Setup (30 min)
**Learning Focus:** VSCode, Python environment, package management
- [ ] Install `openpyxl` package: `pip install openpyxl --break-system-packages`
- [ ] Verify installation: `python -c "import openpyxl; print('Success!')"`
- [ ] Open P_020_TOS_Parser_v2.py in VSCode
- [ ] Familiarize yourself with current code structure

**AI Assistant Prompts to Use:**
```
"Explain what openpyxl does and why we need it"
"Show me how to verify openpyxl is installed correctly"
"Walk me through the current parser code structure"
```

---

#### Task 1.2: Create Tracker Reader Function (90 min)
**Learning Focus:** Reading Excel files with pandas/openpyxl, data structures
- [ ] Create function: `read_tracker_dashboard(file_path)`
- [ ] Handle file not found error
- [ ] Handle file locked by Excel error
- [ ] Extract columns: "Buy" (or "Symbol"), "Date", "Signal Source"
- [ ] Return as dictionary: `{(symbol, date): system_name}`

**Starter Code Template:**
```python
import openpyxl
from datetime import datetime

def read_tracker_dashboard(tracker_path):
    """
    Read Tracker Dashboard and create lookup dictionary.
    
    Returns:
        dict: {(symbol, date): system_name} or None if error
    """
    try:
        # Your code here
        workbook = openpyxl.load_workbook(tracker_path, data_only=True)
        sheet = workbook.active
        
        # Build lookup dictionary
        tracker_lookup = {}
        
        # Add your logic here
        
        return tracker_lookup
        
    except FileNotFoundError:
        print(f"⚠️  WARNING: Tracker Dashboard not found at {tracker_path}")
        print(f"   Continuing with 'TOS_Import' defaults")
        return None
    except Exception as e:
        print(f"⚠️  ERROR reading Tracker: {e}")
        return None
```

**AI Assistant Prompts:**
```
"How do I read an Excel file with openpyxl and find specific columns?"
"Show me how to handle the case where Excel file is locked/open"
"How do I create a dictionary with tuple keys in Python?"
"Explain try/except error handling for beginners"
```

**Testing:**
- Test with Tracker Dashboard at correct path
- Test with file missing
- Test with file locked (open in Excel)
- Print the dictionary to verify contents

---

#### Task 1.3: Create Matching Function (60 min)
**Learning Focus:** String matching, date comparison, conditional logic
- [ ] Create function: `match_system_name(symbol, trade_date, tracker_lookup)`
- [ ] Handle case-insensitive symbol matching
- [ ] Handle date format differences (M/D/YY vs MM/DD/YYYY)
- [ ] Handle option symbol variations (spaces, prefixes)
- [ ] Return matched system or "TOS_Import"

**Starter Code Template:**
```python
def match_system_name(symbol, trade_date, tracker_lookup):
    """
    Match trade to system name from Tracker Dashboard.
    
    Args:
        symbol (str): Stock/option symbol
        trade_date (str): Trade date in M/D/YY format
        tracker_lookup (dict): Lookup dictionary from Tracker
        
    Returns:
        str: System name (P_115, P_116, etc.) or "TOS_Import"
    """
    if tracker_lookup is None:
        return "TOS_Import"
    
    # Normalize symbol (uppercase, strip whitespace)
    clean_symbol = symbol.upper().strip()
    
    # Your date parsing logic here
    # Your matching logic here
    
    # Check lookup dictionary
    lookup_key = (clean_symbol, parsed_date)
    if lookup_key in tracker_lookup:
        return tracker_lookup[lookup_key]
    
    return "TOS_Import"
```

**AI Assistant Prompts:**
```
"How do I compare dates in different formats in Python?"
"Show me how to normalize strings for case-insensitive matching"
"What's the best way to handle option symbols with extra characters?"
```

**Testing:**
- Test with exact match (should return system name)
- Test with no match (should return "TOS_Import")
- Test with case differences (QBTS vs qbts)
- Test with different date formats

---

#### Task 1.4: Integrate into Main Parser (60 min)
**Learning Focus:** Code integration, preserving existing functionality
- [ ] Add Tracker path as configuration variable
- [ ] Call `read_tracker_dashboard()` at start of parsing
- [ ] Update system assignment logic in both OPTIONS and STOCKS sections
- [ ] Preserve all existing functionality
- [ ] Add logging messages for user feedback

**Integration Points:**
```python
# At top of script - configuration
TRACKER_DASHBOARD_PATH = r"C:\Users\Trader\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TtrackerDashboard_V2.xlsx"

# In main() function - early in execution
print("Loading Tracker Dashboard for system matching...")
tracker_lookup = read_tracker_dashboard(TRACKER_DASHBOARD_PATH)
if tracker_lookup:
    print(f"✅ Loaded {len(tracker_lookup)} entries from Tracker Dashboard")
else:
    print("⚠️  Using 'TOS_Import' defaults for all trades")

# In trade processing - replace system assignment
# OLD: system_name = "TOS_Import"
# NEW:
system_name = match_system_name(symbol, trade_date, tracker_lookup)
```

**AI Assistant Prompts:**
```
"Show me how to add configuration variables at the top of a Python script"
"How do I pass data between functions in Python?"
"Explain how to replace existing code without breaking functionality"
```

---

#### Task 1.5: Comprehensive Testing (90 min)
**Learning Focus:** Test-driven validation, debugging
- [ ] Test with live account data (P_020 files)
- [ ] Test with paper account data (D_020 files)
- [ ] Test with Tracker file missing
- [ ] Test with Tracker file locked
- [ ] Test with multiple matching entries
- [ ] Verify date format matching
- [ ] Verify option symbol matching
- [ ] Test with real January 2026 data

**Testing Checklist:**
```
✅ Test Case 1: Perfect Match
   Input: QBTS trade on 1/2/2026
   Tracker: Has QBTS, 1/2/2026, P_118
   Expected: System = "P_118"
   
✅ Test Case 2: No Match - New Trade
   Input: NVDA trade on 2/1/2026
   Tracker: No NVDA entry
   Expected: System = "TOS_Import"
   
✅ Test Case 3: No Tracker File
   Input: Any trade
   Tracker: File not found
   Expected: System = "TOS_Import", warning message shown
   
✅ Test Case 4: Tracker File Locked
   Input: Any trade
   Tracker: File open in Excel
   Expected: Error handled, System = "TOS_Import"
   
✅ Test Case 5: Case Sensitivity
   Input: qbts (lowercase)
   Tracker: Has QBTS (uppercase)
   Expected: Match found, System = "P_118"
```

**AI Assistant Prompts:**
```
"How do I create test data for my Python script?"
"Show me how to debug when my code doesn't match as expected"
"What's the best way to verify my function outputs are correct?"
```

---

### Milestone 1 Deliverables:
📄 Updated P_020_TOS_Parser_v2.2.py with auto-matching  
📄 Test results documentation  
📄 Updated README with new feature  
📊 Before/After comparison showing time saved

---

## 📋 MILESTONE 2: Basic File Monitoring Foundation
**Priority:** MEDIUM  
**Status:** Foundational Work  
**Time Estimate:** 2-3 hours  
**Target:** Mar 1-7, 2026

### What It Does:
Creates a simple file watcher that detects new TOS CSV files in the monitoring folders, laying groundwork for future full automation.

### Success Criteria:
✅ Script monitors `data/tos_exports/live/` folder  
✅ Detects new CSV files added  
✅ Logs file names and timestamps  
✅ Does NOT auto-process (Phase 2 feature)  
✅ Runs as simple command-line tool

### Tasks Breakdown:

#### Task 2.1: Create File Monitor Script (90 min)
**Learning Focus:** File system operations, watching directories
- [ ] Create new file: `P_020_File_Monitor.py`
- [ ] Use `watchdog` library to monitor folder
- [ ] Detect new .csv files only
- [ ] Log detection events
- [ ] Run in foreground (not as service yet)

**Starter Code:**
```python
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TOSFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.csv'):
            print(f"🔔 New TOS file detected: {os.path.basename(event.src_path)}")
            print(f"   Path: {event.src_path}")
            print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            # Future: auto-process here

def monitor_folder(folder_path):
    print(f"👀 Monitoring folder: {folder_path}")
    print("Press Ctrl+C to stop")
    
    event_handler = TOSFileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\tos_exports\live"
    monitor_folder(watch_path)
```

**AI Assistant Prompts:**
```
"Explain how file system monitoring works with watchdog library"
"Show me how to filter for only CSV files in Python"
"How do I run a Python script continuously until I stop it?"
```

**Testing:**
- Run the script
- Copy a CSV file into the monitored folder
- Verify detection message appears
- Test with non-CSV file (should ignore)

---

#### Task 2.2: Add Configuration File (60 min)
**Learning Focus:** JSON configuration, separation of code and config
- [ ] Create `P_020_config.json` for paths and settings
- [ ] Load config in both parser and monitor scripts
- [ ] Make paths configurable (not hard-coded)

**Config File Template:**
```json
{
    "version": "2.2",
    "tracker_dashboard": {
        "path": "C:\\Users\\Trader\\Documents\\AJZStrategiesLLC\\P_115_TrackerAudit\\P_115_118_TtrackerDashboard_V2.xlsx",
        "enabled": true
    },
    "monitoring": {
        "live_folder": "C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\P_020_AJZStrategies_PerformanceAnalysisSystem\\data\\tos_exports\\live",
        "paper_folder": "C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\P_020_AJZStrategies_PerformanceAnalysisSystem\\data\\tos_exports\\paper",
        "check_interval_seconds": 60
    },
    "logging": {
        "enabled": true,
        "level": "INFO"
    }
}
```

**AI Assistant Prompts:**
```
"How do I read a JSON config file in Python?"
"Show me best practices for configuration management"
"How do I handle Windows file paths in JSON?"
```

---

### Milestone 2 Deliverables:
📄 P_020_File_Monitor.py (foundational)  
📄 P_020_config.json  
📄 Documentation on how to use file monitor

---

## 📋 MILESTONE 3: Enhanced Error Handling & Logging
**Priority:** MEDIUM  
**Status:** Quality Improvement  
**Time Estimate:** 2-3 hours  
**Target:** Mar 8-14, 2026

### What It Does:
Improves the parser's robustness with better error messages, logging, and user feedback.

### Tasks:

#### Task 3.1: Add Logging Module (60 min)
- [ ] Implement Python `logging` module
- [ ] Create log files in `logs/` folder
- [ ] Log all operations, warnings, errors
- [ ] Make logs helpful for troubleshooting

#### Task 3.2: Improve Error Messages (60 min)
- [ ] Make error messages user-friendly (9th grade level)
- [ ] Add suggested fixes to error messages
- [ ] Create error categories (Warning, Error, Critical)

#### Task 3.3: Add Progress Indicators (45 min)
- [ ] Show progress during parsing ("Processing trade 45/167...")
- [ ] Display summary statistics at end
- [ ] Show what was matched vs. defaulted

**AI Assistant Prompts:**
```
"Show me how to use Python's logging module for beginners"
"How do I create helpful error messages?"
"What's a good way to show progress in console applications?"
```

---

## 📋 MILESTONE 4: Documentation & Polish
**Priority:** HIGH  
**Status:** Final Step  
**Time Estimate:** 2-3 hours  
**Target:** Mar 8-14, 2026

### Tasks:

#### Task 4.1: Update README (60 min)
- [ ] Document auto-matching feature
- [ ] Add configuration instructions
- [ ] Update troubleshooting section
- [ ] Add new examples

#### Task 4.2: Create User Guide for v2.2 (45 min)
- [ ] Step-by-step setup guide
- [ ] Screenshots or examples
- [ ] FAQ section

#### Task 4.3: Update Enhancement Tracker (30 min)
- [ ] Mark REQ-020126_01 as "Completed"
- [ ] Document lessons learned
- [ ] Add new enhancement ideas discovered during development

---

## 🧪 Testing Strategy

### Unit Testing (Per Task):
Test each function individually as you build it

### Integration Testing (Per Milestone):
Test how components work together

### User Acceptance Testing (Final):
Run through real workflow from start to finish:
1. Export from ThinkorSwim
2. Run parser
3. Verify auto-matching worked
4. Paste into Excel
5. Confirm time saved vs. manual process

---

## 📚 Learning Resources for Each Milestone

### Python Basics You'll Practice:
- ✅ Reading/writing files
- ✅ Working with Excel files (openpyxl)
- ✅ String manipulation and matching
- ✅ Date/time handling
- ✅ Dictionaries and data structures
- ✅ Error handling (try/except)
- ✅ Functions and parameters
- ✅ Configuration management
- ✅ File system monitoring

### VSCode Skills You'll Learn:
- ✅ Opening and navigating projects
- ✅ Running Python scripts
- ✅ Using integrated terminal
- ✅ Debugging basics
- ✅ Using extensions (Python)

### AI Assistant Collaboration:
- ✅ Breaking down complex tasks
- ✅ Understanding code explanations
- ✅ Debugging assistance
- ✅ Best practices guidance
- ✅ Code review and improvements

---

## 🎯 Success Metrics

### Quantitative:
- **Time Saved:** Reduce weekly import from 30 min → 3 min (90% reduction)
- **Accuracy:** 100% correct system assignment for matched trades
- **Coverage:** Auto-match 80%+ of trades (remaining 20% are new/unusual)
- **Reliability:** Handle 100% of edge cases gracefully

### Qualitative:
- **Confidence:** You understand every line of code you wrote
- **Maintainability:** Code is well-documented and easy to modify
- **Learning:** Can explain how auto-matching works to someone else
- **Satisfaction:** Weekly trading workflow feels effortless

---

## 🚧 Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Learning curve steeper than expected | Medium | Medium | Break tasks into smaller chunks, use AI assistant heavily |
| Tracker Dashboard format changes | Low | Medium | Add format validation, clear error messages |
| Time constraints from course | Medium | High | Focus on Milestone 1 only if needed, defer rest |
| Excel file locking issues | Medium | Low | Already handled in error handling design |

---

## 🔄 Phase 2 & 3 Roadmap (Post-Course)

These remain in the backlog but are **NOT** required for course completion:

### Phase 2: Full Automation (Future - April 2026)
- Scheduled task automation
- Auto-append to Excel with formula preservation
- Email notifications
- Weekly summary reports

### Phase 3: Analytics Dashboard (Future - May 2026+)
- System comparison metrics
- Win rate trends
- Risk analytics
- Interactive dashboards

---

## ✅ Weekly Checkpoints

### Week 1 Checkpoint (Feb 21):
- [ ] Environment setup complete
- [ ] Project plan reviewed and understood
- [ ] First AI assistant session completed
- [ ] Ready to start coding

### Week 2 Checkpoint (Feb 28):
- [ ] Task 1.1-1.3 complete (functions written)
- [ ] Basic matching working in isolation
- [ ] Confidence level improving

### Week 3 Checkpoint (Mar 7):
- [ ] Milestone 1 complete and tested
- [ ] v2.2 working with real data
- [ ] Time savings validated

### Week 4 Checkpoint (Mar 14):
- [ ] Documentation updated
- [ ] Course project complete
- [ ] Ready to present/demo

---

## 📝 Course Project Documentation

**For Your AI Fluency Course Submission:**

### Project Summary:
*"Enhanced a Python-based trading data parser with AI assistance to implement automated system name matching, reducing weekly data entry time by 90% (from 30 min to 3 min). Used Claude to break down complex tasks, debug code, and learn Python/VSCode best practices while building production-ready automation."*

### Key Accomplishments:
1. ✅ Implemented Excel file integration with error handling
2. ✅ Created intelligent symbol/date matching algorithm
3. ✅ Built robust fallback system for edge cases
4. ✅ Comprehensive testing across multiple scenarios
5. ✅ Documented code for future maintenance

### AI Collaboration Highlights:
- Used AI to explain openpyxl library functionality
- Got help debugging date format mismatches
- Learned error handling best practices
- Received code review and improvement suggestions
- Built confidence in Python programming

### Measurable Impact:
- **Before:** 30 min/week manual data entry × 52 weeks = 26 hours/year
- **After:** 3 min/week automated process × 52 weeks = 2.6 hours/year
- **Time Saved:** 23.4 hours/year (90% reduction)
- **Error Reduction:** ~100% (no more manual typos in system names)

---

## 🎓 Final Reflection Questions (For Course)

1. **What did you learn about working with AI assistants?**
2. **How did breaking down the project help you succeed?**
3. **What Python concepts did you master through this project?**
4. **How will you use these skills in future projects?**
5. **What would you do differently next time?**

---

**Next Steps:** 
1. Review this plan
2. Approve Milestone 1 scope
3. Install openpyxl
4. Begin Task 1.1

**Ready to start?** Let's dive into Milestone 1, Task 1.1! 🚀
