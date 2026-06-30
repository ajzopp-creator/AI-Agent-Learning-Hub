@echo off
title P_020 Weekly Update (Scheduled)

SET ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem
SET PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
SET PYDIR=%ROOT%\python\database
SET STATUS_FILE=C:\Users\Trader\Desktop\P_020_Weekly_Status.txt

powershell -Command "Get-Date -Format yyyyMMdd" > C:\Temp\p020_date.txt
SET /P LOGDATE= < C:\Temp\p020_date.txt
powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm'" > C:\Temp\p020_runtime.txt
SET /P RUNTIME= < C:\Temp\p020_runtime.txt

SET LOGFILE=%ROOT%\audit_logs\P_020_Weekly_%LOGDATE%.log

echo ============================================================ > "%LOGFILE%"
echo  P_020 AJZ Strategies -- Weekly Update (Scheduled) >> "%LOGFILE%"
echo  %RUNTIME% >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"

cd /d "%PYDIR%"

REM Step 1: Balance snapshot
echo. >> "%LOGFILE%"
echo [1/5] Balance pull... >> "%LOGFILE%"
"%PYTHON%" P_020_Trade_Manager.py balance --account AJZ >> "%LOGFILE%" 2>&1
IF ERRORLEVEL 1 (
    echo WARNING: Balance pull failed -- continuing. >> "%LOGFILE%"
)

REM Step 2: Schwab trade pull
echo. >> "%LOGFILE%"
echo [2/5] Schwab trade pull... >> "%LOGFILE%"
"%PYTHON%" -c "import json; d=json.load(open(r'%ROOT%\data\api_pulls\P_020_last_run.json')); print(d.get('last_run_date','2026-01-01'))" > C:\Temp\p020_last_run.txt 2>&1
SET /P LAST_RUN= < C:\Temp\p020_last_run.txt
IF "%LAST_RUN%"=="" SET LAST_RUN=2026-01-01
echo Last run: %LAST_RUN% >> "%LOGFILE%"
"%PYTHON%" ..\api\P_020_Schwab_Trade_Pull.py --account AJZ --from %LAST_RUN% >> "%LOGFILE%" 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Schwab pull failed -- token may be expired. >> "%LOGFILE%"
    echo FAILED Step 2 Schwab pull %RUNTIME% > "%STATUS_FILE%"
    exit /b 1
)

REM Step 3: Import into database
echo. >> "%LOGFILE%"
echo [3/5] Importing trades... >> "%LOGFILE%"
"%PYTHON%" P_020_Trade_Manager.py import --account AJZ >> "%LOGFILE%" 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Import failed. >> "%LOGFILE%"
    echo FAILED Step 3 Import %RUNTIME% > "%STATUS_FILE%"
    exit /b 1
)

REM Step 4: Generate analysis CSVs
echo. >> "%LOGFILE%"
echo [4/5] Generating analysis CSVs... >> "%LOGFILE%"
"%PYTHON%" P_020_Trade_Manager.py analyze --account AJZ6348 >> "%LOGFILE%" 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Analysis failed. >> "%LOGFILE%"
    echo FAILED Step 4 Analyze %RUNTIME% > "%STATUS_FILE%"
    exit /b 1
)

REM Step 5: Regenerate dashboard
echo. >> "%LOGFILE%"
echo [5/5] Regenerating dashboard... >> "%LOGFILE%"
"%PYTHON%" application\generate_dashboard.py >> "%LOGFILE%" 2>&1
IF ERRORLEVEL 1 (
    echo WARNING: Dashboard generation failed -- data is current, HTML may be stale. >> "%LOGFILE%"
)

echo. >> "%LOGFILE%"
echo RESULT: SUCCESS >> "%LOGFILE%"
echo ============================================================ >> "%LOGFILE%"
echo SUCCESS %RUNTIME% > "%STATUS_FILE%"
exit /b 0
