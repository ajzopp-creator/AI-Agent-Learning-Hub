@echo off
color 0B
TITLE P_300 Bulk Pattern Extraction (WO-P300-E2.001)

echo =======================================================================
echo        P_300 BULK PATTERN EXTRACTION -- PIPELINE A-BULK
echo =======================================================================
echo.
echo Scans data\bulk\ for unprocessed *_Pattern_*.xlsx exports and writes
echo detections to models\research\bulk_research.db. Never touches the
echo live catalog or Pipeline A/B. Checkpoint-resumable -- safe to
echo interrupt and re-run.
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"

cd /d "%PROJECT_ROOT%"

echo [STEP 1] Running bulk-extract...
echo.
"%PYTHON%" "%CLI%" bulk-extract
if errorlevel 1 (
    echo.
    echo [ERROR] bulk-extract failed -- see output above.
    goto :done
)

echo.
echo =======================================================================
echo  DONE  --  see summary above for STRICT/RELAXED counts
echo =======================================================================

:done
echo.
pause
