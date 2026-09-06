$root = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\"
Get-ChildItem $root -Recurse -File -Include *.py,*.sql -ErrorAction SilentlyContinue | ForEach-Object {
    $matches = Select-String -Path $_.FullName -Pattern 'systems'
    foreach ($m in $matches) {
        if ($m.Line -match "seed|INSERT|VALUES|OIL|P_116") {
            "$($_.FullName):$($m.LineNumber): $($m.Line.Trim())"
        }
    }
}
