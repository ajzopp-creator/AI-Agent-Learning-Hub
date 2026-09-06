$hub = "C:\Users\Trader\AI-Agent-Learning-Hub\"
Get-ChildItem $hub -Recurse -File -Include *.md,*.txt,*.csv,*.log -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.FullName -notmatch '\\tests\\|test_') {
        $matches = Select-String -Path $_.FullName -Pattern '\[OIL\]'
        foreach ($m in $matches) {
            "$($_.FullName):$($m.LineNumber): $($m.Line.Trim())"
        }
    }
}
