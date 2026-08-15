$PROJECT_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
$LOG = "$PROJECT_ROOT\P_300_DailyEval_Messages.txt"
$PROMPT_TEMPLATE = "$PROJECT_ROOT\python\utilities\chaikin_batch_prompt.txt"
$SKIP_LIST_CSV = "$PROJECT_ROOT\data\reference\chaikin_skip_list.csv"
$VAULT_DIR = "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\P300\"
$today = Get-Date -Format "yyyy-MM-dd"

# Standalone re-run of the Chaikin Power Gauge step against an existing
# DailyEval log -- for when the batch already ran and archived its XLSX
# files, so a full DailyEval re-run isn't possible/needed. Reads the same
# log DailyEval just wrote; does not touch the catalog, vault, or live/.

$actionable = Select-String -Path $LOG -Pattern "SIGNAL REPORT\s+(\S+)\s+(BUY|WATCH)" |
    ForEach-Object { $_.Matches[0].Groups[1].Value } | Select-Object -Unique

# WO-P300-E5.007: filter symbols Chaikin structurally cannot rate (ETFs,
# OTC mirrors of a non-US primary listing) before spending browser time
# on them. Skip list is hand-maintained, enumeration-only -- see the WO
# for why Class 2 (OTC mirrors) has no programmatic tell.
$skipMap = @{}
if (Test-Path $SKIP_LIST_CSV) {
    Import-Csv $SKIP_LIST_CSV | ForEach-Object { $skipMap[$_.symbol] = $_.reason }
} else {
    Write-Host "WARNING: chaikin_skip_list.csv not found at $SKIP_LIST_CSV -- running without filter." -ForegroundColor Yellow
}
$skipped = $actionable | Where-Object { $skipMap.ContainsKey($_) }
$actionable = $actionable | Where-Object { -not $skipMap.ContainsKey($_) }
foreach ($sym in $skipped) {
    Write-Host "[SKIP] $sym -- $($skipMap[$sym]) (permanent skip list, WO-P300-E5.007)" -ForegroundColor DarkYellow
}

if ($actionable.Count -eq 0) {
    if ($skipped.Count -gt 0) {
        Write-Host "All BUY/WATCH symbols in $LOG are on the Chaikin skip list -- nothing to run." -ForegroundColor Yellow
    } else {
        Write-Host "No BUY/WATCH symbols found in $LOG -- nothing to run." -ForegroundColor Yellow
    }
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

        # WO-P300-E4.009 (2026-08-10): this standalone script previously
        # ran `claude -p $prompt --chrome` with no capture and no failure
        # detection at all -- brought in line with the inline chain in
        # P_300_RunAllDailyEvals.ps1 (same date, same fix). Tee-Object
        # preserves live console output while also capturing it below.
        # Phrase list widened to "n.?t" so contractions ("isn't", "can't")
        # match, not just literal "not" -- a real 2026-08-10 failure used
        # "isn't connected" and slipped past the original literal-"not"
        # patterns. Empty-output check catches the other real 2026-08-10
        # failure mode: the call returning nothing at all, which no
        # phrase list can detect.
        #
        # WO-P300-E4.009 follow-up (2026-08-10): $prompt was passed as a
        # positional CLI argument (`claude -p $prompt --chrome`) --the
        # template contains embedded double-quotes (e.g. `"Oops! Something
        # went wrong"`), and Windows' CreateProcess argument parser can
        # treat an embedded `"` as closing the quoted argument early,
        # silently truncating everything after it. Confirmed live: a real
        # run truncated mid-sentence at exactly that quote. Piping via
        # stdin instead avoids CLI argument parsing entirely -- `-p` reads
        # from stdin when no positional prompt is given (confirmed via
        # `claude --help`: "-p, --print -- Print response and exit
        # (useful for pipes)").
        $batchStartTime = Get-Date
        $chaikinLines = $prompt | claude -p --chrome 2>&1 | Tee-Object -Variable chaikinLinesRaw
        $chaikinText = ($chaikinLinesRaw -join "`n")

        $failureIndicators = @(
            "login page", "not logging in", "sign in to Chaikin",
            "log in to Chaikin", "extension.{0,20}n.?t connected",
            "chrome extension.{0,20}n.?t", "could not connect",
            "unable to connect", "not authenticated", "n.?t connected",
            "can.?t automate the browser"
        )
        $chaikinFailed = $false
        if ([string]::IsNullOrWhiteSpace($chaikinText)) {
            $chaikinFailed = $true
            $chaikinText = "(no output at all -- claude -p --chrome returned nothing)"
        } else {
            foreach ($pattern in $failureIndicators) {
                if ($chaikinText -match $pattern) { $chaikinFailed = $true; break }
            }
        }
        if ($chaikinFailed) {
            Write-Host ""
            Write-Host "=======================================================================" -ForegroundColor Red
            Write-Host " CHAIKIN BATCH LIKELY DID NOT COMPLETE -- see response above." -ForegroundColor Red
            Write-Host " Probable cause: Chaikin login wall or Chrome extension not connected." -ForegroundColor Red
            Write-Host " No Power Gauge data was likely written for: $symbolList" -ForegroundColor Red
            Write-Host " Fix the underlying issue, then re-run this script -- this detection" -ForegroundColor Red
            Write-Host " is best-effort text matching, not guaranteed, so verify by checking" -ForegroundColor Red
            Write-Host " the actual vault notes too." -ForegroundColor Red
            Write-Host "=======================================================================" -ForegroundColor Red
        }

        # WO-P300-E4.009 follow-up (2026-08-10): success previously printed
        # NOTHING beyond the "Running..." line -- indistinguishable at a
        # glance from the exact silent failure this WO exists to catch.
        # Don't trust Claude's own prose summary for the count (format
        # varies run to run, confirmed this session) -- verify directly
        # against the vault notes instead. A symbol can legitimately have
        # NO Chaikin coverage (ETF/unrated) per the prompt's own
        # instructions, so "no fresh section" isn't automatically a
        # failure -- report both counts and let Tony judge the gap using
        # the response text above, don't guess on his behalf.
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
            $summaryLine = "Chaikin batch: $writtenCount / $($actionable.Count) notes updated. NOT updated (verify above -- may be legitimate no-coverage, or a real miss): $($notWritten -join ', ')"
            Write-Host $summaryLine -ForegroundColor Yellow
            $summaryLine | Add-Content -Path $LOG -Encoding UTF8
        }
    }
}
