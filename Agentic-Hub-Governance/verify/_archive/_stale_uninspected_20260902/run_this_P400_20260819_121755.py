"""Compile check for WO-P400-E6.004's second revision -- config.py window
shrink (83/7 -> 7/5) and earnings_lookup.py's missing-symbol behavior
change (skip -> confirmed-clear entry). Self-contained per peh-handoff
v1.4, never modifies production files.
"""
import py_compile
import sys

FILES = [
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python\config.py",
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python\application\earnings_lookup.py",
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
