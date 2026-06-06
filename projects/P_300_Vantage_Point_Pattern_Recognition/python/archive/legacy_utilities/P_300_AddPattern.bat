@echo off
color 0B
TITLE P_300 Pattern Vault Engine (v1.4)
echo =======================================================================
echo                 P_300 VANTAGE POINT PATTERN VAULTING
echo =======================================================================
echo.

:: 1. SET THE ABSOLUTE PROJECT ROOT
set "PROJECT_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"

:: 2. DEFINE THE TARGET SCRIPT
set "LAUNCHER=%PROJECT_ROOT%\python\utilities\P_300_00_AddPatternLauncher.ps1"

echo [ARCHITECTURAL HANDOFF] Launching: 
echo %LAUNCHER%
echo.

:: 3. EXECUTE WITHOUT DOUBLE-NESTING
powershell.exe -ExecutionPolicy Bypass -File "%LAUNCHER%"

echo.
echo =======================================================================
echo                     PIPELINE EXECUTION COMPLETE
echo =======================================================================
echo.
pause