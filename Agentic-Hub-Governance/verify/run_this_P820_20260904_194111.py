"""
P_820 override-order capture: write CRUS discretionary override to the vault.
WO-P820-E1.001. This is a REAL production write via write_to_vault("P820", ...),
not a test -- it is the actual record for a live paper trade. Never modifies
any other production file.
"""
import sys
import os
import glob
from datetime import datetime

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DONE_PATH = os.path.abspath(__file__) + ".done"


def write_done(status: str, exit_code: int) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DONE_PATH, "w", encoding="utf-8") as f:
        f.write(f"timestamp: {ts}\nstatus: {status}\nexit_code: {exit_code}\n")


def fail(msg: str, code: int = 1):
    print("FAIL:", msg)
    write_done("FAIL", code)
    sys.exit(code)


try:
    from shared_resources.python_utils.vault_interface import write_to_vault
except Exception as exc:
    fail(f"import error: {exc!r}")

FIELDS = {
    "symbol": "CRUS",
    "signal_date": "2026-09-04",
    "why_code": "P_300",
    "entry_price": 113.45,
    "stop_price": 109.80,
    "target_price": 119.94,
    "notes": (
        "Discretionary override -- P_300 signal BLOCKED on R:R ~1.78:1 in "
        "P_400 Council, no eval_cache present for symbol on disk. PAPER "
        "trade, 10 shares. Logged via P_820 override path, WO-P820-E1.001."
    ),
    "written_by": "P_820/chat_dictation",
}

vault_dir = r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\P820"
before = set(glob.glob(os.path.join(vault_dir, "*CRUS*")))

try:
    result = write_to_vault("P820", FIELDS)
except Exception as exc:
    fail(f"write_to_vault raised: {exc!r}")

if not result:
    fail("write_to_vault returned False (likely skipped)")

after = set(glob.glob(os.path.join(vault_dir, "*CRUS*")))
new_files = after - before
candidate_files = new_files if new_files else after

if not candidate_files:
    fail(f"no CRUS note found in {vault_dir} after write_to_vault returned True")

note_path = sorted(candidate_files)[-1]

with open(note_path, "r", encoding="utf-8") as f:
    written = f.read()

required_substrings = ["CRUS", "P_300", "113.45", "109.8", "119.94", "Discretionary override"]
missing = [s for s in required_substrings if s not in written]
if missing:
    print("--- Note content ---")
    print(written)
    fail(f"written note missing expected content: {missing}")

print("--- Note path ---")
print(note_path)
print("--- Note content ---")
print(written)
print("PASS")
write_done("PASS", 0)
