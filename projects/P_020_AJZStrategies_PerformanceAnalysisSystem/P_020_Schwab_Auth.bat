@ECHO OFF
SETLOCAL

:: P_020 Schwab Re-Authentication
:: Runs the project's own auto-auth script (UIAutomation callback capture,
:: no copy-paste). Writes the token directly to config\P_020_schwab_token.json
:: -- the file the rest of P_020 actually reads from.
::
:: Do NOT use integrations\schwab_api\P_020_Schwab_Auth.bat for this project --
:: that one is a separate hub-level manual-flow tool that writes to a
:: different credentials file and requires copy-pasting the redirect URL.
::
:: Double-click to run from project root.

SET PYTHON=C:\Users\Trader\.conda\envs\p140\python.exe
SET SCRIPT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\api\P_020_Schwab_Auth.py

ECHO.
ECHO ============================================
ECHO  P_020 — Schwab Re-Authentication
ECHO ============================================
ECHO.
ECHO A browser window will open automatically.
ECHO Log in with your Schwab credentials there.
ECHO Everything else is automatic -- nothing to copy/paste.
ECHO.

"%PYTHON%" "%SCRIPT%"

IF %ERRORLEVEL% NEQ 0 (
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
