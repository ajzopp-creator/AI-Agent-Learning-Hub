# =============================================================================
# hub_mcp_launcher.ps1  --  v1.2  --  2026-09-08
# Shared detached-launch helper for all Hub MCP PowerShell wrappers.
#
# PURPOSE
#   The Windows-MCP PowerShell tool has a ~240-second global MCP ceiling.
#   Any Python script that takes longer than that gets killed mid-run.
#   This helper launches a .bat file in a detached hidden window, writes a
#   status file when the job finishes, and polls until done -- keeping each
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
#   BatPath        -- full path to the .bat file to run
#   StatusFile     -- full path to a temp file used for job signalling
#   PollSeconds    -- how often (seconds) to check if the job is done (default 10)
#   TimeoutMinutes -- how long before giving up and reporting stuck (default 8)
#
# RETURNS (to caller via Write-Output)
#   SUCCESS  -- bat exited 0
#   FAILED:N -- bat exited non-zero (N = exit code)
#   TIMEOUT  -- job did not finish within TimeoutMinutes
#
# v1.2 CHANGE (ref EC-009) -- this file's only non-ASCII character (an
# em-dash, U+2014, used throughout this header) silently broke every
# caller that dot-sources it via a nested "powershell -File wrapper.ps1"
# invocation (as opposed to running inline in the same process): Windows
# PowerShell 5.1 has no BOM to go on and falls back to the OEM codepage
# for a nested nested child process, misreads the em-dash, and the parser
# loses track of brace matching -- "Missing closing '}' in statement
# block" at the function definition, Invoke-HubBat never gets defined,
# and the CommandNotFoundException that follows was uncaught in every
# caller, so $result stayed silently blank/unset instead of ever showing
# FAILED or TIMEOUT. Confirmed 100% reproducible via nested -File
# invocation, 0% via inline execution -- not a race. Fix: replaced every
# em-dash in this file with "--" (file is now pure ASCII, matches the
# rest of the Hub's convention). Callers (P_010 daily/intraday, P_020
# weekly, P_400 batch2b, P_805 daily pipeline) also got a defensive
# retry-and-verify guard right after their dot-source line, and now exit
# with an explicit FATAL message instead of silently continuing if
# Invoke-HubBat still isn't defined after one retry -- belt and
# suspenders, since the same nested-invocation exposure could resurface
# if a future edit reintroduces a non-ASCII character here.
#
# v1.1 CHANGE (ref WO-P000-E18.001) -- status file was never written on
# either branch. Invoke-HubBat launched cmd.exe /c with an inline
# "<bat>" && echo SUCCESS > "<status>" || echo FAILED:%ERRORLEVEL% > "<status>"
# string. cmd /c only preserves outer quoting under a narrow condition
# (exactly two quote chars, nothing special between them, quoted text is an
# executable name). That line has six quote chars, so cmd.exe fell back to
# stripping only the first and last quote of the whole line -- corrupting the
# inner quoting and silently breaking the && / || chain. Neither branch fired
# on success or failure, on any wrapper, since v1.0. Fix: generate a small
# one-off .cmd launcher per call that checks %ERRORLEVEL% with normal batch
# logic instead of shell chaining, and pass BatPath/StatusFile to it as plain
# Start-Process arguments (no inline quoting-heavy one-liner).
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

    # Generate a one-off .cmd launcher next to the status file. This avoids
    # the cmd.exe /c multi-quote parsing failure described above (ref
    # WO-P000-E18.001) -- internal batch errorlevel logic instead of an
    # inline && / || chain.
    $launcherCmd = Join-Path (Split-Path $StatusFile -Parent) `
        "_launcher_$([System.IO.Path]::GetFileNameWithoutExtension($StatusFile)).cmd"
    if (Test-Path $launcherCmd) { Remove-Item $launcherCmd -Force }

    $launcherBody = "@echo off`r`ncall `"%~1`"`r`nif errorlevel 1 (`r`n    echo FAILED:%errorlevel% > `"%~2`"`r`n) else (`r`n    echo SUCCESS > `"%~2`"`r`n)`r`n"
    [System.IO.File]::WriteAllText($launcherCmd, $launcherBody, [System.Text.UTF8Encoding]::new($false))

    # Launch detached -- Start-Process returns immediately. BatPath and
    # StatusFile are passed as separate ArgumentList elements so PowerShell
    # quotes each one correctly -- no manual quote embedding.
    Start-Process -FilePath $launcherCmd -ArgumentList @($BatPath, $StatusFile) -WindowStyle Hidden -ErrorAction Stop

    # --- Poll loop ---
    $deadline = (Get-Date).AddMinutes($TimeoutMinutes)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds $PollSeconds
        if (Test-Path $StatusFile) {
            $result = (Get-Content $StatusFile -Raw).Trim()
            Write-Output $result
            return
        }
        Write-Output "RUNNING -- waiting for job to complete..."
    }

    Write-Output "TIMEOUT -- job did not finish within $TimeoutMinutes minutes. Check logs manually."
}
