$PROJECT_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
$BAT = "$PROJECT_ROOT\P_300_DailyEval_v2.bat"
$LIVE_DIR = "$PROJECT_ROOT\data\live"
$LOG = "$PROJECT_ROOT\P_300_DailyEval_Messages.txt"

"Run started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content -Path $LOG -Encoding UTF8

$files = Get-ChildItem -Path $LIVE_DIR -Filter "History Grid (*).xlsx" | Sort-Object Name
$total = $files.Count
$i = 0
$failedSymbols = @()

foreach ($file in $files) {
    $i++
    $symbol = $file.Name -replace "^History Grid \(", "" -replace "\)\.xlsx$", ""
    $header = "[$i / $total] $symbol"
    Write-Host $header -ForegroundColor Cyan
    $header | Add-Content -Path $LOG -Encoding UTF8

    $result = ("`n`n`n" | cmd /c "`"`"$BAT`" $symbol`"") 2>&1
    $symbolExitCode = $LASTEXITCODE
    $result | Add-Content -Path $LOG -Encoding UTF8
    "" | Add-Content -Path $LOG -Encoding UTF8

    # WO-P300-E4.010: P_300_DailyEval_v2.bat previously had no explicit
    # exit /b at the end -- CMD's default exit code on falling off the
    # end of a .bat is 0 regardless of an internal [ERROR] path, so
    # $LASTEXITCODE here was always 0 even on a real daily-evaluate
    # failure. Fixed at the source (the .bat now tracks EXIT_CODE and
    # calls exit /b explicitly) -- this check is only meaningful because
    # of that fix, not despite it.
    if ($symbolExitCode -ne 0) {
        $failedSymbols += $symbol
        Write-Host "  [FAILED] $symbol (exit $symbolExitCode) -- see $LOG for details" -ForegroundColor Red
    }
}

"Run complete: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $LOG -Encoding UTF8
Write-Host ""
$succeededCount = $total - $failedSymbols.Count
if ($failedSymbols.Count -eq 0) {
    Write-Host "All $total evaluations complete. Log: $LOG" -ForegroundColor Green
} else {
    Write-Host "=======================================================================" -ForegroundColor Red
    Write-Host " $succeededCount / $total evaluations complete -- $($failedSymbols.Count) FAILED: $($failedSymbols -join ', ')" -ForegroundColor Red
    Write-Host " See $LOG for the actual error(s). Failed symbols were NOT archived and" -ForegroundColor Red
    Write-Host " produced no signal -- they will not appear in the Chaikin batch below." -ForegroundColor Red
    Write-Host "=======================================================================" -ForegroundColor Red
}

# --- Chaikin Power Gauge batch (schema-driven scanner, WO-P800-E4.001) ---
# Migrated 2026-08-12 from the old per-project log-parsing + inline claude
# call to the shared Hub-root RunChaikinBatch.ps1 -Schema P300. The shared
# scanner reads write_route directly from vault frontmatter (no date-
# guessing off $LOG, no log parsing) and carries P_300's own permanent
# skip list (WO-P300-E5.007) via SCHEMA_SKIP_LISTS in
# chaikin_enrichment\config.py -- extended the same day specifically so
# this migration wouldn't silently reintroduce that bug. The shared
# RunChaikinBatch.ps1 does its own `claude auth status --text` guard
# internally (streams straight to console -- not duplicated here).
$HUB_RUN_CHAIKIN = "C:\Users\Trader\AI-Agent-Learning-Hub\RunChaikinBatch.ps1"
$LAST_PROMPT = "C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\chaikin_enrichment\_last_prompt.txt"
$VAULT_DIR = "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\P300\"

$batchStartTime = Get-Date
& $HUB_RUN_CHAIKIN -Schema P300
$chaikinExitCode = $LASTEXITCODE

# The wrapper's own exit code is ambiguous between "no candidates, clean
# exit" and "candidates existed, claude -p --chrome's own exit code" --
# _last_prompt.txt's mtime is the durable signal instead: the scanner only
# (re)writes it when candidates are actually found this run (same
# discipline as the vault-note LastWriteTime check below).
$promptIsFresh = (Test-Path $LAST_PROMPT) -and
    ((Get-Item $LAST_PROMPT).LastWriteTime -gt $batchStartTime)

if (-not $promptIsFresh) {
    Write-Host "No BUY/WATCH candidates found for P300 today (or all were skip-listed) -- Chaikin batch was a no-op." -ForegroundColor Yellow
    "Chaikin batch: no candidates (schema-driven scan; see console above for any [SKIP] lines)." | Add-Content -Path $LOG -Encoding UTF8
} else {
    # Candidates existed -- parse "SYMBOL -> path" lines from the actual
    # prompt the scanner built, not a re-derivation (M-082: reuse the real
    # artifact instead of guessing what it should have been).
    $actionable = Select-String -Path $LAST_PROMPT -Pattern '^(\S+) -> ' |
        ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -Unique

    if ($chaikinExitCode -ne 0) {
        Write-Host "Chaikin batch wrapper exited $chaikinExitCode -- verifying against real vault notes below, not trusting the exit code alone." -ForegroundColor Yellow
    }

    # WO-P300-E4.009 discipline, unchanged: never trust claude's own prose
    # or a bare exit code -- verify the actual vault file was written with
    # a fresh Chaikin section, after this run started.
    $writtenCount = 0
    $notWritten = @()
    foreach ($sym in $actionable) {
        $noteFile = Get-ChildItem $VAULT_DIR -File -Filter "*_$sym.md" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($noteFile -and $noteFile.LastWriteTime -gt $batchStartTime -and
            (Select-String -Path $noteFile.FullName -Pattern "## Chaikin Power Gauge" -Quiet)) {
            $writtenCount++
        } else {
            $notWritten += $sym
        }
    }
    Write-Host ""
    if ($notWritten.Count -eq 0) {
        $summaryLine = "Chaikin batch complete: $writtenCount / $($actionable.Count) ratings written successfully."
        Write-Host $summaryLine -ForegroundColor Green
        $summaryLine | Add-Content -Path $LOG -Encoding UTF8
    } else {
        $summaryLine = "Chaikin batch: $writtenCount / $($actionable.Count) notes updated. NOT updated (verify above -- may be legitimate no-coverage, or a real miss, including auth failure -- check console output above): $($notWritten -join ', ')"
        Write-Host $summaryLine -ForegroundColor Yellow
        $summaryLine | Add-Content -Path $LOG -Encoding UTF8
    }
}

