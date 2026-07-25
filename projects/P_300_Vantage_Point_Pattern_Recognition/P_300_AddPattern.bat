@echo off
color 0B
TITLE P_300 Add Pattern (Pipeline A)

echo =======================================================================
echo              P_300 ADD PATTERN  (Pipeline A)
echo =======================================================================
echo.

set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"
set "MODELS_DIR=%PROJECT_ROOT%\models"

set "XLSX=%~1"
if "%XLSX%"=="" (
    set /p XLSX=Enter XLSX path ^(project-relative or absolute^): 
)

echo XLSX    : %XLSX%
echo.

rem -- Determine today's date as MMDDYY (locale format: Tue 06/23/2026) --
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    set "MM=%%a"
    set "DD=%%b"
    set "YYYY=%%c"
)
set "YY=%YYYY:~2,2%"
set "TODAYSTAMP=%MM%%DD%%YY%"

rem -- Find latest digit-prefixed *catalog.db (mirrors db_utils.get_latest_catalog) --
set "LATEST="
for /f "delims=" %%f in ('dir /b /o-n "%MODELS_DIR%\*catalog.db" 2^>nul') do (
    if not defined LATEST (
        echo %%f | findstr /r "^[0-9]" >nul && set "LATEST=%%f"
    )
)

if not defined LATEST (
    echo [ERROR] No catalog.db found in %MODELS_DIR%
    goto :done
)

set "LATEST_DATE=%LATEST:~0,6%"

rem -- M-032: no SETLOCAL ENABLEDELAYEDEXPANSION / !VAR! on this workstation.
rem -- goto-label pattern instead -- keeps each %VAR% reference in its own
rem -- top-level statement context so it re-expands correctly after SET.
if "%LATEST_DATE%"=="%TODAYSTAMP%" goto :catalog_current

set "NEWCATALOG=%TODAYSTAMP%catalog.db"
echo [BACKUP] New catalog day -- copying to %NEWCATALOG%
echo          Source: %MODELS_DIR%\%LATEST%
copy /y "%MODELS_DIR%\%LATEST%" "%MODELS_DIR%\%NEWCATALOG%" >nul
echo          Done.
goto :catalog_baseline

:catalog_current
echo [BACKUP] Catalog already current for today -- %LATEST%

:catalog_baseline
echo.
echo [SUMMARY] Catalog baseline for today...
echo.
"%PYTHON%" "%CLI%" catalog-summary --recent 5

echo.
echo -----------------------------------------------------------------------
echo  Catalog state above is your baseline for today.
echo  Press any key to proceed  --  close window to CANCEL.
echo -----------------------------------------------------------------------
pause >nul

echo.
echo [STEP 1] Ingesting pattern...
echo.
"%PYTHON%" "%CLI%" add-pattern --xlsx "%XLSX%"
if errorlevel 1 (
    echo.
    echo [ERROR] add-pattern failed -- catalog untouched.
    goto :done
)

echo.
echo [STEP 2] Archiving pattern file...
echo.
"%PYTHON%" "%CLI%" archive-pattern --xlsx "%XLSX%"
if errorlevel 1 (
    echo.
    echo [ERROR] archive-pattern failed -- XLSX still in data\historical_patterns\.
    goto :done
)

echo.
echo =======================================================================
echo  DONE  --  pattern ingested and archived.
echo =======================================================================

:done
echo.
pause
