$ErrorActionPreference = "Stop"
$target = 'C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\system-doc-initializer\SKILL.md'

$content = [System.IO.File]::ReadAllText($target)
$lineCountBefore = (Get-Content $target).Count

# --- Edit 1: insert new Step 0.6 before "## Step 1 " using an ASCII-only
# marker (the real header line has an em-dash right after "Step 1", which
# lessons.md flags as unreliable inside a .ps1 anchor -- IndexOf/Substring
# splice on ASCII text sidesteps that instead of matching across it).
$marker = "## Step 1 "
$idxCount = 0
$searchFrom = 0
while (($p = $content.IndexOf($marker, $searchFrom)) -ge 0) { $idxCount++; $searchFrom = $p + 1 }
if ($idxCount -ne 1) {
    Write-Output "ABORT: marker '$marker' found $idxCount times (expected 1) -- not writing"
    exit 1
}
$insertIdx = $content.IndexOf($marker)

$insertion = @'
## Step 0.6 - Boot-File Check (added 2026-09-11, ref WO-P000-E29.001)

After Step 0.5 identifies the Project ID, check for a same-day boot file before running Steps 1/1b/2 in full.

1. `Test-Path Agentic-Hub-Governance\boot\[Project ID]_Boot.md`. Not found -> skip to Step 1, full sequence, unchanged.
2. Found -> fresh check, both must hold: (a) boot file's LastWriteTime is today's calendar date, AND (b) no `WO-[Project ID]-*.md` under `Agentic-Hub-Governance\work_orders\` has a LastWriteTime newer than the boot file's. Either fails -> STALE, skip to Step 1, full sequence, unchanged -- never silently trust a stale boot file.
3. FRESH -> display the boot file's content verbatim (it already carries its own Suggested chat name heading, WO table, flags, next step) instead of Steps 1/1b/2. Step 0 (runtime check) still runs regardless -- a headless run minutes earlier attests to nothing about THIS session's own MCP connection (EC-009 precedent).
4. Lazy-load exception: if the session's actual task needs system-doc detail the boot file doesn't carry (Python architecture rules, exact parameter values, a specific past error correction), run Step 1/2 on demand at that point, not preemptively.
5. On a FRESH hit, Step 3 is already satisfied by the boot file's own heading -- do not regenerate.

---

'@

$content = $content.Substring(0, $insertIdx) + $insertion + $content.Substring($insertIdx)

# --- Edit 2: footer "Last Updated" line -- this snippet is plain ASCII in
# the original (no em-dash), safe for a normal literal .Replace().
$old2 = @'
*Last Updated: 2026-09-07 -- Step 0 re-check trigger added (EC-009): a mid-session Desktop-to-web client switch went undetected for several turns until a live Windows-MCP call failed; Step 0 now re-runs on a call failure or a stated/implied client switch, not just at the session's first message. Prior:
'@

$new2 = @'
*Last Updated: 2026-09-11 -- Step 0.6 Boot-File Check added (ref WO-P000-E29.001): a same-day boot file with no newer WO file for that project lets a live session skip straight to displaying it instead of running Steps 1/1b/2 in full; Step 0's own runtime check still runs every session regardless -- a headless run minutes earlier proves nothing about this session's own MCP connection. Prior: 2026-09-07 -- Step 0 re-check trigger added (EC-009): a mid-session Desktop-to-web client switch went undetected for several turns until a live Windows-MCP call failed; Step 0 now re-runs on a call failure or a stated/implied client switch, not just at the session's first message. Prior:
'@

$hits2 = ([regex]::Matches($content, [regex]::Escape($old2))).Count
Write-Output "Step 0.6 insertion point found once: OK (marker count was $idxCount before insert)"
Write-Output "Footer old2 occurrence check: $hits2"

if ($hits2 -ne 1) {
    Write-Output "ABORT: footer anchor found $hits2 times (expected 1) -- not writing"
    exit 1
}

$content = $content.Replace($old2, $new2)
[System.IO.File]::WriteAllText($target, $content, [System.Text.UTF8Encoding]::new($false))

$verify = [System.IO.File]::ReadAllText($target)
$lineCountAfter = (Get-Content $target).Count
$check1 = $verify.Contains("## Step 0.6 - Boot-File Check")
$check2 = $verify.Contains("*Last Updated: 2026-09-11 -- Step 0.6 Boot-File Check added")
$check3 = $verify.Contains("**EC-002")
$check4 = $verify.Contains("## Step 5")
$protocolCount = ([regex]::Matches($verify, "### Protocol [A-F]")).Count
$stepOneStillThere = ([regex]::Matches($verify, [regex]::Escape($marker))).Count

Write-Output "Lines before: $lineCountBefore  after: $lineCountAfter"
Write-Output "New Step 0.6 present: $check1"
Write-Output "Footer updated: $check2"
Write-Output "EC-002 untouched region intact: $check3"
Write-Output "Step 5 header intact: $check4"
Write-Output "Protocol A-F count (expect 6): $protocolCount"
Write-Output "Step 1 marker still present exactly once (expect 1): $stepOneStillThere"

if ($check1 -and $check2 -and $check3 -and $check4 -and $protocolCount -eq 6 -and $stepOneStillThere -eq 1) {
    Write-Output "RESULT: OK"
} else {
    Write-Output "RESULT: FAIL -- review before trusting this file"
}
