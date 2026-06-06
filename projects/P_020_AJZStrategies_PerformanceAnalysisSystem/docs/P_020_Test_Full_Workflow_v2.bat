@echo off
REM ========================================================================
REM P_020 Full Workflow - TEST VERSION
REM ========================================================================
REM This batch file runs the complete P_020 workflow:
REM   1. Auto-detects latest TOS CSV file (Paper or Live)
REM   2. Parses TOS account statement CSV
REM   3. Imports parsed data to Excel logs (with auto-matching)
REM
REM Usage:
REM   P_020_Test_Full_Workflow.bat Paper    (for paper account - uses D_020)
REM   P_020_Test_Full_Workflow.bat          (for live account - uses P_020)
REM   P_020_Test_Full_Workflow.bat Live     (for live account - uses P_020)
REM
REM The script automatically finds the most recent CSV file!
REM
REM Note: This is for TESTING ONLY. After testing complete, will be merged
REM       into single production batch file.
REM
REM Author: Anthony (AJZ Strategies LLC)
REM Version: 2.2 (Test)
REM Date: 2026-02-07
REM ========================================================================

echo.
echo ========================================================================
echo   P_020 FULL WORKFLOW - TEST VERSION
echo ========================================================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Determine account type (Paper or Live)
set ACCOUNT_TYPE=Live
set FILE_PREFIX=P_020
set TOS_FOLDER=D:\OneDrive\Documents\AJZStrategiesLLC\2026_Operations

if /I "%~1"=="Paper" (
    set ACCOUNT_TYPE=Paper
    set FILE_PREFIX=D_020
    set TOS_FOLDER=%SCRIPT_DIR%data\tos_exports\paper
)

echo Account Type: %ACCOUNT_TYPE%
echo File Prefix:  %FILE_PREFIX%
echo Looking in:   %TOS_FOLDER%
echo.

REM Find latest CSV file matching prefix (exclude parser output files!)
echo Searching for latest %FILE_PREFIX%*AccountStatement*.csv file...
set LATEST_FILE=
for /f "delims=" %%a in ('dir /b /od "%TOS_FOLDER%\%FILE_PREFIX%*AccountStatement*.csv" 2^>nul ^| findstr /V /I "_IMPORT"') do set LATEST_FILE=%%a

if "%LATEST_FILE%"=="" (
    echo.
    echo ERROR: No %FILE_PREFIX% TOS export files found in:
    echo   %TOS_FOLDER%
    echo.
    echo Looking for: %FILE_PREFIX%*AccountStatement*.csv
    echo Excluding: *_IMPORT.csv (parser output files)
    echo.
    echo Please export from ThinkorSwim and save to the folder above!
    echo.
    echo Example TOS export filename:
    if "%ACCOUNT_TYPE%"=="Paper" (
        echo   D_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
    ) else (
        echo   P_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
    )
    echo.
    echo NOTE: If you see *_IMPORT.csv files, those are PARSER OUTPUT,
    echo       not TOS exports. The parser cannot parse its own output!
    echo.
    pause
    exit /b 1
)

set CSV_PATH=%TOS_FOLDER%\%LATEST_FILE%

echo.
echo Found latest file: %LATEST_FILE%
echo Full path: %CSV_PATH%
echo.

REM ========================================================================
REM STEP 1: Run TOS Parser
REM ========================================================================

echo.
echo [STEP 1/2] Running TOS Parser...
echo ========================================================================
echo.

REM Navigate to parser directory
cd /d "%SCRIPT_DIR%python\parsers"

REM Run parser
python P_020_TOS_Parser_v2.py "%CSV_PATH%"

if errorlevel 1 (
    echo.
    echo ERROR: Parser failed! Check error messages above.
    echo.
    cd /d "%SCRIPT_DIR%"
    pause
    exit /b 1
)

echo.
echo Parser completed successfully!
echo.

REM ========================================================================
REM STEP 2: Run Import Script (with auto-matching)
REM ========================================================================

echo.
echo [STEP 2/2] Running Import Script...
echo ========================================================================
echo.
echo This will:
echo   - Import parsed CSV data to Excel logs
echo   - Auto-match System names from Tracker Dashboard
echo   - Preserve formulas in calculated columns
echo.
echo Account Type: %ACCOUNT_TYPE%
echo.

REM Run import script (still in parsers directory)
python P_020_Trade_Import_Enhanced.py

if errorlevel 1 (
    echo.
    echo WARNING: Import script encountered errors. Check messages above.
    echo.
)

REM Navigate back to project root
cd /d "%SCRIPT_DIR%"

REM ========================================================================
REM COMPLETE
REM ========================================================================

echo.
echo ========================================================================
echo   WORKFLOW COMPLETE!
echo ========================================================================
echo.
echo Processed: %ACCOUNT_TYPE% account (%FILE_PREFIX%)
echo File: %LATEST_FILE%
echo.
echo Next steps:
echo   1. Open your Excel logs to verify import
echo   2. Check that System names were matched correctly
echo   3. Verify formulas are still calculating
echo.
echo If everything looks good:
echo   - This workflow is ready for production!
echo   - We can merge into single P_020_AccountParser.bat file
echo.

pause

