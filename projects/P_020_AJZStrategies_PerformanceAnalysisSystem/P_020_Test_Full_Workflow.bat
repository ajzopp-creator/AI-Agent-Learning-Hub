@echo off
REM ========================================================================
REM P_020 Full Workflow - TEST VERSION
REM ========================================================================
REM This batch file runs the complete P_020 workflow:
REM   1. Parse TOS account statement CSV
REM   2. Import parsed data to Excel logs (with auto-matching)
REM
REM Usage:
REM   P_020_Test_Full_Workflow.bat <tos_csv_file>
REM
REM Example:
REM   P_020_Test_Full_Workflow.bat P_020_2026-02-07_AJZ_Strategies_YTD_AccountStatement.csv
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

REM Check if filename was provided
if "%~1"=="" (
    echo ERROR: No CSV file specified!
    echo.
    echo Usage:
    echo   P_020_Test_Full_Workflow.bat ^<tos_csv_file^>
    echo.
    echo Example:
    echo   P_020_Test_Full_Workflow.bat P_020_2026-02-07_AccountStatement.csv
    echo.
    pause
    exit /b 1
)

REM Get the script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM ========================================================================
REM STEP 1: Run TOS Parser
REM ========================================================================

echo.
echo [STEP 1/2] Running TOS Parser...
echo ========================================================================
echo.

REM Navigate to parser directory
cd python\parsers

REM Run parser
"C:\Users\Trader\.conda\envs\p140\python.exe" P_020_TOS_Parser_v2.py "%~1"

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

REM Navigate back to project root
cd /d "%SCRIPT_DIR%"

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

REM Navigate to parser directory (where import script is located)
cd python\parsers

REM Run import script
REM Note: Import script has menu - user must choose which logs to update
"C:\Users\Trader\.conda\envs\p140\python.exe" P_020_Trade_Import_Enhanced.py

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

