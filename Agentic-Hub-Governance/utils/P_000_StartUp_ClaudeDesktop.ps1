# P_000_StartUp_ClaudeDesktop.ps1
# Location: Agentic-Hub-Governance\utils\P_000_StartUp_ClaudeDesktop.ps1
# Purpose:  Morning startup orchestrator.
#           1. Runs the Hub WO status scanner (WO-P000-E21.001) to find which
#              projects actually have open work today.
#           2. For each, launches a scoped headless Claude Code run
#              (read + write-one-file only, no Bash, no Edit) that writes a
#              P_<ID>_Boot.md boot file for that project.
#           3. Waits for all of them, verifies each boot file actually landed
#              fresh (not a stale leftover), reports pass/fail per project.
#           4. Launches Claude Desktop.
# Ref:      WO-P000-E28.001 (INIT rethink)
# Created:  2026-09-09
#
# NOT YET LIVE-TESTED end to end: the scanner portion (steps 1) and the
# project-folder resolution (start of step 2) are proven against the real
# ledger/disk. The headless claude -p launches themselves are NOT tested by
# Claude in this build -- Tony's own sanity check (claude -p "reply PONG" in
# a real terminal, plus a glance at Settings > Usage) was the agreed
# precondition before this runs for real. Do not schedule this until that's
# done once by hand.

param(
    [string]$HubRoot      = "C:\Users\Trader\AI-Agent-Learning-Hub",
    [string]$ScannerPath  = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\utils\hub_wo_status_scan.ps1",
    [string]$BootDir      = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\boot\",
    [string]$LogRoot      = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\",
    [int]$PerProjectTimeoutSec = 480,
    [switch]$SkipDesktopLaunch, [string[]]$Projects = @(), [string]$DailyProjectsFile = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\utils\P_000_DailyProjects.txt",
    [hashtable]$BudgetByProject = @{ P400 = 1.00 },
    [double]$DefaultBudgetUsd = 0.50
)

$ErrorActionPreference = "Stop"
$runStart  = Get-Date
$timestamp = $runStart.ToString("yyyyMMdd_HHmmss")
$logDir    = Join-Path $LogRoot "startup_logs_$timestamp"

New-Item -ItemType Directory -Path $BootDir -Force | Out-Null
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

Write-Output "=== P_000 Startup: $timestamp ==="

# --- Step 1: run the scanner, find which projects have open WOs ---
Write-Output ""
Write-Output "-- Running WO status scan --"
$scanOutput = & $ScannerPath
$scanOutput | Write-Output

$allLines = ($scanOutput -join "`n") -split "`r?`n"
$openProjects = $allLines | Where-Object { $_ -match '^## (P\d+)$' } | ForEach-Object { $Matches[1] }
if ($Projects -and $Projects.Count -gt 0) {
    $targetProjects = $Projects
} elseif (Test-Path $DailyProjectsFile) {
    $targetProjects = Get-Content $DailyProjectsFile -Encoding UTF8 | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith("#") } | ForEach-Object { $_.Trim() }
} else {
    Write-Output "WARNING: daily projects file not found at $DailyProjectsFile -- falling back to hardcoded default"
    $targetProjects = @("P115", "P300", "P400")
}
$targetProjects = $targetProjects | Select-Object -Unique
$openProjects = $openProjects | Select-Object -Unique

Write-Output ""; Write-Output "-- Daily boot list: $($targetProjects -join ', ') --"; foreach ($tp in $targetProjects) { $hasOpenWo = $openProjects -contains $tp; Write-Output "  $tp -- $(if ($hasOpenWo) { 'has open WO(s)' } else { 'no open WOs right now' })" }
if ($targetProjects.Count -eq 0) {
    Write-Output ""
    Write-Output "No projects in scope -- nothing to boot. Launching Desktop only."
}

# --- Step 2: resolve project ID -> folder, built from disk, not hardcoded ---
$projectDirs = @{}
Get-ChildItem -Path (Join-Path $HubRoot "projects") -Directory | ForEach-Object {
    if ($_.Name -match '^P_(\d+)_') {
        $projId = "P" + $Matches[1]
        $projectDirs[$projId] = $_.FullName
    }
}

# --- Step 3: launch one scoped headless run per open project ---
$runs = @()
foreach ($projId in $targetProjects) {
    if (-not $projectDirs.ContainsKey($projId)) {
        Write-Output "SKIP $projId -- no matching folder under projects\ (checked disk, not assumed)"
        continue
    }
    $dir      = $projectDirs[$projId]
    $bootFile = Join-Path $BootDir "$($projId)_Boot.md"
    $logOut   = Join-Path $logDir "$($projId)_stdout.log"
    $logErr   = Join-Path $logDir "$($projId)_stderr.log"

    $prompt = "Run this project's INIT sequence using its project-context skill and any relevant Hub governance skills. Read what you need (WO status, current state, recent lessons) to produce an accurate summary, but do not modify any project file. Write exactly one file, at this path: $bootFile -- a concise Markdown boot summary covering current WO status for this project, any flags or blockers, and one suggested next step. Do not write, edit, or create any other file."

    $budget = if ($BudgetByProject.ContainsKey($projId)) { $BudgetByProject[$projId] } else { $DefaultBudgetUsd }
    $argString = "-p `"$prompt`" --allowedTools `"Read,Grep,Glob,Write`" --disallowedTools `"Bash,Edit`" --restricted --add-dir `"$HubRoot`" --permission-mode acceptEdits --permission-prompts none --max-budget-usd $budget --max-turns 15 --output-format json"
    # No --cwd flag in this CLI version (confirmed via claude --help) -- working
    # directory is set via Start-Process -WorkingDirectory below. --restricted
    # confines file tools to the working dir + --add-dir and drops Bash/
    # PowerShell/REPL/WebFetch by default. --permission-prompts none turns any
    # unanswerable prompt into a clean denial instead of a hang.

    $proc = Start-Process -FilePath "claude" -ArgumentList $argString -WorkingDirectory $dir `
        -RedirectStandardOutput $logOut -RedirectStandardError $logErr `
        -WindowStyle Hidden -PassThru
    $proc.Handle | Out-Null   # retains a valid process handle -- without this ExitCode can come back blank/unreliable after WaitForExit on some builds

    $runs += [PSCustomObject]@{
        ProjectId = $projId
        Process   = $proc
        BootFile  = $bootFile
        LogOut    = $logOut
    }
    Write-Output "LAUNCHED $projId -- pid $($proc.Id), cwd $dir"
}

# --- Step 4: wait for all, then verify each one actually produced a fresh boot file ---
Write-Output ""
Write-Output "-- Waiting on $($runs.Count) headless run(s), up to ${PerProjectTimeoutSec}s each --"

$results = @()
foreach ($r in $runs) {
    $exited = $r.Process.WaitForExit($PerProjectTimeoutSec * 1000)
    $exitCode = $null
    if ($exited) { try { $exitCode = $r.Process.ExitCode } catch { $exitCode = $null } } else {
        try { $r.Process.Kill() } catch {}
    }

    $bootOk = $false
    if (Test-Path $r.BootFile) {
        $mtime = (Get-Item $r.BootFile).LastWriteTime
        $bootOk = ($mtime -ge $runStart)
        if ($bootOk) {
            # Prepend the standard suggested chat-name heading -- deterministic,
            # generated by the script (not the model) so the date/time is always
            # correct. Matches system-doc-initializer's Step 3 format.
            $chatName = "$($r.ProjectId) $($runStart.ToString('dddd, MMMM dd, yyyy HH:mm')) ET"
            $existing = Get-Content $r.BootFile -Raw -Encoding UTF8
            $withHeading = "**Suggested chat name:** $chatName`r`n`r`n" + $existing
            [System.IO.File]::WriteAllText($r.BootFile, $withHeading, [System.Text.UTF8Encoding]::new($false))
        }
    }

    $costNote = "n/a"
    if (Test-Path $r.LogOut) {
        try {
            $parsed = Get-Content $r.LogOut -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($parsed.total_cost_usd) { $costNote = "`$$($parsed.total_cost_usd)" }
            elseif ($parsed.cost_usd)   { $costNote = "`$$($parsed.cost_usd)" }
        } catch { }
    }

    $exitDisplay = if ($null -eq $exitCode) { "unknown" } else { "$exitCode" }
    $status = if (-not $exited) { "TIMED OUT (killed)" }
              elseif (-not $bootOk) { "NO BOOT FILE (exit $exitDisplay) -- see log" }
              elseif ($exitCode -and $exitCode -ne 0) { "BOOT FILE OK but exit $exitDisplay -- check log" }
              else { "OK" }

    $results += [PSCustomObject]@{
        ProjectId = $r.ProjectId
        Status    = $status
        BootFile  = $r.BootFile
        Cost      = $costNote
        Log       = $r.LogOut
    }
}

Write-Output ""
Write-Output "-- Summary --"
foreach ($res in $results) {
    Write-Output "$($res.ProjectId): $($res.Status) -- cost $($res.Cost) -- log $($res.Log)"
}
$failCount = ($results | Where-Object { $_.Status -ne "OK" }).Count
if ($failCount -gt 0) {
    Write-Output ""
    Write-Output "$failCount of $($results.Count) run(s) did not complete cleanly -- check logs above before trusting those boot files."
}

# --- Step 5: launch Claude Desktop ---
if (-not $SkipDesktopLaunch) {
    Write-Output ""
    Write-Output "-- Launching Claude Desktop --"
    Start-Process "shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude"
}

Write-Output ""
Write-Output "Done. Boot files (if any): $BootDir"
Write-Output "Logs: $logDir"
