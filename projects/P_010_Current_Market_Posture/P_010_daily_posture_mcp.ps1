# =============================================================================
# P_010_daily_posture_mcp.ps1  —  v1.0  —  2026-05-29
# MCP-safe launcher for P_010 daily posture + Obsidian note writer.
#
# USE THIS instead of calling P_010_daily_posture.bat directly from Claude.
# P_010_daily_posture.bat runs two Python scripts sequentially.  Total wall
# time can exceed 4 minutes when note-writer fetches external content (quote,
# scripture, humor).  That blows the MCP global ceiling (~240s) and kills the
# job mid-run.  This wrapper launches detached and polls for completion.
#
# USAGE (from Windows-MCP PowerShell tool)
#   & "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_daily_posture_mcp.ps1"
# =============================================================================

$HUB_ROOT    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PROJECT     = "$HUB_ROOT\projects\P_010_Current_Market_Posture"
$BAT         = "$PROJECT\P_010_daily_posture.bat"
$LOGS        = "$PROJECT\logs"
$STATUS_FILE = "$LOGS\mcp_status_daily.txt"

# Ensure logs dir exists
if (-not (Test-Path $LOGS)) { New-Item -ItemType Directory -Path $LOGS | Out-Null }

# Load shared launcher
. "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"

Write-Output "============================================================"
Write-Output " P_010 DAILY POSTURE  —  MCP-Safe Launcher"
Write-Output " $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Output " Bat: $BAT"
Write-Output "============================================================"
Write-Output ""
Write-Output "Launching detached... polling every 10s (timeout 8 min)"
Write-Output ""

$result = Invoke-HubBat -BatPath $BAT `
                        -StatusFile $STATUS_FILE `
                        -PollSeconds 10 `
                        -TimeoutMinutes 8

Write-Output ""
Write-Output "============================================================"
Write-Output " RESULT: $result"
Write-Output " Log:    $LOGS\P_010_Daily_$(Get-Date -Format 'yyyyMMdd').log"
Write-Output "============================================================"
