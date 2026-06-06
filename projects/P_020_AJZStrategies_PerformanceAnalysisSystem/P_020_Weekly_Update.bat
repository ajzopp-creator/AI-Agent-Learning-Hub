@echo off
title P_020 Weekly Update
cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"

echo.
echo ============================================================
echo  P_020 AJZ Strategies -- Weekly Update
echo  %DATE% %TIME%
echo ============================================================
echo.

REM Step 1: Balance snapshot
echo [1/4] Pulling account balance...
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py balance --account AJZ
if errorlevel 1 (
    echo WARNING: Balance pull failed -- continuing.
)
echo.

REM Step 2: Fresh Schwab trade pull (from last run date)
echo [2/4] Pulling latest trades from Schwab...
FOR /F "tokens=*" %%D IN ('C:\Users\Trader\.conda\envs\p140\python.exe -c "import json; d=json.load(open(r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\api_pulls\P_020_last_run.json')); print(d.get('last_run_date','2026-01-01'))"') DO SET LAST_RUN=%%D
echo    Last run: %LAST_RUN%
C:\Users\Trader\.conda\envs\p140\python.exe ..\api\P_020_Schwab_Trade_Pull.py --account AJZ --from %LAST_RUN%
if errorlevel 1 (
    echo ERROR: Schwab pull failed -- check token. Re-run auth if needed.
    pause
    exit /b 1
)
echo.

REM Step 3: Import latest pull file into database
echo [3/4] Importing trades...
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py import --account AJZ
if errorlevel 1 (
    echo ERROR: Import failed -- check output above.
    pause
    exit /b 1
)
echo.

REM Step 4: Generate analysis CSVs
echo [4/4] Generating analysis...
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py analyze --account AJZ6348
if errorlevel 1 (
    echo ERROR: Analysis failed -- check output above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Done. Check audit_logs\ for details.
echo ============================================================
echo.
pause
