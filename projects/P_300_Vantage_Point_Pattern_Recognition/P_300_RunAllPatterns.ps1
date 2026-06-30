$PROJECT_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
$BAT = "$PROJECT_ROOT\P_300_AddPattern.bat"
$PATTERN_DIR = "$PROJECT_ROOT\data\historical_patterns"
$LOG = "$PROJECT_ROOT\P_300_AddPattern_Messages.txt"

"Run started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content -Path $LOG -Encoding UTF8

$files = Get-ChildItem -Path $PATTERN_DIR -Filter "*.xlsx" | Sort-Object Name
$total = $files.Count
$i = 0

foreach ($file in $files) {
    $i++
    $header = "[$i / $total] $($file.Name)"
    Write-Host $header -ForegroundColor Cyan
    $header | Add-Content -Path $LOG -Encoding UTF8

    $result = ("`n`n`n" | cmd /c "`"`"$BAT`" `"$($file.FullName)`"`"") 2>&1
    $result | Add-Content -Path $LOG -Encoding UTF8
    "" | Add-Content -Path $LOG -Encoding UTF8
}

"Run complete: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $LOG -Encoding UTF8
Write-Host ""
Write-Host "All $total patterns processed. Log: $LOG" -ForegroundColor Green
