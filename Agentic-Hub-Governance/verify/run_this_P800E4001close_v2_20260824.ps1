$path = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P800-E4.001.md"
$raw = Get-Content $path -Raw
# normalize all line endings to LF for reliable string matching (file has mixed CRLF/LF)
$content = $raw -replace "`r`n", "`n"

$old1 = @'
**Status:** OWNER_DONE -- build complete, 18/18 tests passing (2026-07-24). P_115 Ack done (2026-07-25). P_300 Ack done (2026-08-12, both real notes independently re-verified same session -- CLIX/NSLR spot-checked again 2026-08-21, both hold up). Both Acks are now DONE -- header corrected 2026-08-21 (was stale, still said "awaiting P_300 Ack" 9 days after that Ack completed).
**BLOCKED FROM CLOSED -- governance gap, not a work gap:** Completion Gate checklist was never added when OWNER_DONE was set (2026-07-24). Per WO_COMPLETION_GATE.md's Enforcement section (added 2026-07-29, ref EC-005): "Completion Gate block must exist at time OWNER_DONE is set, not backfilled later." This WO predates that rule and was never brought into compliance. Adding the checklist now to close it would be exactly the backfill the rule prohibits. Needs Tony's/P_000's call: treat as a named exception, or fold into the same fix as the "ten P_400/P_300 WOs" the Independent Review Requirement section already references as having sat OWNER_DONE with an empty checklist. Not resolved by this session -- flagged, not decided.
'@
$old1 = $old1 -replace "`r`n", "`n"

$new1 = @'
**Status:** CLOSED -- 2026-08-24, Independent Review by a fresh session (wrote none of this WO's build code). Build complete, 18/18 tests passing (2026-07-24). P_115 Ack done (2026-07-25). P_300 Ack done (2026-08-12, both real notes independently re-verified same session -- CLIX/NSLR spot-checked again 2026-08-21, both hold up). Both Acks DONE -- header corrected 2026-08-21.
**Governance-gap resolution (2026-08-24, Tony's direct instruction):** folded into the same fix as the "ten P_400/P_300 WOs" -- WO-P400-E4.004 confirmed as precedent: a genuinely separate session does real verification against actual files, and the checklist below is the record of that review, not a blind backfill. Real gap found in the process (not assumed clean): p115-project-context SKILL.md never referenced this WO's shared package despite P_115's real 2026-07-25 Ack -- P_300's skill file was already correct, P_115's was not. Fixed same session -- see Completion Gate item 2.

## Completion Gate (ref WO-P000-E3.001) -- completed 2026-08-24, Independent Review

[x] All file paths use Hub canonical paths -- confirmed 2026-08-24: `shared_resources\chaikin_enrichment\` (all files present on disk incl. tests), Hub-root `RunChaikinBatch.ps1` present, legacy `P_300_RunChaikinBatch.ps1` confirmed removed from live.
[x] Any new or changed shared-resource location reflected in:
    - P_000_SYSTEM_DOCUMENTATION.md Section 3.3 -- confirmed present (landed via WO-P000-E9.001, 2026-07-27).
    - Affected project CLAUDE.md files -- N/A, neither P_115 nor P_300 uses CLAUDE.md for this.
    - Affected project skill files -- p300-project-context: confirmed current and correct (references shared path, schema flag, runbook). p115-project-context: GAP FOUND -- no Chaikin reference despite the 2026-07-25 Ack. Fixed 2026-08-24: Critical Paths row added (shared package path, `-Schema P115` invocation, Ack date).
[x] CALLER PROPAGATION: P_300's `P_300_RunAllDailyEvals.ps1` migrated to call the shared `RunChaikinBatch.ps1 -Schema P300` (2026-08-12 entry above, confirmed live). P_115's only caller is the direct `RunChaikinBatch.ps1 -Schema P115` invocation verified 2026-07-25 -- no bypass path found.
[x] IMPERATIVE SWEEP: no prior Hub rule described Chaikin batch handling before this WO -- net-new capability, not a rule change. N/A.
[x] Downstream projects in Affects: P_115 and P_300 both notified via their own real Ack sections in this WO. P_116/P_117/P_118 not yet writing vault notes -- extension correctly deferred, not owed now.
[x] No sys.path side-channels -- package imports `VAULT_FOLDER_MAP`/`VAULT_ROOT` from `obsidian_writers.config` via the standard editable install, confirmed in this WO's own WHY section.
[x] Schema/signal contract: unchanged -- Chaikin section is an append to vault notes, does not alter `write_route` or any signal schema.
[x] DRAFT files for this WO: none found in `Agentic-Hub-Governance\work_orders\` (confirmed 2026-08-24).
[x] One ledger entry per WO confirmed -- single canonical `WO-P800-E4.001.md`; backup files present but correctly unregistered per WO_COMPLETION_GATE.md's Never Touch list.

'@
$new1 = $new1 -replace "`r`n", "`n"

if (-not $content.Contains($old1)) { Write-Output "OLD1 STILL NOT FOUND"; exit 1 }
$content = $content.Replace($old1, $new1)
Write-Output "Header/status edit applied"

$closingNote = @'

================================================================================
CLOSED -- 2026-08-24 (Sonnet, Independent Review, Tony's direct go-ahead) --
Completion Gate satisfied via genuine verification, folded into the same fix
as the ten P_400/P_300 WOs; one real gap found and fixed, not assumed clean
================================================================================

Fresh session relative to this WO's build -- wrote none of the shared
chaikin_enrichment code, P_115 code, or P_300 migration code above. Verified
against real files rather than checking boxes from memory: shared package on
disk with tests present, Hub-root RunChaikinBatch.ps1 present, legacy P_300
copy confirmed gone, P_000_SYSTEM_DOCUMENTATION.md Section 3.3 already lists
chaikin_enrichment, zero DRAFT files, single canonical WO file.

p300-project-context skill confirmed correct. p115-project-context skill was
NOT -- no Chaikin reference anywhere despite a real production Ack dated
2026-07-25. Exactly the Caller Propagation / skill-file gap this Completion
Gate item exists to catch, and it would have stayed invisible if only the
already-correct P_300 skill had been checked. Fixed same session: Critical
Paths row added, duplicate tasks/lessons.md file-table row merged (compression
pass), changelog entry added. Skill file edited on disk -- still needs Tony's
Customize -> Skills re-upload in Claude Desktop to go live; a disk edit alone
does not update the running skill.

Both Acks were already DONE (P_115 2026-07-25, P_300 2026-08-12) -- this WO's
LOOP precondition for CLOSED was met weeks ago. The only blocker was the
governance question, resolved by Tony's direct instruction this session.

Status: CLOSED.
================================================================================
'@
$closingNote = $closingNote -replace "`r`n", "`n"

$content = $content + $closingNote

# convert back to consistent CRLF for the whole file
$content = $content -replace "`n", "`r`n"

[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Output "WRITTEN"

$verify = Get-Content $path -Raw
Write-Output ("Status line now CLOSED: " + ($verify -match '\*\*Status:\*\* CLOSED -- 2026-08-24'))
Write-Output ("Completion Gate block present: " + $verify.Contains("## Completion Gate (ref WO-P000-E3.001) -- completed 2026-08-24"))
Write-Output ("Unchecked boxes remaining: " + ([regex]::Matches($verify, '\[ \]')).Count)
Write-Output ("Checked boxes total: " + ([regex]::Matches($verify, '\[x\]')).Count)
Write-Output ("Closing banner present: " + $verify.Contains("Status: CLOSED."))
