@echo off
title P_020 Weekly Update
cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"

echo.
echo ============================================================
echo  P_020 AJZ Strategies -- Weekly Update
echo  Started: %DATE% %TIME%
echo ============================================================
echo.

REM Step 0: Schwab token pre-flight check (WO-P020-E1.007 / BACKLOG-3)
echo [0/5] Token pre-flight check...
C:\Users\Trader\.conda\envs\p140\python.exe ..\api\P_020_Schwab_Token_Manager.py
if errorlevel 1 (
    echo ERROR: Schwab token expired or invalid -- reauth required.
    echo Run: P_020_Schwab_Auth.bat
    pause
    exit /b 2
)
echo.

REM Step 1: Balance snapshot
echo [1/5] Pulling account balance...
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py balance --account AJZ
if errorlevel 1 (
    echo WARNING: Balance pull failed -- continuing.
)
echo.

REM Step 2: Fresh Schwab trade pull (from last run date)
echo [2/5] Pulling latest trades from Schwab...
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
REM ThinkLog: export from TOS and overwrite P_020_ThinkLog_Live_Current.csv
REM before running -- a matching tag always wins over vault/tracker/default
REM (Tony directive 2026-08-16). Missing file = safe no-op, just a warning.
echo [3/5] Importing trades...
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py import --account AJZ --thinklog "..\..\data\thinklog\live\P_020_ThinkLog_Live_Current.csv"
if errorlevel 1 (
    echo ERROR: Import failed -- check output above.
    pause
    exit /b 1
)
echo.

REM Step 4: Generate analysis CSVs
echo [4/5] Generating analysis...
C:\Users\Trader\.conda\envs\p140\python.exe P_020_Trade_Manager.py analyze --account AJZ6348
if errorlevel 1 (
    echo ERROR: Analysis failed -- check output above.
    pause
    exit /b 1
)
echo.

REM Step 5: Regenerate HTML dashboard (BACKLOG-4)
echo [5/5] Regenerating dashboard...
C:\Users\Trader\.conda\envs\p140\python.exe application\generate_dashboard.py
if errorlevel 1 (
    echo WARNING: Dashboard regeneration failed -- check output above.
)

echo.
echo ============================================================
echo  Done.  Completed: %DATE% %TIME%
echo  Dashboard: docs\P_020_Dashboard.html
echo  Check audit_logs\ for details.
echo ============================================================
echo.
pause
