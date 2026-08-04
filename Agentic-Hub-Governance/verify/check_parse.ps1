$e = $null
$t = $null
[System.Management.Automation.Language.Parser]::ParseFile('C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\P_020_WeeklyUpdate_mcp.ps1', [ref]$t, [ref]$e) | Out-Null
if ($e) {
    $e | ForEach-Object { Write-Output "$($_.Message) at line $($_.Extent.StartLineNumber) col $($_.Extent.StartColumnNumber)" }
} else {
    Write-Output "NO PARSE ERRORS"
}
