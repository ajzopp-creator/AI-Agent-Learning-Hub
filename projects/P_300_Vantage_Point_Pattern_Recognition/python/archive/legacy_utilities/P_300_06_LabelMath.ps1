# P_300_06_LabelMath.ps1
Write-Host "--- Executing Confidence Math Engine ---"
& "C:\Users\Trader\.conda\envs\p140\python.exe" "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\labeling\label_outcomes.py"

$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "--- Math Engine successful ---"
    exit 0
} else {
    Write-Error "--- Math Engine failed with exit code $exitCode ---"
    exit $exitCode
}