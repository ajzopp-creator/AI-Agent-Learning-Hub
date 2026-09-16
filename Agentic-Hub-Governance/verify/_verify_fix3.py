import ast
path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database\infrastructure\db_order_writer.py"
with open(path, "r", encoding="utf-8") as f:
    src = f.read()
try:
    ast.parse(src)
    result = "PARSE OK"
except SyntaxError as e:
    result = f"SYNTAX ERROR: {e}"
with open(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\_verify_fix3.txt", "w") as f:
    f.write(result)