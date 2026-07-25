@echo off
color 0B
TITLE P_300 Phase 5 Sector Analysis (WO-P300-E2.002)

echo =======================================================================
echo        P_300 PHASE 5 -- SECTOR-STRATIFIED RESULT ANALYSIS
echo =======================================================================
echo.
echo Backfills symbols.sector from data\reference\sector_map.csv, computes
echo win-rate / mean-return / std-dev per sector x tier x horizon, writes
echo the sector_stats snapshot to models\research\bulk_research.db, and
echo generates a markdown report in outputs\reports\sector_analysis\.
echo Never touches the live catalog or Pipeline A/B. Re-runnable -- each
echo run replaces the prior sector_stats snapshot (DB backups cover
echo history, not row-versioning).
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"

cd /d "%PROJECT_ROOT%"

echo [STEP 1] Running phase5-analysis...
echo.
"%PYTHON%" "%CLI%" phase5-analysis
if errorlevel 1 (
    echo.
    echo [ERROR] phase5-analysis failed -- see output above.
    goto :done
)

echo.
echo =======================================================================
echo  DONE  --  see summary above for row/cell counts and report path
echo =======================================================================

:done
echo.
pause
