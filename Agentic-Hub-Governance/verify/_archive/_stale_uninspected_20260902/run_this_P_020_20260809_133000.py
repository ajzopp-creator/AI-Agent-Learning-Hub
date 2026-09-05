"""Acceptance test for WO-P020-E1.010 auth --project ALL (2026-08-09).

Does NOT run a browser login and does NOT touch real token files. Verifies:
  1. Both changed files compile under -W error::SyntaxWarning
  2. cli.py exposes ALL / P_020 / P_400 and rejects anything else
  3. cmd_auth_all's propagation + verification logic is correct, exercised
     against throwaway temp files with run_auth monkeypatched out
  4. _verify_token_file actually FAILS on a corrupted copy (proves the
     guard is real, not decorative)

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe <this file>
"""

import json
import shutil
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

DB_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)
PY = r"C:\Users\Trader\.conda\envs\p140\python.exe"

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"  [OK] {label}")
    else:
        print(f"  [FAIL] {label} {detail}")
        FAILURES.append(label)


def test_compiles():
    print("1. Compile under warnings-as-errors")
    for rel in ("cli.py", "application/schwab_auth_commands.py"):
        path = DB_DIR / rel
        src = path.read_text(encoding="utf-8")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", SyntaxWarning)
                compile(src, str(path), "exec")
            check(f"{rel} compiles clean", True)
        except Exception as e:
            check(f"{rel} compiles clean", False, f"-- {e}")


def test_cli_choices():
    print("2. CLI accepts ALL, rejects garbage")
    r = subprocess.run(
        [PY, "cli.py", "auth", "--help"],
        cwd=DB_DIR, capture_output=True, text=True, timeout=60,
    )
    out = r.stdout + r.stderr
    check("--help exits 0", r.returncode == 0, f"-- rc={r.returncode}")
    for token in ("ALL", "P_020", "P_400"):
        check(f"help lists {token}", token in out)

    r2 = subprocess.run(
        [PY, "cli.py", "auth", "--project", "P_999"],
        cwd=DB_DIR, capture_output=True, text=True, timeout=60,
    )
    check("rejects unknown project", r2.returncode != 0, f"-- rc={r2.returncode}")


def test_propagation_logic():
    print("3. Propagation + verification against temp files")
    sys.path.insert(0, str(DB_DIR))
    import application.schwab_auth_commands as sac

    sample = {
        "creation_timestamp": 1786295000,
        "token": {
            "expires_in": 1800,
            "token_type": "Bearer",
            "scope": "api",
            "refresh_token": "FAKE_REFRESH_TOKEN_FOR_TEST",
            "access_token": "FAKE_ACCESS",
            "expires_at": 1786296800,
        },
    }

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        primary = tmp / "P_020" / "tok.json"
        secondary = tmp / "P_400" / "tok.json"
        third = tmp / "P_999" / "tok.json"
        primary.parent.mkdir(parents=True)

        def fake_run_auth(config_path, token_path):
            Path(token_path).parent.mkdir(parents=True, exist_ok=True)
            Path(token_path).write_text(json.dumps(sample), encoding="utf-8")

        real_paths = sac.AUTH_TOKEN_PATHS
        try:
            sac.AUTH_TOKEN_PATHS = {
                "P_020": primary, "P_400": secondary, "P_999": third,
            }
            sys.modules["shared_resources.python_utils.schwab_auth"] = type(
                "M", (), {"run_auth": staticmethod(fake_run_auth)}
            )
            rc = sac.cmd_auth_all()
        finally:
            sac.AUTH_TOKEN_PATHS = real_paths

        check("returns 0", rc == 0, f"-- got {rc}")
        check("secondary created", secondary.exists())
        check("third created (n>2 scales)", third.exists())
        check(
            "all three byte-identical",
            primary.read_bytes() == secondary.read_bytes() == third.read_bytes(),
        )
        check(
            "shared refresh_token",
            json.loads(third.read_text())["token"]["refresh_token"]
            == "FAKE_REFRESH_TOKEN_FOR_TEST",
        )


def test_guard_is_real():
    print("4. Verification guard rejects a corrupted copy")
    sys.path.insert(0, str(DB_DIR))
    import application.schwab_auth_commands as sac

    with tempfile.TemporaryDirectory() as td:
        good = Path(td) / "good.json"
        good.write_text('{"token": {"refresh_token": "x"}}', encoding="utf-8")
        src = good.read_bytes()

        bad = Path(td) / "bad.json"
        shutil.copyfile(good, bad)
        bad.write_bytes(src + b"CORRUPTED")

        try:
            sac._verify_token_file(bad, src)
            check("raises on byte mismatch", False, "-- no exception")
        except RuntimeError:
            check("raises on byte mismatch", True)

        missing = Path(td) / "nope.json"
        try:
            sac._verify_token_file(missing, src)
            check("raises on missing file", False, "-- no exception")
        except RuntimeError:
            check("raises on missing file", True)


def main():
    print("=== WO-P020-E1.010 auth --project ALL acceptance ===")
    test_compiles()
    test_cli_choices()
    test_propagation_logic()
    test_guard_is_real()
    print("=" * 45)
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} check(s) failed: {FAILURES}")
        return 1
    print("PASS -- all checks green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
