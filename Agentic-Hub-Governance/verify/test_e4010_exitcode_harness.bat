@echo off
REM Independent review harness for WO-P300-E4.010
REM Reproduces the EXACT control-flow skeleton of P_300_DailyEval_v2.bat
REM (verified byte-for-byte against the real file via direct read) with
REM the two real python/CLI invocations replaced by controlled stand-ins:
REM   %1 = simulated exit code for STEP 1 (daily-evaluate)
REM   %2 = simulated exit code for STEP 2 (archive-eval)
REM Proves EXIT_CODE plumbing + goto :done short-circuit + exit /b,
REM without touching python.exe, the real CLI, or any live data.

set "STEP1_CODE=%~1"
set "STEP2_CODE=%~2"
set "EXIT_CODE=0"
set "STEP2_RAN=NO"

echo [STEP 1] Running Pipeline B evaluation (simulated exit %STEP1_CODE%)...
cmd /c "exit /b %STEP1_CODE%"
if errorlevel 1 (
    echo.
    echo [ERROR] daily-evaluate failed.
    set "EXIT_CODE=1"
    goto :done
)

set "STEP2_RAN=YES"
echo [STEP 2] Archiving eval file (simulated exit %STEP2_CODE%)...
cmd /c "exit /b %STEP2_CODE%"
if errorlevel 1 (
    echo.
    echo [ERROR] archive-eval failed -- XLSX still in data\live\.
    set "EXIT_CODE=1"
    goto :done
)

echo DONE -- both steps ran and passed.

:done
echo STEP2_RAN=%STEP2_RAN%
echo FINAL_EXIT_CODE=%EXIT_CODE%
exit /b %EXIT_CODE%
