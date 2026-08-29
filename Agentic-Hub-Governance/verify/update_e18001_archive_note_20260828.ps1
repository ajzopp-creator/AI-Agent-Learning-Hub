$path = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P000-E18.001.md"
$lines = Get-Content $path

$idx = ($lines | Select-String "propagates to all 7 automatically").LineNumber - 1
Write-Output "Found at 0-based index: $idx"
Write-Output "Line content: $($lines[$idx])"

# Lines to replace: idx (propagates...Note: the two) through idx+3 (scope for this WO).)
$replacement = @(
    "propagates to all 7 automatically, no per-wrapper edit needed. Note: the two",
    "P_300 wrapper files (P_300_AddPattern_mcp.ps1, P_300_DailyEval_mcp.ps1) live",
    "under ``docs\archive\`` only, with no active copy elsewhere in P_300 --",
    "per standing Hub convention, files in an archive folder are deprecated",
    "intentionally, not strays. They are not currently live entry points; the",
    "fix still reaches them since they dot-source the shared function, but the",
    "WO's Affects list of ``7 wrappers`` should be read as 5 active + 2",
    "deprecated. No correction needed -- expected state, not an anomaly."
)

$before = $lines[0..($idx-1)]
$after  = $lines[($idx+4)..($lines.Count-1)]
$final = $before + $replacement + $after
[System.IO.File]::WriteAllText($path, ($final -join "`r`n") + "`r`n", [System.Text.UTF8Encoding]::new($false))
Write-Output "Replaced. Before=$($before.Count) After=$($after.Count)"
