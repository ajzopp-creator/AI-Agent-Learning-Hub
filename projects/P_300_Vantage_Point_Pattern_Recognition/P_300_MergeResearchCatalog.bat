@echo off
color 0B
TITLE P_300 Merge Research Catalog (WO-P300-E2.003)

echo =======================================================================
echo        P_300 MERGE RESEARCH CATALOG -- STAGING BUILD + EVAL
echo =======================================================================
echo.
echo Copies the live catalog, merges every STRICT-tier bulk-scan pattern
echo from models\research\bulk_research.db into the copy, runs the walk-
echo forward eval against BOTH the untouched live catalog and the staging
echo copy, writes both reports. NEVER touches the real live catalog.db --
echo promotion is a separate, explicit command shown at the end.
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"

cd /d "%PROJECT_ROOT%"

echo [STEP 1] Building staging merge + running walk-forward comparison...
echo.
"%PYTHON%" "%CLI%" merge-research-catalog
if errorlevel 1 (
    echo.
    echo [ERROR] merge-research-catalog failed -- see output above.
    goto :done
)

echo.
echo =======================================================================
echo  DONE -- review both reports above before running the --promote
echo  command it printed. Promotion is NOT automatic.
echo =======================================================================

:done
echo.
pause
