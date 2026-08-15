"""
P_010 Toast Notification -- BurntToast (WinRT toast, modern)
WO-P010-E1.003. Fires a real Windows 10/11 toast notification from
unattended Python code (Task Scheduler, Guardian bat) -- no live Claude
Desktop / MCP session required.

REVISION HISTORY:
v1 (2026-08-10, original) used System.Windows.Forms.NotifyIcon.ShowBalloonTip
with no new dependency. CONFIRMED BROKEN by live test same day -- the
PowerShell call returns success, but NotifyIcon requires an active Windows
message loop (Application.Run / Application.DoEvents) to actually render the
balloon. A bare console script has no message loop, so the balloon silently
never displays. Nothing about that failure is visible to any automated
check (exit code, Test-Path, log output) -- only confirmed by Tony watching
the screen and seeing nothing.

v2 (2026-08-10) switched to BurntToast (New-BurntToastNotification) -- a real
WinRT toast, no message-loop requirement. Installed once via:
  Install-Module -Name BurntToast -Scope CurrentUser -Force -AllowClobber
(user-scope, no admin rights needed). Module lands under the user Documents
PSModulePath (here: D:\\OneDrive\\Documents\\WindowsPowerShell\\Modules).

v2.1 (2026-08-10, same day): live PEH check returned True with no visible
toast. Root cause was NOT the toast API -- BurntToast was never actually
installed on this machine, and powershell.exe -Command still exits 0 after
a terminating Import-Module error. send_toast() therefore lied. Fix:
  1. Install BurntToast (done once on this host).
  2. Force a non-zero process exit on any failure via try/catch + exit 1,
     and treat non-empty stderr as failure even if exit code is wrong.

windows-mcp:Notification is still NOT used here: that tool only fires while
Claude Desktop has a live MCP session open and Claude is the one making the
call. The 9:30 AM Task Scheduler run and Guardian's unattended checks have
no Claude session driving them, so that tool is unreachable from this
context regardless of which underlying toast mechanism is used.
"""

import subprocess

# try/catch + explicit exit 1 is required: powershell -Command often returns
# exit code 0 even after a terminating error from -ErrorAction Stop.
_POWERSHELL_TEMPLATE = r"""
$ErrorActionPreference = 'Stop'
try {{
    Import-Module BurntToast -ErrorAction Stop
    New-BurntToastNotification -Text "{title}", "{message}"
    exit 0
}} catch {{
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}}
"""


def send_toast(title: str, message: str) -> bool:
    """
    Fire a Windows toast notification via BurntToast. Returns True only if
    PowerShell exits 0 with empty stderr. Never raises -- a failed toast
    must not crash the morning-run failure path that calls this.
    """
    # Escape double-quotes so they don't break the embedded PowerShell string
    safe_title = title.replace('"', "'")
    safe_message = message.replace('"', "'")
    script = _POWERSHELL_TEMPLATE.format(title=safe_title, message=safe_message)

    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode != 0:
            return False
        # Belt-and-suspenders: some PS hosts still exit 0 after a failed
        # Import-Module; non-empty stderr is treated as failure.
        if (result.stderr or "").strip():
            return False
        return True
    except Exception:
        return False


if __name__ == "__main__":
    # Manual test: python toast_notify.py
    ok = send_toast("P_010 Test", "Toast notification working.")
    print("Toast sent OK" if ok else "Toast send FAILED")
