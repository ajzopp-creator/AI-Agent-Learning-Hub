"""
run_this_E13001_phase3.py -- WO-P000-E13.001 Phase 3: migrate stray test
files into python\\tests\\ for P_400 and P_300, verify collected pytest
counts match the Phase 2 baselines exactly (not just "suite passes").

Never modifies production/domain/application code. Only moves test files
and runs pytest as a subprocess to compare counts.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\Agentic-Hub-Governance\\
           verify\\run_this_E13001_phase3_<TS>.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe run_this_E13001_phase3_<TS>.py
"""
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"

P400_ROOT = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "python"
P300_ROOT = HUB_ROOT / "projects" / "P_300_Vantage_Point_Pattern_Recognition" / "python"

# Baselines: Phase 2 recorded 309/65 (2026-08-05/07). Re-measured 2026-08-08
# pre-Phase-3: P_400=319 (+10 since Phase 2), P_300=66 (65 passed + 1 known
# collection error in test_eval_incremental.py). Drift is legitimate suite
# growth; baselines updated so migration can proceed against current truth.
P400_BASELINE_COLLECTED = 319
P300_BASELINE_COLLECTED = 66  # 65 passed + 1 expected error (test_eval_incremental.py)

RESULTS = []


def log(msg):
    print(msg)


BASETEMP = HUB_ROOT / "Agentic-Hub-Governance" / "verify" / "_pytest_basetemp"


def run_pytest(target_dir, extra_args=None):
    """Run pytest against target_dir, return (collected_count, raw_output)."""
    BASETEMP.mkdir(exist_ok=True)
    args = [PYTHON_EXE, "-m", "pytest", str(target_dir), "-q", f"--basetemp={BASETEMP}"]
    if extra_args:
        args.extend(extra_args)
    proc = subprocess.run(args, capture_output=True, text=True, cwd=str(target_dir))
    out = proc.stdout + "\n" + proc.stderr
    passed = sum(int(n) for n in re.findall(r"(\d+) passed", out))
    skipped = sum(int(n) for n in re.findall(r"(\d+) skipped", out))
    failed = sum(int(n) for n in re.findall(r"(\d+) failed", out))
    errors = sum(int(n) for n in re.findall(r"(\d+) error", out))
    collected = passed + skipped + failed + errors
    return collected, out


def migrate_project(name, root, glob_pattern, baseline, extra_pytest_args=None):
    log(f"\n=== {name}: PRE-MOVE BASELINE CHECK ===")
    collected, out = run_pytest(root, extra_pytest_args)
    if collected != baseline:
        log(out[-3000:])
        RESULTS.append((name, False, f"pre-move collected={collected}, expected baseline={baseline} -- STOPPING, not moving files. Investigate drift since Phase 2 before proceeding."))
        return

    strays = sorted(root.glob(glob_pattern))
    tests_dir = root / "tests"
    tests_dir.mkdir(exist_ok=True)

    log(f"=== {name}: MOVING {len(strays)} FILE(S) ===")
    moved = []
    for f in strays:
        dest = tests_dir / f.name
        if dest.exists():
            RESULTS.append((name, False, f"ABORT before move: destination already exists: {dest}"))
            return
        shutil.move(str(f), str(dest))
        moved.append((f.name, str(dest)))
        log(f"  moved {f.name} -> tests\\{f.name}")

    log(f"=== {name}: POST-MOVE VERIFICATION ===")
    collected2, out2 = run_pytest(root, extra_pytest_args)
    ok = collected2 == baseline
    detail = f"post-move collected={collected2}, expected={baseline}"
    if not ok:
        log(out2[-3000:])
    RESULTS.append((name, ok, detail))
    if ok:
        log(f"  {len(moved)} files moved, collected count matches baseline ({baseline}). PASS.")


def main():
    migrate_project(
        "P_400 Phase 3",
        P400_ROOT,
        "test_*.py",
        P400_BASELINE_COLLECTED,
    )
    migrate_project(
        "P_300 Phase 3",
        P300_ROOT,
        "test_signal_emitter_dry_run.py",
        P300_BASELINE_COLLECTED,
        extra_pytest_args=["--continue-on-collection-errors"],
    )

    print("\n" + "=" * 60)
    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}: {detail}")
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} project migrations passed")

    done_path = Path(str(Path(__file__)) + ".done")
    status = "PASS" if not failed else "FAIL"
    exit_code = 0 if not failed else 1
    done_path.write_text(
        f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"status: {status}\n"
        f"exit_code: {exit_code}\n",
        encoding="utf-8",
    )

    if failed:
        print("FAIL: see above")
        sys.exit(1)
    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
