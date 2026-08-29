param(
    [Parameter(Mandatory=$true)]
    [string]$Schema
)

# Schema-driven Chaikin Power Gauge batch enrichment. Replaces P_300's
# project-local P_300_RunChaikinBatch.ps1 (WO-P800-E4.001, retired to
# archive 2026-08-21 -- E:\AI-Agent-Learning-Hub_BackupFiles\P_300\
# P_300_ArchiveFiles.zip). The Python scanner reads write_route from
# vault frontmatter directly -- no log parsing, no date-guessing in the
# prompt. Enabled-schema validation lives in
# shared_resources\chaikin_enrichment\config.py (SCHEMAS_ENABLED), not
# duplicated here.
#
# WO-P300-E4.009 (2026-08-21): loud failure detection (Tee-Object capture,
# failure-phrase match, red banner, dedicated failure log) restored here.
# The 2026-08-12 migration to this shared script dropped it -- only the
# separate vault-note completion-count check in each project's own
# DailyEval wrapper survived, which caught the SYMPTOM (0/N updated) but
# never named a likely CAUSE or wrote one durably to disk. Real gap: the
# 2026-08-21 P_300 failure's actual explanation (WebFetch/403 fallback)
# only existed in Tony's terminal scrollback until he pasted it back.
#
# Also restores the stdin-piping fix (WO-P300-E4.009, 2026-08-10): the
# prompt template contains embedded double-quotes; passing it as a
# positional CLI argument risks Windows' CreateProcess parser treating an
# embedded quote as closing the argument early, silently truncating the
# prompt. This migration had regressed back to positional-argument
# passing -- fixed here too.

$HUB_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PYTHON = "C:\Users\Trader\.conda\envs\p140\python.exe"
$RUN_SCRIPT = "$HUB_ROOT\shared_resources\chaikin_enrichment\application\run_chaikin_batch.py"
$PROMPT_FILE = "$HUB_ROOT\shared_resources\chaikin_enrichment\_last_prompt.txt"
$FAILURE_LOG = "$HUB_ROOT\shared_resources\chaikin_enrichment\chaikin_failures.log"

& $PYTHON $RUN_SCRIPT --schema $Schema
$scanExitCode = $LASTEXITCODE

if ($scanExitCode -eq 0) {
    exit 0
}

if (-not (Test-Path $PROMPT_FILE)) {
    Write-Host "Scanner reported candidates but $PROMPT_FILE is missing -- aborting." -ForegroundColor Red
    exit 1
}

$prompt = Get-Content $PROMPT_FILE -Raw

# M-097 guard: claude -p shares interactive auth/session state (same
# credential store), but nothing here previously verified it before
# calling out -- a missing/expired login printed one easy-to-miss line
# and silently produced nothing. Check first, fail loud.
$authCheck = claude auth status --text 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Chaikin batch SKIPPED -- Claude Code not authenticated. Run 'claude /login' then re-run this script." -ForegroundColor Red
    exit 1
}

Write-Host "Running Chaikin Power Gauge batch for schema $Schema" -ForegroundColor Cyan

# M-019/EC-069-class bug found 2026-08-21: active console code page (437,
# OEM US) mis-decodes claude's UTF-8 stdout -- em dashes etc. came through
# as "ΓÇö" in the failure log. chcp 65001 switches the console to UTF-8
# before the call so captured text (especially the failure log, where
# accuracy of the actual response matters) isn't corrupted.
chcp 65001 | Out-Null

$chaikinLines = $prompt | claude -p --chrome 2>&1 | Tee-Object -Variable chaikinLinesRaw
$chaikinText = ($chaikinLinesRaw -join "`n")

# Phrase list carried forward from P_300_RunChaikinBatch.ps1 (archived
# 2026-08-21), contraction-aware ("n.?t" matches "isn't"/"can't"), plus
# four new entries for the 2026-08-21 WebFetch/403 fallback shape --
# claude attempting WebFetch instead of the --chrome browser tool and
# hitting Chaikin's auth wall directly, a third failure mode distinct
# from login-wall and disconnected-extension.
$failureIndicators = @(
    "login page", "not logging in", "sign in to Chaikin",
    "log in to Chaikin", "extension.{0,20}n.?t connected",
    "chrome extension.{0,20}n.?t", "could not connect",
    "unable to connect", "not authenticated", "n.?t connected",
    "can.?t automate the browser",
    "WebFetch", "403 Forbidden", "no login session",
    "don.?t have a browser automation tool", "auth-walled"
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
    Write-Host " Schema: $Schema" -ForegroundColor Red
    Write-Host " Probable cause: Chaikin login wall, Chrome extension not connected," -ForegroundColor Red
    Write-Host " or a WebFetch/auth-wall fallback instead of the browser tool." -ForegroundColor Red
    Write-Host " Fix the underlying issue, then re-run this script -- this detection" -ForegroundColor Red
    Write-Host " is best-effort text matching, not guaranteed, so verify by checking" -ForegroundColor Red
    Write-Host " the actual vault notes too." -ForegroundColor Red
    Write-Host "=======================================================================" -ForegroundColor Red

    $logEntry = @"
---
$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") | schema=$Schema | CHAIKIN BATCH FAILURE
$chaikinText
---
"@
    Add-Content -Path $FAILURE_LOG -Value $logEntry -Encoding UTF8
    exit 1
}

exit 0