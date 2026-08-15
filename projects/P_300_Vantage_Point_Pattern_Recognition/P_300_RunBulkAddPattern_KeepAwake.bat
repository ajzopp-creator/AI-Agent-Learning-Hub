@echo off
setlocal
REM P_300_RunBulkAddPattern_KeepAwake.bat
REM
REM Wraps P_300_RunBulkAddPattern.ps1: captures whatever the machine's current
REM AC and DC sleep-after-inactivity settings actually are, disables sleep for
REM the duration of the run, then restores exactly what was captured -- no
REM hardcoded assumption about what "default" is.
REM
REM Why this exists: 2026-08-05/06 overnight BulkAddPattern run hit 8 separate
REM Modern Standby cycles (confirmed via Kernel-Power event log, IDs 506/507),
REM totaling ~8.5 of a 9.5-hour run. AC was already set to Never (0) -- the
REM actual trigger was the DC (battery) timeout at 30 min, since the machine
REM was unplugged overnight. Windows' sleep timer runs off keyboard/mouse
REM idle time, not CPU load, so a CPU-pegged Python process does not by
REM itself prevent this.

set PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition

echo Capturing current sleep-after-inactivity settings...
for /f "tokens=2 delims=:" %%A in ('powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE ^| findstr /C:"Current AC Power Setting Index"') do set AC_HEX=%%A
for /f "tokens=2 delims=:" %%A in ('powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE ^| findstr /C:"Current DC Power Setting Index"') do set DC_HEX=%%A
set /a AC_SEC=%AC_HEX%
set /a DC_SEC=%DC_HEX%
set /a AC_MIN=AC_SEC/60
set /a DC_MIN=DC_SEC/60
echo   Current: AC=%AC_MIN% min, DC=%DC_MIN% min (0 = Never)

echo Disabling sleep-on-inactivity for this run (AC and DC)...
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0

echo.
echo Running P_300_RunBulkAddPattern.ps1...
echo.
powershell -File "%PROJECT_ROOT%\P_300_RunBulkAddPattern.ps1"
set RUN_EXIT=%ERRORLEVEL%

echo.
echo Restoring sleep-after-inactivity: AC=%AC_MIN% min, DC=%DC_MIN% min...
powercfg /change standby-timeout-ac %AC_MIN%
powercfg /change standby-timeout-dc %DC_MIN%

echo Done. BulkAddPattern exit code: %RUN_EXIT%
exit /b %RUN_EXIT%
