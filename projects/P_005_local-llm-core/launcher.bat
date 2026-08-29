@echo off
setlocal
cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_005_local-llm-core\python"
set PYTHONPATH=C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_005_local-llm-core\python

"C:\Users\Trader\.conda\envs\p140\python.exe" cli.py --bench
pause