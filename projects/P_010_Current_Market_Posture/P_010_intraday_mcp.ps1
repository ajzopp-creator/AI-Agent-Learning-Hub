# =============================================================================
# P_010_intraday_mcp.ps1  —  v1.0  —  2026-05-29
# MCP-safe launcher for P_010 intraday VP check.
#
# USE THIS instead of calling P_010_run_intraday_vp_check.bat directly.
#
# USAGE (from Windows-MCP PowerShell tool)
#   & "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_intraday_mcp.ps1"
# =============================================================================

$HUB_ROOT    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PROJECT     = "$HUB_ROOT\projects\P_010_Current_Market_Posture"
$BAT         = "$PROJECT\P_010_run_intraday_vp_check.bat"
$LOGS        = "$PROJECT\logs"
$STATUS_FILE = "$LOGS\mcp_status_intraday.txt"

if (-not (Test-Path $LOGS)) { New-Item -ItemType Directory -Path $LOGS | Out-Null }

. "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"

Write-Output "============================================================"
Write-Output " P_010 INTRADAY VP CHECK  —  MCP-Safe Launcher"
Write-Output " $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Output " Bat: $BAT"
Write-Output "============================================================"
Write-Output ""
Write-Output "Launching detached... polling every 10s (timeout 5 min)"
Write-Output ""

$result = Invoke-HubBat -BatPath $BAT `
                        -StatusFile $STATUS_FILE `
                        -PollSeconds 10 `
                        -TimeoutMinutes 5

Write-Output ""
Write-Output "============================================================"
Write-Output " RESULT: $result"
Write-Output " Log:    $LOGS\P_010_Daily_$(Get-Date -Format 'yyyyMMdd').log"
Write-Output "============================================================"
