@echo off
setlocal enabledelayedexpansion

REM ========================================================================
REM P_020 Full Workflow - SIMPLIFIED VERSION
REM ========================================================================
REM This version has better error handling and debugging output
REM ========================================================================

echo.
echo ========================================================================
echo   P_020 FULL WORKFLOW - SIMPLIFIED VERSION
echo ========================================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM ========================================================================
REM Determine Account Type
REM ========================================================================

set "ACCOUNT_TYPE=Live"
set "FILE_PREFIX=P_020"

if /I "%~1"=="Paper" (
    set "ACCOUNT_TYPE=Paper"
    set "FILE_PREFIX=D_020"
)

echo Account Type: %ACCOUNT_TYPE%
echo File Prefix:  %FILE_PREFIX%
echo.

REM ========================================================================
REM Set Folder Paths
REM ========================================================================

if /I "%ACCOUNT_TYPE%"=="Paper" (
    set "TOS_FOLDER=%SCRIPT_DIR%data\tos_exports\paper"
) else (
    set "TOS_FOLDER=D:\OneDrive\Documents\AJZStrategiesLLC\2026_Operations"
)

echo Looking in: %TOS_FOLDER%
echo.

REM Check if folder exists
if not exist "%TOS_FOLDER%" (
    echo ERROR: Folder does not exist: %TOS_FOLDER%
    echo.
    echo Please create this folder first!
    pause
    exit /b 1
)

REM ========================================================================
REM Find TOS Export File
REM ========================================================================

echo Searching for TOS export files...
echo.
echo Files found in folder:
dir /b "%TOS_FOLDER%\%FILE_PREFIX%*.csv" 2>nul
echo.

REM Find the most recent AccountStatement file (exclude _IMPORT files)
set "LATEST_FILE="
set "LATEST_TIME=0"

for %%f in ("%TOS_FOLDER%\%FILE_PREFIX%*AccountStatement*.csv") do (
    set "FILENAME=%%~nxf"
    echo Checking: !FILENAME!
    
    REM Check if filename contains _IMPORT
    echo !FILENAME! | findstr /I "_IMPORT" >nul
    if errorlevel 1 (
        REM Does NOT contain _IMPORT - this is good!
        set "LATEST_FILE=%%f"
        echo   ^-^> This is a TOS export file! Will use this one.
    ) else (
        echo   ^-^> Contains _IMPORT, skipping (this is parser output)
    )
)

echo.

REM Check if we found a file
if not defined LATEST_FILE (
    echo ========================================================================
    echo ERROR: No TOS export file found!
    echo ========================================================================
    echo.
    echo Looking for: %FILE_PREFIX%*AccountStatement*.csv
    echo In folder:   %TOS_FOLDER%
    echo Excluding:   *_IMPORT.csv files
    echo.
    echo What you need:
    if "%ACCOUNT_TYPE%"=="Paper" (
        echo   File like: D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
    ) else (
        echo   File like: P_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
    )
    echo.
    echo Files with _IMPORT in name are PARSER OUTPUT, not TOS exports!
    echo.
    echo Steps to fix:
    echo   1. Export from ThinkorSwim
    echo   2. Save to: %TOS_FOLDER%
    echo   3. Make sure filename does NOT have _IMPORT in it
    echo   4. Run this batch file again
    echo.
    pause
    exit /b 1
)

echo Found TOS export: %LATEST_FILE%
echo.

REM ========================================================================
REM STEP 1: Run Parser
REM ========================================================================

echo.
echo ========================================================================
echo [STEP 1/2] Running TOS Parser
echo ========================================================================
echo.
echo Parser input: %LATEST_FILE%
echo.

cd /d "%SCRIPT_DIR%python\parsers"

"C:\Users\Trader\.conda\envs\p140\python.exe" P_020_TOS_Parser_v2.py "%LATEST_FILE%"

if errorlevel 1 (
    echo.
    echo ========================================================================
    echo ERROR: Parser failed!
    echo ========================================================================
    echo.
    echo The parser encountered an error. Common issues:
    echo   - CSV file is not a TOS export (might be parser output)
    echo   - File is corrupted or empty
    echo   - TOS export format changed
    echo.
    echo Check the error messages above for details.
    echo.
    cd /d "%SCRIPT_DIR%"
    pause
    exit /b 1
)

echo.
echo Parser completed successfully!
echo.

cd /d "%SCRIPT_DIR%"

REM ========================================================================
REM STEP 2: Run Import Script
REM ========================================================================

echo.
echo ========================================================================
echo [STEP 2/2] Running Import Script
echo ========================================================================
echo.
echo This will import the parsed data to Excel and auto-match System names.
echo.

cd /d "%SCRIPT_DIR%python\parsers"

"C:\Users\Trader\.conda\envs\p140\python.exe" P_020_Trade_Import_Enhanced.py

if errorlevel 1 (
    echo.
    echo WARNING: Import script had errors. Check messages above.
    echo.
)

cd /d "%SCRIPT_DIR%"

REM ========================================================================
REM Complete
REM ========================================================================

echo.
echo ========================================================================
echo WORKFLOW COMPLETE!
echo ========================================================================
echo.
echo Processed: %ACCOUNT_TYPE% account
echo File: %LATEST_FILE%
echo.
echo Next steps:
echo   1. Open your Excel logs to verify import
echo   2. Check System names were matched correctly
echo   3. Verify formulas are calculating
echo.

pause


