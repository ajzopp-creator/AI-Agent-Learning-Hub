@echo off
color 0B
TITLE P_300 Preflight (Catalog + LM Studio Status)

echo =======================================================================
echo        P_300 PREFLIGHT -- CATALOG + LM STUDIO STATUS
echo =======================================================================
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "SCRIPT=%PROJECT_ROOT%\python\utilities\preflight_status.py"

echo [STEP 1] Gathering catalog + LM Studio status...
echo.
"%PYTHON%" "%SCRIPT%"
if errorlevel 1 (
    echo.
    echo [ERROR] preflight_status.py failed -- see output above.
    goto :done
)

echo.
echo =======================================================================
echo  DONE  --  P_300_preflight_status.json written to project root
echo =======================================================================

:done
echo.
pause
