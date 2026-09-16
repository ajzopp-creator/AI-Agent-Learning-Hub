@echo off
REM -----------------------------------------------------------------
REM  P_805 Consensus Dashboard Launcher
REM  Run after the 9:15 AM P_805 pipeline. Double-click to run.
REM -----------------------------------------------------------------

SET PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
SET PYFOLDER=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\python

cd /d "%PYFOLDER%"
"%PYTHON%" -m p805_consensus.cli
pause