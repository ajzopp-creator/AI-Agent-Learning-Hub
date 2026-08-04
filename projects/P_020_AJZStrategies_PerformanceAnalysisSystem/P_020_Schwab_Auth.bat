@ECHO OFF
SETLOCAL

:: P_020 Schwab Re-Authentication (WO-P020-E1.010)
:: Runs the shared login module via cli.py auth --project P_020.
:: Writes the token directly to config\P_020_schwab_token.json --
:: the file the rest of P_020 actually reads from. Old standalone script
:: (P_020_Schwab_Auth.py) is retired -- see python\api\_RETIRED_P_020_Schwab_Auth.py.
::
:: To (re)issue P_400's token instead, run from this same folder:
::   python\database\cli.py auth --project P_400
::
:: Double-click to run from project root.

SET PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
SET CLI_DIR=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database

ECHO.
ECHO ============================================
ECHO  P_020 — Schwab Re-Authentication
ECHO ============================================
ECHO.
ECHO A browser window will open automatically.
ECHO Log in with your Schwab credentials there.
ECHO Everything else is automatic -- nothing to copy/paste.
ECHO.

PUSHD "%CLI_DIR%"
"%PYTHON%" cli.py auth --project P_020
SET ERR=%ERRORLEVEL%
POPD

IF %ERR% NEQ 0 (
    ECHO.
    ECHO ERROR: Authentication failed. Check output above.
    PAUSE
    EXIT /B 1
)

ECHO.
ECHO ============================================
ECHO  Done. Token saved.
ECHO ============================================
ECHO.
PAUSE
