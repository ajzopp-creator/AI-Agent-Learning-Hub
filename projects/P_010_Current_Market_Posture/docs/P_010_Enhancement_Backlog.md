# P_010 ENHANCEMENT BACKLOG
**Last Updated:** March 23, 2026
**Location:** docs/P_010_Enhancement_Backlog.md

---

## STATUS KEY
- ✅ DONE       -- Completed and verified
- 🔄 IN PROGRESS -- Currently being built
- ⚠️ KNOWN ISSUE -- Documented problem, fix pending
- 📋 QUEUED     -- Approved, not yet started
- 💡 IDEA       -- Under consideration

---

## ✅ COMPLETED


### [2026-03-23] At Startup Time Guard (Late Boot Fix)
- **Problem:** Task Scheduler DisallowStartIfOnBatteries=true is Windows-enforced on
  this machine -- cannot be changed via PowerShell or XML import. When laptop boots
  on battery after the 7:30 AM window, posture run silently skipped.
- **Root cause confirmed:** Laptop booted at 10:30 AM on battery (3/23/2026) -- morning
  posture never ran, session used stale 03/19 grid data all day
- **Fix:** Added missed-run check to P_010_Start_Guardian.bat
  - On launch: checks for today's log in logs/P_010_Daily_YYYYMMDD.log
  - If missing: auto-calls P_010_daily_posture.bat, waits for completion, then starts Guardian
  - If present: prints OK and proceeds to monitor as normal
- **Result:** Guardian bat is now the safety net -- posture guaranteed to run at session
  start regardless of boot time or battery state
- System documentation updated to v3.3

### [2026-03-23] At Startup Time Guard (Late Boot Fix)
- **Problem:** Task Scheduler DisallowStartIfOnBatteries=true is Windows-enforced on
  this machine -- cannot be changed via PowerShell or XML import. When laptop boots
  on battery after the 7:30 AM window, posture run silently skipped.
- **Root cause confirmed:** Laptop booted at 10:30 AM on battery (3/23/2026) -- morning
  posture never ran, session used stale 03/19 grid data all day
- **Fix:** Added missed-run check to P_010_Start_Guardian.bat
  - On launch: checks for today's log in logs/P_010_Daily_YYYYMMDD.log
  - If missing: auto-calls P_010_daily_posture.bat, waits for completion, then starts Guardian
  - If present: prints OK and proceeds to monitor as normal
- **Result:** Guardian bat is now the safety net -- posture guaranteed to run at session
  start regardless of boot time or battery state
- System documentation updated to v3.3
### [2026-03-10] At Startup Trigger
- Added At Startup trigger to P_010_Daily_Posture_930AM Task Scheduler task
- Fires morning batch (posture + note writer) on any laptop boot, any day
- Existing safeguards handle weekends (note writer skips Sat/Sun) and mid-day reboots (note never overwrites)
- System doc updated to v3.1

### [2026-02-xx] ONE Master Config File Architecture
- P_010_RiskConfig.json is single source of truth for P_115/P_118
- Morning creates, intraday updates in place

### [2026-02-xx] Task Scheduler Automation
- P_010_Daily_Posture_930AM -- weekdays 9:30 AM
- P_010_Intraday_Check_200PM -- weekdays 2:00 PM
- StartWhenAvailable = true on both tasks

### [2026-02-xx] VXX Sentiment Overlay (v5)
- VXX posture added as confirmation layer
- Signals: BULLISH_CONFIRM / NEUTRAL / CAUTION / WARNING
- Does not change risk_mode, advisory only

### [2026-02-xx] Obsidian Daily Note Writer
- P_010_write_daily_note.py auto-generates pre-filled trading journal
- Template-driven (P_010_TemplateSchema_v*.md auto-selects latest version)
- Injects VP data, VXX signal, scripture, quote, humor
- Safety: never overwrites, skips weekends, respects SKIP_TODAY.flag

---

## 🔄 IN PROGRESS

### EZBreakouts Daily Automation
- **Goal:** Auto-fetch Eddie Z's daily stock picks + IBD exposure level
- **Status:** URL pattern solved (Teachable auto-increment IDs, no date formula)
- **Approach:** Scrape sidebar for today's date match --> extract lecture URL --> parse content
- **Output 1:** Inject IBD exposure level + stock picks into Obsidian daily note
- **Output 2:** Feed 10 stock picks to P_115 as candidate watchlist
- **Dependency:** Windows-MCP:Scrape works without login for sidebar content
- **Next Step:** Build Python script P_010_fetch_ez_picks.py
- **Sub-tasks:**
  - Parse exposure level (e.g. '20%-40%') --> store in RiskConfig or separate EZ json
  - Parse 10 stock picks + breakout points --> write to EZ_Picks_YYYYMMDD.json
  - P_115 reads EZ_Picks_YYYYMMDD.json for daily candidate list

---

## ⚠️ KNOWN ISSUES (Pending Fix)



### Chrome Extension Settings Popup
- **Problem:** Each new Claude in Chrome session opens keyboard shortcuts settings page
- **Impact:** Requires manual click-through before browser automation works
- **Pending Fix:** Investigate Chrome extension activation key conflict -- may need shortcut reassignment

---

## 📋 QUEUED (Approved, Not Yet Started)

### IBD Exposure Field in Obsidian Note
- Add manual input field to P_010_TemplateSchema for IBD market exposure level
- User types it in each morning (~5 seconds)
- Field: `ibdExposure: ___` in frontmatter + visible line in Section 5
- Blocked by: template schema update needed

### P_300 Migration to P_010
- **Problem:** P_300 system was built in wrong project folder
- **Goal:** Move all working P_300 code into P_010 structure (python/, tos_scripts/, data/, forecasts/, outputs/)
- **Status:** Working code exists, migration not yet executed
- **Priority:** Medium -- does not block current trading

---

## 💡 IDEAS (Under Consideration)

### Unified Morning + Intraday Program
- Consolidate separate morning and intraday scripts into one unified program
- Tony's plan: run separately for a period first, then merge
- Dependency: Both systems proven stable individually first

### Single Python Environment
- Consolidate all projects to conda p140 environment
- Motivation: venv fragile after CHKDSK/disk utilities; conda more resilient
- Current: p140 is primary, venv_old archived

### EZBreakouts Exposure --> P_010_RiskConfig.json
- Write parsed IBD exposure level directly into RiskConfig as advisory field
- Would allow P_115/P_118 to read it programmatically
- Design question: how to handle when EZ site is unavailable

---

## REFERENCE -- Enhancement Sources
- SESSION_INITIALIZATION_PROMPT_v2.7.md
- P_010_System_Documentation_v3.md
- P_010_Quick_Reference_Guide.md
- Session conversations (Claude Desktop)


