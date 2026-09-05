"""
run_this_E13001_phase4.py -- WO-P000-E13.001 Phase 4: repair P_400's
regression guard (test_p400_known_bugs.py) and sweep the sys.path
side-channel out of the other 15 files in the suite (Finding 8).

REQUIRES Phase 3 to have already run (files must already be in
python\\tests\\). Aborts if it detects Phase 3 has not happened.

What this does:
1. Full-content replace of tests\\test_p400_known_bugs.py from the
   validated sidecar (hash-verified before write). Converts the old
   RESULTS/check() harness to plain pytest asserts, makes ROOT derive
   from __file__ instead of a hardcoded drive letter, drops the two
   sys.path.insert() calls (redundant now that conftest.py handles it),
   and adds the missing E2.016 guard test (Finding 6).
2. Sweeps sys.path.insert(...) lines out of the other 15 test files in
   tests\\ -- mechanical line removal only, nothing else in each file is
   touched. Before/after occurrence counts are checked per file; a
   mismatch aborts that file's write rather than guessing.
3. Runs the full P_400 suite and reports: total collected count (expected
   310 = Phase 3's 309 baseline + 1 new E2.016 test -- an increase here
   is correct, not a regression), zero sys.path.insert remaining in the
   swept files, guard file's own 25 tests collected and passing.
4. Checks every row in .claude\\skills\\p400-project-context\\SKILL.md's
   Bugs Already Fixed table against the guard's test names for a match.
   Reports gaps, does not silently add tests for them (WO's own
   instruction, item 12).

Never modifies domain/application/config code. Only test files and the
guard.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\Agentic-Hub-Governance\\
           verify\\run_this_E13001_phase4_<TS>.py
           (sidecar: run_this_E13001_phase4_<TS>_guard_content.b64,
           same folder, must be transferred alongside this script)

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe run_this_E13001_phase4_<TS>.py
"""
import base64
import hashlib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"
P400_PY = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "python"
TESTS_DIR = P400_PY / "tests"
GUARD_PATH = TESTS_DIR / "test_p400_known_bugs.py"
SKILL_PATH = HUB_ROOT / ".claude" / "skills" / "p400-project-context" / "SKILL.md"

# Known-good hash of the validated new guard content (sandbox-built, py_compiled,
# compiled with warnings-as-errors -- see WO-P000-E13.001 Phase 4 handoff notes).
EXPECTED_GUARD_SHA256 = "f86d79f2e0c78851ae1b2b38817a7249c4354bee12dfae4c6d7e2f04358c6005"

# Files (in tests\ post-Phase-3) needing sys.path.insert removed, with
# their expected pre-sweep call count (from the Finding-8 grep).
SWEEP_TARGETS = {
    "test_build_option_spec.py": 1,
    "test_council.py": 2,
    "test_dispose_failed.py": 2,
    "test_evaluate_options.py": 1,
    "test_evaluate_spread.py": 1,
    "test_options_council.py": 1,
    "test_options_sizer.py": 1,
    "test_record_commands.py": 1,
    "test_record_writer_derived.py": 1,
    "test_record_writer.py": 1,
    "test_risk_vote.py": 2,
    "test_screen.py": 2,
    "test_sizing.py": 2,
    "test_spread_council.py": 2,
    "test_spread_sizer.py": 1,
}
EXPECTED_TOTAL_SWEPT_CALLS = sum(SWEEP_TARGETS.values())  # 21

# Phase 2 baseline was 309; live pre-Phase-3 count on 2026-08-08 is 319.
# Phase 4 adds one new guard test (E2.016) so post-Phase-4 expected is 320.
PHASE3_BASELINE_COLLECTED = 319
EXPECTED_POST_PHASE4_COLLECTED = 320  # +1 for the new E2.016 test

RESULTS = []


def log(msg):
    print(msg)


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    log(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" -- {detail}" if detail and not ok else ""))


def run_pytest(target, extra_args=None):
    # target may be a directory (full suite) or a single test file (guard alone).
    # cwd must always be a directory -- use parent when target is a file.
    target_path = Path(target)
    cwd = str(target_path if target_path.is_dir() else target_path.parent)
    args = [PYTHON_EXE, "-m", "pytest", str(target_path), "-q"]
    if extra_args:
        args.extend(extra_args)
    proc = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    out = proc.stdout + "\n" + proc.stderr
    passed = sum(int(n) for n in re.findall(r"(\d+) passed", out))
    skipped = sum(int(n) for n in re.findall(r"(\d+) skipped", out))
    failed = sum(int(n) for n in re.findall(r"(\d+) failed", out))
    errors = sum(int(n) for n in re.findall(r"(\d+) error", out))
    collected = passed + skipped + failed + errors
    return collected, passed, failed, errors, out


def main():
    script_dir = Path(__file__).parent
    b64_sidecar = script_dir / (Path(__file__).stem + "_guard_content.b64")

    # --- Phase 3 precondition check ---
    if not (TESTS_DIR / "test_council.py").exists():
        check("phase3_precondition", False,
              "python\\tests\\test_council.py not found -- Phase 3 migration "
              "must complete before Phase 4 runs. Aborting, nothing written.")
        finish(fatal=True)
        return

    if not GUARD_PATH.exists():
        check("guard_file_exists", False, f"{GUARD_PATH} not found. Aborting.")
        finish(fatal=True)
        return

    if not b64_sidecar.exists():
        check("sidecar_present", False,
              f"{b64_sidecar} not found -- transfer it alongside this script "
              "before running. Aborting, nothing written.")
        finish(fatal=True)
        return

    # --- Step 1: backup + replace guard file, hash-verified ---
    b64_content = b64_sidecar.read_text(encoding="ascii").strip()
    new_guard_bytes = base64.b64decode(b64_content)
    actual_hash = hashlib.sha256(new_guard_bytes).hexdigest()
    if actual_hash != EXPECTED_GUARD_SHA256:
        check("guard_content_hash", False,
              f"sidecar decoded hash {actual_hash} != expected {EXPECTED_GUARD_SHA256}. "
              "Not writing -- content may be corrupt or wrong file.")
        finish(fatal=True)
        return
    check("guard_content_hash", True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = GUARD_PATH.with_name(GUARD_PATH.name + f".backup_{ts}_E13001phase4")
    backup_path.write_bytes(GUARD_PATH.read_bytes())
    GUARD_PATH.write_bytes(new_guard_bytes)
    written_hash = hashlib.sha256(GUARD_PATH.read_bytes()).hexdigest()
    check("guard_file_written", written_hash == EXPECTED_GUARD_SHA256,
          f"post-write hash {written_hash}")

    # --- Step 2: sweep sys.path.insert out of the other 15 files ---
    pattern = re.compile(r"^[ \t]*sys\.path\.insert\([^\n]*\)[ \t]*\n?", re.MULTILINE)
    total_removed = 0
    for fname, expected_before in SWEEP_TARGETS.items():
        fpath = TESTS_DIR / fname
        if not fpath.exists():
            check(f"sweep_{fname}", False, f"file not found at {fpath}")
            continue
        src = fpath.read_text(encoding="utf-8")
        before_count = len(pattern.findall(src))
        if before_count != expected_before:
            check(f"sweep_{fname}", False,
                  f"expected {expected_before} sys.path.insert call(s), found {before_count} -- "
                  "not touching this file, count mismatch means content drifted since audit.")
            continue
        new_src = pattern.sub("", src)
        after_count = len(pattern.findall(new_src))
        if after_count != 0:
            check(f"sweep_{fname}", False, "post-removal count is not 0, aborting this file's write.")
            continue
        bpath = fpath.with_name(fpath.name + f".backup_{ts}_E13001phase4")
        bpath.write_text(src, encoding="utf-8")
        fpath.write_text(new_src, encoding="utf-8")
        total_removed += before_count
        check(f"sweep_{fname}", True, f"removed {before_count}")

    check("sweep_total_matches_finding8", total_removed == EXPECTED_TOTAL_SWEPT_CALLS,
          f"removed {total_removed}, expected {EXPECTED_TOTAL_SWEPT_CALLS}")

    # --- Step 3: full suite collected count ---
    collected, passed, failed, errors, out = run_pytest(P400_PY)
    check("full_suite_collected_count",
          collected == EXPECTED_POST_PHASE4_COLLECTED,
          f"got {collected} (passed={passed} failed={failed} errors={errors}), "
          f"expected {EXPECTED_POST_PHASE4_COLLECTED}")
    if collected != EXPECTED_POST_PHASE4_COLLECTED or failed or errors:
        log(out[-4000:])

    # --- Step 4: zero sys.path.insert left in the 16-file scope (conftest.py excluded/expected) ---
    remaining = 0
    for fname in list(SWEEP_TARGETS.keys()) + ["test_p400_known_bugs.py"]:
        fpath = TESTS_DIR / fname
        if fpath.exists():
            remaining += len(pattern.findall(fpath.read_text(encoding="utf-8")))
    check("zero_sys_path_insert_remaining", remaining == 0, f"found {remaining}")

    # --- Step 5: guard file runs standalone under pytest, all 25 pass ---
    gcollected, gpassed, gfailed, gerrors, gout = run_pytest(GUARD_PATH)
    check("guard_runs_under_plain_pytest", gcollected == 25 and gpassed == 25 and gfailed == 0,
          f"collected={gcollected} passed={gpassed} failed={gfailed} errors={gerrors}")
    if gfailed or gerrors:
        log(gout[-4000:])

    # --- Step 6: table <-> guard correspondence check ---
    if SKILL_PATH.exists():
        skill_src = SKILL_PATH.read_text(encoding="utf-8")
        wo_ids_in_table = set(re.findall(r"\|\s*(E\d\.\d+(?:/E\d\.\d+)?(?:\s*\(\w[^)]*\))?)\s*\|", skill_src))
        # Normalize to leading WO tokens like E2.007, E4.005, E4.006, E3.010, E3.011, E2.016 etc.
        wo_tokens = set()
        for raw in wo_ids_in_table:
            for tok in re.findall(r"E\d\.\d+", raw):
                wo_tokens.add(tok.lower().replace(".", ""))
        guard_src = GUARD_PATH.read_text(encoding="utf-8")
        guard_test_names = re.findall(r"^def (test_\w+)", guard_src, re.MULTILINE)
        missing = []
        for tok in sorted(wo_tokens):
            # tok like "e2007" -- look for it embedded in some test_ function name
            if not any(tok in name.lower() for name in guard_test_names):
                missing.append(tok)
        # Gaps are reported, not failed: WO item 12 / Phase 4 context say list
        # E4.005/E4.006 (and similar) for the WO write-up; do not silently add
        # tests, and do not fail the run over known correspondence gaps.
        gap_detail = (
            f"table rows with NO matching guard test: {sorted(missing)} -- "
            "listed per WO instruction, not fixed here."
            if missing else "all table WO tokens have a matching guard test"
        )
        check("table_guard_correspondence", True, gap_detail)
        if missing:
            log(f"[INFO] correspondence gaps (expected to list, not fix): {sorted(missing)}")
    else:
        check("table_guard_correspondence", False, f"{SKILL_PATH} not found")

    finish()


def finish(fatal=False):
    print("\n" + "=" * 60)
    failed = [r for r in RESULTS if not r[1]]
    for name, ok, detail in RESULTS:
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}" + (f" -- {detail}" if detail else ""))
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")

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
