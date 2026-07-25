@echo off
color 0B
TITLE P_300 Mine Patterns (WO-P300-E3.002 Phase 1)

echo =======================================================================
echo        P_300 MINE PATTERNS -- OUTCOME-FIRST PATTERN MINER (PHASE 1)
echo =======================================================================
echo.
echo Scans data\bulk\mine\ for crossover-gated >=15%% forward moves (either
echo direction, 5/7/10/15/20-day horizons + extended search to 180 days).
echo Writes a markdown report + mine_candidates.csv (keep column defaults
echo YES) to outputs\reports\mine\. Report-only -- never touches any
echo catalog.db. Review/edit the CSV's keep column, then run
echo P_300_IngestMined.bat to audit-gate and stage the approved rows.
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"

cd /d "%PROJECT_ROOT%"

echo [STEP 1] Running mine-patterns...
echo.
"%PYTHON%" "%CLI%" mine-patterns
if errorlevel 1 (
    echo.
    echo [ERROR] mine-patterns failed -- see output above.
    goto :done
)

echo.
echo =======================================================================
echo  DONE -- review the report + edit mine_candidates.csv's keep column,
echo  then run P_300_IngestMined.bat when ready.
echo =======================================================================

:done
echo.
pause
