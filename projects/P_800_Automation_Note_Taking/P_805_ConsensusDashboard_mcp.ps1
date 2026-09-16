# =============================================================================
# P_805_ConsensusDashboard_mcp.ps1  --  v1.0  --  2026-09-08
# MCP-safe launcher for the P_805 Consensus Dashboard build (WO-P800-E6.001).
#
# USAGE (from Windows-MCP PowerShell tool)
#   & "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\P_805_ConsensusDashboard_mcp.ps1"
# =============================================================================

$HUB_ROOT    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PROJECT     = "$HUB_ROOT\projects\P_800_Automation_Note_Taking"
$BAT         = "$PROJECT\python\p805_consensus\launch_consensus_dashboard.bat"
$LOGS        = "$PROJECT\logs"
$STATUS_FILE = "$LOGS\mcp_status_p805_consensus.txt"

if (-not (Test-Path $LOGS)) { New-Item -ItemType Directory -Path $LOGS | Out-Null }

. "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"
if (-not (Get-Command Invoke-HubBat -ErrorAction SilentlyContinue)) {
    # Transient dot-source race (ref EC-009) -- retry once before giving up
    Start-Sleep -Milliseconds 500
    . "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"
}
if (-not (Get-Command Invoke-HubBat -ErrorAction SilentlyContinue)) {
    Write-Output "FATAL: hub_mcp_launcher.ps1 failed to load Invoke-HubBat after retry -- aborting, nothing was run."
    exit 1
}

Write-Output "============================================================"
Write-Output " P_805 CONSENSUS DASHBOARD  --  MCP-Safe Launcher"
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
Write-Output " Logs:   $LOGS\"
Write-Output "============================================================"