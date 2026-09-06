$root = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\"
Get-ChildItem $root -Recurse -File -Include *.py,*.bat -ErrorAction SilentlyContinue | ForEach-Object {
    $matches = Select-String -Path $_.FullName -Pattern 'seed_all|seed_systems|import db_seeder|from.*db_seeder'
    foreach ($m in $matches) {
        "$($_.FullName):$($m.LineNumber): $($m.Line.Trim())"
    }
}
