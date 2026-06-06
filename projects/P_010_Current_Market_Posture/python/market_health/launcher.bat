@echo off
REM ===========================================================================
REM P_010 Market Health -- launcher.bat
REM
REM Runs the Distribution Day Tracker via p140 conda python.
REM Forwards all args to market_health.cli (--date, --dry-run, --verbose).
REM
REM Spec: docs/P_010_MarketHealth_Spec_v1_1.md Section 9
REM ===========================================================================

setlocal

set PYTHON_EXE=C:\Users\Trader\.conda\envs\p140\python.exe
set PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture
set PYTHON_DIR=%PROJECT_ROOT%\python

if not exist "%PYTHON_EXE%" (
    echo [ERROR] p140 python not found at: %PYTHON_EXE%
    endlocal & exit /b 10
)
if not exist "%PYTHON_DIR%\market_health\cli.py" (
    echo [ERROR] cli.py not found under: %PYTHON_DIR%\market_health\
    endlocal & exit /b 11
)

echo === %DATE% %TIME% market_health launcher start ===

cd /d "%PYTHON_DIR%"
"%PYTHON_EXE%" -m market_health.cli %*
set EXIT_CODE=%ERRORLEVEL%

echo === %DATE% %TIME% market_health launcher exit=%EXIT_CODE% ===

endlocal & exit /b %EXIT_CODE%
