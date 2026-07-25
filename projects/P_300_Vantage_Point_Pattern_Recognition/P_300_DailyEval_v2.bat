@echo off
color 0B
TITLE P_300 Daily Evaluate + Obsidian Write + Archive (v2.4)

echo =======================================================================
echo        P_300 DAILY EVALUATE + OBSIDIAN LOG + ARCHIVE
echo =======================================================================
echo.

set "SYMBOL=%~1"
if "%SYMBOL%"=="" (
    set /p SYMBOL=Enter symbol ^(e.g. VZ^): 
)

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"
set "XLSX=%PROJECT_ROOT%\data\live\History Grid (%SYMBOL%).xlsx"
set "EXIT_CODE=0"

echo Symbol  : %SYMBOL%
echo File    : %XLSX%
echo.

echo [STEP 1] Running Pipeline B evaluation...
echo.
"%PYTHON%" "%CLI%" daily-evaluate --xlsx "%XLSX%" --clean
if errorlevel 1 (
    echo.
    echo [ERROR] daily-evaluate failed.
    set "EXIT_CODE=1"
    goto :done
)

echo.
echo [STEP 2] Archiving eval file...
echo.
"%PYTHON%" "%CLI%" archive-eval --xlsx "%XLSX%"
if errorlevel 1 (
    echo.
    echo [ERROR] archive-eval failed -- XLSX still in data\live\.
    set "EXIT_CODE=1"
    goto :done
)

echo.
echo =======================================================================
echo  DONE  %SYMBOL%  --  report / vault logged / XLSX archived
echo =======================================================================

:done
echo.
pause
exit /b %EXIT_CODE%
