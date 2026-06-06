@ECHO OFF
SETLOCAL

:: P_020 Create Database — Phase 3A
:: Runs init-db then verify to confirm setup
:: Double-click to run from project root

SET PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
SET CLI=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database\cli.py

ECHO.
ECHO ============================================
ECHO  P_020 — Database Initialization
ECHO ============================================
ECHO.

ECHO [1/2] Creating database, tables, and seed data...
"%PYTHON%" "%CLI%" init-db
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO ERROR: init-db failed. Check output above.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO [2/2] Verifying database...
"%PYTHON%" "%CLI%" verify
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO ERROR: verify failed. Check output above.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO ============================================
ECHO  Setup complete. Database is ready.
ECHO ============================================
ECHO.
PAUSE
