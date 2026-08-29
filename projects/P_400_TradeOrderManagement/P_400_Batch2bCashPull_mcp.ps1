# =============================================================================
# P_400_Batch2bCashPull_mcp.ps1  --  v1.0  --  2026-08-25
# MCP-safe launcher for P_400 batch-2b with auto cash-pull (P_020 balance pull
# chained into P_400 batch-2b --cash).
#
# USAGE (from Windows-MCP PowerShell tool, or run directly)
#   & "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\P_400_Batch2bCashPull_mcp.ps1"
# =============================================================================

$HUB_ROOT    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PROJECT     = "$HUB_ROOT\projects\P_400_TradeOrderManagement"
$BAT         = "$PROJECT\P_400_Batch2b_CashPull.bat"
$LOGS        = "$PROJECT\audit_logs"
$STATUS_FILE = "$LOGS\mcp_status_batch2b_cashpull.txt"

if (-not (Test-Path $LOGS)) { New-Item -ItemType Directory -Path $LOGS | Out-Null }

. "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"

Write-Output "============================================================"
Write-Output " P_400 BATCH-2B (CASH PULL + RUN)  --  MCP-Safe Launcher"
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