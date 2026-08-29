# =============================================================================
# hub_chrome_claude_startup.ps1  â€”  v1.0  â€”  2026-08-28
# Hub-wide shared infrastructure (ref WO-P000-E16.001, owned by P_000).
#
# PURPOSE
#   Launches Chrome (if not already running) and a claude --chrome session
#   scoped to a target project, then automates /login and /chrome so nothing
#   manual is needed at morning startup.
#
# USAGE
#   One-time install (creates the Windows sign-in shortcut):
#     powershell -File hub_chrome_claude_startup.ps1 -InstallStartupShortcut
#   Normal run (this is what the shortcut calls automatically at sign-in):
#     powershell -File hub_chrome_claude_startup.ps1 [-TargetProject "C:\...\P_115..."]
#
# PARAMETERS
#   TargetProject             â€” working directory claude --chrome opens in.
#                                Default: Hub root (P_000's own context, per
#                                Tony's 2026-08-10 decision -- no project
#                                bias in shared infra).
#   ClaudeStartupDelaySeconds â€” wait after launch before sending /login.
#                                Tune this if /login fires before Claude Code
#                                has finished starting up.
#   CommandDelaySeconds       â€” wait between /login and /chrome.
#   InstallStartupShortcut    â€” switch. Creates the shell:startup .lnk and
#                                exits; does not launch anything itself.
#
# KNOWN RISK (ref WO-P000-E16.001 primary technical risk)
#   Slash commands are interactive-mode only in Claude Code -- there is no
#   scripted-stdin path for /login or /chrome (confirmed against Anthropic's
#   own documentation and issue tracker, 2026-08-28). This script drives them
#   via WScript.Shell SendKeys against the launched window instead, which is
#   timing-dependent by nature. If commands fire before Claude Code is ready,
#   raise ClaudeStartupDelaySeconds. Expect a tuning pass on Tony's own
#   machine before this is fully reliable -- not a guaranteed one-shot fix.
# =============================================================================

param(
    [string]$TargetProject             = "C:\Users\Trader\AI-Agent-Learning-Hub",
    [int]$ClaudeStartupDelaySeconds    = 12,
    [int]$CommandDelaySeconds          = 3,
    [switch]$InstallStartupShortcut
)

# --- Install mode: create the shell:startup shortcut and stop ---
if ($InstallStartupShortcut) {
    $startupDir = [Environment]::GetFolderPath("Startup")
    $lnkPath    = Join-Path $startupDir "hub_chrome_claude_startup.lnk"
    $wshInstall = New-Object -ComObject WScript.Shell
    $shortcut   = $wshInstall.CreateShortcut($lnkPath)
    $shortcut.TargetPath       = "powershell.exe"
    $shortcut.Arguments        = "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $shortcut.WorkingDirectory = Split-Path $PSCommandPath -Parent
    $shortcut.WindowStyle      = 1
    $shortcut.Save()
    Write-Output "Startup shortcut installed: $lnkPath"
    return
}

# --- Chrome: launch only if not already running ---
if (-not (Get-Process -Name "chrome" -ErrorAction SilentlyContinue)) {
    Start-Process "chrome.exe"
    Write-Output "Chrome launched."
} else {
    Write-Output "Chrome already running -- skipped launch."
}

# --- claude --chrome, scoped to TargetProject, in a visible terminal window ---
if (-not (Test-Path $TargetProject)) {
    Write-Output "ERROR: TargetProject not found: $TargetProject"
    return
}

$claudeProc = Start-Process -FilePath "powershell.exe" `
    -ArgumentList @("-NoExit", "-Command", "claude --chrome") `
    -WorkingDirectory $TargetProject `
    -PassThru

Write-Output "claude --chrome launching (PID $($claudeProc.Id)) in: $TargetProject"

# --- Wait for Claude Code to be ready, then automate /login and /chrome ---
Start-Sleep -Seconds $ClaudeStartupDelaySeconds

$wshell    = New-Object -ComObject WScript.Shell
$activated = $wshell.AppActivate("Claude Code")  # title match -- Windows Terminal owns the window, not the launched powershell.exe PID (confirmed 2026-08-28 live test)
if (-not $activated) {
    Write-Output "WARNING: could not focus claude --chrome window -- /login and /chrome were not sent. Run them manually."
    return
}

$wshell.SendKeys("/login")
Start-Sleep -Milliseconds 400
$wshell.SendKeys("{ENTER}")

Start-Sleep -Seconds $CommandDelaySeconds

$wshell.AppActivate("Claude Code") | Out-Null  # title match, same reason as above
$wshell.SendKeys("/chrome")
Start-Sleep -Milliseconds 400
$wshell.SendKeys("{ENTER}")

Write-Output "Startup sequence complete -- /login and /chrome sent."
