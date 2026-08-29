$path = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\utils\hub_chrome_claude_startup.ps1"
$backup = "C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\utils\hub_chrome_claude_startup.ps1.backup_2026-08-28_1215"
Copy-Item $path $backup -Force

$lines = Get-Content $path

# Line 85 (1-based) -> index 84
$lines[84] = '$activated = $wshell.AppActivate("Claude Code")  # title match -- Windows Terminal owns the window, not the launched powershell.exe PID (confirmed 2026-08-28 live test)'

# Line 97 (1-based) -> index 96
$lines[96] = '$wshell.AppActivate("Claude Code") | Out-Null  # title match, same reason as above'

[System.IO.File]::WriteAllText($path, ($lines -join "`r`n") + "`r`n", [System.Text.UTF8Encoding]::new($false))
Write-Output "Updated lines 85 and 97"
