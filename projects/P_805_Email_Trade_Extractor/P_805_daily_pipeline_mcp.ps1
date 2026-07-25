# =============================================================================
# P_805_daily_pipeline_mcp.ps1  —  v1.0  —  2026-07-18
# MCP-safe launcher for P_805 daily pipeline (Phase 3 -> 3.5 -> 4 -> 5.3).
#
# USE THIS instead of calling P_805_daily_pipeline.bat directly from Claude.
# The bat runs four Python phases sequentially including live IMAP calls.
# Total wall time can exceed the MCP global ceiling (~240s). This wrapper
# launches detached and polls for completion.
#
# USAGE (from Windows-MCP PowerShell tool)
#   & "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\P_805_daily_pipeline_mcp.ps1"
# =============================================================================

$HUB_ROOT    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PROJECT     = "$HUB_ROOT\projects\P_805_Email_Trade_Extractor"
$BAT         = "$PROJECT\P_805_daily_pipeline.bat"
$LOGS        = "$PROJECT\python\logs"
$STATUS_FILE = "$LOGS\mcp_status_daily.txt"

# Ensure logs dir exists
if (-not (Test-Path $LOGS)) { New-Item -ItemType Directory -Path $LOGS | Out-Null }

# Load shared launcher
. "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"

Write-Output "============================================================"
Write-Output " P_805 DAILY PIPELINE  —  MCP-Safe Launcher"
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
Write-Output " Log:    $LOGS\pipeline_runs.log"
Write-Output "============================================================"
