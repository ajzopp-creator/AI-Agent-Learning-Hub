# hub_git_triage.ps1
# Save to: C:\Users\Trader\AI-Agent-Learning-Hub\hub_git_triage.ps1
# Run from: Anaconda Prompt / PowerShell, from anywhere (it cd's itself)
#
# What this does, in order:
#   1. Backs up .gitignore before touching it
#   2. Adds ignore patterns for unambiguous build-artifact files only
#      (.b64tmp, .done markers, pytest temp dirs) - NOT the run_this_*.py
#      PEH-handoff files, since those are a documented staging pattern,
#      not scratch. You decide on those separately - see the printed list.
#   3. Stages everything, shows you the status, and STOPS for you to read it
#   4. Asks Y/N before committing
#   5. Asks Y/N again before pushing
#   6. Prints final git status so you can confirm clean before cloning to the LG

$hubRoot = "C:\Users\Trader\AI-Agent-Learning-Hub"
Set-Location $hubRoot

Write-Host "`n=== Step 1: Backing up .gitignore ===" -ForegroundColor Cyan
$ts = Get-Date -Format "yyyy-MM-dd_HHmmss"
Copy-Item ".gitignore" ".gitignore.bak_$ts"
Write-Host "Backup written: .gitignore.bak_$ts"

Write-Host "`n=== Step 2: Adding build-artifact ignore patterns ===" -ForegroundColor Cyan
$patternsToAdd = @(
    "",
    "# Added by hub_git_triage.ps1 on $ts",
    "# Build/verification artifacts - not meant to be committed",
    "*.b64tmp",
    "*.py.done",
    "**/_pytest_basetemp*/"
)
Add-Content ".gitignore" -Value $patternsToAdd
Write-Host "Added 3 patterns to .gitignore (.b64tmp, .py.done, _pytest_basetemp dirs)"

Write-Host "`n=== Step 3: Staging everything ===" -ForegroundColor Cyan
git add -A

Write-Host "`n=== Step 4: Current status (READ THIS BEFORE CONTINUING) ===" -ForegroundColor Yellow
git status

Write-Host "`n=== Files still untracked that look like PEH-handoff staging files ===" -ForegroundColor Yellow
Write-Host "These were NOT auto-ignored - decide yourself whether to keep them tracked:"
git status --short | Select-String "run_this_.*\.py$|run_this_.*_context\.txt$|run_this_.*_output\.json$|run_this_.*stdout|run_this_.*stderr"

Write-Host "`n=== Step 5: Ready to commit? ===" -ForegroundColor Cyan
$confirmCommit = Read-Host "Type YES to commit everything currently staged, anything else to stop here"
if ($confirmCommit -ne "YES") {
    Write-Host "Stopped before commit. Nothing was committed. Re-run this script when ready." -ForegroundColor Red
    exit
}

$commitMsg = Read-Host "Enter commit message (or press Enter for a default message)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Pre-clone sync: P_010/P_020/P_115/P_300/P_400 work, new work orders, journal entries as of $ts"
}
git commit -m "$commitMsg"

Write-Host "`n=== Step 6: Ready to push to origin/main? ===" -ForegroundColor Cyan
$confirmPush = Read-Host "Type YES to push now, anything else to stop here (commit is already saved locally either way)"
if ($confirmPush -ne "YES") {
    Write-Host "Stopped before push. Your commit is saved locally but NOT on GitHub yet." -ForegroundColor Red
    Write-Host "Run 'git push' manually when ready." -ForegroundColor Red
    exit
}
git push

Write-Host "`n=== Step 7: Final status - confirm this says clean and up to date ===" -ForegroundColor Cyan
git status

Write-Host "`nDone. If the status above says 'nothing to commit, working tree clean' and 'up to date with origin/main', the LG clone is safe now." -ForegroundColor Green
