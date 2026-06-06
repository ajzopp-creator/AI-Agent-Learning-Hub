@echo off
REM Global P_010 Initializer
REM Can be run from anywhere

if /i "%1"=="" (
    echo Usage: INIT daily  OR  INIT intraday
    exit /b 1
)

cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture"
call P_010_INIT.bat %1
