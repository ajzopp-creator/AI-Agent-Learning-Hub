Write-Host "--- Starting P_300 Daily Pattern Analysis ---"

$basePath = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities"

# Step 1: Ingest
Write-Host "Executing P_300_05_ingest.ps1..."
& "$basePath\P_300_05_ingest.ps1"
if ($LASTEXITCODE -ne 0) { Write-Error "CRITICAL FAILURE: Ingestion step failed. Pipeline stopped."; exit $LASTEXITCODE }

# Step 2: Confidence Math Engine (NEW)
Write-Host "Executing P_300_06_LabelMath.ps1..."
& "$basePath\P_300_06_LabelMath.ps1"
if ($LASTEXITCODE -ne 0) { Write-Error "CRITICAL FAILURE: Math Engine failed. Pipeline stopped."; exit $LASTEXITCODE }

# Step 3: Archive
Write-Host "Executing P_300_10_ArchiveCSV.ps1..."
& "$basePath\P_300_10_ArchiveCSV.ps1"
if ($LASTEXITCODE -ne 0) { Write-Error "CRITICAL FAILURE: Archiving failed. Pipeline stopped."; exit $LASTEXITCODE }

# Step 4: Match
Write-Host "Executing P_300_20_PatternMatch.ps1..."
& "$basePath\P_300_20_PatternMatch.ps1"
if ($LASTEXITCODE -ne 0) { Write-Error "CRITICAL FAILURE: Matching failed. Pipeline stopped."; exit $LASTEXITCODE }

# Step 5: Report
Write-Host "Executing P_300_50_ConReport.ps1..."
& "$basePath\P_300_50_ConReport.ps1"
if ($LASTEXITCODE -ne 0) { Write-Error "CRITICAL FAILURE: Reporting failed. Pipeline stopped."; exit $LASTEXITCODE }

Write-Host "--- Workflow Complete ---"