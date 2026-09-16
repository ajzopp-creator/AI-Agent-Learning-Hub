# launch_independent_review.ps1
# Location: Agentic-Hub-Governance\utils\launch_independent_review.ps1
# Purpose:  Launch a headless, background Claude Code session to perform
#           Independent Review on any WO, in any project -- reusable,
#           not P_020-specific. Detached (--bg): returns a session id
#           immediately, does not block the calling session.
#
# Usage:
#   .\launch_independent_review.ps1 -WOId "WO-P020-E1.018"
#   .\launch_independent_review.ps1 -WOId "WO-P400-E7.002" -MaxBudget 5.00 -MaxTurns 60
#
# Check on it later:
#   claude logs <session-id>
#   Or just re-open the WO file -- Status line says CLOSED or still
#   OWNER_DONE with a BLOCKED ON: line.
#
# Mechanics note (found 2026-09-15): passing a multi-line prompt via
# -ArgumentList to Start-Process is unreliable (embedded newlines break
# Windows command-line argument parsing -- the child process falls back
# to stdin and finds nothing). This script pipes the prompt via stdin
# instead, which is reliable regardless of length.
#
# Created: 2026-09-15, ref WO-P020-E1.018 Independent Review session.

param(
    [Parameter(Mandatory=$true)][string]$WOId,
    [double]$MaxBudget = 3.00,
    [int]$MaxTurns = 40,
    [string]$HubRoot = "C:\Users\Trader\AI-Agent-Learning-Hub"
)

$ErrorActionPreference = "Stop"

$woPath = Join-Path $HubRoot "Agentic-Hub-Governance\work_orders\$WOId.md"
if (-not (Test-Path $woPath)) {
    Write-Output "ERROR: WO file not found: $woPath"
    exit 1
}

# Resolve project folder from the WO ID's number (e.g. WO-P020-E1.018 -> 020)
# -- scans disk rather than hardcoding names, since folder naming has
# drifted before (P_020_AJZStrategiesPerformanceAnalysisSystem vs
# P_020_AJZStrategies_PerformanceAnalysisSystem -- see p020-project-context
# skill). Same resolution approach as P_000_StartUp_ClaudeDesktop.ps1.
if ($WOId -notmatch '^WO-P(\d+)-') {
    Write-Output "ERROR: WOId doesn't match expected WO-P<number>-... pattern: $WOId"
    exit 1
}
$projNum = $Matches[1]

$projectDir = $null
Get-ChildItem -Path (Join-Path $HubRoot "projects") -Directory | ForEach-Object {
    if ($_.Name -match "^P_$projNum`_") {
        $projectDir = $_.FullName
    }
}
if (-not $projectDir) {
    Write-Output "ERROR: no project folder found under projects\ matching P_$projNum`_*"
    exit 1
}

$ts = (Get-Date).ToString("yyyyMMdd_HHmmss")
$logDir = Join-Path $HubRoot "Agentic-Hub-Governance\verify\review_${WOId}_$ts"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$promptFile = Join-Path $logDir "prompt.txt"

$promptText = @"
Perform an Independent Review of $WOId at:
$woPath

You are a SEPARATE session from whichever session implemented this WO,
per WO_COMPLETION_GATE.md's Independent Review Requirement (same folder
as the WO -- read it first for what Independent Review is and is not).

Project root: $projectDir

Steps:
1. Read the WO file in full -- WHY, scope/fix section, Acceptance
   Criteria, Files Built/Changed if present, Completion Gate, Occurrence
   Log.
2. Re-verify EVERY Acceptance Criteria item against live code, live
   tests, and live data -- never trust the WO's own prose as evidence.
   Where the WO names specific files, tests, or commands, run/read them
   yourself and quote actual output.
3. Re-run this project's regression test suite live (find its test
   folder(s) -- commonly tests\ and/or python\*\tests\ -- and its
   conda/python interpreter, commonly
   C:\Users\Trader\.conda\envs\p140\python.exe) and confirm the actual
   pass/fail count. Do not trust a pass count stated in the WO -- verify
   it yourself.
4. If the WO lists specific files it built or changed, compile-check
   each one under p140 with:
     python -W error::SyntaxWarning -m py_compile <file>
   and check each file's line count against this Hub's 300-line-per-file
   hard cap (flag anything at or over 300).
5. If the WO describes a live smoke test or a specific command to run,
   run it yourself and confirm the behavior matches what's claimed.
6. Check for any project-specific INIT/context skill for this project
   (search .claude\skills\ or ask if unsure) and follow any project-
   specific rules it names for this kind of review.

Verdict:
If everything above holds: edit ONLY the WO file ($WOId.md) to add an
"## Independent Review ($(Get-Date -Format 'yyyy-MM-dd'))" section
documenting exactly what you re-verified and how -- be specific (actual
counts, actual line counts, actual command output), not vague. Check the
Independent Review Acceptance Criteria box. Change the Status line at
the top from OWNER_DONE to CLOSED with a one-line note.

If ANYTHING does not hold -- a test fails, a claim doesn't match what you
find, a file is over 300 lines, something the WO says was built isn't
actually there -- do NOT mark it CLOSED. Add the same Independent Review
section documenting the specific discrepancy, leave Status as
OWNER_DONE, and add a clear "BLOCKED ON:" line describing exactly what
needs fixing.

Do not modify, edit, or create any file other than $WOId.md. Do not fix
anything you find wrong -- your job is to report, not to fix. Running
tests/compiles read-only against the code (which may write
__pycache__/.pytest_cache as a side effect) is expected; writing to any
other tracked file is not.
"@

Set-Content -Path $promptFile -Value $promptText -Encoding UTF8 -NoNewline

Write-Output "Project: $projectDir"
Write-Output "WO: $woPath"
Write-Output "Prompt saved: $promptFile"
Write-Output ""

Get-Content $promptFile -Raw | & claude --bg `
    --allowedTools "Read,Grep,Glob,Bash,Write" `
    --disallowedTools "Edit" `
    --restricted `
    --add-dir $HubRoot `
    --permission-mode acceptEdits `
    --permission-prompts none `
    --max-budget-usd $MaxBudget `
    --max-turns $MaxTurns `
    --name "$WOId Independent Review"
