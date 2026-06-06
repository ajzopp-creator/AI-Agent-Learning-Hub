@echo off
REM P_010 Intraday VP Band Check
REM Run anytime after 9:30 AM (2 PM, 3 PM, 4 PM, evening)
REM Uses grid_snapshot_latest.json (created at 9:30 AM)

setlocal enabledelayedexpansion

cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture"

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Set log file
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
set logfile=logs\P_010_Daily_%mydate%.log

REM Run the Python script
echo.
echo ================================================================================
echo P_010 INTRADAY VP BAND CHECK
echo Time: %date% %time%
echo Mode: Validation (uses grid snapshot from 9:30 AM)
echo ================================================================================
echo.

REM Use full path to Python in venv (no activation needed)
"C:\Users\Trader\.conda\envs\p140\python.exe"    

if %errorlevel% equ 0 (
    echo [SUCCESS] Intraday VP band check completed.
    echo Created:
    echo   - intraday_vp_check_YYYYMMDD_HHMMSS.json (in outputs/)
    echo Check logs\*.log and outputs\intraday_vp_check_*.json for results.
    echo Log file: %logfile%
) else (
    echo [ERROR] Intraday check failed with exit code %errorlevel%
    echo Check %logfile% for details.
)

echo.
echo ================================================================================
echo.
