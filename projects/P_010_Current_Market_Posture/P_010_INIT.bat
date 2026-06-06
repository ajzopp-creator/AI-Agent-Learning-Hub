@echo off
REM P_010 Initialization Wrapper
REM Usage: P_010_INIT daily  (or "intraday")

setlocal

cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture"

if /i "%1"=="daily" (
    echo.
    echo ========================================
    echo RUNNING P_010 DAILY POSTURE (9:30 AM)
    echo ========================================
    echo.
    call P_010_daily_posture.bat
    goto :end
)

if /i "%1"=="intraday" (
    echo.
    echo ========================================
    echo RUNNING P_010 INTRADAY VP CHECK (2 PM+)
    echo ========================================
    echo.
    call P_010_run_intraday_vp_check.bat
    goto :end
)

REM If no valid parameter, show usage
echo.
echo ========================================
echo P_010 INITIALIZATION
echo ========================================
echo.
echo Usage:
echo   P_010_INIT daily      - Run morning posture (9:30 AM)
echo   P_010_INIT intraday   - Run intraday VP check (2 PM+)
echo.
echo Current files:
echo   - P_010_RiskConfig.json
type P_010_RiskConfig.json 2>nul
echo.
echo   - Latest intraday check:
dir /b /o-d outputs\intraday_vp_check_*.json 2>nul | findstr /n "^" | findstr "^1:"
echo.

:end
endlocal
