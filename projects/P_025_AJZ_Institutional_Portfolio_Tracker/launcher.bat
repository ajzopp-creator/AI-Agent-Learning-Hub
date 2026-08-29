@echo off
REM P_025 AJZ Institutional Portfolio Tracker Launcher
REM Lives in project root; calls python\cli.py under p140.
REM
REM Examples:
REM   launcher.bat build
REM   launcher.bat build --mode yearly
REM   launcher.bat build --mode ytd
REM   launcher.bat update
REM   launcher.bat quick

setlocal
set PYTHON_EXE=C:\Users\Trader\.conda\envs\p140\python.exe
set PROJ=%~dp0
set PYDIR=%PROJ%python

if not exist "%PYTHON_EXE%" (
    echo ERROR: p140 environment not found at %PYTHON_EXE%
    exit /b 1
)
if not exist "%PYDIR%\cli.py" (
    echo ERROR: cli.py not found at %PYDIR%\cli.py
    exit /b 1
)

cd /d "%PYDIR%"
"%PYTHON_EXE%" cli.py %*
endlocal@echo off
REM P_025 AJZ Institutional Portfolio Tracker Launcher
REM Lives in project root; calls python\cli.py under p140.

setlocal
set PYTHON_EXE=C:\Users\Trader\.conda\envs\p140\python.exe
set PROJ=%~dp0
set PYDIR=%PROJ%python

if not exist "%PYTHON_EXE%" (
    echo ERROR: p140 environment not found at %PYTHON_EXE%
    exit /b 1
)
if not exist "%PYDIR%\cli.py" (
    echo ERROR: cli.py not found at %PYDIR%\cli.py
    exit /b 1
)

cd /d "%PYDIR%"
"%PYTHON_EXE%" cli.py %*
if errorlevel 1 (
    echo ERROR: cli.py failed
    exit /b 1
)
endlocal
exit /b 0