@echo off
REM ================================================================================
REM P_020_AccountParser.bat
REM Simplified TOS Account Statement Parser Runner
REM ================================================================================
REM Usage: P_020_AccountParser.bat <filename>
REM Example: P_020_AccountParser.bat D_020_2026-02-07-AJZ_Stategies_YTD_AccountStatement.csv
REM ================================================================================

SETLOCAL EnableDelayedExpansion

REM Check if filename was provided
IF "%~1"=="" (
    echo.
    echo ERROR: No filename provided!
    echo.
    echo Usage: P_020_AccountParser.bat ^<filename^>
    echo.
    echo Example:
    echo   P_020_AccountParser.bat D_020_2026-02-07-AJZ_Stategies_YTD_AccountStatement.csv
    echo.
    pause
    exit /b 1
)

REM Get the filename (extract just filename from any path provided)
set FILENAME=%~nx1

REM Determine account type from filename prefix
echo %FILENAME% | findstr /B "P_020" >nul
if %ERRORLEVEL%==0 (
    set ACCOUNT_TYPE=live
    goto :FoundType
)

echo %FILENAME% | findstr /B "D_020" >nul
if %ERRORLEVEL%==0 (
    set ACCOUNT_TYPE=paper
    goto :FoundType
)

REM If we get here, invalid prefix
echo.
echo ERROR: Invalid filename prefix!
echo Filename must start with P_020 (live account) or D_020 (paper account)
echo.
echo Your filename: %FILENAME%
echo.
pause
exit /b 1

:FoundType

REM Construct the full input path
set INPUT_PATH=data\tos_exports\%ACCOUNT_TYPE%\%FILENAME%

REM Check if file exists
if not exist "%INPUT_PATH%" (
    echo.
    echo ERROR: File not found!
    echo.
    echo Looking for: %FILENAME%
    echo In folder: %CD%\data\tos_exports\%ACCOUNT_TYPE%\
    echo.
    echo Full path: %CD%\%INPUT_PATH%
    echo.
    echo Please verify:
    echo 1. File is in correct folder (live\ or paper\)
    echo 2. Filename is spelled correctly
    echo 3. File exists
    echo.
    pause
    exit /b 1
)

REM Display banner
echo.
echo ================================================================================
echo                    P_020 TOS ACCOUNT PARSER
echo ================================================================================
echo Input File:    %FILENAME%
echo Account Type:  %ACCOUNT_TYPE%
echo Input Path:    %INPUT_PATH%
echo ================================================================================
echo.

REM Run the parser
"C:\Users\Trader\.conda\envs\p140\python.exe" python\parsers\P_020_TOS_Parser_v2.py "%INPUT_PATH%"

REM Check if parser succeeded
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ================================================================================
    echo ERROR: Parser failed!
    echo ================================================================================
    pause
    exit /b 1
)

REM Display output location
echo.
echo ================================================================================
echo                         OUTPUT FILES LOCATION
echo ================================================================================
echo Folder: %CD%\data\processed\%ACCOUNT_TYPE%\
echo.
echo Files created:
echo   - %FILENAME:~0,-4%_OPTIONS_IMPORT.csv
echo   - %FILENAME:~0,-4%_STOCKS_IMPORT.csv
echo ================================================================================
echo.
echo Next Steps:
echo 1. Navigate to: data\processed\%ACCOUNT_TYPE%\
echo 2. Open the _OPTIONS_IMPORT.csv file
echo 3. Copy all rows (Ctrl+A, Ctrl+C)
if "%ACCOUNT_TYPE%"=="live" (
    echo 4. Paste into: D:\OneDrive\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx
) else (
    echo 4. Paste into: tracking_logs\paper\D_020__Paper_Options_Log_v2.xlsx
)
echo 5. Use "Paste Special -^> Values" to preserve formulas!
echo 6. Update "System" column from "TOS_Import" to correct system
echo 7. Repeat for _STOCKS_IMPORT.csv
echo ================================================================================
echo.

pause


