$ErrorActionPreference = "Stop"
$target = 'C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P000-E29.001.md'

$old1 = @'
**Status:** PENDING -- filed at Tony's explicit direction to hold scope; deprioritized until he chooses to build it. Nothing built, nothing scoped in detail yet.
'@

$new1 = @'
**Status:** IN_PROGRESS -- prioritized 2026-09-11 after a live symptom (P_115 chat title not reflecting the boot-file suggested name) confirmed the consumer-side gap this WO exists to close. Scoping section added below; SKILL.md revision + live dry run not yet started.
'@

$old2 = @'
## Next Steps

1. Stays PENDING until Tony prioritizes it.
2. When he does: scope the detection/behavior questions above, then revise system-doc-initializer SKILL.md (version bump), with a live INIT dry run before calling it OWNER_DONE -- same rollout discipline as prior skill revisions (P_300 SIP v3.3 precedent, E21.001/E28.001 pilot-then-verify precedent).
'@

$new2 = @'
## Scoping (2026-09-11)

Answering the Detection/Behavior questions and folded-in Questions 1/3/4, based on today's P_115 boot file (`P115_Boot.md`, correct heading confirmed on disk) and E28.001's own gap note.

**Detection -- fresh vs. stale.** A live session can't reuse the orchestrator's `$runStart` mtime check verbatim (no equivalent clock at INIT time in a live chat). Proposed rule: a boot file is fresh if (a) its mtime is from the current calendar day, AND (b) no WO file for that project has a LastWriteTime newer than the boot file's. (b) catches the case where a separate session closed or updated a WO after the boot ran, which (a) alone would miss.

**Behavior on hit.** If fresh by both checks: skip straight to displaying the boot file's content (WO table, flags, next step) plus the Suggested chat name heading it already contains -- fastest path, the whole point of this WO. Still run Step 0 (live env/runtime check) every session regardless -- that's about THIS session's own MCP connection, not something a headless run minutes earlier can attest to (EC-009 precedent: client switches happen mid-session with no signal).

**Behavior on miss.** Unchanged -- falls back to today's Steps 0-5 in full. This WO adds a faster path in front of that, doesn't remove it.

**Q1 -- mechanical vs. live-judgment.** Boot-file-coverable: Step 0.5 (project ID -- the matched boot filename effectively confirms it), Step 1b (daily gate check -- already close to the scanner's job), Step 3 (chat name -- already done, confirmed working on disk today). Stays live: Step 0 (this session's own env check, not transferable), Step 1/2 (system doc's 4 sections -- Definitions, AI Behavior Rules, Error Corrections, Parameter Registry -- none of which a project boot file covers, see Q4), Step 4 (apply params -- ongoing behavior, not a one-time step), Step 5 (Protocols A-F -- ongoing behavior for the whole session, not an init-time check).

**Q3 -- run every session or staleness-gated?** Gate it: on a fresh-boot hit, skip the full re-derivation and go straight to Step 0 + display. Only fall through to full Steps 1-2 if the boot is missing/stale, or if the session's actual task needs system-doc detail the boot file doesn't carry (e.g., touching Python architecture rules, parameter registry values) -- lazy-load rather than always front-loading all 4 sections.

**Q4 -- trim the 4-section load?** No -- these were never WO-status content, so scanner offload doesn't touch them. They're the live-judgment layer (definitions, MUST/MUST NOT rules, error corrections, exact parameter values) that no boot file or scanner run produces. One real trim candidate flagged, not decided: Section 6 (Error Corrections Log) is now 11 entries and growing -- could filter to "recent + still-relevant" instead of "all" at load time. Separate scope, not deciding here.

**Not yet decided:** exact SKILL.md wording/structure for the new boot-file-check step this implies, and where it slots relative to existing Step 0/0.5. Needs the actual revision pass.

## Next Steps

1. DONE 2026-09-11 -- prioritized; Status moved PENDING -> IN_PROGRESS; scoping section above.
2. Revise system-doc-initializer SKILL.md (version bump) per the scoping decisions above, with a live INIT dry run before calling it OWNER_DONE -- same rollout discipline as prior skill revisions (P_300 SIP v3.3 precedent, E21.001/E28.001 pilot-then-verify precedent). Not yet started -- needs Tony's go-ahead on the scoping answers first.
'@

$content = [System.IO.File]::ReadAllText($target)
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
$check1 = $verify.Contains('**Status:** IN_PROGRESS -- prioritized 2026-09-11')
$check2 = $verify.Contains('## Scoping (2026-09-11)')
$check3 = $verify.Contains('DONE 2026-09-11 -- prioritized')
$check4 = $verify.Contains('**Depends On:** WO-P000-E28.001')
$check5 = $verify.Contains('*Created 2026-09-10, P_000 session.')

Write-Output "Status updated: $check1"
Write-Output "Scoping section present: $check2"
Write-Output "Next Steps updated: $check3"
Write-Output "Untouched header field intact: $check4"
Write-Output "Untouched footer intact: $check5"

if ($check1 -and $check2 -and $check3 -and $check4 -and $check5) {
    Write-Output "RESULT: OK"
} else {
    Write-Output "RESULT: FAIL -- review before trusting this file"
}
