@echo off
color 0B
TITLE P_300 Daily Evaluate + Archive (v1.0)

echo =======================================================================
echo              P_300 DAILY EVALUATE + ARCHIVE
echo =======================================================================
echo.

:: -----------------------------------------------------------------------
:: SYMBOL: pass as argument  ->  P_300_DailyEval.bat SPY
::         or leave blank    ->  prompted at runtime
:: -----------------------------------------------------------------------
set "SYMBOL=%~1"
if "%SYMBOL%"=="" (
    set /p SYMBOL=Enter symbol ^(e.g. SPY^): 
)

:: -----------------------------------------------------------------------
:: PATHS
:: -----------------------------------------------------------------------
set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"
set "XLSX=%PROJECT_ROOT%\data\live\History Grid (%SYMBOL%).xlsx"
set "REPORTS=%PROJECT_ROOT%\outputs\reports"

echo Symbol  : %SYMBOL%
echo File    : %XLSX%
echo.

:: -----------------------------------------------------------------------
:: STEP 1 -- DAILY EVALUATE
:: -----------------------------------------------------------------------
echo [STEP 1] Running Pipeline B evaluation...
echo.
"%PYTHON%" "%CLI%" daily-evaluate --xlsx "%XLSX%"
if errorlevel 1 (
    echo.
    echo [ERROR] daily-evaluate failed -- archive step skipped.
    echo         Check output above for details.
    goto :done
)

:: -----------------------------------------------------------------------
:: STEP 2 -- ARCHIVE  (only runs if Step 1 succeeded)
:: Requires report in outputs/reports/ -- archive_live_file.py enforces
:: this and will exit 1 if no report found.
:: On success: XLSX is moved into data/processed/YYYY-MM.zip and
:: DELETED from data/live/.
:: -----------------------------------------------------------------------
echo.
echo [STEP 2] Archiving eval file...
echo.
"%PYTHON%" "%CLI%" archive-eval --xlsx "%XLSX%"
if errorlevel 1 (
    echo.
    echo [ERROR] archive-eval failed -- XLSX still in data\live\.
    echo         Check outputs\reports\ for the report and retry.
    goto :done
)

echo.
echo =======================================================================
echo  DONE  %SYMBOL%  --  report in outputs\reports\  /  XLSX archived
echo =======================================================================

:done
echo.
pause
