# =============================================================================
# P_020_WeeklyUpdate_mcp.ps1  —  v1.0  —  2026-05-29
# MCP-safe launcher for P_020 weekly update (balance + import + analyze).
#
# USAGE (from Windows-MCP PowerShell tool)
#   & "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\P_020_WeeklyUpdate_mcp.ps1"
# =============================================================================

$HUB_ROOT    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PROJECT     = "$HUB_ROOT\projects\P_020_AJZStrategies_PerformanceAnalysisSystem"
$BAT         = "$PROJECT\P_020_Weekly_Update.bat"
$LOGS        = "$PROJECT\audit_logs"
$STATUS_FILE = "$LOGS\mcp_status_weekly.txt"

if (-not (Test-Path $LOGS)) { New-Item -ItemType Directory -Path $LOGS | Out-Null }

. "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"

Write-Output "============================================================"
Write-Output " P_020 WEEKLY UPDATE  —  MCP-Safe Launcher"
Write-Output " $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Output " Bat: $BAT"
Write-Output "============================================================"
Write-Output ""
Write-Output "Launching detached... polling every 10s (timeout 10 min)"
Write-Output ""

$result = Invoke-HubBat -BatPath $BAT `
                        -StatusFile $STATUS_FILE `
                        -PollSeconds 10 `
                        -TimeoutMinutes 10

Write-Output ""
Write-Output "============================================================"
Write-Output " RESULT: $result"
Write-Output " Logs:   $LOGS\"
Write-Output "============================================================"
