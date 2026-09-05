# Launcher: runs P_400 Tier-1 screen-all against the current signal inbox.
# Output goes to the console as normal AND to a fixed log file Claude reads directly.
Set-Location 'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python'
$env:PYTHONPATH = 'C:\Users\Trader\AI-Agent-Learning-Hub'
$logPath = 'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\audit_logs\P_400_ScreenAll_last_output.txt'
& 'C:\Users\Trader\.conda\envs\p140\python.exe' cli.py screen-all 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath $logPath