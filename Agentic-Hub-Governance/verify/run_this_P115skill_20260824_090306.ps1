$path = "C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\p115-project-context\SKILL.md"
$content = Get-Content $path -Raw

$old1 = @'
| `tasks/lessons.md` | Durable trade/process lessons -- READ AT INIT STEP 0.5 (folded in 2026-08-17 after sitting orphaned since 2026-06-09 creation; its own header said to read at every INIT but nothing did until now). APPEND new durable lessons here going forward, not just this skill file. |
| `tasks/lessons.md` | Durable trade/process lessons -- read at INIT (Session-Start Checklist below), appended same session when a lesson surfaces |
'@
$new1 = @'
| `tasks/lessons.md` | Durable trade/process lessons -- READ AT INIT STEP 0.5 (folded in 2026-08-17 after sitting orphaned since 2026-06-09 creation). APPEND new durable lessons here same session when one surfaces. |
'@

if (-not $content.Contains($old1)) { Write-Output "OLD1 NOT FOUND"; exit 1 }
$content = $content.Replace($old1, $new1)
Write-Output "Edit 1 applied"

$old2 = @'
| Vault output | `<Hub>\trading_journal\TradeManagement\P115\` |
'@
$new2 = @'
| Vault output | `<Hub>\trading_journal\TradeManagement\P115\` |
| Chaikin enrichment | `<Hub>\shared_resources\chaikin_enrichment\` (shared, P_800-owned) -- batch via Hub-root `RunChaikinBatch.ps1 -Schema P115`; real Ack 2026-07-25 (EMR/OGN/PH enriched, read back confirmed, WO-P800-E4.001) |
'@

if (-not $content.Contains($old2)) { Write-Output "OLD2 NOT FOUND"; exit 1 }
$content = $content.Replace($old2, $new2)
Write-Output "Edit 2 applied"

$old3 = @'
## Changelog

### 2026-08-17
'@
$new3 = @'
## Changelog

### 2026-08-24
- **Chaikin Power Gauge batch path added (Completion Gate skill-file gap from WO-P800-E4.001).** P_115 ran a real Chaikin enrichment Ack on 2026-07-25 (EMR/OGN/PH via `RunChaikinBatch.ps1 -Schema P115`) but this skill never referenced it -- WO-P800-E4.001 sat OWNER_DONE with that Completion Gate item unsatisfied for P_115 specifically (P_300's skill file was already correct). Fix: Critical Paths row added. Also merged two duplicate `tasks/lessons.md` file-table rows into one (compression pass).

### 2026-08-17
'@

if (-not $content.Contains($old3)) { Write-Output "OLD3 NOT FOUND"; exit 1 }
$content = $content.Replace($old3, $new3)
Write-Output "Edit 3 applied"

[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))
Write-Output "WRITTEN"

$verify = Get-Content $path -Raw
Write-Output ("Contains Chaikin row: " + $verify.Contains("Chaikin enrichment"))
Write-Output ("Contains merged lessons row: " + $verify.Contains("APPEND new durable lessons here same session when one surfaces."))
Write-Output ("Contains changelog entry: " + $verify.Contains("### 2026-08-24"))
Write-Output ("No more duplicate lessons row: " + (-not $verify.Contains("appended same session when a lesson surfaces")))
