$ProjectDir = "C:\Users\Trader\AI-Agent-Learning-Hub\projects"

# Find the latest file matching the pattern
$LatestDB = Get-ChildItem -Path $ProjectDir -Filter "*geminicatalog.db" -Recurse | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 1

if ($null -eq $LatestDB) {
    Write-Host "CRITICAL: No catalog database found in $ProjectDir" -ForegroundColor Red
    $manualPath = Read-Host "Please enter the full path to your catalog database"
    if (Test-Path $manualPath) {
        $DBPath = $manualPath
    } else {
        Write-Host "Invalid path. Exiting." -ForegroundColor Red
        return
    }
} else {
    $DBPath = $LatestDB.FullName
    Write-Host "Dynamic Resolver: Using latest catalog -> $($LatestDB.Name)" -ForegroundColor Green
}

# Return the path for use in other scripts
return $DBPath