# apply_p000_startup_budget_edit_20260911_091653.ps1
# One-off targeted edit: add per-project budget cap params to
# P_000_StartUp_ClaudeDesktop.ps1 and use them when building $argString.
# Target: Agentic-Hub-Governance\utils\P_000_StartUp_ClaudeDesktop.ps1
$ErrorActionPreference = "Stop"
$target = 'C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\utils\P_000_StartUp_ClaudeDesktop.ps1'

$old1 = @'
    [switch]$SkipDesktopLaunch, [string[]]$Projects = @(), [string]$DailyProjectsFile = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\utils\P_000_DailyProjects.txt"
)
'@

$new1 = @'
    [switch]$SkipDesktopLaunch, [string[]]$Projects = @(), [string]$DailyProjectsFile = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\utils\P_000_DailyProjects.txt",
    [hashtable]$BudgetByProject = @{ P400 = 1.00 },
    [double]$DefaultBudgetUsd = 0.50
)
'@

$old2 = @'
    $argString = "-p `"$prompt`" --allowedTools `"Read,Grep,Glob,Write`" --disallowedTools `"Bash,Edit`" --restricted --add-dir `"$HubRoot`" --permission-mode acceptEdits --permission-prompts none --max-budget-usd 0.50 --max-turns 15 --output-format json"
'@

$new2 = @'
    $budget = if ($BudgetByProject.ContainsKey($projId)) { $BudgetByProject[$projId] } else { $DefaultBudgetUsd }
    $argString = "-p `"$prompt`" --allowedTools `"Read,Grep,Glob,Write`" --disallowedTools `"Bash,Edit`" --restricted --add-dir `"$HubRoot`" --permission-mode acceptEdits --permission-prompts none --max-budget-usd $budget --max-turns 15 --output-format json"
'@

$content = [System.IO.File]::ReadAllText($target)
$lineCountBefore = (Get-Content $target).Count

$hits1 = ([regex]::Matches($content, [regex]::Escape($old1))).Count
$hits2 = ([regex]::Matches($content, [regex]::Escape($old2))).Count
Write-Output "Occurrence check -- old1: $hits1, old2: $hits2"

if ($hits1 -ne 1 -or $hits2 -ne 1) {
    Write-Output "ABORT: expected exactly 1 occurrence each, found old1=$hits1 old2=$hits2 -- not writing"
    exit 1
}

$updated = $content.Replace($old1, $new1).Replace($old2, $new2)
[System.IO.File]::WriteAllText($target, $updated, [System.Text.UTF8Encoding]::new($false))

$verify = [System.IO.File]::ReadAllText($target)
$lineCountAfter = (Get-Content $target).Count
$check1 = $verify.Contains('[hashtable]$BudgetByProject = @{ P400 = 1.00 }')
$check2 = $verify.Contains('--max-budget-usd $budget')
$check3 = -not $verify.Contains('--max-budget-usd 0.50 --max-turns')
$check4 = $verify.Contains('Start-Process "shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude"')

Write-Output "Lines before: $lineCountBefore  after: $lineCountAfter (expect +3)"
Write-Output "New param present: $check1"
Write-Output "New budget var used: $check2"
Write-Output "Old hardcoded 0.50 gone: $check3"
Write-Output "Untouched region intact (Step 5 launch line): $check4"

if ($check1 -and $check2 -and $check3 -and $check4) {
    Write-Output "RESULT: OK"
} else {
    Write-Output "RESULT: FAIL -- review before trusting this file"
}
