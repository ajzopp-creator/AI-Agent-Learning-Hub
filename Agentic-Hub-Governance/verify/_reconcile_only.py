import os
import subprocess

STATEMENT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\tos_exports\paper\D_020_2026-07-27_YTD_AccountStatement.csv"
PY = r"C:\Users\Trader\.conda\envs\p140\python.exe"
CLI_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"

env = os.environ.copy()
env["PYTHONPATH"] = r"C:\Users\Trader\AI-Agent-Learning-Hub"
result = subprocess.run(
    [PY, "cli.py", "reconcile", "--paper", "--statement", STATEMENT],
    cwd=CLI_DIR, env=env, capture_output=True, text=True, timeout=100,
)
with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_reconcile_only.txt", "w") as f:
    f.write(f"exit code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")