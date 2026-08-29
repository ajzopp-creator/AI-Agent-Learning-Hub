$path = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P000-E18.001.md"
$lines = Get-Content $path

$gateHeaderIdx = ($lines | Select-String "## Completion Gate \(ref WO-P000-E3.001\)").LineNumber - 1

$newBlock = @(
    "[x] Fix built in ``shared_resources\hub_mcp_launcher.ps1`` -- v1.1, 2026-08-28",
    "[x] Verified against a representative success case and failure case (test",
    "    bats exit /b 0 / exit /b 1) -- both branches now write the status file",
    "    correctly. Not run against all 7 live wrappers individually; the fix",
    "    is in the shared function all 7 call, verified via caller propagation",
    "    check below.",
    "[x] CALLER PROPAGATION -- confirmed no wrapper has its own local copy of",
    "    the old inline chaining pattern; all 7 dot-source Invoke-HubBat",
    "[x] Regression test -- N/A-language caveat applies (PowerShell/batch, not",
    "    Python); documented before/after repro above stands in for a pytest",
    "    regression test",
    "[x] Downstream projects in Affects notified -- documented above; Tony",
    "    informed in session, single-operator Hub",
    "[x] DRAFT files cleanup / one ledger entry confirmed -- no DRAFT files",
    "    for this WO; test artifacts removed from verify\ after use"
)

# idx0=header, idx1=blank, idx2..idx12=old checklist (11 lines), idx13=blank, idx14=---
$before = $lines[0..($gateHeaderIdx+1)]
$after  = $lines[($gateHeaderIdx+13)..($lines.Count-1)]

$final = $before + $newBlock + $after
[System.IO.File]::WriteAllText($path, ($final -join "`r`n") + "`r`n", [System.Text.UTF8Encoding]::new($false))
Write-Output "Gate block replaced. Header was at line $($gateHeaderIdx+1). Before count=$($before.Count) After count=$($after.Count)"
