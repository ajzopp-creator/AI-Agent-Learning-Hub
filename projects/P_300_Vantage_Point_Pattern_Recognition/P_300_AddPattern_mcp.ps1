# =============================================================================
# P_300_AddPattern_mcp.ps1  —  v1.0  —  2026-05-29
# MCP-safe launcher for P_300 add-pattern pipeline.
#
# USAGE (from Windows-MCP PowerShell tool)
#   & "...\P_300_AddPattern_mcp.ps1" -XlsxPath "data\historical_patterns\History Grid (AAPL).xlsx"
#   & "...\P_300_AddPattern_mcp.ps1" -XlsxPath "C:\full\absolute\path.xlsx"
# =============================================================================

param(
    [Parameter(Mandatory)][string]$XlsxPath
)

$HUB_ROOT    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PROJECT     = "$HUB_ROOT\projects\P_300_Vantage_Point_Pattern_Recognition"
$BAT         = "$PROJECT\P_300_AddPattern.bat"
$LOGS        = "$PROJECT\logs"

# Derive a safe filename for the status file from the xlsx name
$xlsxSafe    = [System.IO.Path]::GetFileNameWithoutExtension($XlsxPath) -replace '[^a-zA-Z0-9_]', '_'
$STATUS_FILE = "$LOGS\mcp_status_addpat_$xlsxSafe.txt"

if (-not (Test-Path $LOGS)) { New-Item -ItemType Directory -Path $LOGS | Out-Null }

# Resolve relative path relative to project root
if (-not [System.IO.Path]::IsPathRooted($XlsxPath)) {
    $XlsxPath = Join-Path $PROJECT $XlsxPath
}

if (-not (Test-Path $XlsxPath)) {
    Write-Output "ERROR: XLSX not found: $XlsxPath"
    exit 1
}

. "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"

# Argument-passing wrapper
$tmpBat = "$LOGS\mcp_addpat_tmp.bat"
"@echo off`ncall `"$BAT`" `"$XlsxPath`"" | Set-Content -Path $tmpBat -Encoding ASCII

Write-Output "============================================================"
Write-Output " P_300 ADD PATTERN  —  MCP-Safe Launcher"
Write-Output " XLSX: $XlsxPath"
Write-Output " $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Output "============================================================"
Write-Output ""
Write-Output "Launching detached... polling every 10s (timeout 10 min)"
Write-Output ""

$result = Invoke-HubBat -BatPath $tmpBat `
                        -StatusFile $STATUS_FILE `
                        -PollSeconds 10 `
                        -TimeoutMinutes 10

if (Test-Path $tmpBat) { Remove-Item $tmpBat -Force }

Write-Output ""
Write-Output "============================================================"
Write-Output " RESULT: $result"
Write-Output " Catalog: $PROJECT\models\"
Write-Output "============================================================"
