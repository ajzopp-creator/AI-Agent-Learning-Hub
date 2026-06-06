================================================================================
✅ P_010 SYSTEM INITIALIZATION PROMPT v2.7
================================================================================

PROJECT LOCATION:
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\

CRITICAL: Read this entire document before starting any P_010 work.

================================================================================
CLAUDE ENVIRONMENT & MCP TOOLS - READ THIS FIRST
================================================================================

**ENVIRONMENT: Claude Desktop Application**

This project runs in Claude Desktop with Windows-MCP server enabled. Claude has
DIRECT ACCESS to the Windows file system through MCP tools.

**CRITICAL REMINDERS:**
- NEVER say "I don't have access to your file system"
- NEVER suggest the user needs to run commands manually
- NEVER forget which environment you're running in
- The user is frustrated when you forget these capabilities!

**PRIMARY MCP TOOL: Windows-MCP:Shell**

This is your MAIN tool for all P_010 operations:
- Execute PowerShell commands on Windows system
- Read/write files
- Run batch files
- Check directory contents
- View logs

**TOOL NAME IS CRITICAL:**
❌ WRONG: "Powershell-Tool", "Windows-MCP:Powershell-Tool"
✅ RIGHT: "Windows-MCP:Shell"

**VERIFYING MCP CONNECTION:**

If Windows-MCP:Shell doesn't work:
1. The tool name is "Windows-MCP:Shell" - check spelling
2. Settings → MCP Servers → Windows-MCP should show "running"
3. TRY AGAIN with correct tool name
4. DO NOT immediately give up and suggest manual approaches

**COMMON P_010 COMMANDS:**

Navigate to project:
<function_calls>
<invoke name="Windows-MCP:Shell">
<parameter name="command">Set-Location "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture"; Get-Location</parameter>
</invoke>
</function_calls>

List files:
<function_calls>
<invoke name="Windows-MCP:Shell">
<parameter name="command">Get-ChildItem -Name</parameter>
</invoke>
</function_calls>

Read config file:
<function_calls>
<invoke name="Windows-MCP:Shell">
<parameter name="command">Get-Content "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json"</parameter>
</invoke>
</function_calls>

Run morning batch:
<function_calls>
<invoke name="Windows-MCP:Shell">
<parameter name="command">Set-Location "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture"; & .\P_010_daily_posture.bat</parameter>
</invoke>
</function_calls>

Check latest log:
<function_calls>
<invoke name="Windows-MCP:Shell">
<parameter name="command">Get-ChildItem "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\logs" -Filter "P_010_Daily_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 30</parameter>
</invoke>
</function_calls>

**INIT COMMAND WORKFLOW:**

When user says "INIT daily":
1. Navigate to P_010 directory
2. Run .\P_010_daily_posture.bat using Windows-MCP:Shell
3. Check P_010_RiskConfig.json was created/updated
4. Check grid_snapshot_latest.json was created
5. Review latest log file for errors
6. Report results to user with risk_mode and position sizing

DO NOT ask user to run it themselves - YOU run it with MCP tools!

================================================================================
SYSTEM ARCHITECTURE - ONE MASTER CONFIG FILE
================================================================================

**KEY CONCEPT: ONE FILE FOR EVERYTHING**

P_010_RiskConfig.json is THE ONLY file that P_115/P_118 read for trading decisions.

Morning script (9:30 AM):
  → CREATES P_010_RiskConfig.json with baseline risk_mode

Intraday script (2:00 PM+):
  → UPDATES P_010_RiskConfig.json by adding intraday fields
  → Creates timestamped audit file in outputs/ (for records only)

Result: ONE config file contains BOTH morning baseline + intraday adjustments

================================================================================
DAILY WORKFLOW
================================================================================

MORNING (9:30 AM):
──────────────────────────────────────────────────────────────────────────────
USER COMMAND: "INIT daily" or "Run morning system"

Claude executes:
  Windows-MCP:Shell: & .\P_010_daily_posture.bat

What it does:
  ✓ Reads Grid EXCEL files (History Grid SPY/QQQ_v3.xlsx)
  ✓ Calculates market posture from Medium/Long Term Differences
  ✓ Determines risk_mode: FULL (≥1.0), HALF (0.0-1.0), OFF (<0.0)
  ✓ Creates grid_snapshot_latest.json (VP Grid snapshot)
  ✓ CREATES/OVERWRITES P_010_RiskConfig.json with morning baseline

Outputs:
  ✓ grid_snapshot_latest.json (root) - VP Grid snapshot for intraday use
  ✓ P_010_RiskConfig.json (root) - Master config with risk_mode
  ✓ logs/P_010_Daily_YYYYMMDD.log - Execution record

P_010_RiskConfig.json structure (morning):
{
  "timestamp": "2026-02-06T09:30:00",
  "spy_posture": -3.94,
  "qqq_posture": -9.79,
  "avg_posture": -6.87,
  "risk_mode": "OFF",                ← Use this for position sizing
  "source": "Grid_XLSX",
  "spy_grid_date": "02/05/2026",
  "qqq_grid_date": "02/05/2026"
}

For Trading:
  → Read: P_010_RiskConfig.json
  → Value: "risk_mode"
  → Apply to P_115/P_118 position sizing:
     • FULL (≥1.0): Use 100% position sizing
     • HALF (0.0-1.0): Use 50% position sizing  
     • OFF (<0.0): Don't trade longs, 0% sizing


AFTERNOON (2:00 PM or later):
──────────────────────────────────────────────────────────────────────────────
USER COMMAND: "INIT intraday" or "Run intraday check"

Claude executes:
  Windows-MCP:Shell: & .\P_010_run_intraday_vp_check.bat

What it does:
  ✓ Loads grid_snapshot_latest.json (from 9:30 AM run)
  ✓ Fetches current SPY/QQQ prices via yfinance
  ✓ Validates prices vs VP predicted bands (PRANGE)
  ✓ Calculates deviation percentages
  ✓ Determines intraday adjustment: NONE/HALF/REDUCED
  ✓ UPDATES P_010_RiskConfig.json (adds 2 fields)
  ✓ Creates timestamped audit file in outputs/

Outputs:
  ✓ UPDATES P_010_RiskConfig.json (adds intraday_adjustment + reason)
  ✓ outputs/intraday_vp_check_YYYYMMDD_HHMMSS.json - Detailed audit
  ✓ logs/P_010_Daily_YYYYMMDD.log - Appended execution record

P_010_RiskConfig.json structure (after intraday):
{
  "timestamp": "2026-02-06T09:30:00",
  "spy_posture": -3.94,
  "qqq_posture": -9.79,
  "avg_posture": -6.87,
  "risk_mode": "OFF",                     ← Morning baseline
  "source": "Grid_XLSX",
  "spy_grid_date": "02/05/2026",
  "qqq_grid_date": "02/05/2026",
  "intraday_adjustment": "REDUCED",       ← Added by intraday
  "intraday_reason": "Both symbols outside PRANGE"  ← Added by intraday
}

For Trading:
  → Read: SAME FILE - P_010_RiskConfig.json
  → Check if "intraday_adjustment" field exists
  → If exists: Apply MIN(risk_mode, intraday_adjustment)
  → If missing: Use risk_mode only
  → Example: risk_mode=FULL + intraday_adjustment=HALF = use HALF sizing

Can run multiple times:
  • 2:00 PM ✓
  • 3:00 PM ✓
  • 4:00 PM ✓
  • Evening ✓
  
  Each run OVERWRITES the intraday fields (latest data wins)
  Each run CREATES new timestamped audit file (history preserved)

================================================================================
FILE LOCATIONS
================================================================================

Root Files (P_010 directory):
  ✓ P_010_daily_posture.bat - 9:30 AM runner
  ✓ P_010_run_intraday_vp_check.bat - 2 PM runner
  ✓ grid_snapshot_latest.json - VP snapshot (created by 9:30 AM)
  ✓ P_010_RiskConfig.json - Master config (ONE FILE for everything)

Python Scripts:
  ✓ python/P_010_daily_posture_v4.py - 9:30 AM logic
  ✓ python/P_010_intraday_vp_check_v4.py - 2 PM logic

Data:
  ✓ data/History Grid (SPY)_v3.xlsx - SPY Grid data
  ✓ data/History Grid (QQQ)_v3.xlsx - QQQ Grid data

Outputs:
  ✓ outputs/intraday_vp_check_*.json - Detailed audit files
  ✓ logs/P_010_Daily_*.log - Execution logs

================================================================================
INTEGRATION WITH P_115 / P_118
================================================================================

READ ONE FILE: P_010_RiskConfig.json

Location: 
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json

Integration Logic:

1. Load P_010_RiskConfig.json
2. Extract risk_mode (always present)
3. Check if intraday_adjustment field exists
4. Calculate final position sizing:

   IF intraday_adjustment field missing:
     → Use risk_mode only
     
   IF intraday_adjustment field present:
     → Apply: MIN(risk_mode, intraday_adjustment)
     
   Risk hierarchy (most restrictive wins):
     OFF < REDUCED < HALF < NONE < FULL

Position Sizing Translation:
  • FULL: 100% position sizing
  • HALF: 50% position sizing
  • REDUCED: 25% position sizing (or skip trade)
  • OFF: 0% position sizing (no trades)

Examples:
  Morning: risk_mode="FULL" (no intraday field)
    → Use 100% sizing
    
  Morning + Intraday: risk_mode="FULL", intraday_adjustment="HALF"
    → Use MIN(FULL, HALF) = HALF = 50% sizing
    
  Morning + Intraday: risk_mode="OFF", intraday_adjustment="REDUCED"
    → Use MIN(OFF, REDUCED) = OFF = 0% sizing

================================================================================
SYSTEM STATUS
================================================================================

✅ 9:30 AM SYSTEM: FULLY OPERATIONAL
  • Batch: P_010_daily_posture.bat
  • Script: python/P_010_daily_posture_v4.py
  • Status: PRODUCTION READY
  • Input: Excel files (History Grid SPY/QQQ_v3.xlsx)
  • Output: P_010_RiskConfig.json + grid_snapshot_latest.json
  • Tested: ✅ Multiple successful runs
  • Ready: YES - Use immediately for trading

✅ 2:00 PM SYSTEM: FULLY OPERATIONAL
  • Batch: P_010_run_intraday_vp_check.bat
  • Script: python/P_010_intraday_vp_check_v4.py
  • Status: PRODUCTION READY
  • Input: grid_snapshot_latest.json + live prices
  • Output: UPDATES P_010_RiskConfig.json + creates audit file
  • Tested: ✅ Multiple successful runs
  • Ready: YES - Use immediately for trading

✅ INTEGRATION: READY
  • P_115 can read P_010_RiskConfig.json
  • P_118 can read P_010_RiskConfig.json
  • Position sizing integration ready
  • All paths correct
  • ONE FILE architecture confirmed

================================================================================
EXAMPLE DAILY WORKFLOW
================================================================================

9:30 AM:
────────
USER: "INIT daily"

Claude uses Windows-MCP:Shell to run:
  Set-Location "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture"
  & .\P_010_daily_posture.bat
  
Creates:
  ✓ grid_snapshot_latest.json
  ✓ P_010_RiskConfig.json with risk_mode: OFF
  
Action:
  → P_115/P_118 read P_010_RiskConfig.json
  → See risk_mode: OFF
  → No intraday_adjustment field exists
  → Use 0% position sizing (don't trade)

2:00 PM:
────────
USER: "INIT intraday"

Claude uses Windows-MCP:Shell to run:
  & .\P_010_run_intraday_vp_check.bat
  
Updates:
  ✓ P_010_RiskConfig.json (adds intraday_adjustment: REDUCED)
  ✓ outputs/intraday_vp_check_20260206_140000.json (audit)
  
Action:
  → P_115/P_118 re-read P_010_RiskConfig.json
  → See risk_mode: OFF + intraday_adjustment: REDUCED
  → Apply MIN(OFF, REDUCED) = OFF
  → Still 0% position sizing (stay out)

3:00 PM (Second Run):
──────────────────────
USER: "Run intraday again"

Claude uses Windows-MCP:Shell to run:
  & .\P_010_run_intraday_vp_check.bat
  
Updates:
  ✓ P_010_RiskConfig.json (overwrites intraday_adjustment: NONE)
  ✓ outputs/intraday_vp_check_20260206_150000.json (new audit)
  
Action:
  → P_115/P_118 re-read P_010_RiskConfig.json
  → See risk_mode: OFF + intraday_adjustment: NONE
  → Apply MIN(OFF, NONE) = OFF
  → Still 0% position sizing

4:00 PM (Review):
─────────────────
USER: "Check logs"

Claude uses Windows-MCP:Shell to:
  → Check logs/P_010_Daily_20260206.log for execution record
  → Review audit files in outputs/ for detailed validation history
  → Verify P_010_RiskConfig.json has latest data
  → Ready for next trading day

================================================================================
BATCH FILE NAMES
================================================================================

Morning (9:30 AM):
  NAME: P_010_daily_posture.bat
  SCRIPT: python\P_010_daily_posture_v4.py
  ✓ Tested and operational

Afternoon (2:00 PM+):
  NAME: P_010_run_intraday_vp_check.bat
  SCRIPT: python\P_010_intraday_vp_check_v4.py
  ✓ Tested and operational

================================================================================
CRITICAL REMINDERS
================================================================================

1. MCP TOOL ACCESS:
   ✅ RIGHT: Use Windows-MCP:Shell to run all commands
   ❌ WRONG: Tell user to run commands themselves
   
2. ENVIRONMENT AWARENESS:
   ✅ RIGHT: Know you're in Claude Desktop with MCP
   ❌ WRONG: Forget what environment you're in
   
3. FILE NAMING:
   ❌ WRONG: risk_config.json
   ✅ RIGHT: P_010_RiskConfig.json
   
4. ARCHITECTURE:
   ❌ WRONG: Read two separate files
   ✅ RIGHT: Read ONE file (P_010_RiskConfig.json)
   
5. INTRADAY BEHAVIOR:
   ❌ WRONG: Creates separate timestamped file for trading
   ✅ RIGHT: UPDATES master config + creates audit file
   
6. DATA INPUT:
   ❌ WRONG: Reads XML files
   ✅ RIGHT: Reads Excel files (History Grid SPY/QQQ_v3.xlsx)
   
7. FIELD STRUCTURE:
   ✅ P_010_RiskConfig.json contains MINIMAL data
   ✅ outputs/intraday_vp_check_*.json contains DETAILED data
   
8. MULTIPLE RUNS:
   ✅ Each intraday run OVERWRITES previous intraday fields
   ✅ Latest data always wins
   ✅ Audit files preserve history

9. USER FRUSTRATION PREVENTION:
   ✅ Read this document carefully EVERY session
   ✅ Remember MCP tool names and capabilities
   ✅ Don't make user repeat what you should remember
   ✅ Use Windows-MCP:Shell proactively

================================================================================
TESTING VERIFICATION
================================================================================

✅ Test 1 - Morning System:
  Command: Windows-MCP:Shell: & .\P_010_daily_posture.bat
  Result: ✅ PASS - PRODUCTION READY
  • Reads Excel Grid files
  • Calculates posture from Medium/Long Term Differences
  • Creates grid_snapshot_latest.json
  • Creates P_010_RiskConfig.json with risk_mode
  • Logs execution to P_010_Daily_YYYYMMDD.log

✅ Test 2 - Afternoon System:
  Command: Windows-MCP:Shell: & .\P_010_run_intraday_vp_check.bat
  Result: ✅ PASS - PRODUCTION READY
  • Loads grid_snapshot_latest.json
  • Fetches live SPY/QQQ prices
  • Validates against PRANGE
  • UPDATES P_010_RiskConfig.json (adds 2 fields)
  • Creates timestamped audit file
  • Logs execution to P_010_Daily_YYYYMMDD.log

✅ Test 3 - Multiple Intraday Runs:
  Result: ✅ PASS
  • Second run overwrites intraday fields
  • No data accumulation
  • Latest data always current
  • Audit files preserve history

✅ Test 4 - Integration:
  Result: ✅ PASS
  • P_010_RiskConfig.json readable by other projects
  • Fields correctly formatted
  • JSON valid and parseable
  • Path accessible from P_115/P_118

✅ Test 5 - MCP Tool Access:
  Result: ✅ PASS
  • Windows-MCP:Shell executes PowerShell commands
  • Can run batch files
  • Can read/write files
  • Can navigate directories
  • Tool name: "Windows-MCP:Shell" confirmed

================================================================================
READY TO TRADE
================================================================================

✅ Use Windows-MCP:Shell to run P_010_daily_posture.bat at 9:30 AM
✅ Read P_010_RiskConfig.json for risk_mode
✅ Apply to P_115/P_118 position sizing
✅ Optional: Use Windows-MCP:Shell to run P_010_run_intraday_vp_check.bat at 2 PM
✅ Re-read P_010_RiskConfig.json for intraday_adjustment
✅ Apply MIN(risk_mode, intraday_adjustment) logic

YOU'RE ALL SET! 🚀

================================================================================
VERSION HISTORY
================================================================================

v2.7 (2026-02-08):
  • Added comprehensive CLAUDE ENVIRONMENT & MCP TOOLS section
  • Documented Windows-MCP:Shell tool name and syntax
  • Added MCP command examples for all P_010 operations
  • Added INIT command workflow documentation
  • Added critical reminders about MCP tool usage
  • Added user frustration prevention guidelines
  • Documented correct tool name: Windows-MCP:Shell

v2.6 (2026-02-07):
  • Integrated intraday validation system into main workflow
  • Documented ONE MASTER FILE architecture
  • Added MIN function logic for risk combination
  • Updated JSON structure examples
  • Added multiple intraday run behavior

v2.5 and earlier:
  • Initial system development and documentation

================================================================================
