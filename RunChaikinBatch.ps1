param(
    [Parameter(Mandatory=$true)]
    [string]$Schema
)

# Schema-driven Chaikin Power Gauge batch enrichment. Replaces P_300's
# project-local P_300_RunChaikinBatch.ps1 (WO-P800-E4.001). The Python
# scanner reads write_route from vault frontmatter directly -- no log
# parsing, no date-guessing in the prompt. Enabled-schema validation lives
# in shared_resources\chaikin_enrichment\config.py (SCHEMAS_ENABLED), not
# duplicated here.

$HUB_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub"
$PYTHON = "C:\Users\Trader\.conda\envs\p140\python.exe"
$RUN_SCRIPT = "$HUB_ROOT\shared_resources\chaikin_enrichment\application\run_chaikin_batch.py"
$PROMPT_FILE = "$HUB_ROOT\shared_resources\chaikin_enrichment\_last_prompt.txt"

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
claude -p $prompt --chrome
