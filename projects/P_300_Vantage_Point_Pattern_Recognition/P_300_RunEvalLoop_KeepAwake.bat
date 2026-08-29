@echo off
setlocal
REM P_300_RunEvalLoop_KeepAwake.bat
REM
REM Wraps run_eval_loop.py directly (NOT run_eval_loop.bat -- that file ends
REM in `pause`, which would hang forever on an unattended overnight run with
REM nobody there to press a key). Same capture/disable/restore sleep pattern
REM as P_300_RunBulkAddPattern_KeepAwake.bat: captures whatever the machine's
REM current AC/DC sleep-after-inactivity settings actually are, disables
REM sleep for the run, restores exactly what was captured -- no hardcoded
REM assumption about what "default" is.
REM
REM Why this exists: run_eval_loop.py's walk-forward scoring calls
REM similarity.rank_by_distance() live per pattern (no topk_cache in this
REM path) against each pattern's own date-filtered prior corpus. WO-P300-
REM E5.004 measured this same uncached DTW-search shape at ~24h for 14,812
REM patterns; this catalog is 44,399 patterns now (3x, and each pattern's
REM own corpus grows with catalog size). Real overnight-or-longer job --
REM same sleep risk as the BulkAddPattern incident this pattern was built
REM for (2026-08-05/06: 8 Modern Standby cycles across a 9.5h run, AC was
REM already Never but DC/battery timeout at 30 min fired since the machine
REM was unplugged -- Windows' sleep timer runs off keyboard/mouse idle, not
REM CPU load, so a CPU-pegged Python process does not by itself prevent it).
REM
REM Usage: P_300_RunEvalLoop_KeepAwake.bat [buy-min-z-override]
REM   (no arg)  -> config.py BUY_MIN_Z_SCORE default (current production gate)
REM   1.0       -> example override, e.g. P_300_RunEvalLoop_KeepAwake.bat 1.0
REM No pause at the end -- this is meant to finish and restore sleep settings
REM unattended; check outputs\reports\eval\ for the report when you're back.

set PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition
set PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
set SCRIPT=%PROJECT_ROOT%\python\application\run_eval_loop.py
set BUYMINZ=%~1

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
echo =======================================================================
echo  P_300 WALK-FORWARD EVAL LOOP -- STAGE 6 (Keep-Awake wrapper)
echo =======================================================================
echo Read-only against the catalog. This can run for a very long time on
echo the current 44,399-pattern catalog (no topk_cache in this path) --
echo overnight or longer, based on WO-P300-E5.004's uncached-DTW precedent.
echo.

if "%BUYMINZ%"=="" (
    "%PYTHON%" "%SCRIPT%"
) else (
    "%PYTHON%" "%SCRIPT%" --buy-min-z %BUYMINZ%
)
set RUN_EXIT=%ERRORLEVEL%

echo.
echo Restoring sleep-after-inactivity: AC=%AC_MIN% min, DC=%DC_MIN% min...
powercfg /change standby-timeout-ac %AC_MIN%
powercfg /change standby-timeout-dc %DC_MIN%

echo Done. run_eval_loop.py exit code: %RUN_EXIT%
exit /b %RUN_EXIT%
