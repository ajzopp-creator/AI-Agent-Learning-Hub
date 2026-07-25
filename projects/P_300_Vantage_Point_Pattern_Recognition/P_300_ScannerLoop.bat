@echo off
color 0B
TITLE P_300 Scanner Loop (WO-P300-E3.001)

echo =======================================================================
echo        P_300 SCANNER LOOP -- NIGHTLY CROSSOVER WATCHLIST
echo =======================================================================
echo.
echo Scans data\bulk\nightly_scan\ for IntelliScan-crossover bulk exports,
echo re-applies the full 9-condition STRICT test, and writes a watchlist
echo report to outputs\reports\scanner\. Every processed file archives to
echo E:\AI-Agent-Learning-Hub_BackupFiles\10_Pattern_BulkCreate^<MMMYY^>.zip
echo regardless of hit/no-hit. Report-only -- never touches any catalog.db.
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"

cd /d "%PROJECT_ROOT%"

echo [STEP 1] Running scanner-loop...
echo.
"%PYTHON%" "%CLI%" scanner-loop
if errorlevel 1 (
    echo.
    echo [ERROR] scanner-loop failed -- see output above.
    goto :done
)

echo.
echo =======================================================================
echo  DONE  --  see summary above for STRICT hit count + report path
echo =======================================================================

:done
echo.
pause
