@echo off
setlocal
REM P_300_CheckPatternDups.bat
REM
REM Runs the CLI's check-pattern command (WO-P300-E5.003): read-only
REM pre-export duplicate check. Default mode scans data\live\ for
REM "History Grid (SYMBOL).xlsx" exports and reports catalog status per
REM symbol -- answers whether a symbol is already captured before Tony
REM spends a manual VP export + bulk-ingest cycle on it.
REM
REM Usage:
REM   P_300_CheckPatternDups.bat
REM   P_300_CheckPatternDups.bat --symbol AAPL,MSFT,TSLA
REM
REM See python\utilities\check_pattern.py for the underlying logic.

set PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition
set PYTHON_EXE=C:\Users\Trader\.conda\envs\p140\python.exe

echo.
echo Running P_300 check-pattern (duplicate check)...
echo.
"%PYTHON_EXE%" "%PROJECT_ROOT%\python\cli.py" check-pattern %*
set RUN_EXIT=%ERRORLEVEL%

echo.
echo Done. check-pattern exit code: %RUN_EXIT%
exit /b %RUN_EXIT%
