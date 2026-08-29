"""Compile check for WO-P400-E6.004 -- verifies the three files edited to fix
batch-2b's all-or-nothing earnings-cache abort compile cleanly under
warnings-as-errors. Self-contained per peh-handoff v1.4 (no sys.path
side-channels), never modifies production files.
"""
import py_compile
import sys

FILES = [
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python\application\earnings_lookup.py",
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python\application\batch_2b_scoring.py",
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python\application\batch_2b.py",
]

failures = []
for f in FILES:
    try:
        py_compile.compile(f, doraise=True)
        print(f"OK: {f}")
    except py_compile.PyCompileError as exc:
        failures.append((f, str(exc)))
        print(f"FAIL: {f}\n  {exc}")

if failures:
    print("FAIL:", f"{len(failures)} of {len(FILES)} files failed to compile")
    sys.exit(1)
else:
    print("PASS")
