@echo off
REM P_025_DeployPEH.bat — overlay python\ from a PEH zip, copy run_this_P025_*.py
REM to verify\, run with p140. Does not rmtree python\. Does not edit WOs.
REM Usage: P_025_DeployPEH.bat [zip-path]
REM Default zip: C:\Users\Trader\Downloads\run_this_P025_20260920_103700.zip

setlocal EnableDelayedExpansion
set HUB_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub
set PY=C:\Users\Trader\.conda\envs\p140\python.exe
set PROJ=%HUB_ROOT%\projects\P_025_AJZ_Institutional_Portfolio_Tracker
set VERIFY=%HUB_ROOT%\Agentic-Hub-Governance\verify
set ZIP=%~1
if "%ZIP%"=="" set ZIP=C:\Users\Trader\Downloads\run_this_P025_20260920_103700.zip

if not exist "%ZIP%" (
    echo ERROR: zip not found: %ZIP%
    exit /b 1
)
if not exist "%PY%" (
    echo ERROR: p140 not found: %PY%
    exit /b 1
)
if not exist "%PROJ%\python\" (
    echo ERROR: python\ missing at %PROJ%\python — refusing extract
    exit /b 1
)

set STAGE=%TEMP%\p025_peh_extract_%RANDOM%
mkdir "%STAGE%"
tar -xf "%ZIP%" -C "%STAGE%"
if errorlevel 1 (
    echo ERROR: zip extract failed
    rmdir /s /q "%STAGE%"
    exit /b 1
)
if not exist "%STAGE%\python\" (
    echo ERROR: zip has no python\ overlay
    rmdir /s /q "%STAGE%"
    exit /b 1
)

REM Overlay only. Never rmtree dest python\.
xcopy /E /Y /Q "%STAGE%\python\*" "%PROJ%\python\" >nul
if errorlevel 1 (
    echo ERROR: python overlay copy failed
    rmdir /s /q "%STAGE%"
    exit /b 1
)

set PEH=
for %%F in ("%STAGE%\run_this_P025_*.py") do set PEH=%%~nxF
if "%PEH%"=="" (
    echo ERROR: no run_this_P025_*.py in zip
    rmdir /s /q "%STAGE%"
    exit /b 1
)

copy /Y "%STAGE%\%PEH%" "%VERIFY%\%PEH%" >nul
rmdir /s /q "%STAGE%"

echo Overlay complete. Running %PEH% from verify\
cd /d "%VERIFY%"
"%PY%" "%PEH%"
exit /b %ERRORLEVEL%
