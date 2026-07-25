@echo off
color 0B
TITLE P_300 Ingest Mined (WO-P300-E3.002 Phase 2)

echo =======================================================================
echo        P_300 INGEST MINED -- STAGING BUILD + AUDIT GATE + EVAL
echo =======================================================================
echo.
echo Reads the operator-approved mine_candidates.csv, re-reads each
echo approved symbol's source grid file fresh from data\bulk\mine\, audits
echo every row (domain\mine_audit.py) against a real recompute, and
echo inserts audit-passed rows into a STAGING COPY of the live catalog.
echo Runs the walk-forward eval against BOTH the untouched live catalog
echo and the staging copy. NEVER touches the real live catalog.db --
echo promotion is a separate, explicit command shown at the end.
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"

cd /d "%PROJECT_ROOT%"

echo [STEP 1] Building staging ingest + running walk-forward comparison...
echo.
"%PYTHON%" "%CLI%" ingest-mined
if errorlevel 1 (
    echo.
    echo [ERROR] ingest-mined failed -- see output above.
    goto :done
)

echo.
echo =======================================================================
echo  DONE -- review both reports + any audit failures above before
echo  running the --promote command it printed. Promotion is NOT automatic.
echo =======================================================================

:done
echo.
pause
