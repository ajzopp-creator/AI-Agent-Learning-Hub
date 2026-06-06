# P_300_05_ingest.ps1
# VERSION: 1.2 (DYNAMIC PROTOCOL)

$env:PYTHONPATH = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"

Write-Host "--- Executing Dynamic Ingestion Pipeline ---"

# PROTOCOL: We do NOT pass --db-path. Python v2.0 will now handle discovery.
& "C:\Users\Trader\.conda\envs\p140\python.exe" "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\ingest\ingest_vp_catalog.py" --type PATTERN_IDENT

if ($LASTEXITCODE -eq 0) {
    Write-Host "--- Ingestion Successful: Target Synced via db_utils ---"
    exit 0
} else {
    Write-Error "--- Ingestion Failed ---"
    exit $LASTEXITCODE
}