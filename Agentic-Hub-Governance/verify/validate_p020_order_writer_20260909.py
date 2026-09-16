import py_compile
import sys

target = r"C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python_utils\p020_order_writer.py"
result_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\validate_p020_order_writer_result.txt"

try:
    py_compile.compile(target, doraise=True)
    with open(result_path, "w") as f:
        f.write("PASS\n")
except Exception as e:
    with open(result_path, "w") as f:
        f.write("FAIL: " + str(e) + "\n")
    sys.exit(1)
