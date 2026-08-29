@echo off
REM P_025 AJZ Institutional Portfolio Tracker Launcher
REM Activates the p140 conda environment and runs the CLI.

setlocal
set CONDA_ENV=p140
set PYTHON_EXE=C:\Users\Trader\.conda\envs\p140\python.exe

if not exist "%PYTHON_EXE%" (
    echo ERROR: p140 environment not found at %PYTHON_EXE%
    exit /b 1
)

cd /d "%~dp0"
"%PYTHON_EXE%" cli.py %*
endlocal
