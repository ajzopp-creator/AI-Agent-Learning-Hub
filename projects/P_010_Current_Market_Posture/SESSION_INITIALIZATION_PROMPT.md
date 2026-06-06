================================================================================
P_010 SESSION INITIALIZATION PROMPT v2.8
================================================================================
PROJECT: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\
================================================================================

## ENVIRONMENT
Claude Desktop + Windows-MCP. Claude has DIRECT file system access.
NEVER say "I don't have access". NEVER ask user to run commands manually.
MCP tool: windows-mcp:PowerShell

================================================================================
## CRITICAL: POWERSHELL EXECUTION RULES (bug confirmed 2026-06-01)
================================================================================

BANNED — Start-Process -NoNewWindow (any variant — blocks MCP ~4 min):
  Start-Process python.exe -NoNewWindow [-Wait|-PassThru|nothing]

ALWAYS — Start-Job + cmd /c:

  # CALL 1: launch
  $job = Start-Job -ScriptBlock {
      cmd /c """C:\path\python.exe"" ""script.py"" > ""C:\out.txt"" 2>&1"
  }

  # CALL 2: read (separate tool call)
  Start-Sleep -Seconds 45
  Get-Content "C:\out.txt"

Sleep sizing: no subprocess=0s | Python no Excel=20s | Python+Excel=45s | batch/backfill=90s
Working dir: cmd /c "cd /d ""C:\project\python"" && ""python.exe"" -m module > ""out.txt"" 2>&1"

================================================================================
## ARCHITECTURE
================================================================================

ONE FILE: P_010_RiskConfig.json — only file P_115/P_118 read for decisions.

Morning (9:30 AM) -> CREATES P_010_RiskConfig.json
Intraday (2 PM+)  -> UPDATES P_010_RiskConfig.json + creates audit in outputs/

================================================================================
## DAILY WORKFLOW
================================================================================

INIT DAY / INIT daily:
  $job = Start-Job -ScriptBlock {
      cmd /c "cd /d ""C:\...\P_010_Current_Market_Posture"" && ""python.exe"" ""python\P_010_daily_posture_v5.py"" > ""C:\out.txt"" 2>&1"
  }
  # 45s later: Get-Content "C:\out.txt"
  Produces: P_010_RiskConfig.json + grid_snapshot_latest.json + Obsidian note
            + data/snapshots/market_health/YYYYMMDD.json

INIT intraday:
  $job = Start-Job -ScriptBlock {
      cmd /c "cd /d ""C:\..."" && ""python.exe"" ""python\P_010_intraday_vp_check_v4.py"" > ""C:\out.txt"" 2>&1"
  }
  Produces: UPDATES P_010_RiskConfig.json (intraday_adjustment) + audit in outputs/

Verify morning:  read P_010_RiskConfig.json + latest log tail
Verify intraday: outputs/intraday_vp_check_*.json (sort LastWriteTime desc)

================================================================================
## FILE LOCATIONS
================================================================================

P_010_RiskConfig.json               Master config
grid_snapshot_latest.json           VP snapshot
P_010_MarketHealth.json             Distribution day / rally state
P_010_daily_posture.bat             Morning runner (steps 1+2+3)
P_010_run_intraday_vp_check.bat     Intraday runner

python/P_010_daily_posture_v5.py         Morning posture + VXX
python/P_010_intraday_vp_check_v4.py     Intraday PRANGE
python/P_010_write_daily_note.py         Obsidian note writer
python/application/health_runner.py      Market health orchestration
python/market_health/cli.py              Market health CLI

data/excel_exports/History Grid (SPY/QQQ/VXX)_v3.xlsx
data/snapshots/market_health/YYYYMMDD.json

================================================================================
## RISK MODES
================================================================================

avg_posture >= 1.0  -> FULL  (100%)
avg_posture 0-1.0   -> HALF  (50%)
avg_posture < 0     -> OFF   (0%, simulation only)
avg_posture > 1.08  -> HOT MARKET: HT6=2% HT7=3% HT8=4% HT9+=5%

Intraday: NONE / HALF (1 symbol >2% outside PRANGE) / REDUCED (both outside or >5%)
Final = MIN(risk_mode, intraday_adjustment)
Hierarchy: OFF < REDUCED < HALF < NONE < FULL

VXX signal (overlay only, does not change risk_mode):
  < -1.0  -> BULLISH_CONFIRM | -1 to 0.5 -> NEUTRAL
  0.5-1.5 -> CAUTION         | > 1.5      -> WARNING

================================================================================
## ERROR CORRECTIONS LOG
================================================================================

ERROR 001 — Intraday Cascading Upgrade Bug
Fixed: 2026-03-31 | Severity: HIGH
Symptom:  Multiple intraday runs caused OFF->HALF->FULL escalation.
Cause:    Script read morning_baseline from risk_config['risk_mode'] (overwritten each run).
Fix:      Script writes 'morning_risk_mode' on first run; always reads from it.
Rule:     NEVER read morning baseline from 'risk_mode'. Use 'morning_risk_mode'.
Verify:   After intraday, JSON must have BOTH:
            "morning_risk_mode": "OFF"   <- locked
            "risk_mode": "HALF"          <- adjusted

ERROR 002 — Windows-MCP Start-Process Hang Bug
Fixed: 2026-06-01 | Severity: HIGH
Symptom:  Start-Process -NoNewWindow blocked MCP ~4 min then timed out.
Cause:    Child inherits MCP stdio pipes; server blocks until child exits.
Fix:      All launches use Start-Job + cmd /c (see Critical section above).
Rule:     NEVER use Start-Process -NoNewWindow. ALWAYS use Start-Job.
Verify:   ~4 min hang with no output -> suspect -NoNewWindow.

================================================================================
## VERSION HISTORY
================================================================================
v2.8 (2026-06-01): Added PowerShell execution rules + ERROR 002; added market health step.
v2.7 (2026-02-08): Added MCP environment section and INIT workflow.
================================================================================
