@echo off
REM ─────────────────────────────────────────────────────────────
REM  P_115 Backfill Launcher
REM  Double-click to run, or pass flags:
REM    launch_backfill.bat --dry-run
REM    launch_backfill.bat --limit 10
REM    launch_backfill.bat --overwrite
REM ─────────────────────────────────────────────────────────────

SET PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
SET SCRIPTS=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts

cd /d "%SCRIPTS%"
"%PYTHON%" -m p115_backfill.cli %*
pause
