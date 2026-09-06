$root = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\"
Get-ChildItem $root -Recurse -File -Include *.py -ErrorAction SilentlyContinue | ForEach-Object {
    $matches = Select-String -Path $_.FullName -Pattern 'VALID_SYSTEMS\s*='
    foreach ($m in $matches) {
        "$($_.FullName):$($m.LineNumber): $($m.Line.Trim())"
    }
}
Select-String -Path "$root\python\database\infrastructure\db_seeder.py" -Pattern '"P_105"|"P_110"|"P_120"|"P_210"'
