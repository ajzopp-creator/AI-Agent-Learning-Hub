@ECHO OFF
SETLOCAL

:: P_020 Schwab Re-Authentication (WO-P020-E1.010)
:: Runs the shared login module via cli.py auth --project ALL --
:: ONE browser login, propagated to every registered project's token file
:: (currently P_020 + P_400). Updated 2026-08-09: single-project mode
:: (--project P_020 alone) re-grants against the shared app registration
:: and silently kills the OTHER project's token without replacing it --
:: ALL is now the standard path. See WO-P020-E1.010 SCOPE AMENDMENT.
:: Old standalone script (P_020_Schwab_Auth.py) is retired -- see
:: python\api\_RETIRED_P_020_Schwab_Auth.py.
::
:: To reauth only one project (rare -- breaks the other's token):
::   python\database\cli.py auth --project P_020
::   python\database\cli.py auth --project P_400
::
:: Double-click to run from project root.

SET PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
SET CLI_DIR=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database

ECHO.
ECHO ============================================
ECHO  P_020 — Schwab Re-Authentication (ALL projects)
ECHO ============================================
ECHO.
ECHO A browser window will open automatically.
ECHO Log in with your Schwab credentials there.
ECHO One login covers every registered project -- nothing else to do.
ECHO.

PUSHD "%CLI_DIR%"
"%PYTHON%" cli.py auth --project ALL
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
ECHO  Done. All projects share one token.
ECHO ============================================
ECHO.
PAUSE
