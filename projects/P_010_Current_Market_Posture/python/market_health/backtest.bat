@echo off
REM ===========================================================================
REM P_010 Market Health -- backtest.bat
REM
REM Runs the Phase 2 Workstream C Backtest Harness via p140 conda python.
REM Forwards all args to market_health.cli_backtest:
REM   --start YYYY-MM-DD   first backtest date (default: earliest after warmup)
REM   --end YYYY-MM-DD     last backtest date (default: latest VP row)
REM   --warmup-days N      warmup buffer (default: 30)
REM   --output PATH        CSV output path (default: data/backtests/...)
REM   --verbose            debug logging
REM
REM Spec: docs/P_010_MarketHealth_Phase2_Plan_v1_1.md Workstream C
REM ===========================================================================

setlocal

set PYTHON_EXE=C:\Users\Trader\.conda\envs\p140\python.exe
set PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture
set PYTHON_DIR=%PROJECT_ROOT%\python

if not exist "%PYTHON_EXE%" (
    echo [ERROR] p140 python not found at: %PYTHON_EXE%
    endlocal & exit /b 10
)
if not exist "%PYTHON_DIR%\market_health\cli_backtest.py" (
    echo [ERROR] cli_backtest.py not found under: %PYTHON_DIR%\market_health\
    endlocal & exit /b 11
)

echo === %DATE% %TIME% backtest launcher start ===

cd /d "%PYTHON_DIR%"
"%PYTHON_EXE%" -m market_health.cli_backtest %*
set EXIT_CODE=%ERRORLEVEL%

echo === %DATE% %TIME% backtest launcher exit=%EXIT_CODE% ===

endlocal & exit /b %EXIT_CODE%
