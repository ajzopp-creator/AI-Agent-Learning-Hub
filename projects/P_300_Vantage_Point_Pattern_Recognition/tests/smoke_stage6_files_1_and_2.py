"""
FILE: smoke_stage6_files_1_and_2.py
PURPOSE: Live p140 import + happy-path validation of Stage 6 File #1
         (config.py v1.2) and File #2 (schemas_pipeline_b.py v1.0).
         Closes the "container-side only" caveat from 2026-05-16.

RUN (from project root, with ISE profile's p140 PATH prepend active):
    python tests/smoke_stage6_files_1_and_2.py

OR (from anywhere):
    python C:/Users/Trader/AI-Agent-Learning-Hub/projects/P_300_Vantage_Point_Pattern_Recognition/tests/smoke_stage6_files_1_and_2.py

Expected output: each check prefixed with "OK"; final line "ALL CHECKS PASSED".
Exit code 0 = full pass, 1 = any failure.

Per M-016: verify `(Get-Command python).Source` returns p140 python.exe
BEFORE running. If it returns Python 3.14 system, fix the ISE profile first.

Note: docstring path examples use forward slashes to avoid Python 3.12+
SyntaxWarning on backslash escape sequences (renders as red NativeCommandError
in PowerShell per M-011 stderr pattern, even though it's only a warning).
"""
import sys
from pathlib import Path
from datetime import date

# Add the project's python/ folder to sys.path so `import config` and
# `import schemas_pipeline_b` resolve, regardless of where this script
# is invoked from.
_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent / "python"
sys.path.insert(0, str(_PYTHON_DIR))

print(f"Python: {sys.executable}")
print(f"Python version: {sys.version.split()[0]}")
print(f"Added to sys.path: {_PYTHON_DIR}")


def section(name: str) -> None:
    print(f"\n=== {name} ===")


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


# ─── File #1 — config.py v1.2 ─────────────────────────────────────────────
section("File #1 - config.py v1.2")
try:
    import config
    ok("import config")
except Exception as e:
    fail(f"import config: {type(e).__name__}: {e}")

expected_constants = {
    "TOP_K_MATCHES": 20,
    "BUY_MIN_MATCHES": 5,
    "BUY_MIN_WIN_RATE": 0.70,
    "BUY_MIN_Z_SCORE": 1.0,
    "WATCH_MIN_MATCHES": 3,
    "WATCH_MIN_WIN_RATE": 0.60,
    "WATCH_MIN_Z_SCORE": 0.0,
    "HISTORY_GRID_GLOB_PATTERN": "History Grid (*).xlsx",
}
for name, expected in expected_constants.items():
    actual = getattr(config, name, "<MISSING>")
    if actual == expected:
        ok(f"{name} = {actual!r}")
    else:
        fail(f"{name} expected {expected!r}, got {actual!r}")

if len(config.SIMILARITY_FEATURES) == 10:
    ok(f"SIMILARITY_FEATURES = 10 entries")
else:
    fail(f"SIMILARITY_FEATURES expected 10, got {len(config.SIMILARITY_FEATURES)}")

if isinstance(config.REPORTS_DIR, Path):
    ok(f"REPORTS_DIR is Path = {config.REPORTS_DIR}")
else:
    fail(f"REPORTS_DIR not a Path: {type(config.REPORTS_DIR).__name__}")


# ─── File #2 - schemas_pipeline_b.py v1.0 ─────────────────────────────────
section("File #2 - schemas_pipeline_b.py v1.0")
try:
    import schemas_pipeline_b as spb
    ok("import schemas_pipeline_b")
except Exception as e:
    fail(f"import schemas_pipeline_b: {type(e).__name__}: {e}")

expected_models = {
    "NormalizedBar", "LiveCandidate", "ForwardLabelLite",
    "MatchResult", "AggregatedSignalPerHorizon",
    "SignalClass", "SignalReport",
}
present = {n for n in dir(spb) if n in expected_models}
if present == expected_models:
    ok(f"all 7 models present")
else:
    fail(f"missing: {expected_models - present}")

if [c.value for c in spb.SignalClass] == ["BUY", "WATCH", "PASS"]:
    ok("SignalClass values = BUY / WATCH / PASS")
else:
    fail(f"SignalClass values wrong: {[c.value for c in spb.SignalClass]}")

# Happy-path constructions across the 7 models
try:
    fl = spb.ForwardLabelLite(return_pct=0.05, is_profitable=True)
    ok("ForwardLabelLite constructs")
except Exception as e:
    fail(f"ForwardLabelLite: {type(e).__name__}: {e}")

try:
    bar = spb.NormalizedBar(
        bar_offset=0, bar_date=date(2026, 1, 27),
        open=258.0, high=260.0, low=256.0, close=258.27, volume=1_000_000,
        stdiff=0.5, mtdiff=1.2, ltdiff=2.1,
        pred_high=261.0, pred_low=255.0, pred_range=6.0,
        williams_emai=-15.0, psi=72.5, neural_index=1.0,
        triple_cross_short=1.0, triple_cross_medium=1.0, triple_cross_long=1.0,
        close_pct_from_anchor=0.0, range_pct=0.015, body_pct=0.001,
        volume_zscore=0.3, stdiff_pct=0.002, mtdiff_pct=0.005,
        ltdiff_pct=0.008, pred_high_pct=0.011, pred_low_pct=-0.013,
        pred_range_pct=0.023,
    )
    ok("NormalizedBar constructs")
except Exception as e:
    fail(f"NormalizedBar: {type(e).__name__}: {e}")

# Validator-fires check (negative test)
from pydantic import ValidationError
try:
    spb.NormalizedBar(**{**bar.model_dump(), "high": 50.0, "low": 100.0})
    fail("validator did NOT fire on high<low")
except (ValidationError, ValueError):
    ok("validator fires on high < low")

# ─── Final ────────────────────────────────────────────────────────────────
print("\nALL CHECKS PASSED")
sys.exit(0)
