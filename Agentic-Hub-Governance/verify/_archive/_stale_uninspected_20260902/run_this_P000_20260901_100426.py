# WO-P000-E20.001 verify: lessons_audit compile check + import + smoke test.
# Reads P_000's real tasks\lessons.md (READ-ONLY). Writes its own scratch
# output to this verify\ folder only -- never touches tasks\lessons.md or
# writes the real tasks\lessons_audit_status.json. Self-contained, no
# sys.path insert (ref WO-P000-E2.003).

import py_compile
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

SELF = Path(__file__)
VERIFY_DIR = SELF.parent
LESSONS_AUDIT_DIR = (
    SELF.parent.parent.parent
    / "shared_resources" / "python_utils" / "lessons_audit"
)


def write_done(status: str, exit_code: int) -> None:
    done_path = SELF.with_suffix(SELF.suffix + ".done")
    done_path.write_text(
        f"status={status}\n"
        f"exit_code={exit_code}\n"
        f"timestamp={datetime.now(timezone.utc).isoformat()}\n",
        encoding="utf-8",
    )


def compile_check() -> str | None:
    """Compile all six new files under -W error::SyntaxWarning. Returns
    an error message on failure, None on success."""
    warnings.simplefilter("error", SyntaxWarning)
    for py_file in sorted(LESSONS_AUDIT_DIR.glob("*.py")):
        try:
            py_compile.compile(str(py_file), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning) as exc:
            return f"{py_file.name}: {exc}"
    return None


def main() -> int:
    compile_error = compile_check()
    if compile_error:
        print(f"FAIL: compile check -- {compile_error}")
        write_done("FAIL", 1)
        return 1

    try:
        from shared_resources.python_utils.lessons_audit import config
        from shared_resources.python_utils.lessons_audit import lessons_audit as la
    except ImportError as exc:
        print(f"FAIL: import via editable install failed -- {exc}")
        write_done("FAIL", 1)
        return 1

    if not la.DEFAULT_LESSONS_PATH.exists():
        print(f"FAIL: expected lessons.md not found at {la.DEFAULT_LESSONS_PATH}")
        write_done("FAIL", 1)
        return 1

    try:
        status = la.run(la.DEFAULT_LESSONS_PATH, config.DEFAULT_MIN_SHARED_TERMS)
    except Exception as exc:
        print(f"FAIL: run() raised -- {exc!r}")
        write_done("FAIL", 1)
        return 1

    if status.total_lessons == 0:
        print(
            "FAIL: parsed 0 lesson entries -- header regex likely doesn't "
            "match this file's actual M-series header format"
        )
        write_done("FAIL", 1)
        return 1

    scratch_output = VERIFY_DIR / "lessons_audit_status_SCRATCH_verify.json"
    scratch_output.write_text(status.model_dump_json(indent=2), encoding="utf-8")

    counts: dict[str, int] = {}
    for flag in status.flags:
        counts[flag.classification] = counts.get(flag.classification, 0) + 1

    print(f"Compile check: PASS (6 files, -W error::SyntaxWarning)")
    print(f"Parsed {status.total_lessons} lesson entries from {la.DEFAULT_LESSONS_PATH}")
    print(f"Classification counts: {counts}")
    print(f"Scratch output (not production): {scratch_output}")
    print("PASS")
    write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
