$path = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P000-E16.001.md"
$backup = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P000-E16.001.md.backup_2026-08-28_1220"
Copy-Item $path $backup -Force

$lines = Get-Content $path

# --- Header field updates (0-based indices) ---
$lines[1] = '**Status:** OWNER_DONE -- built and verified live 2026-08-28. See RESOLUTION section below.'
$lines[5] = "**Verified:** 2026-08-28, live end-to-end test on Tony's machine -- see RESOLUTION."

# --- RESOLUTION block as a literal here-string (avoids quote-escaping problems entirely) ---
$resolutionText = @'
--------------------------------------------------------------------------------
RESOLUTION (2026-08-28)
--------------------------------------------------------------------------------
Built: Agentic-Hub-Governance\utils\hub_chrome_claude_startup.ps1 (102 lines).
Params: TargetProject (default Hub root), ClaudeStartupDelaySeconds (default 12),
CommandDelaySeconds (default 3), InstallStartupShortcut (switch).

Chrome check-before-launch added per Tony's request during build (Get-Process
guard, only launches if not already running -- Chrome itself is single-instance
safe regardless, this just avoids an unnecessary extra window).

PRIMARY RISK RESOLVED: slash commands are interactive-mode only in Claude Code
(confirmed against Anthropic's own docs/issue tracker) -- no scripted-stdin path
exists. Built via WScript.Shell SendKeys against the launched window instead.

ITERATION DURING LIVE TEST: first live run failed -- AppActivate(processId)
could not find a window, because Windows Terminal (not the launched
powershell.exe child process) owns the top-level window. Fixed by switching
to AppActivate title-matching on "Claude Code" instead of matching by process
ID, which is stable regardless of which process actually owns the window.
Re-test succeeded -- both /login and /chrome fired without the activation
warning.

SECOND FINDING (accepted, not fixed): /login opens an interactive OAuth
sub-prompt ("Paste code here if prompted") when a fresh login is actually
needed, rather than returning immediately to the normal prompt. On those
days, /chrome sent on the fixed delay can land as literal text in that box
instead of firing as a command. Confirmed live: /chrome had to be re-sent
manually after Tony completed sign-in. Decided with Tony not to add
state-detection complexity for this -- most days the session is already
authenticated (confirmed in the same test round: /login was a clean no-op
when already signed in), and the failure mode is harmless (stray text in a
code box, cleared with Esc) rather than damaging.

Also confirmed: /login opens the OAuth URL in the OS default browser (Edge
on this machine), not the Chrome window this script launches -- expected,
not a bug. Actual credential entry stays manual either way, which is
correct and not something this script should automate.

FULL VERIFICATION, in order, same live session:
1. -InstallStartupShortcut: shell:startup .lnk created, target/args/workdir
   confirmed correct via WScript.Shell inspection.
2. Chrome-not-running -> full run: Chrome launched, claude --chrome launched
   scoped to Hub root, title-match activation succeeded, /login fired and
   returned "Login successful" (session was already authenticated from a
   prior run at this point).
3. Second full run after Tony force-closed Chrome (fresh-login scenario):
   AppActivate + /login fired correctly, opened OAuth sub-prompt as
   described above; Tony completed sign-in manually; /chrome then sent
   manually to confirm the connection path -- returned "Status: Enabled,
   Extension: Installed, Enabled by default: Yes".

Independent Review note: this script is 102 lines, over the ~50-line
precedent this WO's own NEXT STEP section cites for skipping Independent
Review. Not skipping it on that basis -- flagging explicitly rather than
silently claiming the exemption still applies.

--------------------------------------------------------------------------------
## Completion Gate (ref WO-P000-E3.001)
--------------------------------------------------------------------------------
[x] All file paths use Hub canonical paths -- Agentic-Hub-Governance\utils\
    (existing folder, per this WO's own RESOLVED Location decision)
[x] New/changed shared-resource location reflected: this WO is the record;
    no P_000_SYSTEM_DOCUMENTATION.md Document Index entry needed (utils\ is
    already a known canonical path, not a new one); no project CLAUDE.md or
    skill file references this script yet, so none to update
[x] CALLER PROPAGATION: N/A -- this is a new standalone entry point (the
    shell:startup shortcut), not a change to an existing shared function
    with other callers to check
[x] IMPERATIVE SWEEP: N/A -- no existing rule/Must/anti-pattern changed
[x] Downstream projects in Affects notified -- Affects is Hub-wide/all
    projects but shared infra with no project-specific logic touched;
    documented here, Tony present for the entire live test
[x] No sys.path side-channels introduced -- N/A, PowerShell not Python
[x] No schema/signal contract changed -- N/A
[x] DRAFT files cleanup / one ledger entry confirmed -- no DRAFT files for
    this WO
[ ] Independent Review -- NOT YET DONE. Flagged above: script exceeds the
    ~50-line no-review precedent this WO cited, so Independent Review in a
    separate session is recommended before treating this as fully closed,
    even though OWNER_DONE is appropriate now that build + live
    verification are complete.
'@

$resolutionBlock = $resolutionText -split "`r?`n"

$before = $lines[0..91]
$after  = $lines[92..($lines.Count-1)]
$final = $before + $resolutionBlock + $after
[System.IO.File]::WriteAllText($path, ($final -join "`r`n") + "`r`n", [System.Text.UTF8Encoding]::new($false))
Write-Output "Inserted. Before=$($before.Count) Block=$($resolutionBlock.Count) After=$($after.Count)"
