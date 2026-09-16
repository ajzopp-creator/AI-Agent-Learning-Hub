# hub_wo_status_scan.ps1
# Location: Agentic-Hub-Governance\utils\hub_wo_status_scan.ps1
# Purpose:  Hub-wide work order status scan, ALL projects, one pass.
#           Replaces per-project INIT WO review with one consolidated report.
#           Ref: WO-P000-E21.001 (pivoted from Cowork / parallel-window
#           evaluation once both were confirmed not viable).
# Usage:    powershell -NoProfile -ExecutionPolicy Bypass -File hub_wo_status_scan.ps1
# Created:  2026-09-09
# v1.1 (2026-09-09): fixed Get-Content encoding (was garbling em-dashes on
#   read -- mojibake in v1.0 output); status field now captures full text,
#   not just first token -- P_300/P_400 use freeform status phrases
#   ("CODE FIX BUILT", "BOTH PARTS CLOSED", "MERGED into ...") that don't
#   match the canonical PENDING/IN_PROGRESS/BLOCKED/OWNER_DONE/COMPLETE/
#   CLOSED vocabulary; these are now shown in full and flagged NONSTANDARD
#   rather than silently mis-bucketed. Title fallback added for WOs using
#   a different template (e.g. P_025's Project:/Type: header, no title text
#   on the # line).

param(
    [string]$LedgerPath = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\",
    [string]$OutputDir  = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\"
)

$ErrorActionPreference = "Stop"
$dash = [char]0x2014
$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = Join-Path $OutputDir "hub_wo_status_$timestamp.md"
$closedStatuses = @('COMPLETE', 'CLOSED')
$canonicalStatuses = @('PENDING', 'IN_PROGRESS', 'BLOCKED', 'OWNER_DONE', 'COMPLETE', 'CLOSED')

# Canonical WO filenames only: WO-P<digits>-<phase>.<seq>.md
# Any backup/draft/scratch suffix breaks this pattern and is skipped by design.
$candidates = Get-ChildItem -Path $LedgerPath -Filter "*.md" -File

$records = @()

foreach ($f in $candidates) {
    if ($f.BaseName -notmatch '^WO-(P\d+)-([A-Za-z0-9]+)\.(\d{2,4})$') { continue }
    $projectId  = $Matches[1]
    $phaseToken = $Matches[2]
    $seqStr     = $Matches[3]

    $phaseNum = 0
    if ($phaseToken -match '(\d+)') { $phaseNum = [int]$Matches[1] }
    $seqNum = [int]$seqStr

    $content = Get-Content $f.FullName -Raw -Encoding UTF8
    $lines   = $content -split "`r?`n"

    $statusLine = ($lines | Select-String -Pattern '\*\*Status:\*\*' | Select-Object -First 1).Line
    $statusFull = ""
    if ($statusLine -and $statusLine -match '\*\*Status:\*\*\s*(.+)$') {
        $statusFull = $Matches[1].Trim()
    }
    $statusFirstWord = "UNKNOWN"
    if ($statusFull) {
        $statusFirstWord = (($statusFull -split '\s+')[0]).ToUpper().TrimEnd(',', '.', ':')
    }
    if ($closedStatuses -contains $statusFirstWord) { continue }
    $isNonstandard = $canonicalStatuses -notcontains $statusFirstWord

    $statusDisplay = $statusFull
    if ($statusDisplay.Length -gt 130) { $statusDisplay = $statusDisplay.Substring(0, 130) + '...' }

    $titleLine = ($lines | Where-Object { $_ -match '^#\s' } | Select-Object -First 1)
    $titleRaw  = if ($titleLine) { $titleLine -replace '^#\s*', '' } else { '' }
    $titleStripped = $titleRaw -replace [regex]::Escape($f.BaseName), ''
    $titleStripped = $titleStripped -replace ('^[\s\-' + $dash + ':]+'), ''
    $titleStripped = $titleStripped.Trim()
    if (-not $titleStripped) { $titleStripped = "(untitled -- non-standard template, check file)" }

    $affectsLine = ($lines | Select-String -Pattern '\*\*Affects:\*\*' | Select-Object -First 1).Line
    if ($affectsLine) { $affectsLine = $affectsLine -replace '\*\*Affects:\*\*\s*', '' } else { $affectsLine = '' }
    if ($affectsLine.Length -gt 110) { $affectsLine = $affectsLine.Substring(0, 110) + '...' }

    $dependsLine = ($lines | Select-String -Pattern '\*\*Depends On:\*\*' | Select-Object -First 1).Line
    $blockerLine = ($lines | Select-String -Pattern '\*\*Blocker:\*\*' | Select-Object -First 1).Line

    $records += [PSCustomObject]@{
        ProjectId         = $projectId
        WoId              = "WO-$projectId-$phaseToken.$seqStr"
        PhaseNum          = $phaseNum
        SeqNum            = $seqNum
        StatusFirstWord   = $statusFirstWord
        StatusDisplay     = $statusDisplay
        IsNonstandard     = $isNonstandard
        Title             = $titleStripped
        Affects           = $affectsLine.Trim()
        HasAffects        = ($affectsLine.Trim().Length -gt 0)
        HasCompletionGate = ($content -match '## Completion Gate')
        DependsOn         = $(if ($dependsLine) { $dependsLine -replace '\*\*Depends On:\*\*\s*', '' } else { '' })
        Blocker           = $(if ($blockerLine) { $blockerLine -replace '\*\*Blocker:\*\*\s*', '' } else { '' })
    }
}

$draftFiles = Get-ChildItem -Path $LedgerPath -Filter "*DRAFT*" -File | Select-Object -ExpandProperty Name

$totalOpen       = $records.Count
$totalBlocked    = ($records | Where-Object { $_.StatusFirstWord -eq 'BLOCKED' }).Count
$totalPending    = ($records | Where-Object { $_.StatusFirstWord -eq 'PENDING' }).Count
$totalNonstd     = ($records | Where-Object { $_.IsNonstandard }).Count
$gateFlags       = $records | Where-Object { $_.StatusFirstWord -eq 'OWNER_DONE' -and -not $_.HasCompletionGate }
$affectsFlags    = $records | Where-Object { -not $_.HasAffects }
$grouped         = $records | Group-Object ProjectId | Sort-Object Name

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("# Hub Work Order Status Scan")
[void]$sb.AppendLine("Run: $timestamp | Ledger: $LedgerPath")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("## Summary")
[void]$sb.AppendLine("- Open WOs: $totalOpen across $($grouped.Count) projects")
[void]$sb.AppendLine("- BLOCKED: $totalBlocked | PENDING: $totalPending | NONSTANDARD status text: $totalNonstd")
if ($draftFiles.Count -gt 0) {
    [void]$sb.AppendLine("- FLAG: $($draftFiles.Count) orphaned DRAFT file(s) -- $($draftFiles -join ', ')")
}
if ($gateFlags.Count -gt 0) {
    $ids = ($gateFlags | ForEach-Object { $_.WoId }) -join ', '
    [void]$sb.AppendLine("- FLAG: $($gateFlags.Count) OWNER_DONE WO(s) missing Completion Gate block -- $ids")
}
if ($affectsFlags.Count -gt 0) {
    $ids = ($affectsFlags | ForEach-Object { $_.WoId }) -join ', '
    [void]$sb.AppendLine("- FLAG: $($affectsFlags.Count) open WO(s) missing Affects: -- $ids")
}
if ($totalNonstd -gt 0) {
    [void]$sb.AppendLine("- NOTE: NONSTANDARD-status WOs are shown in full below, not auto-classified. Confirm manually whether each is really still open.")
}
[void]$sb.AppendLine("")

foreach ($g in $grouped) {
    [void]$sb.AppendLine("## $($g.Name)")
    $sorted = $g.Group | Sort-Object PhaseNum, SeqNum
    foreach ($r in $sorted) {
        $marker = switch ($r.StatusFirstWord) {
            'BLOCKED' { ' [BLOCKED]' }
            'PENDING' { ' [PENDING]' }
            default   { '' }
        }
        if ($r.IsNonstandard) { $marker += ' [NONSTANDARD STATUS]' }
        [void]$sb.AppendLine("- **$($r.WoId)**$marker -- $($r.Title)")
        [void]$sb.AppendLine("  - Status: $($r.StatusDisplay)")
        if ($r.Affects) { [void]$sb.AppendLine("  - Affects: $($r.Affects)") }
        if ($r.StatusFirstWord -eq 'BLOCKED') {
            if ($r.DependsOn) { [void]$sb.AppendLine("  - Depends On: $($r.DependsOn)") }
            if ($r.Blocker)   { [void]$sb.AppendLine("  - Blocker: $($r.Blocker)") }
        }
    }
    [void]$sb.AppendLine("")
}

$reportText = $sb.ToString()
[System.IO.File]::WriteAllText($reportFile, $reportText, [System.Text.UTF8Encoding]::new($false))

Write-Output $reportText
Write-Output "---"
Write-Output "Report written to: $reportFile"
