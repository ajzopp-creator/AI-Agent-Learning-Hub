$PROJECT_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
$LOG = "$PROJECT_ROOT\P_300_DailyEval_Messages.txt"
$PROMPT_TEMPLATE = "$PROJECT_ROOT\python\utilities\chaikin_batch_prompt.txt"
$today = Get-Date -Format "yyyy-MM-dd"

# Standalone re-run of the Chaikin Power Gauge step against an existing
# DailyEval log -- for when the batch already ran and archived its XLSX
# files, so a full DailyEval re-run isn't possible/needed. Reads the same
# log DailyEval just wrote; does not touch the catalog, vault, or live/.

$actionable = Select-String -Path $LOG -Pattern "SIGNAL REPORT\s+(\S+)\s+(BUY|WATCH)" |
    ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -Unique

if ($actionable.Count -eq 0) {
    Write-Host "No BUY/WATCH symbols found in $LOG -- nothing to run." -ForegroundColor Yellow
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
        claude -p $prompt --chrome
    }
}
