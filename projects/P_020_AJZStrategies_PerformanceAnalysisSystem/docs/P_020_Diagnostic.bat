@echo off
REM ========================================================================
REM P_020 Folder Diagnostic Script
REM ========================================================================
REM This script checks your folder setup and shows what files are where
REM ========================================================================

echo.
echo ========================================================================
echo   P_020 FOLDER DIAGNOSTIC
echo ========================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo Script Location: %SCRIPT_DIR%
echo.

REM ========================================================================
REM Check Paper Account Folders
REM ========================================================================

echo ========================================================================
echo PAPER ACCOUNT - TOS EXPORTS FOLDER
echo ========================================================================
echo Location: data\tos_exports\paper\
echo.

if exist "data\tos_exports\paper\" (
    echo Folder exists: YES
    echo.
    echo CSV files found:
    dir /b "data\tos_exports\paper\*.csv" 2>nul
    if errorlevel 1 (
        echo   (No CSV files found)
    )
) else (
    echo Folder exists: NO - NEED TO CREATE THIS!
)

echo.
echo ========================================================================
echo PAPER ACCOUNT - PARSER OUTPUT FOLDER
echo ========================================================================
echo Location: data\processed\paper\
echo.

if exist "data\processed\paper\" (
    echo Folder exists: YES
    echo.
    echo CSV files found:
    dir /b "data\processed\paper\*.csv" 2>nul
    if errorlevel 1 (
        echo   (No CSV files found)
    )
) else (
    echo Folder exists: NO - NEED TO CREATE THIS!
)

echo.
echo ========================================================================
echo PAPER ACCOUNT - EXCEL LOGS
echo ========================================================================
echo Location: data\
echo.

if exist "data\D_020_2026_AJZ_Strategies_Options_Log_V1.xlsx" (
    echo Options Log: FOUND
) else (
    echo Options Log: NOT FOUND
)

if exist "data\D_020_2026__AJZ_Strategies_Stock_Log_V1.xlsx" (
    echo Stocks Log:  FOUND
) else (
    echo Stocks Log:  NOT FOUND
)

echo.
echo ========================================================================
echo LIVE ACCOUNT - TOS EXPORTS FOLDER
echo ========================================================================
echo Location: D:\OneDrive\Documents\AJZStrategiesLLC\2026_Operations\
echo.

if exist "D:\OneDrive\Documents\AJZStrategiesLLC\2026_Operations\" (
    echo Folder exists: YES
    echo.
    echo P_020 CSV files found:
    dir /b "D:\OneDrive\Documents\AJZStrategiesLLC\2026_Operations\P_020*.csv" 2>nul
    if errorlevel 1 (
        echo   (No P_020 CSV files found)
    )
) else (
    echo Folder exists: NO
)

echo.
echo ========================================================================
echo TRACKER DASHBOARD
echo ========================================================================
echo Location: D:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\
echo.

if exist "D:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx" (
    echo Tracker Dashboard: FOUND
) else (
    echo Tracker Dashboard: NOT FOUND
)

echo.
echo ========================================================================
echo PYTHON SCRIPTS
echo ========================================================================
echo Location: python\parsers\
echo.

if exist "python\parsers\P_020_TOS_Parser_v2.py" (
    echo Parser Script:       FOUND
) else (
    echo Parser Script:       NOT FOUND
)

if exist "python\parsers\P_020_Trade_Import_Enhanced.py" (
    echo Import Script:       FOUND
) else (
    echo Import Script:       NOT FOUND
)

echo.
echo ========================================================================
echo SUMMARY
echo ========================================================================
echo.
echo Review the output above to see what's missing or misconfigured.
echo.
echo Key things to check:
echo   1. TOS export files should be in tos_exports\ folder
echo   2. Parser output (*_IMPORT.csv) should be in processed\ folder
echo   3. TOS export files should NOT have _IMPORT in the name
echo   4. Excel logs should be in data\ folder
echo   5. Tracker Dashboard should exist
echo.

pause

