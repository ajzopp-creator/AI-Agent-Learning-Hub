# Init_Claude_Skills.ps1
# ----------------------------------------------------------------------
# Creates the .claude\skills\ folder structure for the AI-Agent-Learning-Hub
# and reports any existing SKILL.md files so they can be moved into place.
#
# HOW TO RUN:
#   1. Open PowerShell
#   2. cd "C:\Users\Trader\AI-Agent-Learning-Hub"
#   3. .\Init_Claude_Skills.ps1
# ----------------------------------------------------------------------

$ErrorActionPreference = 'Stop'

$HubRoot    = "C:\Users\Trader\AI-Agent-Learning-Hub"
$SkillsRoot = Join-Path $HubRoot ".claude\skills"

Write-Host ""
Write-Host "=== Claude Skills Folder Initializer ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create the skills root folder
if (-not (Test-Path $SkillsRoot)) {
    New-Item -ItemType Directory -Path $SkillsRoot -Force | Out-Null
    Write-Host "Created: $SkillsRoot" -ForegroundColor Green
} else {
    Write-Host "Already exists: $SkillsRoot" -ForegroundColor Yellow
}

# Step 2: Create a subfolder for each known skill
$KnownSkills = @(
    "p000-chat-session-initializer",
    "system-doc-initializer",
    "python-project-architecture",
    "p020-project-context"
)

foreach ($skill in $KnownSkills) {
    $skillPath = Join-Path $SkillsRoot $skill
    if (-not (Test-Path $skillPath)) {
        New-Item -ItemType Directory -Path $skillPath -Force | Out-Null
        Write-Host "Created: $skillPath" -ForegroundColor Green
    } else {
        Write-Host "Already exists: $skillPath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Existing SKILL.md Files Found in the Hub ===" -ForegroundColor Cyan
Write-Host ""

# Step 3: Find all existing SKILL.md files OUTSIDE the new .claude folder
$existing = Get-ChildItem -Path $HubRoot -Filter "SKILL.md" -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "*\.claude\*" }

if ($existing) {
    foreach ($file in $existing) {
        Write-Host "  Found: $($file.FullName)" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "NEXT STEP: Move each SKILL.md above into the matching folder under:" -ForegroundColor Yellow
    Write-Host "  $SkillsRoot" -ForegroundColor Yellow
    Write-Host "Use File Explorer or Move-Item." -ForegroundColor Yellow
} else {
    Write-Host "  No existing SKILL.md files found in Hub folders." -ForegroundColor Yellow
    Write-Host "  Paste each skill's content into the matching subfolder when ready." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
