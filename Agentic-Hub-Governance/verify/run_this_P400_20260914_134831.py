"""
run_this_P400_20260914_134831.py

Verifies: `cli.py evaluate ADP` (five-role council verdict) runs cleanly
with vehicle=STOCK passed through from the prior `compare` result (Must
#13, p400-project-context), and returns a recognized verdict tier.
Self-contained; never modifies production files.
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_PYTHON_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python"
)
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"
DONE_PATH = Path(__file__).with_name(Path(__file__).name + ".done")

VERDICT_TOKENS = [
    "APPROVED_WITH_SEVERE_WARNING",
    "APPROVED_WITH_CAUTION",
    "APPROVED",
    "BLOCKED",
]

CASH = "16729.05"


def write_done(status: str, exit_code: int) -> None:
    with open(DONE_PATH, "w", encoding="utf-8") as f:
        f.write(f"timestamp={datetime.now().isoformat()}\n")
        f.write(f"status={status}\n")
        f.write(f"exit_code={exit_code}\n")


def run(args):
    return subprocess.run(
        [PYTHON_EXE] + args,
        cwd=str(PROJECT_PYTHON_DIR),
        capture_output=True,
        text=True,
        timeout=120,
    )


def main() -> None:
    # STOCK vehicle = default evaluate path (no --options/--spread).
    # CLI requires --snapshot and --cash; there is no --vehicle flag.
    result = run([
        "cli.py",
        "evaluate",
        "ADP",
        "--snapshot",
        "snapshot_ADP.json",
        "--cash",
        CASH,
    ])

    if result.returncode != 0:
        print("First attempt failed, checking `cli.py evaluate --help` for correct usage:")
        help_result = run(["cli.py", "evaluate", "--help"])
        print("HELP STDOUT:")
        print(help_result.stdout)
        print("HELP STDERR:")
        print(help_result.stderr)
        print("ORIGINAL ATTEMPT STDOUT:")
        print(result.stdout)
        print("ORIGINAL ATTEMPT STDERR:")
        print(result.stderr)
        write_done("FAIL", result.returncode)
        print(
            "FAIL: cli.py evaluate ADP --snapshot snapshot_ADP.json --cash "
            f"{CASH} exited {result.returncode} -- see help output above, "
            "correct this script's invocation (do not touch production code "
            "unless the help output shows a real evaluate_signal.py/council.py error)."
        )
        sys.exit(1)

    # Stock-path evaluate caches spec_text but does not print it. `spec`
    # is the SIP next step after APPROVED and prints "Stock OCO Bracket".
    spec_result = run([
        "cli.py",
        "spec",
        "ADP",
        "--snapshot",
        "snapshot_ADP.json",
        "--cash",
        CASH,
    ])
    combined_stdout = (result.stdout or "") + "\n" + (spec_result.stdout or "")
    combined_stderr = (result.stderr or "") + "\n" + (spec_result.stderr or "")

    print("STDOUT:")
    print(combined_stdout)
    print("STDERR:")
    print(combined_stderr)

    if spec_result.returncode != 0:
        write_done("FAIL", spec_result.returncode)
        print(f"FAIL: cli.py spec ADP exited {spec_result.returncode}")
        sys.exit(1)

    upper_out = combined_stdout.upper()
    matched = [tok for tok in VERDICT_TOKENS if tok in upper_out]
    if not matched:
        write_done("FAIL", 1)
        print("FAIL: no recognized verdict tier in output")
        sys.exit(1)

    if "STOCK" not in upper_out:
        write_done("FAIL", 1)
        print("FAIL: output does not show vehicle=STOCK passed through from compare")
        sys.exit(1)

    write_done("PASS", 0)
    print(f"PASS (verdict tier found: {matched[0]})")


if __name__ == "__main__":
    main()
