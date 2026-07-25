"""
test_p300_known_bugs.py -- Regression guard for the P_300 Anti-Patterns
table (EC-001 through EC-070) in .claude/skills/p300-project-context/SKILL.md.

One test per anti-pattern that has a concrete, checkable fix in the code.
Run this after ANY edit to the files it covers, and before calling a fix
"done." Per WO-P020-E1.003's Hub-wide rule (2026-07-06), any future bug
added to this project's anti-pattern list gets a matching test added here
in the same session as the fix.

Two kinds of test, both labeled below:
  BEHAVIOR -- calls the real function against a tiny synthetic input and
              checks the actual output. Confirms the bug cannot recur.
  SOURCE   -- greps the file for the fix's signature. Cheaper, but only
              confirms the fix line is still there, not full behavior.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_300_Vantage_Point_Pattern_Recognition\\python\\tests\\
           test_p300_known_bugs.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_p300_known_bugs.py
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python")
DOMAIN = ROOT / "domain"
INFRA = ROOT / "infrastructure"
APPLICATION = ROOT / "application"
UTILITIES = ROOT / "utilities"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DOMAIN))
sys.path.insert(0, str(UTILITIES))

RESULTS = []


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def test_similarity_dtw_identical_zero():
    """BEHAVIOR -- identical sequences must score 0.0 (EC-046/048)."""
    import similarity as sim
    d = sim.dtw_distance([0.0, 1.0, 2.0, 3.0, 4.0], [0.0, 1.0, 2.0, 3.0, 4.0])
    check("similarity_dtw_identical_zero", "BEHAVIOR", d == 0.0, f"got {d!r}")


def test_similarity_dtw_shifted():
    """BEHAVIOR -- uniform 0.5 shift over 5 points must sum to 2.5."""
    import similarity as sim
    d = sim.dtw_distance([0.0, 1.0, 2.0, 3.0, 4.0], [0.5, 1.5, 2.5, 3.5, 4.5])
    check("similarity_dtw_shifted", "BEHAVIOR", d == 2.5, f"got {d!r}")


def test_similarity_composite_missing_feature_raises():
    """BEHAVIOR -- composite_distance must raise on a missing feature
    rather than silently sum a partial set (M-009-class drift guard,
    anti-pattern #3: raw/partial values must never substitute for the
    full normalized column set)."""
    import similarity as sim
    from config import SIMILARITY_FEATURES
    try:
        sim.composite_distance({SIMILARITY_FEATURES[0]: 1.0})
        ok = False
    except ValueError:
        ok = True
    check("similarity_composite_missing_feature_raises", "BEHAVIOR", ok)


def test_db_utils_digit_prefix_filter():
    """BEHAVIOR -- get_latest_catalog must ignore non-digit-prefixed
    files (e.g. 'org_...' backups) to prevent lexicographical collision
    (EC-049/058)."""
    import db_utils
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "062026catalog.db").touch()
        (tmp_path / "org_070126catalog.db").touch()
        orig_dir = db_utils.MODELS_DIR
        orig_pattern = db_utils.CATALOG_GLOB_PATTERN
        db_utils.MODELS_DIR = tmp_path
        db_utils.CATALOG_GLOB_PATTERN = "*catalog.db"
        try:
            latest = db_utils.get_latest_catalog()
            ok = Path(latest).name == "062026catalog.db"
        finally:
            db_utils.MODELS_DIR = orig_dir
            db_utils.CATALOG_GLOB_PATTERN = orig_pattern
        check("db_utils_digit_prefix_filter", "BEHAVIOR", ok, f"got {latest}")


def test_no_window_locking_slice_in_ingest():
    """SOURCE -- ingest-path files must not use .tail(N)/.head(N), which
    silently locks the window and drops bars (EC-060)."""
    files = [INFRA / "vp_xlsx_reader.py", APPLICATION / "add_pattern_pipeline.py"]
    bad = []
    for f in files:
        src = f.read_text(encoding="utf-8")
        if ".tail(" in src or ".head(" in src:
            bad.append(f.name)
    check("no_window_locking_slice_in_ingest", "SOURCE", not bad, f"found in {bad}")


def test_schema_symbol_id_is_int():
    """SOURCE -- symbol_id fields must be typed int, never a bare TEXT/str
    field masquerading as an FK (EC-061)."""
    src = (ROOT / "schemas.py").read_text(encoding="utf-8")
    ok = "symbol_id: int" in src
    check("schema_symbol_id_is_int", "SOURCE", ok)


def test_domain_layer_has_no_io():
    """SOURCE -- domain/ must contain no sqlite3, requests, or open()
    calls (layer-mixing guard, EC-027)."""
    bad = []
    for f in DOMAIN.glob("*.py"):
        src = f.read_text(encoding="utf-8")
        if "import sqlite3" in src or "import requests" in src or "open(" in src:
            bad.append(f.name)
    check("domain_layer_has_no_io", "SOURCE", not bad, f"found in {bad}")


def test_signal_classifier_no_llm_import():
    """SOURCE -- signal_classifier.py must never import the LLM client;
    BUY/WATCH/PASS stays deterministic Python only (EC-022, ID-005)."""
    src = (DOMAIN / "signal_classifier.py").read_text(encoding="utf-8")
    ok = "llm_client" not in src and "import llm" not in src
    check("signal_classifier_no_llm_import", "SOURCE", ok)


def test_catalog_writer_lock_temp_atomic_pattern():
    """SOURCE -- catalog_writer.py must document/use the Lock + Temp-DB +
    Atomic Move pattern, never a direct write to the master DB."""
    src = (INFRA / "catalog_writer.py").read_text(encoding="utf-8")
    ok = "Temp-DB" in src and "Atomic Move" in src
    check("catalog_writer_lock_temp_atomic_pattern", "SOURCE", ok)


def test_report_writer_ascii_sanitize():
    """SOURCE -- stdout paths must ASCII-sanitize before printing; a raw
    Unicode write through cp1252 PowerShell crashes (EC-069, M-019)."""
    src = (INFRA / "report_writer.py").read_text(encoding="utf-8")
    ok = 'encode("ascii", "replace")' in src
    check("report_writer_ascii_sanitize", "SOURCE", ok)


def test_hub_root_uses_five_parents():
    """SOURCE -- _HUB_ROOT in daily_evaluate_pipeline.py must resolve via
    5 x .parent from application/, not 4 (M-036 -- 4x lands one directory
    short, at projects/ instead of the Hub root)."""
    src = (APPLICATION / "daily_evaluate_pipeline.py").read_text(encoding="utf-8")
    ok = "_HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent" in src
    check("hub_root_uses_five_parents", "SOURCE", ok)


def test_no_stdlib_name_collisions():
    """SOURCE -- no domain/ or infrastructure/ module may shadow a stdlib
    name (signal, csv, json, time, math), which breaks on sys.path[0]
    prepend via circular import (EC-068, M-018)."""
    reserved = {"signal.py", "csv.py", "json.py", "time.py", "math.py"}
    found = []
    for folder in (DOMAIN, INFRA):
        for f in folder.glob("*.py"):
            if f.name in reserved:
                found.append(str(f))
    check("no_stdlib_name_collisions", "SOURCE", not found, f"found {found}")


def test_pipeline_a_b_stay_separate():
    """SOURCE -- Pipeline A (add_pattern_pipeline.py) and Pipeline B
    (daily_evaluate_pipeline.py) must remain distinct files; merging
    corrupts both designs (EC-067)."""
    a = APPLICATION / "add_pattern_pipeline.py"
    b = APPLICATION / "daily_evaluate_pipeline.py"
    ok = a.exists() and b.exists() and a != b
    check("pipeline_a_b_stay_separate", "SOURCE", ok)


def main():
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tests:
        try:
            t()
        except Exception as e:
            check(t.__name__, "ERROR", False, repr(e))

    failed = [r for r in RESULTS if not r[2]]
    for name, kind, passed, detail in RESULTS:
        mark = "PASS" if passed else "FAIL"
        line = f"[{mark}] ({kind}) {name}"
        if detail and not passed:
            line += f" -- {detail}"
        print(line)

    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
