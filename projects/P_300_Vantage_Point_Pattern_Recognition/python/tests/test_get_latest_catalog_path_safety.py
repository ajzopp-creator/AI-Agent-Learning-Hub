"""
test_get_latest_catalog_path_safety.py -- Regression guard for M-089/
M-095 (get_latest_catalog() returns str by design; every caller must
wrap it in Path()).

M-089 fixed one call site (mine_patterns_pipeline.py, script-local).
M-095 (2026-07-14) found the SAME unwrapped pattern recurring at 3 MORE
call sites -- 2 in application/catalog_merge_pipeline.py
(build_staging_merge, promote_staging_to_live) and 1 in application/
ingest_mined_pipeline.py (run_ingest_mined) -- discovered live, during
WO-P300-E3.002's first real production promote, when
promote_staging_to_live() crashed ('str' object has no attribute
'exists') the first time it was ever called without an explicit
--live-db. The other 2 sites never crashed because shutil.copy2() and
load_full_catalog() both tolerate a raw str -- silently wrong, not
silently safe.

This is a static source-scan test, not a runtime test: it greps the
known-fixed files for the exact unwrapped pattern and fails if it
reappears (e.g. from a careless future edit reverting the Path() wrap).
Scoped to the 3 call sites actually fixed this session -- not a
project-wide linter (cap_sensitivity_audit.py, loo_replay.py, and
db_connect.py also call get_latest_catalog() unwrapped in places; those
are pre-existing, out of this WO's scope, and noted separately in
lessons.md M-095 rather than fixed here).

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_300_Vantage_Point_Pattern_Recognition\\python\\tests\\
           test_get_latest_catalog_path_safety.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_get_latest_catalog_path_safety.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python")

RESULTS = []

# (file relative to ROOT, function name, must NOT appear literally)
UNWRAPPED_PATTERN = re.compile(r"else\s+get_latest_catalog\(\)")
WRAPPED_PATTERN = re.compile(r"else\s+Path\(get_latest_catalog\(\)\)")

CHECKS = [
    ("application/catalog_merge_pipeline.py", "build_staging_merge"),
    ("application/catalog_merge_pipeline.py", "promote_staging_to_live"),
    ("application/ingest_mined_pipeline.py", "run_ingest_mined"),
]


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def test_no_unwrapped_get_latest_catalog_calls():
    """BEHAVIOR (M-089/M-095) -- every 'else get_latest_catalog()' style
    fallback in the 3 fixed files must be wrapped in Path(). A bare
    unwrapped occurrence anywhere in these 2 files is a regression."""
    for rel_path, _ in {(c[0], None) for c in CHECKS}:
        full_path = ROOT / rel_path
        text = full_path.read_text(encoding="utf-8")
        unwrapped = UNWRAPPED_PATTERN.findall(text)
        wrapped = WRAPPED_PATTERN.findall(text)
        check(
            f"no_unwrapped_get_latest_catalog[{rel_path}]", "BEHAVIOR",
            len(unwrapped) == 0,
            f"unwrapped_occurrences={len(unwrapped)} wrapped_occurrences={len(wrapped)}",
        )


def test_expected_wrapped_count_present():
    """BEHAVIOR -- sanity check that the fix is actually present (not
    just absent-of-bug), i.e. each file has at least as many wrapped
    occurrences as it has functions that resolve a default live path."""
    expected_min = {
        "application/catalog_merge_pipeline.py": 2,  # build_staging_merge + promote_staging_to_live
        "application/ingest_mined_pipeline.py": 1,   # run_ingest_mined
    }
    for rel_path, min_count in expected_min.items():
        full_path = ROOT / rel_path
        text = full_path.read_text(encoding="utf-8")
        wrapped = WRAPPED_PATTERN.findall(text)
        check(
            f"expected_wrapped_count[{rel_path}]", "BEHAVIOR",
            len(wrapped) >= min_count,
            f"found={len(wrapped)} expected_min={min_count}",
        )


def main():
    test_no_unwrapped_get_latest_catalog_calls()
    test_expected_wrapped_count_present()

    print(f"{'NAME':<55} {'KIND':<10} RESULT")
    all_pass = True
    for name, kind, passed, detail in RESULTS:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"{name:<55} {kind:<10} {status}  {detail}")
    print()
    n_pass = sum(1 for _, _, p, _ in RESULTS if p)
    if all_pass:
        print(f"PASS ({n_pass}/{len(RESULTS)})")
    else:
        print(f"FAIL ({n_pass}/{len(RESULTS)})")
        sys.exit(1)


if __name__ == "__main__":
    main()
