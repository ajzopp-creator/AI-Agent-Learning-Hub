# P_300_RunBulkAddPattern.ps1
# "BulkAddPattern" process -- automated equivalent of manual AddPattern,
# applied exhaustively across a symbol's full history instead of one
# live setup at a time. mine-patterns (find candidates) -> ingest-mined
# (audit gate + staging insert + M-079 eval, already built in) -> archive
# every processed file to E:\ (Tony's call, 2026-07-14: mined files
# aren't one-shot like Pipeline A's, but re-exporting from VP if a
# re-mine is ever needed is an accepted tradeoff vs. keeping everything
# on local disk forever).
#
# --promote is deliberately NOT part of this script -- same posture as
# every other catalog-writing WO in this project. Review both
# walk-forward reports (printed by ingest-mined) before promoting
# manually.
#
# Mirrors P_300_AddPattern.bat's dated-catalog-rollover + baseline-
# summary + pause-to-confirm shape, ported to PowerShell.

$PROJECT_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
$PYTHON = "C:\Users\Trader\.conda\envs\p140\python.exe"
$CLI = "$PROJECT_ROOT\python\cli.py"
$MODELS_DIR = "$PROJECT_ROOT\models"
$MINE_DIR = "$PROJECT_ROOT\data\bulk\mine"

Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "        P_300 BULK ADD PATTERN  (mine-patterns -> ingest-mined -> archive)" -ForegroundColor Cyan
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host ""

# --- Dated catalog rollover (mirrors P_300_AddPattern.bat's goto-label logic) ---
$today = Get-Date -Format "MMddyy"
$latest = Get-ChildItem -Path $MODELS_DIR -Filter "*catalog.db" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^\d" } |
    Sort-Object Name -Descending |
    Select-Object -First 1

if (-not $latest) {
    Write-Host "[ERROR] No catalog.db found in $MODELS_DIR" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

$latestDate = $latest.Name.Substring(0, 6)
if ($latestDate -eq $today) {
    Write-Host "[BACKUP] Catalog already current for today -- $($latest.Name)" -ForegroundColor Green
} else {
    $newCatalog = "${today}catalog.db"
    Write-Host "[BACKUP] New catalog day -- copying to $newCatalog" -ForegroundColor Yellow
    Write-Host "         Source: $($latest.FullName)"
    Copy-Item -Path $latest.FullName -Destination "$MODELS_DIR\$newCatalog"
    Write-Host "         Done."
}

# --- Baseline summary + confirm ---
Write-Host ""
Write-Host "[SUMMARY] Catalog baseline for today..."
Write-Host ""
& $PYTHON $CLI catalog-summary --recent 5

Write-Host ""
Write-Host "-----------------------------------------------------------------------"
Write-Host " Catalog state above is your baseline for today."
Write-Host " Press Enter to proceed  --  Ctrl+C to CANCEL."
Write-Host "-----------------------------------------------------------------------"
Read-Host | Out-Null

# --- Step 1: mine-patterns (report-only, scans data/bulk/mine/) ---
Write-Host ""
Write-Host "[STEP 1] Running mine-patterns..." -ForegroundColor Cyan
Write-Host ""
& $PYTHON $CLI mine-patterns
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] mine-patterns failed -- see output above." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

# --- Step 2: ingest-mined (audit gate runs automatically per row; never
# touches the real live catalog.db -- writes to a staging copy only) ---
Write-Host ""
Write-Host "[STEP 2] Running ingest-mined..." -ForegroundColor Cyan
Write-Host ""
& $PYTHON $CLI ingest-mined
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] ingest-mined failed -- see output above. Files NOT archived." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

# --- Step 3: archive every file that was part of this batch ---
Write-Host ""
Write-Host "[STEP 3] Archiving processed files from data\bulk\mine\..." -ForegroundColor Cyan
Write-Host ""
$files = Get-ChildItem -Path $MINE_DIR -Filter "*.xlsx" -ErrorAction SilentlyContinue | Sort-Object Name
$total = $files.Count
$i = 0
$archiveFailures = 0

foreach ($file in $files) {
    $i++
    Write-Host "[$i / $total] $($file.Name)"
    & $PYTHON $CLI archive-mined --xlsx "$($file.FullName)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] archive-mined failed for $($file.Name) -- left in place." -ForegroundColor Red
        $archiveFailures++
    }
}

Write-Host ""
Write-Host "=======================================================================" -ForegroundColor Green
Write-Host " DONE -- $($total - $archiveFailures) / $total files archived."
if ($archiveFailures -gt 0) {
    Write-Host " $archiveFailures file(s) failed to archive -- left in data\bulk\mine\, see errors above." -ForegroundColor Yellow
}
Write-Host " Review both walk-forward reports (printed above by ingest-mined),"
Write-Host " then promote manually when ready:"
Write-Host "   python cli.py ingest-mined --promote <staging_db_path>"
Write-Host "=======================================================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"
