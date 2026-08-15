@echo off
REM P_010 Daily Posture Analyzer V5 + Obsidian Note Writer
REM Run at 9:30 AM to read Grid XLSX files and create P_010_RiskConfig.json
REM V5: Added VXX sentiment overlay + auto-generates Obsidian daily note
REM WO-P010-E1.003 (2026-08-10): halt before STEP 2 if STEP 1 wrote
REM   MORNING_RUN_FAILED.flag -- the note writer must never run against a
REM   failed/stale morning posture read. STEP 3 (market_health) unchanged
REM   in this pass -- see session note on whether it should also skip.

setlocal enabledelayedexpansion

cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture"

if not exist "logs" mkdir logs

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
set logfile=logs\P_010_Daily_%mydate%.log

echo.
echo ================================================================================
echo P_010 DAILY POSTURE ANALYZER V5.0 - 9:30 AM Run
echo Time: %date% %time%
echo ================================================================================
echo.

REM --- STEP 1: Run market posture analysis ---
echo [STEP 1/2] Running market posture analysis...
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\P_010_daily_posture_v5.py" >> "%logfile%" 2>&1

if %errorlevel% equ 0 (
    echo [SUCCESS] Posture analysis complete.
    echo   - grid_snapshot_latest.json updated
    echo   - P_010_RiskConfig.json updated
) else (
    echo [ERROR] Posture analysis failed - exit code %errorlevel%
    echo   Check %logfile% for details.
)

echo.

REM --- Halt check: skip STEP 2 if STEP 1 flagged a failed run ---
if exist "MORNING_RUN_FAILED.flag" (
    echo ================================================================================
    echo [HALT] MORNING_RUN_FAILED.flag present -- skipping STEP 2 (Obsidian note writer^)
    echo   Posture data is FAILED/STALE -- note writer must not run against it.
    echo   See MORNING_RUN_FAILED.flag and %logfile% for details.
    echo   Fix the underlying issue and re-run this batch manually to clear the flag.
    echo ================================================================================
    echo.
    goto :step3
)

REM --- STEP 2: Write Obsidian daily note ---
echo [STEP 2/2] Writing Obsidian daily note...
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\P_010_write_daily_note.py" >> "%logfile%" 2>&1

if %errorlevel% equ 0 (
    echo [SUCCESS] Obsidian note ready in TradingJournal/
) else (
    echo [WARNING] Note writer returned an error - check %logfile%
    echo   Posture data is still valid - this is non-critical.
)

echo.

:step3
REM --- STEP 3: Run market health tracker (distribution days + rally state) ---
echo [STEP 3/3] Running market health tracker...
"C:\Users\Trader\.conda\envs\p140\python.exe" -m market_health.cli >> "%logfile%" 2>&1

if %errorlevel% equ 0 (
    echo [SUCCESS] Market health snapshot written to data/snapshots/market_health/
) else (
    echo [WARNING] Market health runner returned an error - check %logfile%
    echo   Posture data is still valid - this is non-critical.
)

echo.
echo ================================================================================
echo P_010 MORNING RUN COMPLETE - %date% %time%
echo Log: %logfile%
echo ================================================================================
echo.
