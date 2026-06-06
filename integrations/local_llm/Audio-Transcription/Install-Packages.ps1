# LM Studio Transcription Installation Script
# PowerShell version - safe to run in PowerShell

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LM Studio Transcription Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$basePath = "C:\Users\Trader\AI-Agent-Learning-Hub"

# Check if we're in the right location
if (-not (Test-Path $basePath)) {
    Write-Host "Error: AI-Agent-Learning-Hub not found at $basePath" -ForegroundColor Red
    exit 1
}

Set-Location $basePath

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Installing required packages..." -ForegroundColor Yellow
Write-Host "  - openai-whisper (audio transcription)" -ForegroundColor Gray
Write-Host "  - requests (API communication)" -ForegroundColor Gray
Write-Host ""

# Upgrade pip first
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --break-system-packages 2>&1 | Out-Null

# Install packages
Write-Host "Installing openai-whisper..." -ForegroundColor Yellow
python -m pip install openai-whisper --break-system-packages

Write-Host "Installing requests..." -ForegroundColor Yellow  
python -m pip install requests --break-system-packages

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Install FFmpeg: choco install ffmpeg" -ForegroundColor White
Write-Host "2. Open LM Studio" -ForegroundColor White
Write-Host "3. Load your Llama 4 Scout model" -ForegroundColor White
Write-Host "4. Start the server (Local Server tab)" -ForegroundColor White
Write-Host "5. Test: .\TEST_LMSTUDIO.bat" -ForegroundColor White
Write-Host ""

# Check for FFmpeg
Write-Host "Checking for FFmpeg..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg is installed: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ FFmpeg not found. Install with: choco install ffmpeg" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
