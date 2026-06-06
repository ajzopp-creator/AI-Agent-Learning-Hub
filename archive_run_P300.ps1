# =============================================================================
# run_P300.ps1 - Quick launcher for P_300 Posture System
# =============================================================================
# Usage: .\run_P300.ps1 [mode]
# Modes: live, backtest, test
# Example: .\run_P300.ps1 live
# =============================================================================

param(
    [string]$Mode = "live"
)

$p300Path = Join-Path $PSScriptRoot "projects\P_300_Vantage_Point_Pattern_Recognition\python"

if (Test-Path $p300Path) {
    Push-Location $p300Path
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  P_300 Posture System - $Mode mode" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Directory: $p300Path" -ForegroundColor Gray
    Write-Host ""
    
    python P_300_Posture_V2.py $Mode
    
    Pop-Location
} else {
    Write-Host "Error: P_300 folder not found" -ForegroundColor Red
    Write-Host "Expected: $p300Path" -ForegroundColor Red
}
