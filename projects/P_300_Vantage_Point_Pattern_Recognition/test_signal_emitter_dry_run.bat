@echo off
REM TEST: signal_emitter dry-run via p140 conda env
REM Prepends p140 to PATH, then runs the test script

setlocal enabledelayedexpansion

set PATH=C:\Users\Trader\.conda\envs\p140;%PATH%

cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"

echo Testing signal_emitter with p140 Python...
echo.

python test_signal_emitter_dry_run.py

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Dry-test passed. Ready for live test.
) else (
    echo.
    echo [FAILED] See error above.
)

pause
