@echo off
REM ==============================================================================
REM P_035 Local Vector RAG Engine Launcher
REM Binds to conda environment 'p140' and runs the CLI interface
REM ==============================================================================

set CONDA_ENV_PATH=C:\Users\Trader\.conda\envs\p140\python.exe
set SCRIPT_DIR=%~dp0
set CLI_PATH=%SCRIPT_DIR%python\cli.py

if not exist "%CONDA_ENV_PATH%" (
    echo [ERROR] Conda environment python not found at: %CONDA_ENV_PATH%
    pause
    exit /b 1
)

if "%~1"=="" (
    "%CONDA_ENV_PATH%" "%CLI_PATH%" --help
) else (
    "%CONDA_ENV_PATH%" "%CLI_PATH%" %*
)