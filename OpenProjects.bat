@echo off
SET "HUB=C:\Users\Trader\AI-Agent-Learning-Hub\projects"
SET "P140=C:\Users\Trader\.conda\envs\p140"
SET "PATH=%P140%;%P140%\Scripts;%PATH%"

echo.
echo  ==========================================
echo   AJZ Strategies - AI-Agent-Learning-Hub
echo  ==========================================
echo.

REM --- Confirm active Python ------------------------------------------------
FOR /F "tokens=*" %%V IN ('"python --version" 2^>^&1') DO SET PYVER=%%V
echo   Python : %PYVER%
echo   Env    : %P140%
echo.
echo  ==========================================
echo.

echo  Hub Projects
echo  -------------------------
echo   1  D_130  TradetheBounce_OIL
echo   2  P_000  PythonClaudeLocalLLM
echo   3  P_010  Current_Market_Posture
echo   4  P_020  AJZStrategies
echo   5  P_115  BuytheDip
echo   6  P_300  VantagePoint_PatternRecognition
echo   7  P_301  Bullish_Trend_V2.5
echo   8  P_400  TradeManagement
echo   9  P_800  Automation_NoteTaking
echo   0  P_805  Email_TradeExtractor
echo.
choice /c 1234567890 /n /m "Select: "

if errorlevel 10 goto :dir0
if errorlevel 9  goto :dir9
if errorlevel 8  goto :dir8
if errorlevel 7  goto :dir7
if errorlevel 6  goto :dir6
if errorlevel 5  goto :dir5
if errorlevel 4  goto :dir4
if errorlevel 3  goto :dir3
if errorlevel 2  goto :dir2
if errorlevel 1  goto :dir1
goto :launch

:dir0
cd /d "%HUB%\P_805_Email_Trade_Extractor"
goto :launch
:dir9
cd /d "%HUB%\P_800_Automation_Note_Taking"
goto :launch
:dir8
cd /d "%HUB%\P_400_TradeManagementSystem"
goto :launch
:dir7
cd /d "%HUB%\P_301_Bullish_Trend_Pattern_V2.5"
goto :launch
:dir6
cd /d "%HUB%\P_300_Vantage_Point_Pattern_Recognition"
goto :launch
:dir5
cd /d "%HUB%\P_115_BuytheDipTradingSystem"
goto :launch
:dir4
cd /d "%HUB%\P_020_AJZStrategies_PerformanceAnalysisSystem"
goto :launch
:dir3
cd /d "%HUB%\P_010_Current_Market_Posture"
goto :launch
:dir2
cd /d "%HUB%\P_000_PythonClaudeLocalLLM"
goto :launch
:dir1
cd /d "%HUB%\D_130_TradetheBounce_OIL"
goto :launch

:launch
cmd /k
