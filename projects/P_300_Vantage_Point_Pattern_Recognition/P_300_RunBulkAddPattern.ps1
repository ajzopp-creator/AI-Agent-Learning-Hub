# P_300_RunBulkAddPattern.ps1
# VERSION: 2.0  --  2026-07-28  (WO-P300-E5.005)
#
# "BulkAddPattern" process -- automated equivalent of manual AddPattern,
# applied exhaustively across a symbol's full history instead of one
# live setup at a time. mine-patterns (find candidates) -> ingest-mined
# (audit gate + staging insert + M-079 eval) -> promote-gate (quality
# check) -> promote (if clean) -> archive processed files to E:\.
#
# WHAT CHANGED IN v2.0 -- three fixes, all from real failures:
#
#  1. AUTO-PROMOTE ON A CLEAN GATE. v1.x deliberately left --promote
#     manual. That posture assumed the operator would come back and do
#     it. On 2026-07-25 a batch staged at 16:15, was never promoted,
#     and was silently destroyed three days later when the next run's
#     staging rebuild (shutil.copy2 from live) overwrote it. Nobody
#     noticed until 2026-07-28. A staged batch that nobody promotes is
#     not "safely pending" -- it is scheduled for deletion.
#
#  2. TRANSCRIPT LOG. v1.x was console-only Write-Host. When Tony
#     reported "no output" from a run that had actually succeeded,
#     there was nothing to check after the window closed.
#
#  3. ROLLOVER COPY MOVED AFTER THE CONFIRM PROMPT. v1.x copied the
#     catalog to a new dated filename BEFORE the baseline summary and
#     the Ctrl+C confirm. Cancelling at that prompt -- or any later
#     failure -- still left a dated copy on disk containing nothing
#     new. That produced 072526catalog.db and 072826catalog.db, both
#     byte-identical to 072326catalog.db (same MD5, same 7/23 mtime,
#     because Copy-Item preserves LastWriteTime). Since the selector
#     sorts by Name descending, each empty copy then became the source
#     for the next one.
#
# NOTE: get_latest_catalog() (db_utils.py) sorts by NAME descending,
# and so does the rollover below. They agree -- do not "fix" either to
# sort by mtime without changing both.

$PROJECT_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
$PYTHON = "C:\Users\Trader\.conda\envs\p140\python.exe"
$CLI = "$PROJECT_ROOT\python\cli.py"
$MODELS_DIR = "$PROJECT_ROOT\models"
$MINE_DIR = "$PROJECT_ROOT\data\bulk\mine"
$STAGING_DB = "$MODELS_DIR\staging_ingest_mined.db"
$LOG_DIR = "$PROJECT_ROOT\logs"

if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR | Out-Null }
$LOG = "$LOG_DIR\BulkAddPattern_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Start-Transcript -Path $LOG -ErrorAction SilentlyContinue | Out-Null
$scriptStart = Get-Date

Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host "        P_300 BULK ADD PATTERN  (mine -> ingest -> gate -> promote)" -ForegroundColor Cyan
Write-Host "=======================================================================" -ForegroundColor Cyan
Write-Host " Log: $LOG"
Write-Host ""

# --- Locate the current catalog (NAME descending -- matches db_utils) ---
$latest = Get-ChildItem -Path $MODELS_DIR -Filter "*catalog.db" -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^\d" } |
    Sort-Object Name -Descending |
    Select-Object -First 1

if (-not $latest) {
    Write-Host "[ERROR] No catalog.db found in $MODELS_DIR" -ForegroundColor Red
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    Read-Host "Press Enter to close"
    exit 1
}

# --- Baseline summary + confirm (BEFORE any file is created) ---
Write-Host "[SUMMARY] Catalog baseline for today -- $($latest.Name)"
Write-Host ""
& $PYTHON $CLI catalog-summary --recent 5 2>&1 | Out-String -Stream

Write-Host ""
Write-Host "-----------------------------------------------------------------------"
Write-Host " Catalog state above is your baseline for today."
Write-Host " Press Enter to proceed  --  Ctrl+C to CANCEL."
Write-Host "-----------------------------------------------------------------------"
Read-Host | Out-Null

# --- Dated catalog rollover (AFTER the confirm -- see header note 3) ---
$today = Get-Date -Format "MMddyy"
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

# --- Step 1: mine-patterns (report-only, scans data/bulk/mine/) ---
Write-Host ""
Write-Host "[STEP 1] Running mine-patterns..." -ForegroundColor Cyan
Write-Host ""
$step1Start = Get-Date
& $PYTHON $CLI mine-patterns 2>&1 | Out-String -Stream
$step1Duration = (Get-Date) - $step1Start
Write-Host " [STEP 1] duration: $('{0:hh\:mm\:ss}' -f $step1Duration)"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] mine-patterns failed -- see output above." -ForegroundColor Red
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    Read-Host "Press Enter to close"
    exit 1
}

# --- Step 2: ingest-mined (audit gate per row; writes a staging copy only) ---
Write-Host ""
Write-Host "[STEP 2] Running ingest-mined..." -ForegroundColor Cyan
Write-Host ""
$step2Start = Get-Date
& $PYTHON $CLI ingest-mined 2>&1 | Out-String -Stream
$step2Duration = (Get-Date) - $step2Start
Write-Host " [STEP 2] duration: $('{0:hh\:mm\:ss}' -f $step2Duration)"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] ingest-mined failed -- see output above. Files NOT archived." -ForegroundColor Red
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    Read-Host "Press Enter to close"
    exit 1
}

# --- Step 3: promote-gate (decides only; never writes a catalog) ---
Write-Host ""
Write-Host "[STEP 3] Running promote-gate..." -ForegroundColor Cyan
Write-Host ""
$step3Start = Get-Date
& $PYTHON $CLI promote-gate --staging-db "$STAGING_DB" 2>&1 | Out-String -Stream
$gateResult = $LASTEXITCODE
$step3Duration = (Get-Date) - $step3Start
Write-Host " [STEP 3] duration: $('{0:hh\:mm\:ss}' -f $step3Duration)"

$promoted = $false
if ($gateResult -eq 0) {
    # --- Step 4: auto-promote (gate clean) ---
    Write-Host ""
    Write-Host "[STEP 4] Gate PASSED -- promoting staging to live..." -ForegroundColor Green
    Write-Host "         This can take over an hour on a large batch (topk_cache)."
    Write-Host ""
    $step4Start = Get-Date
    & $PYTHON $CLI ingest-mined --promote "$STAGING_DB" 2>&1 | Out-String -Stream
    $step4Duration = (Get-Date) - $step4Start
    Write-Host "         [STEP 4] duration: $('{0:hh\:mm\:ss}' -f $step4Duration)"
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Promote FAILED -- staging left in place, files NOT archived." -ForegroundColor Red
        Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
        Read-Host "Press Enter to close"
        exit 1
    }
    $promoted = $true
} elseif ($gateResult -eq 2) {
    Write-Host ""
    Write-Host "[STOP] Gate BLOCKED this batch -- NOT promoted." -ForegroundColor Yellow
    Write-Host "       Staging DB left in place: $STAGING_DB"
    Write-Host "       A marker was written; INIT will surface it next session."
    Write-Host "       WARNING: the next ingest-mined run REBUILDS staging from"
    Write-Host "       live and will destroy this batch. Decide before then."
} else {
    Write-Host ""
    Write-Host "[ERROR] promote-gate could not evaluate (exit $gateResult)." -ForegroundColor Red
    Write-Host "        This is NOT a quality failure -- the batch was never"
    Write-Host "        assessed. Staging left in place, files NOT archived."
    Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
    Read-Host "Press Enter to close"
    exit 1
}

# --- Step 5: archive processed files (ONLY after a successful promote) ---
$total = 0
$archiveFailures = 0
if ($promoted) {
    Write-Host ""
    Write-Host "[STEP 5] Archiving processed files from data\bulk\mine\..." -ForegroundColor Cyan
    Write-Host ""
    $files = Get-ChildItem -Path $MINE_DIR -Filter "*.xlsx" -ErrorAction SilentlyContinue | Sort-Object Name
    $total = $files.Count
    $i = 0
    $step5Start = Get-Date
    foreach ($file in $files) {
        $i++
        Write-Host "[$i / $total] $($file.Name)"
        & $PYTHON $CLI archive-mined --xlsx "$($file.FullName)" 2>&1 | Out-String -Stream
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [ERROR] archive-mined failed for $($file.Name) -- left in place." -ForegroundColor Red
            $archiveFailures++
        }
    }
    $step5Duration = (Get-Date) - $step5Start
    Write-Host " [STEP 5] duration: $('{0:hh\:mm\:ss}' -f $step5Duration)"
} else {
    Write-Host ""
    Write-Host "[STEP 5] SKIPPED -- batch was not promoted, so source files stay" -ForegroundColor Yellow
    Write-Host "         in data\bulk\mine\ and can be re-run without unzipping."
}

# --- Summary ---
Write-Host ""
Write-Host "=======================================================================" -ForegroundColor Green
if ($promoted) {
    Write-Host " DONE -- batch PROMOTED to live."
    Write-Host " Archived $($total - $archiveFailures) / $total files."
    if ($archiveFailures -gt 0) {
        Write-Host " $archiveFailures file(s) failed to archive -- left in data\bulk\mine\." -ForegroundColor Yellow
    }
    Write-Host " Re-run P_300_Preflight.bat so INIT reads current catalog counts."
} else {
    Write-Host " DONE -- batch STAGED BUT NOT PROMOTED (gate blocked it)."
    Write-Host " Review the gate output above, then either:"
    Write-Host "   promote anyway:  $PYTHON $CLI ingest-mined --promote `"$STAGING_DB`""
    Write-Host "   or discard:      delete $STAGING_DB"
}
$totalDuration = (Get-Date) - $scriptStart
Write-Host " Total runtime: $('{0:hh\:mm\:ss}' -f $totalDuration)"
Write-Host " Log: $LOG"
Write-Host "=======================================================================" -ForegroundColor Green
Write-Host ""
Stop-Transcript -ErrorAction SilentlyContinue | Out-Null
Read-Host "Press Enter to close"
