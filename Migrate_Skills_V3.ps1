# Migrate_Skills_V3.ps1
# ----------------------------------------------------------------------
# V3: Fixes the auto-linkification issue that broke V2.
# The skill filename is assembled at runtime from two halves so the literal
# pattern never appears as a standalone string anywhere in this file.
#
# Moves the 3 canonical skill source files from shared_resources\skills\
# to .claude\skills\.
#
# Safety: skips any move where the target already exists.
# Idempotent: safe to run more than once.
#
# HOW TO RUN:
#   1. Open PowerShell
#   2. cd "C:\Users\Trader\AI-Agent-Learning-Hub"
#   3. .\Migrate_Skills_V3.ps1
# ----------------------------------------------------------------------

$ErrorActionPreference = 'Stop'

$HubRoot   = "C:\Users\Trader\AI-Agent-Learning-Hub"
$Source    = Join-Path $HubRoot "shared_resources\skills"
$Target    = Join-Path $HubRoot ".claude\skills"
$SkillFile = "SKILL" + ".md"   # Assembled at runtime to avoid markdown linkification

Write-Host ""
Write-Host "=== Migrating canonical skill files ===" -ForegroundColor Cyan
Write-Host ""

$Migrations = @(
    "p000-chat-session-initializer",
    "p020-project-context",
    "python-project-architecture"
)

foreach ($skill in $Migrations) {
    $srcFile = Join-Path $Source "$skill\$SkillFile"
    $dstFile = Join-Path $Target "$skill\$SkillFile"

    if (-not (Test-Path $srcFile)) {
        Write-Host "NOT FOUND in source: $skill" -ForegroundColor Red
        continue
    }

    if (Test-Path $dstFile) {
        Write-Host "SKIPPED (target already exists): $skill" -ForegroundColor Yellow
        continue
    }

    Move-Item -Path $srcFile -Destination $dstFile
    Write-Host "MOVED: $skill" -ForegroundColor Green
}

# Clean up empty source folders left behind
Write-Host ""
Write-Host "=== Cleaning up empty source folders ===" -ForegroundColor Cyan
Write-Host ""

foreach ($skill in $Migrations) {
    $srcFolder = Join-Path $Source $skill
    if (-not (Test-Path $srcFolder)) { continue }

    $items = Get-ChildItem -Path $srcFolder -Recurse -Force | Measure-Object
    if ($items.Count -eq 0) {
        Remove-Item -Path $srcFolder -Force
        Write-Host "Removed empty folder: $srcFolder" -ForegroundColor Green
    } else {
        Write-Host "Folder not empty, kept: $srcFolder" -ForegroundColor Yellow
    }
}

# Final review list - descriptive only, no literal filename to trip parsing
Write-Host ""
Write-Host "=== Items left in place - review on your own time ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. docs\perplexity-skills\ (6 skill source files)" -ForegroundColor White
Write-Host "   Older imports covering oil bounce, TOS parsing, VantagePoint, etc." -ForegroundColor Gray
Write-Host "   Promote to active skills only if you actually use them." -ForegroundColor Gray
Write-Host ""
Write-Host "2. projects\P_020_AJZStrategies_PerformanceAnalysisSystem\docs\" -ForegroundColor White
Write-Host "   Contains a skill source file - likely a duplicate of p020-project-context." -ForegroundColor Gray
Write-Host ""
Write-Host "3. .claude\skills\system-doc-initializer\ (empty folder)" -ForegroundColor White
Write-Host "   No source file was found in the Hub. Either populate or delete." -ForegroundColor Gray

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
