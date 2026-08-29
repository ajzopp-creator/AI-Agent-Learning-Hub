@echo off
REM =============================================================================
REM P_025 Ops Wrapper — On-demand / scheduled build for weekly P_020 cadence
REM Lives in project root; calls python\cli.py under p140.
REM =============================================================================
REM Usage:
REM   ops_wrapper.bat [full|yearly|ytd]
REM   (default mode = full)
REM
REM Exit codes: 0 = success, 1 = failure
REM =============================================================================

setlocal EnableDelayedExpansion

set PYTHON_EXE=C:\Users\Trader\.conda\envs\p140\python.exe
set PROJ=%~dp0
set PYDIR=%PROJ%python
set MODE=%~1
if "%MODE%"=="" set MODE=full

if not exist "%PYTHON_EXE%" (
    echo ERROR: p140 environment not found at %PYTHON_EXE%
    exit /b 1
)
if not exist "%PYDIR%\cli.py" (
    echo ERROR: cli.py not found at %PYDIR%\cli.py
    exit /b 1
)

cd /d "%PYDIR%"

echo ============================================================
echo P_025 Ops Wrapper  %date% %time%
echo Mode: %MODE%
echo ============================================================

"%PYTHON_EXE%" cli.py build --mode %MODE%
if errorlevel 1 (
    echo ERROR: build failed
    exit /b 1
)

"%PYTHON_EXE%" -c "from application.format_analytics import run_format_analytics; run_format_analytics()"
if errorlevel 1 (
    echo WARNING: format_analytics returned non-zero — Data Lake is still written
)

echo ============================================================
echo P_025 Ops Wrapper complete
echo ============================================================
endlocal
exit /b 0