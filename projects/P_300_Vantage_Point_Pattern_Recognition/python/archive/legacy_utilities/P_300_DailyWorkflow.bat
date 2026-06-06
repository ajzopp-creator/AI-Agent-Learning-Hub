@echo off
TITLE P_300 Daily Decision Engine (v1.1)
echo --- Starting P_300 Daily Pattern Analysis ---

:: 1. Run the Combined Evaluation Script (v1.1)
:: This handles: Convert v4 -> Posture Scan -> Z-Score Math -> P_000 Sizing
"C:\Users\Trader\.conda\envs\p140\python.exe" "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities\P_300_EvaluateTrade.py"

echo.
echo --- Workflow Complete ---
pause