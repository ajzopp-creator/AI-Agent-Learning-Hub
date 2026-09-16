"""
run_this_P400_20260914_133655.py

Verifies: `cli.py compare ADP` (options-first vehicle selection, Must #13
of p400-project-context) runs cleanly and returns a recognizable vehicle
recommendation. Self-contained; never modifies production files.
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

VEHICLE_TOKENS = ["STOCK", "OPTION", "SPREAD", "NEITHER"]


def write_done(status: str, exit_code: int) -> None:
    with open(DONE_PATH, "w", encoding="utf-8") as f:
        f.write(f"timestamp={datetime.now().isoformat()}\n")
        f.write(f"status={status}\n")
        f.write(f"exit_code={exit_code}\n")


def main() -> None:
    try:
        result = subprocess.run(
            [
                PYTHON_EXE,
                "cli.py",
                "compare",
                "ADP",
                "--snapshot",
                "snapshot_ADP.json",
                "--chain",
                "chain_ADP.json",
                "--cash",
                "16729.05",
            ],
            cwd=str(PROJECT_PYTHON_DIR),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        print("STDOUT so far:", exc.stdout)
        print("STDERR so far:", exc.stderr)
        write_done("FAIL", -1)
        print("FAIL: cli.py compare ADP exceeded 120s local timeout")
        sys.exit(1)

    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)

    if result.returncode != 0:
        write_done("FAIL", result.returncode)
        print(f"FAIL: cli.py compare ADP exited {result.returncode}")
        sys.exit(1)

    upper_out = result.stdout.upper()
    if not any(token in upper_out for token in VEHICLE_TOKENS):
        write_done("FAIL", 1)
        print("FAIL: no recognizable vehicle recommendation (STOCK/OPTION/SPREAD/NEITHER) in output")
        sys.exit(1)

    write_done("PASS", 0)
    print("PASS")


if __name__ == "__main__":
    main()
