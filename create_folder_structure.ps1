# =============================================================================
# Trading Projects Folder Structure Generator
# =============================================================================
# Run this script from your AI-Agent-Learning-Hub root directory
# Usage: .\create_folder_structure.ps1
# =============================================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Trading Projects Folder Structure Setup  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$rootPath = Get-Location
Write-Host "Creating folders in: $rootPath" -ForegroundColor Yellow
Write-Host ""

# -----------------------------------------------------------------------------
# PROJECT FOLDERS
# -----------------------------------------------------------------------------

Write-Host "Creating PROJECT folders..." -ForegroundColor Green

$projectFolders = @(
    # P_300_Vantage_Point_Pattern_Recognition
    "projects\P_300_Vantage_Point_Pattern_Recognition\python",
    "projects\P_300_Vantage_Point_Pattern_Recognition\tos_scripts",
    "projects\P_300_Vantage_Point_Pattern_Recognition\data\xml_exports",
    "projects\P_300_Vantage_Point_Pattern_Recognition\data\processed",
    "projects\P_300_Vantage_Point_Pattern_Recognition\data\historical",
    "projects\P_300_Vantage_Point_Pattern_Recognition\models\trained",
    "projects\P_300_Vantage_Point_Pattern_Recognition\models\configs",
    "projects\P_300_Vantage_Point_Pattern_Recognition\outputs\reports",
    "projects\P_300_Vantage_Point_Pattern_Recognition\outputs\charts",
    "projects\P_300_Vantage_Point_Pattern_Recognition\outputs\alerts",
    
    # D_130_TradetheBounce_OIL
    "projects\D_130_TradetheBounce_OIL\python",
    "projects\D_130_TradetheBounce_OIL\tos_scripts",
    "projects\D_130_TradetheBounce_OIL\data\xml_exports",
    "projects\D_130_TradetheBounce_OIL\data\price_data",
    "projects\D_130_TradetheBounce_OIL\data\correlations",
    "projects\D_130_TradetheBounce_OIL\strategies\rules",
    "projects\D_130_TradetheBounce_OIL\strategies\backtests",
    "projects\D_130_TradetheBounce_OIL\outputs\trade_logs",
    "projects\D_130_TradetheBounce_OIL\outputs\performance",
    "projects\D_130_TradetheBounce_OIL\outputs\alerts",
    
    # P_010_Market_Posture_Weekly_Forecasts
    "projects\P_010_Market_Posture_Weekly_Forecasts\python",
    "projects\P_010_Market_Posture_Weekly_Forecasts\tos_scripts",
    "projects\P_010_Market_Posture_Weekly_Forecasts\data\xml_exports",
    "projects\P_010_Market_Posture_Weekly_Forecasts\data\weekly_snapshots",
    "projects\P_010_Market_Posture_Weekly_Forecasts\data\economic_calendar",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\2025\Q1",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\2025\Q2",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\2025\Q3",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\2025\Q4",
    "projects\P_010_Market_Posture_Weekly_Forecasts\forecasts\archive",
    "projects\P_010_Market_Posture_Weekly_Forecasts\outputs\reports",
    "projects\P_010_Market_Posture_Weekly_Forecasts\outputs\visualizations",
    "projects\P_010_Market_Posture_Weekly_Forecasts\outputs\email_summaries"
)

foreach ($folder in $projectFolders) {
    $fullPath = Join-Path $rootPath $folder
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  + $folder" -ForegroundColor DarkGreen
    } else {
        Write-Host "  = $folder (exists)" -ForegroundColor DarkGray
    }
}

# -----------------------------------------------------------------------------
# SHARED RESOURCES
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "Creating SHARED RESOURCES folders..." -ForegroundColor Magenta

$sharedFolders = @(
    "shared_resources\tos_scripts\indicators",
    "shared_resources\tos_scripts\scanners",
    "shared_resources\tos_scripts\strategies",
    "shared_resources\tos_scripts\templates",
    "shared_resources\python_utils",
    "shared_resources\data_exports\raw",
    "shared_resources\data_exports\cleaned",
    "shared_resources\data_exports\combined",
    "shared_resources\llm_prompts\analysis",
    "shared_resources\llm_prompts\summarization",
    "shared_resources\llm_prompts\trade_review"
)

foreach ($folder in $sharedFolders) {
    $fullPath = Join-Path $rootPath $folder
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  + $folder" -ForegroundColor DarkMagenta
    } else {
        Write-Host "  = $folder (exists)" -ForegroundColor DarkGray
    }
}

# -----------------------------------------------------------------------------
# INTEGRATIONS
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "Creating INTEGRATIONS folders..." -ForegroundColor Blue

$integrationFolders = @(
    "integrations\lm_studio\models",
    "integrations\lm_studio\prompts",
    "integrations\lm_studio\outputs",
    "integrations\schwab_api\credentials",
    "integrations\schwab_api\wrappers",
    "integrations\automation\schedulers",
    "integrations\automation\workflows",
    "integrations\automation\email_agents",
    "integrations\automation\alerts"
)

foreach ($folder in $integrationFolders) {
    $fullPath = Join-Path $rootPath $folder
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  + $folder" -ForegroundColor DarkBlue
    } else {
        Write-Host "  = $folder (exists)" -ForegroundColor DarkGray
    }
}

# -----------------------------------------------------------------------------
# DOCS
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "Creating DOCS folders..." -ForegroundColor Yellow

$docFolders = @(
    "docs\learning_modules",
    "docs\project_notes"
)

foreach ($folder in $docFolders) {
    $fullPath = Join-Path $rootPath $folder
    if (!(Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "  + $folder" -ForegroundColor DarkYellow
    } else {
        Write-Host "  = $folder (exists)" -ForegroundColor DarkGray
    }
}

# -----------------------------------------------------------------------------
# CREATE .GITIGNORE
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "Creating .gitignore file..." -ForegroundColor White

$gitignoreContent = @"
# =============================================================================
# Trading Projects .gitignore
# =============================================================================

# Sensitive data - NEVER commit these
integrations/schwab_api/credentials/
*.env
**/api_keys.*
**/*secret*
**/*password*

# Data files (too large for git)
**/data/xml_exports/*.xml
**/data/historical/
**/data/price_data/
**/data/weekly_snapshots/
shared_resources/data_exports/raw/
shared_resources/data_exports/combined/

# Outputs (can be regenerated)
**/outputs/
**/forecasts/archive/
integrations/lm_studio/outputs/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
*.egg-info/
dist/
build/

# IDE and editors
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db
Desktop.ini

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
.cache/
"@

$gitignorePath = Join-Path $rootPath ".gitignore"
if (!(Test-Path $gitignorePath)) {
    $gitignoreContent | Out-File -FilePath $gitignorePath -Encoding utf8
    Write-Host "  + .gitignore created" -ForegroundColor DarkGreen
} else {
    Write-Host "  = .gitignore already exists (not modified)" -ForegroundColor DarkGray
}

# -----------------------------------------------------------------------------
# CREATE README FILES
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "Creating README files..." -ForegroundColor White

$readmeProjects = @{
    "projects\P_300_Vantage_Point_Pattern_Recognition\README.md" = @"
# P_300 - Vantage Point Pattern Recognition

## Purpose
Pattern recognition system for identifying trading setups using Vantage Point analysis.

## Key Files
- ``python/v2_posture.py`` - Main analysis script
- ``data/xml_exports/`` - TOS grid exports (SPY, QQQ)

## Workflow
1. Export grid data from TOS → ``data/xml_exports/``
2. Run ``v2_posture.py`` for pattern analysis
3. Review outputs in ``outputs/reports/``

## Status
🟡 In Development
"@

    "projects\D_130_TradetheBounce_OIL\README.md" = @"
# D_130 - Trade the Bounce (OIL)

## Purpose
Bounce trading strategy focused on oil instruments.

## Key Files
- ``python/bounce_detector.py`` - Bounce identification logic
- ``strategies/rules/`` - Entry/exit criteria

## Workflow
1. Monitor oil levels via TOS scripts
2. Run bounce detection analysis
3. Log trades in ``outputs/trade_logs/``

## Status
🟡 In Development
"@

    "projects\P_010_Market_Posture_Weekly_Forecasts\README.md" = @"
# P_010 - Market Posture Weekly Forecasts

## Purpose
Weekly market analysis and forecasting system for 2025.

## Key Files
- ``python/weekly_posture.py`` - Forecast generator
- ``forecasts/2025/`` - Organized by quarter

## Workflow
1. Gather weekly data → ``data/weekly_snapshots/``
2. Run forecast analysis
3. Generate reports → ``outputs/reports/``

## Status
🟡 In Development
"@
}

foreach ($readme in $readmeProjects.GetEnumerator()) {
    $readmePath = Join-Path $rootPath $readme.Key
    if (!(Test-Path $readmePath)) {
        $readme.Value | Out-File -FilePath $readmePath -Encoding utf8
        Write-Host "  + $($readme.Key)" -ForegroundColor DarkGreen
    } else {
        Write-Host "  = $($readme.Key) (exists)" -ForegroundColor DarkGray
    }
}

# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!                          " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Folder structure created at:" -ForegroundColor White
Write-Host "  $rootPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Move v2_posture.py to projects\P_300_...\python\" -ForegroundColor Gray
Write-Host "  2. Move XML files to projects\P_300_...\data\xml_exports\" -ForegroundColor Gray
Write-Host "  3. Initialize git: git init" -ForegroundColor Gray
Write-Host "  4. Create virtual environment in each project" -ForegroundColor Gray
Write-Host ""