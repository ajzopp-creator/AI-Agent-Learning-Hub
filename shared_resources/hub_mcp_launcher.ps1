# =============================================================================
# hub_mcp_launcher.ps1  —  v1.0  —  2026-05-29
# Shared detached-launch helper for all Hub MCP PowerShell wrappers.
#
# PURPOSE
#   The Windows-MCP PowerShell tool has a ~240-second global MCP ceiling.
#   Any Python script that takes longer than that gets killed mid-run.
#   This helper launches a .bat file in a detached hidden window, writes a
#   status file when the job finishes, and polls until done — keeping each
#   individual poll call well inside the 30-second safe window.
#
# USAGE (from a project wrapper script)
#   . "$HUB_ROOT\shared_resources\hub_mcp_launcher.ps1"
#   Invoke-HubBat -BatPath "C:\...\P_010_daily_posture.bat" `
#                 -StatusFile "C:\...\logs\mcp_status_daily.txt" `
#                 -PollSeconds 10 `
#                 -TimeoutMinutes 8
#
# PARAMETERS
#   BatPath        — full path to the .bat file to run
#   StatusFile     — full path to a temp file used for job signalling
#   PollSeconds    — how often (seconds) to check if the job is done (default 10)
#   TimeoutMinutes — how long before giving up and reporting stuck (default 8)
#
# RETURNS (to caller via Write-Output)
#   SUCCESS  — bat exited 0
#   FAILED:N — bat exited non-zero (N = exit code)
#   TIMEOUT  — job did not finish within TimeoutMinutes
# =============================================================================

function Invoke-HubBat {
    param(
        [Parameter(Mandatory)][string]$BatPath,
        [Parameter(Mandatory)][string]$StatusFile,
        [int]$PollSeconds    = 10,
        [int]$TimeoutMinutes = 8
    )

    # --- Pre-flight ---
    if (-not (Test-Path $BatPath)) {
        Write-Output "ERROR: BatPath not found: $BatPath"
        return
    }

    # Remove stale status file from a prior run
    if (Test-Path $StatusFile) { Remove-Item $StatusFile -Force }

    # Wrapper cmd that runs the bat, then writes exit code to the status file.
    # Using cmd.exe /c so the bat's own internal `call` and `exit /b` work correctly.
    $cmd = "cmd.exe"
    $args = @(
        "/c",
        "`"$BatPath`" && echo SUCCESS > `"$StatusFile`" || echo FAILED:%ERRORLEVEL% > `"$StatusFile`""
    )

    # Launch detached — Start-Process returns immediately
    Start-Process -FilePath $cmd -ArgumentList $args -WindowStyle Hidden -ErrorAction Stop

    # --- Poll loop ---
    $deadline = (Get-Date).AddMinutes($TimeoutMinutes)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds $PollSeconds
        if (Test-Path $StatusFile) {
            $result = (Get-Content $StatusFile -Raw).Trim()
            Write-Output $result
            return
        }
        Write-Output "RUNNING — waiting for job to complete..."
    }

    Write-Output "TIMEOUT — job did not finish within $TimeoutMinutes minutes. Check logs manually."
}
