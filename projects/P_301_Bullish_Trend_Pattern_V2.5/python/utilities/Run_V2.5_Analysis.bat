@echo off
echo.
echo =====================================================
echo   BULLISH TREND PATTERN PROJECT V2.5 - MCP LAUNCHER
echo =====================================================
echo.

echo [1] Listing files in data\live\...
dir "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_301_Bullish_Trend_Pattern_V2.5\data\live"

echo.
echo [2] Running V2.5 MCP Analysis + Auto-Archive...
cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_301_Bullish_Trend_Pattern_V2.5\python"
python V2.5_MCP_Launcher.py

echo.
echo =====================================================
echo Workflow complete.
pause