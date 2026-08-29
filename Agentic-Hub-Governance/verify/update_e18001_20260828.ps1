$path = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P000-E18.001.md"
$backup = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P000-E18.001.md.backup_2026-08-28_1145"
Copy-Item $path $backup -Force

$raw = Get-Content $path -Raw

$oldStatus = "**Status:** PENDING -- root cause confirmed, fix designed, not yet built. Deferred by Tony (2026-08-25): investigate/fix under this WO later rather than blocking the current session."
$newStatus = "**Status:** OWNER_DONE -- fix built and verified 2026-08-28. See RESOLUTION section below."
$raw = $raw.Replace($oldStatus, $newStatus)

$resolutionMarker = "## Completion Gate (ref WO-P000-E3.001) -- not started"
$resolution = @'
## RESOLUTION (2026-08-28)

`shared_resources\hub_mcp_launcher.ps1` bumped v1.0 -> v1.1. `Invoke-HubBat`
now generates a one-off `.cmd` launcher per call (`_launcher_<statusfile>.cmd`,
next to the status file, overwritten each run) that checks `%errorlevel%`
with normal batch `if` logic instead of the old inline `cmd /c "<bat>" &&
echo SUCCESS > "<status>" || echo FAILED:%ERRORLEVEL% > "<status>"` chain.
`Start-Process` launches the generated `.cmd` directly with `BatPath` and
`StatusFile` as separate `-ArgumentList` array elements, so PowerShell
quotes each one correctly -- no manual multi-quote one-liner, no `cmd /c`
edge case.

**Verification:** same repro as the original diagnosis -- two trivial test
bats (`exit /b 0`, `exit /b 1`) run through the fixed `Invoke-HubBat`.
Success case returned `SUCCESS`, failure case returned `FAILED:1`. Both
branches fire correctly; prior to the fix, neither wrote a status file at
all. Test artifacts removed from `Agentic-Hub-Governance\verify\` after.

**Caller propagation check:** all 7 affected wrappers (P_010_daily_posture_mcp.ps1,
P_010_intraday_mcp.ps1, P_020_WeeklyUpdate_mcp.ps1, P_300_AddPattern_mcp.ps1,
P_300_DailyEval_mcp.ps1, P_805_daily_pipeline_mcp.ps1,
P_400_Batch2bCashPull_mcp.ps1) dot-source the shared function and call
`Invoke-HubBat` -- none carry a local copy of the old inline chain. Fix
propagates to all 7 automatically, no per-wrapper edit needed. Note: the two
P_300 wrapper files currently live under `docs\archive\`, not the project
root alongside the others -- flagged to Tony, not corrected here (out of
scope for this WO).

**Downstream notification:** documented here and reported to Tony directly
in session (2026-08-28) -- single-operator Hub, no separate downstream
session to notify beyond this WO record and this chat.

**Backup of pre-fix file:** `hub_mcp_launcher.ps1.backup_2026-08-28_1131`

---

## Completion Gate (ref WO-P000-E3.001)
'@

$raw = $raw.Replace($resolutionMarker, $resolution)

$oldGate = @'
[ ] Fix built in `shared_resources\hub_mcp_launcher.ps1`
[ ] Verified against all 7 affected `_mcp.ps1` wrappers (or at minimum a
    representative success case and failure case), not just P_400's
[ ] CALLER PROPAGATION -- confirm no wrapper has its own local copy of the
    old inline chaining pattern outside the shared function
[ ] Regression test added per python-project-architecture (N/A language
    caveat: this is PowerShell/batch, not Python -- confirm whether the
    Hub-wide regression-test convention extends here or whether a documented
    before/after repro in this WO is sufficient)
[ ] Downstream projects in Affects notified
[ ] DRAFT files cleanup / one ledger entry confirmed
'@

$newGate = @'
[x] Fix built in `shared_resources\hub_mcp_launcher.ps1` -- v1.1, 2026-08-28
[x] Verified against a representative success case and failure case (test
    bats exit /b 0 / exit /b 1) -- both branches now write the status file
    correctly. Not run against all 7 live wrappers individually; the fix is
    in the shared function all 7 call, verified via caller propagation check
    below.
[x] CALLER PROPAGATION -- confirmed no wrapper has its own local copy of the
    old inline chaining pattern; all 7 dot-source Invoke-HubBat
[x] Regression test -- N/A-language caveat applies (PowerShell/batch, not
    Python); documented before/after repro above stands in for a pytest
    regression test
[x] Downstream projects in Affects notified -- documented above; Tony
    informed in session, single-operator Hub
[x] DRAFT files cleanup / one ledger entry confirmed -- no DRAFT files for
    this WO; test artifacts removed from verify\ after use
'@

$raw = $raw.Replace($oldGate, $newGate)

[System.IO.File]::WriteAllText($path, $raw, [System.Text.UTF8Encoding]::new($false))
Write-Output "WO-P000-E18.001.md updated"
