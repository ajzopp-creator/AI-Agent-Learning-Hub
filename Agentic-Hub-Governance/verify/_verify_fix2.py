import ast
path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database\domain\order_reconciler.py"
with open(path, "r", encoding="utf-8") as f:
    src = f.read()
try:
    ast.parse(src)
    result = "PARSE OK"
except SyntaxError as e:
    result = f"SYNTAX ERROR: {e}"

import sys
sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database")
try:
    import domain.order_reconciler as m
    result += f"\nIMPORT OK, compute_exit_pnl = {m.compute_exit_pnl}"
except Exception as e:
    result += f"\nIMPORT ERROR: {type(e).__name__}: {e}"

with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_verify_fix2.txt", "w") as f:
    f.write(result)