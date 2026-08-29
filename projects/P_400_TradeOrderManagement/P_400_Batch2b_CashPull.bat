@echo off
title P_400 Batch-2b (Cash Pull + Run)
REM =============================================================================
REM P_400_Batch2b_CashPull.bat  --  v1.0  --  2026-08-25
REM Pulls fresh Schwab cash balance (P_020), then runs P_400 batch-2b using the
REM freshly-pulled Cash Available for Trading figure. Implements the batch-2b
REM --cash auto-read reversal of Section 3.3 (P_400 batch-2b ONLY -- evaluate,
REM spec, and compare stay manual-cash per architecture).
REM =============================================================================

set HUB_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub
set PY=C:\Users\Trader\.conda\envs\p140\python.exe
set P020_DIR=%HUB_ROOT%\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database
set P400_DIR=%HUB_ROOT%\projects\P_400_TradeOrderManagement\python
set PARAMS_FILE=%HUB_ROOT%\projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md
set PYTHONPATH=%HUB_ROOT%

echo.
echo ============================================================
echo  P_400 BATCH-2B -- CASH PULL + BATCH RUN
echo  Started: %DATE% %TIME%
echo ============================================================
echo.

REM --- Step 1: Pull fresh Schwab balance (auto-writes to P_000 params file) ---
echo [1/3] Pulling Schwab account balance...
pushd "%P020_DIR%"
"%PY%" P_020_Trade_Manager.py balance --account AJZ
if errorlevel 1 (
    echo.
    echo ERROR: Balance pull failed. Aborting.
    popd
    exit /b 1
)
popd
echo.

REM --- Step 2: Parse Cash Available for Trading out of the P_000 params file ---
echo [2/3] Reading Cash Available for Trading from params file...
set CASH_VALUE=
set CASHRAW=
for /f "tokens=2 delims=$" %%A in ('findstr /C:"Cash Available for Trading" "%PARAMS_FILE%"') do set CASHRAW=%%A
for /f "tokens=1 delims= " %%B in ("%CASHRAW%") do set CASH_VALUE=%%B
set CASH_VALUE=%CASH_VALUE:,=%

if "%CASH_VALUE%"=="" (
    echo.
    echo ERROR: Could not parse Cash Available for Trading from params file. Aborting.
    exit /b 1
)
echo    Cash Available for Trading: $%CASH_VALUE%
echo.

REM --- Step 3: Run batch-2b with the freshly-pulled cash figure ---
echo [3/3] Running batch-2b --cash %CASH_VALUE% ...
echo.
pushd "%P400_DIR%"
"%PY%" cli.py batch-2b --cash %CASH_VALUE%
set BATCH_EXIT=%ERRORLEVEL%
popd

echo.
echo ============================================================
if %BATCH_EXIT% NEQ 0 (
    echo  RESULT: FAILED -- exit %BATCH_EXIT%
) else (
    echo  RESULT: SUCCESS -- cash used: $%CASH_VALUE%
)
echo ============================================================
echo.

exit /b %BATCH_EXIT%