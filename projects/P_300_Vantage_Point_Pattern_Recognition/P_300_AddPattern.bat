@echo off
color 0A
TITLE P_300 Add Pattern (v1.5)

echo =======================================================================
echo              P_300 ADD PATTERN  (Pipeline A)
echo =======================================================================
echo.

:: -----------------------------------------------------------------------
:: XLSX argument -- quoted or unquoted, absolute or project-relative
:: -----------------------------------------------------------------------
set "XLSX=%~1"
if "%XLSX%"=="" set /p XLSX=Enter XLSX path (project-relative or absolute): 

:: -----------------------------------------------------------------------
:: PATHS
:: -----------------------------------------------------------------------
set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
set "PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe"
set "CLI=%PROJECT_ROOT%\python\cli.py"

cd /d "%PROJECT_ROOT%"

echo XLSX    : %XLSX%
echo.

:: -----------------------------------------------------------------------
:: TODAY in MMDDYY via direct %date% slice -- US locale: "Thu 05/21/2026"
::   %date:~4,2%  = MM
::   %date:~7,2%  = DD
::   %date:~12,2% = YY
:: -----------------------------------------------------------------------
set "TODAY=%date:~4,2%%date:~7,2%%date:~12,2%"
set "TODAY_DB=%PROJECT_ROOT%\models\%TODAY%catalog.db"

:: -----------------------------------------------------------------------
:: CATALOG DATE CHECK
:: Today's catalog exists  -- skip to ingest (backup + summary already done)
:: Today's catalog missing -- copy latest, run summary once, pause to review
:: -----------------------------------------------------------------------
if exist "%TODAY_DB%" goto :ingest

:: Find latest catalog -- take first result from descending name sort
set "SOURCE_DB="
for /f "delims=" %%f in ('dir /b /o-n "%PROJECT_ROOT%\models\*catalog.db" 2^>nul') do (
    set "SOURCE_DB=%PROJECT_ROOT%\models\%%f"
    goto :found_source
)
:found_source

if "%SOURCE_DB%"=="" (
    echo [ERROR] No existing catalog found in models\. Cannot create backup.
    goto :done
)

echo [BACKUP] New catalog day -- copying to %TODAY%catalog.db
echo          Source: %SOURCE_DB%
copy "%SOURCE_DB%" "%TODAY_DB%" >nul
if errorlevel 1 (
    echo [ERROR] Backup copy failed. Ingest cancelled.
    goto :done
)
echo          Done.
echo.

echo [SUMMARY] Catalog baseline for today...
echo.
"%PYTHON%" "%CLI%" catalog-summary
if errorlevel 1 (
    echo.
    echo [ERROR] catalog-summary failed. Check output above.
    goto :done
)

echo.
echo -----------------------------------------------------------------------
echo  Catalog state above is your baseline for today.
echo  Press any key to proceed  --  close window to CANCEL.
echo -----------------------------------------------------------------------
pause > nul
echo.

:: -----------------------------------------------------------------------
:: INGEST
:: -----------------------------------------------------------------------
:ingest
echo [INGEST] Running add-pattern...
echo.
"%PYTHON%" "%CLI%" add-pattern --xlsx "%XLSX%"
if errorlevel 1 (
    echo.
    echo [ERROR] add-pattern failed. Catalog unchanged -- check output above.
    goto :done
)

:: -----------------------------------------------------------------------
:: ARCHIVE  (only runs if ingest succeeded)
:: Appends XLSX to data\processed\YYYY-MM.zip and deletes from
:: data\historical_patterns\. Zip write is verified before delete.
:: -----------------------------------------------------------------------
echo.
echo [ARCHIVE] Archiving pattern file...
echo.
"%PYTHON%" "%CLI%" archive-pattern --xlsx "%XLSX%"
if errorlevel 1 (
    echo.
    echo [ERROR] archive-pattern failed -- XLSX still in data\historical_patterns\.
    echo         Check output above and archive manually if needed.
    goto :done
)

echo.
echo =======================================================================
echo  DONE  --  pattern ingested and archived.
echo =======================================================================

:done
echo.
pause
