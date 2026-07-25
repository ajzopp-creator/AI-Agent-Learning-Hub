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

# --- Chaikin Power Gauge batch (Claude Code /chrome) ---
# NOTE: vault notes are filed under anchor_date (last market close), not the
# eval run date -- a same-day filename match against $today will almost
# always miss. Pull BUY/WATCH tickers directly from this run's own log instead.
$PROMPT_TEMPLATE = "$PROJECT_ROOT\python\utilities\chaikin_batch_prompt.txt"
$today = Get-Date -Format "yyyy-MM-dd"

$actionable = Select-String -Path $LOG -Pattern "SIGNAL REPORT\s+(\S+)\s+(BUY|WATCH)" |
    ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -Unique

if ($actionable.Count -eq 0) {
    Write-Host "No BUY/WATCH symbols today -- skipping Chaikin batch." -ForegroundColor Yellow
} else {
    $symbolList = $actionable -join ", "
    $prompt = (Get-Content $PROMPT_TEMPLATE -Raw) -replace "\{DATE\}", $today -replace "\{SYMBOLS\}", $symbolList

    # M-097 guard: claude -p shares interactive auth/session state (same
    # credential store), but nothing here previously verified it before
    # calling out -- a missing/expired login printed one easy-to-miss line
    # and silently produced nothing. Check first, fail loud.
    $authCheck = claude auth status --text 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Chaikin batch SKIPPED -- Claude Code not authenticated. Run 'claude /login' then re-run this script." -ForegroundColor Red
    } else {
        Write-Host "Running Chaikin Power Gauge batch for: $symbolList" -ForegroundColor Cyan

        # WO-P300-E4.009: claude -p --chrome can exit 0 with a normal-
        # looking response while the underlying Chaikin task did NOT
        # actually happen -- a login wall or a disconnected Chrome
        # extension both produce coherent prose describing the failure,
        # not a script-detectable error code (confirmed 2026-07-21: a
        # real login-wall failure printed and scrolled past unremarked).
        # Tee-Object preserves live console output while also capturing
        # it for inspection below. Best-effort text match on Claude's own
        # phrasing -- not guaranteed exhaustive, since it's prose, not a
        # fixed error code -- so treat a MISS here as "not flagged", not
        # as proof the batch actually worked. Read the response either way.
        $chaikinLines = claude -p $prompt --chrome 2>&1 | Tee-Object -Variable chaikinLinesRaw
        $chaikinText = ($chaikinLinesRaw -join "`n")
        $failureIndicators = @(
            "login page", "not logging in", "sign in to Chaikin",
            "log in to Chaikin", "extension.{0,20}not connected",
            "chrome extension.{0,20}not", "could not connect",
            "unable to connect", "not authenticated"
        )
        $chaikinFailed = $false
        foreach ($pattern in $failureIndicators) {
            if ($chaikinText -match $pattern) { $chaikinFailed = $true; break }
        }
        if ($chaikinFailed) {
            Write-Host ""
            Write-Host "=======================================================================" -ForegroundColor Red
            Write-Host " CHAIKIN BATCH LIKELY DID NOT COMPLETE -- see response above." -ForegroundColor Red
            Write-Host " Probable cause: Chaikin login wall or Chrome extension not connected." -ForegroundColor Red
            Write-Host " No Power Gauge data was likely written for: $symbolList" -ForegroundColor Red
            Write-Host " Fix the underlying issue, then re-run the Chaikin step for these" -ForegroundColor Red
            Write-Host " symbols -- this detection is best-effort text matching, not" -ForegroundColor Red
            Write-Host " guaranteed, so verify by checking the actual vault notes too." -ForegroundColor Red
            Write-Host "=======================================================================" -ForegroundColor Red
            "CHAIKIN BATCH LIKELY FAILED (login wall / extension not connected) for: $symbolList" | Add-Content -Path $LOG -Encoding UTF8
        }
    }
}
