# Logging-enabled MCP filesystem server launcher
$LogDir = "C:\Users\Trader\AI-Agent-Learning-Hub\integrations\mcp_servers\logs"
$LogFile = Join-Path $LogDir "mcp_fs_server_$(Get-Date -Format 'yyyy-MM-dd').log"

# Ensure log directory exists
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

# Write startup header
"==== MCP Filesystem Server Startup $(Get-Date) ====" | Out-File -FilePath $LogFile -Append

# Path to Python environment
$Python = "C:\Users\Trader\.conda\envs\p140\python.exe"

# Command to run the MCP server
$Cmd = "`"$Python`" -m mcp_server_filesystem --root C:/ >> `"$LogFile`" 2>&1"

# Use cmd.exe to avoid PowerShell redirect bug
Start-Process -FilePath "cmd.exe" -ArgumentList "/c $Cmd" -WindowStyle Hidden
