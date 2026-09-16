"""
run_this_P300_20260910_195500.py
WO-P300-E5.001 -- Batch 1 verification (PatternMetadata/MineCandidateRow
relocation out of infrastructure/, schemas.py + schemas_pipeline_b.py
file-size split). Read-only against production code: compiles every
touched/created file under warnings-as-errors, then actually imports
each one (not just syntax-checks) to catch import-resolution problems
a compile pass alone would miss -- especially the schemas.py <->
schemas_catalog_records.py partial-circular import and the two
re-export shims (schemas.py, schemas_pipeline_b.py).

Modifies nothing. Safe to re-run.
"""
import sys
import traceback
import warnings
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
PYTHON_DIR = PROJECT_ROOT / "python"
sys.path.insert(0, str(PYTHON_DIR))
sys.path.insert(0, str(PYTHON_DIR / "tests"))

warnings.simplefilter("error", SyntaxWarning)

NEW_FILES = [
    "schemas_pipeline_b_bar.py",
    "schemas_pipeline_b_report.py",
    "schemas_vp_raw.py",
    "schemas_catalog_records.py",
    "schemas_mine.py",
]
REWRITTEN_FILES = [
    "schemas.py",
    "schemas_pipeline_b.py",
]
EDITED_FILES = [
    "infrastructure/catalog_reader.py",
    "infrastructure/mine_report_writer.py",
    "infrastructure/eval_io.py",
    "application/incremental_post_batch.py",
    "domain/eval_incremental.py",
    "domain/eval_scoring.py",
    "domain/reconstruct_from_topk.py",
    "domain/topk_cache.py",
    "domain/mine_audit.py",
    "schemas_bulk.py",  # reverted -- confirm back to original, unbroken
]
TEST_FILES = [
    "tests/test_eval_incremental.py",
    "tests/test_eval_scoring.py",
    "tests/test_incremental_post_batch.py",
    "tests/test_mine_audit.py",
    "tests/test_reconstruct_from_topk.py",
    "tests/test_topk_cache.py",
]

ALL_FILES = NEW_FILES + REWRITTEN_FILES + EDITED_FILES + TEST_FILES

failures = []

# --- Phase 1: compile every file under warnings-as-errors ---
print("=== Phase 1: compile check ===")
for rel in ALL_FILES:
    p = PYTHON_DIR / rel
    try:
        src = p.read_text(encoding="utf-8")
        compile(src, str(p), "exec", dont_inherit=True)
        print(f"  OK   compile: {rel}")
    except Exception as e:
        failures.append((rel, "compile", repr(e)))
        print(f"  FAIL compile: {rel} -- {e!r}")

# --- Phase 2: actually import each new/rewritten module ---
print("=== Phase 2: import resolution ===")
import importlib

MODULES_TO_IMPORT = [
    "schemas_pipeline_b_bar",
    "schemas_pipeline_b_report",
    "schemas_vp_raw",
    "schemas_catalog_records",
    "schemas_mine",
    "schemas",
    "schemas_pipeline_b",
    "schemas_bulk",
]
for mod_name in MODULES_TO_IMPORT:
    try:
        mod = importlib.import_module(mod_name)
        print(f"  OK   import: {mod_name}")
    except Exception as e:
        failures.append((mod_name, "import", repr(e)))
        print(f"  FAIL import: {mod_name} -- {e!r}")
        traceback.print_exc()

# --- Phase 3: re-export shim completeness ---
print("=== Phase 3: re-export shim completeness ===")
try:
    import schemas
    expected_schemas = [
        "DataOriginType", "SourceFormat", "ColumnMapEntry", "IgnoredColumnEntry",
        "ValidationRules", "IngestManifest", "VPBarRaw", "PatternFileMetadata",
        "PatternFileParse", "SymbolRecord", "SourceFileRecord", "FeatureSetRecord",
        "PatternInstanceRecord", "PatternBarRecord", "ForwardLabelRecord", "PowerGaugeResult",
    ]
    missing = [n for n in expected_schemas if not hasattr(schemas, n)]
    if missing:
        failures.append(("schemas.py", "shim", f"missing names: {missing}"))
        print(f"  FAIL schemas.py shim missing: {missing}")
    else:
        print(f"  OK   schemas.py re-exports all {len(expected_schemas)} original names")
except Exception as e:
    failures.append(("schemas.py", "shim-check", repr(e)))
    print(f"  FAIL schemas.py shim check errored: {e!r}")

try:
    import schemas_pipeline_b
    expected_b = [
        "NormalizedBar", "LiveCandidate", "ForwardLabelLite", "MatchResult",
        "PatternMetadata", "AggregatedSignalPerHorizon", "Severity",
        "VolatilityDivergence", "SignalClass", "SignalReport",
    ]
    missing_b = [n for n in expected_b if not hasattr(schemas_pipeline_b, n)]
    if missing_b:
        failures.append(("schemas_pipeline_b.py", "shim", f"missing names: {missing_b}"))
        print(f"  FAIL schemas_pipeline_b.py shim missing: {missing_b}")
    else:
        print(f"  OK   schemas_pipeline_b.py re-exports all {len(expected_b)} original names")
except Exception as e:
    failures.append(("schemas_pipeline_b.py", "shim-check", repr(e)))
    print(f"  FAIL schemas_pipeline_b.py shim check errored: {e!r}")

# --- Phase 4: import every edited domain/infrastructure/application file ---
print("=== Phase 4: import every edited production module ===")
EDITED_MODULE_NAMES = [
    "infrastructure.catalog_reader",
    "infrastructure.mine_report_writer",
    "infrastructure.eval_io",
    "application.incremental_post_batch",
    "domain.eval_incremental",
    "domain.eval_scoring",
    "domain.reconstruct_from_topk",
    "domain.topk_cache",
    "domain.mine_audit",
]
for mod_name in EDITED_MODULE_NAMES:
    try:
        importlib.import_module(mod_name)
        print(f"  OK   import: {mod_name}")
    except Exception as e:
        failures.append((mod_name, "import", repr(e)))
        print(f"  FAIL import: {mod_name} -- {e!r}")
        traceback.print_exc()

# --- Phase 5: PatternMetadata / MineCandidateRow identity check ---
# Confirm every importer gets the SAME class object (not two copies from
# a duplicated definition somewhere the file sweep missed).
print("=== Phase 5: single-definition identity check ===")
try:
    from schemas_pipeline_b import PatternMetadata as PM_shim
    from schemas_pipeline_b_bar import PatternMetadata as PM_direct
    from infrastructure.catalog_reader import PatternMetadata as PM_via_catalog_reader
    from infrastructure.eval_io import PatternMetadata as PM_via_eval_io
    from domain.topk_cache import PatternMetadata as PM_via_topk_cache
    from domain.mine_audit import mine_bars  # noqa: F401 -- just proving mine_audit still imports cleanly
    all_same = (PM_shim is PM_direct is PM_via_catalog_reader is PM_via_eval_io is PM_via_topk_cache)
    if all_same:
        print("  OK   PatternMetadata: single definition, identical object via every import path")
    else:
        failures.append(("PatternMetadata", "identity", "not the same object across import paths"))
        print("  FAIL PatternMetadata: different objects across import paths")
except Exception as e:
    failures.append(("PatternMetadata", "identity-check", repr(e)))
    print(f"  FAIL PatternMetadata identity check errored: {e!r}")
    traceback.print_exc()

try:
    from schemas_mine import MineCandidateRow as MCR_direct
    from infrastructure.mine_report_writer import MineCandidateRow as MCR_via_writer
    from domain.mine_audit import MineCandidateRow as MCR_via_audit
    all_same_mcr = (MCR_direct is MCR_via_writer is MCR_via_audit)
    if all_same_mcr:
        print("  OK   MineCandidateRow: single definition, identical object via every import path")
    else:
        failures.append(("MineCandidateRow", "identity", "not the same object across import paths"))
        print("  FAIL MineCandidateRow: different objects across import paths")
except Exception as e:
    failures.append(("MineCandidateRow", "identity-check", repr(e)))
    print(f"  FAIL MineCandidateRow identity check errored: {e!r}")
    traceback.print_exc()

# --- Result ---
print()
if failures:
    print(f"FAIL: {len(failures)} problem(s) found")
    for f in failures:
        print(f"  - {f}")
    result_line = f"FAIL: {len(failures)} problem(s)\n"
    exit_code = 1
else:
    print("PASS")
    result_line = "PASS\n"
    exit_code = 0

done_path = Path(__file__).with_suffix(".py.done")
import datetime
done_path.write_text(
    f"timestamp: {datetime.datetime.now().isoformat()}\n"
    f"status: {'PASS' if exit_code == 0 else 'FAIL'}\n"
    f"exit_code: {exit_code}\n",
    encoding="utf-8",
)
sys.exit(exit_code)
