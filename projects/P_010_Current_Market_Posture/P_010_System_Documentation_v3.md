# P_010 MARKET POSTURE SYSTEM — SYSTEM DOCUMENTATION
**Version:** 3.3
**Last Updated:** March 23, 2026
**Status:** PRODUCTION

---

## 1. PURPOSE

P_010 provides daily market posture assessment using VantagePoint Grid predictions
to determine appropriate risk levels for P_115 and P_118 trading strategies.
The system outputs a risk recommendation that trading systems interpret with
documented override logic. The system also auto-generates a pre-filled Obsidian
daily journal note every morning.

---

## 2. SYSTEM ARCHITECTURE

### Three-Script Pipeline (9:30 AM)

```
P_010_daily_posture.bat
  STEP 1 --> P_010_daily_posture_v5.py
               Reads: data/excel_exports/History Grid (SPY)_v3.xlsx
               Reads: data/excel_exports/History Grid (QQQ)_v3.xlsx
               Reads: data/excel_exports/History Grid (VXX)_v3.xlsx
               Writes: P_010_RiskConfig.json  (master config)
               Writes: grid_snapshot_latest.json  (intraday snapshot)
               Writes: data/snapshots/grid_snapshot_YYYYMMDD_HHMMSS.json

  STEP 2 --> P_010_write_daily_note.py
               Reads: P_010_RiskConfig.json
               Reads: grid_snapshot_latest.json
               Reads: Templates/P_010_TemplateSchema_v*.md  (auto-picks latest)
               Fetches: Scripture API, Quote API, Joke API (live)
               Writes: TradingJournal/DD-MM-YYYY.md  (Obsidian vault)
```

### Intraday Pipeline (2:00 PM+)

```
P_010_run_intraday_vp_check.bat
  --> P_010_intraday_vp_check_v4.py
        Reads: grid_snapshot_latest.json
        Fetches: Live SPY/QQQ prices via yfinance
        UPDATES: P_010_RiskConfig.json  (adds intraday_adjustment field)
        Writes: outputs/intraday_vp_check_YYYYMMDD_HHMMSS.json  (audit)
```

---

## 3. FILE LOCATIONS

### Project Root
```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\
```

### Key Files
```
P_010_RiskConfig.json               Master config -- ONE file for all decisions
grid_snapshot_latest.json           VP Grid snapshot (intraday use)
P_010_daily_posture.bat             Morning runner (Steps 1+2)
P_010_run_intraday_vp_check.bat     Intraday runner
SKIP_TODAY.flag                     Drop here to skip all automation today
P_010_Start_Guardian.bat            Session error watcher launcher (run each morning)
P_010_Claude_Session_Guardian.ps1   PowerShell background watcher script
```

### Python Scripts (python/)
```
P_010_daily_posture_v5.py           ACTIVE -- morning posture + VXX
P_010_intraday_vp_check_v4.py       ACTIVE -- intraday PRANGE validation
P_010_write_daily_note.py           ACTIVE -- Obsidian note writer
requirements.txt                    pip dependencies
archive/                            Prior versions (reference only)
```

### Data Files (data/excel_exports/)
```
History Grid (SPY)_v3.xlsx          VantagePoint SPY grid (update nightly ~6:30 PM)
History Grid (QQQ)_v3.xlsx          VantagePoint QQQ grid
History Grid (VXX)_v3.xlsx          VantagePoint VXX grid
```

### Outputs
```
outputs/intraday_vp_check_*.json    Detailed intraday audit files
logs/P_010_Daily_YYYYMMDD.log       Daily execution log
data/snapshots/                     Timestamped grid snapshots
```

### Obsidian Vault
```
C:\Users\Trader\Documents\AJZStrategies_TradingJournal\Trading Journal\
  Templates/P_010_TemplateSchema_v1.md    Template schema (source of truth for layout)
  TradingJournal/DD-MM-YYYY.md            Daily notes (auto-generated)
```

---

## 4. RISK MODE CALCULATION

### Morning Baseline
```
Medium_Term_Diff = (predicted_close - current_close) / current_close x 100
Long_Term_Diff   = similar calculation with longer timeframe
Posture_Score    = (Medium_Term_Diff + Long_Term_Diff) / 2

SPY_posture and QQQ_posture calculated separately
avg_posture = (SPY_posture + QQQ_posture) / 2

IF avg_posture >= 1.0  --> risk_mode = "FULL"
IF avg_posture >= 0.0  --> risk_mode = "HALF"
IF avg_posture <  0.0  --> risk_mode = "OFF"
```

### VXX Sentiment Overlay (v5 addition)
```
VXX posture calculated same way as SPY/QQQ but INVERTED in interpretation:
  vxx_posture < -1.0          --> vxx_signal = "BULLISH_CONFIRM"
  -1.0 <= vxx_posture < 0.5   --> vxx_signal = "NEUTRAL"
  0.5 <= vxx_posture < 1.5    --> vxx_signal = "CAUTION"
  vxx_posture >= 1.5           --> vxx_signal = "WARNING"

VXX does NOT change risk_mode. It is a sentiment confirmation layer only.
```

### Intraday Adjustment
```
Both symbols within PRANGE         --> intraday_adjustment = "NONE"
One symbol outside PRANGE (>2%)    --> intraday_adjustment = "HALF"
Both outside OR deviation >5%      --> intraday_adjustment = "REDUCED"

Final mode = MIN(risk_mode, intraday_adjustment)
Risk hierarchy (most restrictive): OFF < REDUCED < HALF < NONE < FULL
```

---

## 5. P_010_RiskConfig.json SCHEMA (v5)

### After Morning Run (Step 1)
```json
{
  "timestamp": "2026-03-10T09:30:00",
  "spy_posture": -4.1273,
  "qqq_posture": -1.2808,
  "avg_posture": -2.7040,
  "risk_mode": "OFF",
  "source": "Grid_XLSX",
  "spy_grid_date": "03/06/2026",
  "qqq_grid_date": "03/06/2026",
  "vxx_posture": 3.0279,
  "vxx_signal": "WARNING",
  "vxx_note": "VP predicts sharp VXX rise -- potential fear spike, reduce exposure",
  "vxx_close": 35.67,
  "vxx_pred_high": 37.71,
  "vxx_pred_low": 33.83,
  "vxx_grid_date": "03/06/2026"
}
```

### After Intraday Run (Step 2 adds 2 fields)
```json
{
  ... all morning fields above ...,
  "intraday_adjustment": "REDUCED",
  "intraday_reason": "Both symbols outside PRANGE"
}
```

---

## 6. POSITION SIZING

| Risk Mode | Sizing | Guidance |
|-----------|--------|----------|
| FULL      | 100%   | Standard $525 risk (or tiered in hot market) |
| HALF      | 50%    | $262.50 risk -- neutral market caution |
| OFF       | 0%     | No long trades -- calculation shown for simulation only |

### Hot Market (avg_posture > 1.08)
| HybridTier | Risk % | Dollar Risk |
|------------|--------|-------------|
| HT 6       | 2.0%   | $700        |
| HT 7       | 3.0%   | $1,050      |
| HT 8       | 4.0%   | $1,400      |
| HT 9+      | 5.0%   | $1,750      |

### OFF Mode Override
OFF mode is a strong warning, not an absolute block. Trading systems still
calculate and display position sizing with prominent CORRECTION MODE warnings
to preserve educational value and user autonomy. Eddie Z Rule applies:
"Avoid breakouts during distribution phase."

---

## 7. OBSIDIAN DAILY NOTE WRITER

### How It Works
P_010_write_daily_note.py reads the template schema, replaces all Templater
tags with real values, injects VP data into Section 5, injects the pre-market
price table into Section 6, and writes the completed note to the vault.

### Template Selection
The script searches Templates/ for all files matching P_010_TemplateSchema_v*.md
and automatically selects the highest version number. Drop a v2 in the folder
and it picks it up the next morning -- no code change needed.

### What Gets Auto-Filled
- Frontmatter: date, day, week + P_010 fields
- Section 1: Scripture (labs.bible.org), Quote (zenquotes.io), Humor (jokeapi.dev)
- Section 5: Full VP data table, VXX signal, suggested Bias + Risk Level checkboxes
- Section 6: SPY/QQQ/VXX closes + predicted high/low + PRANGE table

### What Tony Fills In (~45 seconds)
- Market Bias checkbox confirmation (suggestion provided)
- Market Regime (one word)
- Key Setups / Notes (1-2 lines)
- Section 3: Google Calendar events (from sidebar plugin)
- Section 4: WhatsApp channel content
- Section 7: Trade execution log

### Safety Rules
- NEVER overwrites an existing note
- Skips weekends (Mon-Fri only)
- Respects SKIP_TODAY.flag
- Falls back to hardcoded layout with callout warning if template missing
- All three API fetches fail gracefully with inline message

---

## 8. DAILY WORKFLOW

### Morning (9:30 AM -- automated via Task Scheduler)
```
Task: P_010_Daily_Posture_930AM
Triggers:
  1. Weekdays 7:30 AM (StartWhenAvailable = true)
Runs: P_010_daily_posture.bat
  --> Step 1: Posture analysis --> P_010_RiskConfig.json
  --> Step 2: Note writer --> TradingJournal/DD-MM-YYYY.md
```

**✅ LATE LAPTOP START -- RESOLVED VIA GUARDIAN BAT (2026-03-23):**
```
Root cause: Task Scheduler DisallowStartIfOnBatteries = true (Windows-enforced,
cannot be overridden via PowerShell or XML import on this machine). When laptop
boots on battery after the 7:30 AM window, the posture run is silently skipped
even with StartWhenAvailable = true.

Fix applied 2026-03-23: P_010_Start_Guardian.bat now includes a missed-run check.
  IF today's posture log is missing --> auto-calls P_010_daily_posture.bat first
  IF today's posture log exists     --> prints OK and starts Guardian monitor

Result: Launching the Guardian at session start guarantees the posture will run
regardless of boot time or battery state. No manual INIT required.
```

### Intraday (2:00 PM -- automated via Task Scheduler)
```
Task: P_010_Intraday_Check_200PM
Runs: P_010_run_intraday_vp_check.bat
  --> UPDATES P_010_RiskConfig.json with intraday_adjustment
  --> Creates timestamped audit in outputs/
Can be run multiple times -- latest data always wins
```

### Manual Triggers (Claude Desktop)
```
"INIT daily"     --> Claude runs P_010_daily_posture.bat via Windows-MCP:Shell
"INIT intraday"  --> Claude runs P_010_run_intraday_vp_check.bat
```
### Morning Startup Sequence (Manual Steps Before Trading)
```
Step 1: Double-click P_010_Start_Guardian.bat  -- starts background error watcher
Step 2: Open Claude Desktop -- Guardian monitors silently while you work
Step 3: Verify P_010_RiskConfig.json was created by Task Scheduler (or INIT daily)

Guardian alert types:
  DATA LOSS WARNING  [RED]    -- sync_loss_accepted: stop pasting new work immediately
  Sync Blocked       [YELLOW] -- messages not saving to server
  Server Error       [YELLOW] -- Anthropic API returning 500 errors
  Request Failed     [RED]    -- non-retryable failure on last message

Guardian runs until you close it. Leave it running all session.
```

---

## 9. INTEGRATION WITH P_115 / P_118

```
Read:  P_010_RiskConfig.json
Field: risk_mode (always present)
Check: intraday_adjustment (may not exist before 2 PM run)

Logic:
  IF intraday_adjustment exists --> final = MIN(risk_mode, intraday_adjustment)
  ELSE                          --> final = risk_mode

Apply final to position sizing per Section 6 table above.
```

---

## 10. TROUBLESHOOTING

| Problem | Action |
|---------|--------|
| RiskConfig.json not found | Run morning batch; fallback to standard 1.5% risk |
| Stale data (timestamp > 24hr) | VP grid not exported -- re-export from VantagePoint |
| Note already exists | Delete DD-MM-YYYY.md from TradingJournal/ to regenerate |
| Template not found | Add P_010_TemplateSchema_v*.md to Templates/ folder |
| yfinance module missing | conda activate p140; pip install yfinance |
| MCP tool not responding | Start fresh Claude Desktop conversation |
| Task Scheduler not firing | Check StartWhenAvailable flag; verify bat file paths unchanged |

---

## 11. TASK SCHEDULER

```
Task 1: P_010_Daily_Posture_930AM
  Trigger:   Weekdays 7:30 AM  (StartWhenAvailable = true)
  Action:    P_010_daily_posture.bat
  Battery fix: P_010_Start_Guardian.bat handles missed runs (see Section 8)

Task 2: P_010_Intraday_Check_200PM
  Trigger:  Weekdays 2:00 PM
  Action:   P_010_run_intraday_vp_check.bat
  Settings: StartWhenAvailable = true
```

**CRITICAL:** Batch file names must never change. Task Scheduler references them directly.
Current bat names are locked:
- P_010_daily_posture.bat
- P_010_run_intraday_vp_check.bat

---

## 12. VERSION HISTORY

**v3.3 (March 23, 2026):**
- Diagnosed late laptop start logic gap: Task Scheduler DisallowStartIfOnBatteries=true
  cannot be overridden on this machine (Windows enforces it regardless of XML/PS edits)
- Fix: Added missed-run check to P_010_Start_Guardian.bat -- checks for today's log on
  launch, auto-calls P_010_daily_posture.bat if missing, then starts Guardian monitor
- Removed At Startup trigger from P_010_Daily_Posture_930AM (no longer needed)
- Section 8 updated: At Startup Known Issue --> Resolved via Guardian bat
- Section 11 updated: Task Scheduler entry corrected
- Enhancement Backlog: At Startup time guard moved to Completed

**v3.2 (March 11, 2026):**
- Added Claude Session Guardian (P_010_Start_Guardian.bat + P_010_Claude_Session_Guardian.ps1)
- Guardian monitors Claude Desktop log for server errors and data loss events
- Pops Windows toast notifications for: sync_loss_accepted, sync_blocked, API 500s, Request Failed
- Added to Section 3 (File Locations) and Section 8 (Morning Startup Sequence)
- Fixed DST drift on both Task Scheduler tasks (930AM + 200PM) -- both now confirmed 9:30/14:00 EDT
- Confirmed At Startup trigger active on P_010_Daily_Posture_930AM (added via elevated PS)

**v3.1 (March 10, 2026):**
- Added At Startup trigger to P_010_Daily_Posture_930AM Task Scheduler task
- Documented At Startup known issue (Obsidian note writer conflict)
- Documented pending fix: time guard or bat split needed
- Section 8 and Section 11 updated
- Created docs/P_010_Enhancement_Backlog.md -- see Section 13

**v3.0 (March 8, 2026):**
- Added VXX sentiment overlay (v5 script)
- Added P_010_RiskConfig.json v5 schema (VXX fields)
- Added Obsidian daily note writer documentation
- Added template-driven architecture (P_010_TemplateSchema_v*.md)
- Updated python/ folder structure (production vs archive)
- Added Google Calendar integration note
- python/ cleanup -- production scripts only in root, archive/ for prior versions

**v2.x (February 2026):**
- Morning + intraday system fully operational
- ONE master config file architecture
- MIN() logic for risk combination
- Excel-based grid reading (v4+ scripts)

**v1.x (January 2026):**
- Initial P_010 development
- XML-based grid reading (deprecated)


---

## 13. ENHANCEMENT BACKLOG

All pending enhancements, known issues, in-progress work, and future ideas
are tracked in a dedicated file:

    docs/P_010_Enhancement_Backlog.md

### Current Status Summary (as of March 23, 2026)

| Item | Status |
|------|--------|
| At Startup trigger | ✅ Done |
| EZBreakouts automation + P_115 feed | 🔄 In Progress |
| At Startup time guard | ✅ Done (Guardian bat) |
| Chrome extension settings popup | ⚠️ Known Issue |
| IBD Exposure field in Obsidian note | 📋 Queued |
| P_300 migration to P_010 | 📋 Queued |
| Unified morning + intraday program | 💡 Idea |
| Single Python environment (conda p140) | 💡 Idea |

See docs/P_010_Enhancement_Backlog.md for full details on each item.
