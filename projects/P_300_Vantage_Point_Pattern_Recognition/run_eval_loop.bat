@echo off
color 0B
TITLE P_300 Walk-Forward Eval Loop (Stage 6)

echo =======================================================================
echo        P_300 WALK-FORWARD EVAL LOOP -- STAGE 6
echo =======================================================================
echo.
echo Read-only against the catalog. Scores every PATTERN_IDENT pattern
echo against its date-filtered prior corpus, writes an edge-vs-base-rate
echo table to outputs\reports\eval\.
echo.
echo Usage: run_eval_loop.bat [buy-min-z-override]
echo   (no arg)  -> config.py BUY_MIN_Z_SCORE default
echo   1.0       -> example override, e.g. run_eval_loop.bat 1.0
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "SCRIPT=%PROJECT_ROOT%\python\application\run_eval_loop.py"
set "BUYMINZ=%~1"

echo [STEP 1] Running walk-forward eval loop...
echo.
if "%BUYMINZ%"=="" (
    "%PYTHON%" "%SCRIPT%"
) else (
    "%PYTHON%" "%SCRIPT%" --buy-min-z %BUYMINZ%
)
if errorlevel 1 (
    echo.
    echo [ERROR] run_eval_loop.py failed -- see output above.
    goto :done
)

echo.
echo =======================================================================
echo  DONE  --  report written to outputs\reports\eval\
echo =======================================================================

:done
echo.
pause
