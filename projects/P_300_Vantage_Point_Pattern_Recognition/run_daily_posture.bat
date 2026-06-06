@echo off
REM P_300 Daily Posture Analyzer
REM Run at 9:30 AM to create grid snapshot + risk_config

setlocal enabledelayedexpansion

cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Set log file with timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
set logfile=logs\P_300_Daily_%mydate%.log

REM Run the Python script
echo.
echo ================================================================================
echo P_300 DAILY POSTURE ANALYZER - 9:30 AM Run
echo Time: %date% %time%
echo Mode: FRESH (creates grid snapshot + risk_config)
echo ================================================================================
echo.

REM Use full path to Python in venv (no activation needed)
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\P_300_Posture_v2.6.py" live >> "%logfile%" 2>&1

if %errorlevel% equ 0 (
    echo [SUCCESS] Daily posture analysis completed.
    echo Created:
    echo   - grid_snapshot_latest.json (root)
    echo   - risk_config.json (root)
    echo   - Backups in outputs/
    echo Check logs\*.log for details.
    echo Log file: %logfile%
) else (
    echo [ERROR] Posture analysis failed with exit code %errorlevel%
    echo Check %logfile% for details.
)

echo.
echo ================================================================================
echo.
