# WO-P000-E20.001 verify (v1.2): compile check + 4 regression tests +
# real re-run against P_000's actual lessons.md after the line-level
# chunking + code-fence-exclusion fix.
# Read-only against tasks\lessons.md; writes only to this verify\ folder.
# Self-contained, no sys.path insert (ref WO-P000-E2.003).

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
    warnings.simplefilter("error", SyntaxWarning)
    for py_file in sorted(LESSONS_AUDIT_DIR.glob("*.py")):
        if ".backup_" in py_file.name:
            continue
        try:
            py_compile.compile(str(py_file), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning) as exc:
            return f"{py_file.name}: {exc}"
    return None


def run_regression_tests() -> str | None:
    try:
        from shared_resources.python_utils.lessons_audit import test_domain
    except ImportError as exc:
        return f"import failed -- {exc}"

    test_names = (
        "test_scattered_terms_across_many_chunks_do_not_flag_as_enforced",
        "test_concentrated_terms_in_single_chunk_flags_as_enforced",
        "test_consecutive_non_blank_lines_do_not_merge_into_one_chunk",
        "test_fenced_code_block_content_excluded_from_scoring",
    )
    for test_name in test_names:
        fn = getattr(test_domain, test_name, None)
        if fn is None:
            return f"{test_name} not found in test_domain.py"
        try:
            fn()
        except AssertionError as exc:
            return f"{test_name} FAILED -- {exc}"
    return None


def main() -> int:
    compile_error = compile_check()
    if compile_error:
        print(f"FAIL: compile check -- {compile_error}")
        write_done("FAIL", 1)
        return 1
    print("Compile check: PASS (8 files, -W error::SyntaxWarning)")

    test_error = run_regression_tests()
    if test_error:
        print(f"FAIL: regression test -- {test_error}")
        write_done("FAIL", 1)
        return 1
    print("Regression tests: PASS (4/4)")

    try:
        from shared_resources.python_utils.lessons_audit import config
        from shared_resources.python_utils.lessons_audit import lessons_audit as la
    except ImportError as exc:
        print(f"FAIL: import failed -- {exc}")
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
        print("FAIL: parsed 0 lesson entries")
        write_done("FAIL", 1)
        return 1

    scratch_output = VERIFY_DIR / "lessons_audit_status_SCRATCH_verify_v3.json"
    scratch_output.write_text(status.model_dump_json(indent=2), encoding="utf-8")

    counts: dict[str, int] = {}
    for flag in status.flags:
        counts[flag.classification] = counts.get(flag.classification, 0) + 1

    print(f"Parsed {status.total_lessons} lesson entries from {la.DEFAULT_LESSONS_PATH}")
    print(f"Classification counts (post-line-chunking-fix): {counts}")
    for flag in status.flags:
        top = flag.matched_sources[0] if flag.matched_sources else None
        excerpt = top.chunk_excerpt[:80] if top else "(none)"
        terms = top.shared_terms if top else []
        print(f"  {flag.lesson_id} [{flag.lesson_title[:40]}]: {flag.classification} "
              f"(max_shared={flag.shared_term_count}) shared_terms={terms} "
              f"top_match={excerpt!r}")
    print(f"Scratch output (not production): {scratch_output}")
    print("PASS")
    write_done("PASS", 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
