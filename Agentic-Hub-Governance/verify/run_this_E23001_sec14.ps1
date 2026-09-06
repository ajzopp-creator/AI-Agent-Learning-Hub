$path = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\docs\P_000_SYSTEM_DOCUMENTATION.md"
$lines = Get-Content $path
$start = ($lines | Select-String -Pattern '1\.4' | Select-Object -First 1).LineNumber
$verLine = ($lines | Select-String -Pattern '^\*\*Version' | Select-Object -First 1)
"Section 1.4 header at line: $start"
"Version line: $verLine"
$lines[($start-1)..($start+40)]
