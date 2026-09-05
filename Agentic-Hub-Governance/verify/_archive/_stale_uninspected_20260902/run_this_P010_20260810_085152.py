"""
peh verify script -- P_010, WO-P010-E1.003 toast fix (v2, BurntToast)
Generated: 2026-08-10 08:51:52

v1 (NotifyIcon.ShowBalloonTip) was confirmed broken -- PowerShell call
returned success but no balloon ever rendered, because NotifyIcon needs an
active Windows message loop this script doesn't have. This tests v2
(BurntToast) actually fires a real, visible toast -- something no automated
check can fully confirm. The script's own checks cover the mechanics (import
succeeds, PowerShell call returns 0); Tony's eyes on the screen are the only
real confirmation that a toast rendered this time.
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture")
PY_DIR = PROJECT_ROOT / "python"
sys.path.insert(0, str(PY_DIR))

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label} -- {detail}")
        failures.append(label)


print("=" * 70)
print("P_010 TOAST FIX VERIFICATION (v2, BurntToast)")
print("=" * 70)

try:
    import toast_notify
    check("toast_notify module imports cleanly", True)
except Exception as e:
    check("toast_notify module imports cleanly", False, str(e))
    Path(__file__).with_suffix(".py.done").write_text(
        f"STATUS: FAIL\nEXIT_CODE: 1\nTIMESTAMP: {datetime.now().isoformat()}\n", encoding="utf-8")
    sys.exit(1)

print()
print("  >>> WATCH YOUR SCREEN NOW -- firing a real toast via BurntToast.")
print("      Look bottom-right, standard Windows 10/11 toast notification")
print("      area (not the system tray -- that was the old, broken method).")
print()

result = toast_notify.send_toast(
    "P_010 Toast Fix Verification",
    f"If you can read this, BurntToast is working. Sent at {datetime.now().strftime('%H:%M:%S')}."
)
check("send_toast() returned True (PowerShell call exit code 0)", result is True, f"got {result}")

print()
print("=" * 70)
status = "FAIL" if failures else "PASS"
exit_code = 1 if failures else 0
Path(__file__).with_suffix(".py.done").write_text(
    f"STATUS: {status}\nEXIT_CODE: {exit_code}\nTIMESTAMP: {datetime.now().isoformat()}\n",
    encoding="utf-8"
)
if failures:
    print(f"FAIL: {len(failures)} check(s) failed -- {failures}")
    sys.exit(1)
else:
    print("PASS (mechanics only -- Tony must confirm the toast was actually VISIBLE)")
    sys.exit(0)
