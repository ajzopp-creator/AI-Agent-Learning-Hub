Set-Location "C:\Users\Trader\AI-Agent-Learning-Hub" 
Write-Host "" 
Write-Host "  ==========================================" -ForegroundColor Cyan 
Write-Host "     AJZ Strategies - AI-Agent-Learning-Hub" -ForegroundColor Cyan 
Write-Host "  ==========================================" -ForegroundColor Cyan 
Write-Host "" 
Write-Host "  Projects:" -ForegroundColor Yellow 
Get-ChildItem "C:\Users\Trader\AI-Agent-Learning-Hub\projects" -Directory | ForEach-Object { Write-Host "    $_" -ForegroundColor White } 
Write-Host "" 
Write-Host "  Integrations:" -ForegroundColor Yellow 
Get-ChildItem "C:\Users\Trader\AI-Agent-Learning-Hub\integrations" -Directory | ForEach-Object { Write-Host "    $_" -ForegroundColor White } 
Write-Host "" 
Write-Host "  Python: C:\Users\Trader\.conda\envs\p140\python.exe" -ForegroundColor Green 
Write-Host "" 
