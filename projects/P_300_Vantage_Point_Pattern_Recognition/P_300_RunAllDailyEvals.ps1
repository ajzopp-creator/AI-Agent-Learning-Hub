$PROJECT_ROOT = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
$BAT = "$PROJECT_ROOT\P_300_DailyEval_v2.bat"
$LIVE_DIR = "$PROJECT_ROOT\data\live"
$LOG = "$PROJECT_ROOT\P_300_DailyEval_Messages.txt"

"Run started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Set-Content -Path $LOG -Encoding UTF8

$files = Get-ChildItem -Path $LIVE_DIR -Filter "History Grid (*).xlsx" | Sort-Object Name
$total = $files.Count
$i = 0

foreach ($file in $files) {
    $i++
    $symbol = $file.Name -replace "^History Grid \(", "" -replace "\)\.xlsx$", ""
    $header = "[$i / $total] $symbol"
    Write-Host $header -ForegroundColor Cyan
    $header | Add-Content -Path $LOG -Encoding UTF8

    $result = ("`n`n`n" | cmd /c "`"`"$BAT`" $symbol`"") 2>&1
    $result | Add-Content -Path $LOG -Encoding UTF8
    "" | Add-Content -Path $LOG -Encoding UTF8
}

"Run complete: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Add-Content -Path $LOG -Encoding UTF8
Write-Host ""
Write-Host "All $total evaluations complete. Log: $LOG" -ForegroundColor Green
