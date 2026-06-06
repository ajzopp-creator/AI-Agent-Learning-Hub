# =============================================================================
# P_300_DailyEval_mcp.ps1  —  v1.0  —  2026-05-29
# MCP-safe launcher for P_300 daily evaluate + Obsidian write + archive.
#
# USE THIS instead of calling P_300_DailyEval_v2.bat directly from Claude.
# Pass the stock symbol as the first argument.
#
# USAGE (from Windows-MCP PowerShell tool)
#   & "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\P_300_DailyEval_mcp.ps1" -Symbol VZ
#   & "...\P_300_DailyEval_mcp.ps1" -Symbol SPY
# =============================================================================

param(
    [Parameter(Mandatory)][string]$Symbol
)

$HUB_ROOT    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PROJECT     = "$HUB_ROOT\projects\P_300_Vantage_Point_Pattern_Recognition"
$BAT         = "$PROJECT\P_300_DailyEval_v2.bat"
$LOGS        = "$PROJECT\logs"
$STATUS_FILE = "$LOGS\mcp_status_eval_$Symbol.txt"

if (-not (Test-Path $LOGS)) { New-Item -ItemType Directory -Path $LOGS | Out-Null }

# Validate XLSX exists before launching
$XLSX = "$PROJECT\data\live\History Grid ($Symbol).xlsx"
if (-not (Test-Path $XLSX)) {
    Write-Output "ERROR: XLSX not found: $XLSX"
    Write-Output "Ensure the file is in data\live\ before running."
    exit 1
}

. "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"

# Build a wrapper bat that passes the symbol argument to P_300_DailyEval_v2.bat
$tmpBat = "$LOGS\mcp_eval_$Symbol`_tmp.bat"
"@echo off`ncall `"$BAT`" $Symbol" | Set-Content -Path $tmpBat -Encoding ASCII

Write-Output "============================================================"
Write-Output " P_300 DAILY EVAL  —  MCP-Safe Launcher"
Write-Output " Symbol : $Symbol"
Write-Output " $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Output " XLSX   : $XLSX"
Write-Output "============================================================"
Write-Output ""
Write-Output "Launching detached... polling every 10s (timeout 10 min)"
Write-Output ""

$result = Invoke-HubBat -BatPath $tmpBat `
                        -StatusFile $STATUS_FILE `
                        -PollSeconds 10 `
                        -TimeoutMinutes 10

# Clean up tmp bat
if (Test-Path $tmpBat) { Remove-Item $tmpBat -Force }

Write-Output ""
Write-Output "============================================================"
Write-Output " RESULT: $result"
Write-Output " Reports: $PROJECT\outputs\reports\"
Write-Output "============================================================"
