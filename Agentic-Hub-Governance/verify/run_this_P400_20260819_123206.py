"""Compile check for WO-P400-E6.006 -- surface options-council reasoning in
batch-2b's printed table (vehicle_reason field threaded through
schemas.py/batch_2b_scoring.py/batch_2b.py). Self-contained per
peh-handoff v1.4, never modifies production files.
"""
import py_compile
import sys

FILES = [
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python\schemas.py",
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
