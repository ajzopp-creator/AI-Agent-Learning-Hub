@echo off
REM P_020_Schwab_Auth.bat
REM Location: AI-Agent-Learning-Hub\integrations\schwab_api\

SET PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
SET SCRIPT_DIR=%~dp0
SET LOG=%SCRIPT_DIR%schwab_auth_log.txt

cd /d %SCRIPT_DIR%

IF "%1"=="" (
    echo.
    echo Usage: P_020_Schwab_Auth.bat [auth / check / test]
    echo.
    echo   auth   = First-time Schwab login
    echo   check  = Check token, refresh if needed
    echo   test   = Test live API connection
    echo.
    pause
    exit /b 1
)

echo Running: %1 > "%LOG%"
%PYTHON% -u cli.py %1 >> "%LOG%" 2>&1

echo.
type "%LOG%"
echo.

IF %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Command failed. Check messages above.
) ELSE (
    echo [OK] Command completed.
)
echo.
pause
