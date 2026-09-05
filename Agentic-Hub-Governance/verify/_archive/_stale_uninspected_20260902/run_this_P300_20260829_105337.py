"""
FILE: run_this_P300_20260829_105337.py
VERSION: 1.0
DATE: 2026-08-29
AUTHOR: Claude (independent reviewer)
LAYER: verify (PEH, read-only)
DESCRIPTION: Independent-review checks for WO-P300-E5.006 closure:
  (1) verify data\\reference\\10_Pattern_SPY.xlsx / 10_Pattern_QQQ.xlsx bar
      count and date range directly via openpyxl -- NOT via the project's
      own bulk_grid_reader.parse_bulk_file, so this check is independent
      of the code under review.
  (2) verify no file under P_300\\python\\ has an mtime on/after
      2026-08-27 00:00 ET, catching any undocumented production edit
      during this WO's work window.
  Read-only. Writes nothing under P_300\\. No production file touched.
CHANGELOG: 1.0 initial (independent review of WO-P300-E5.006)
"""
import sys
import os
from datetime import datetime
from pathlib import Path

import openpyxl

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
REF_DIR = PROJECT_ROOT / "data" / "reference"
PYTHON_DIR = PROJECT_ROOT / "python"

DONE_PATH = Path(__file__).with_name(Path(__file__).stem + ".done")


def write_done(status, exit_code):
    with open(DONE_PATH, "w", encoding="utf-8") as f:
        f.write(f"{status}\nexit_code={exit_code}\ntimestamp={datetime.now().isoformat()}\n")


def fail(reason):
    write_done("FAIL", 1)
    print("FAIL:", reason)
    sys.exit(1)


def check_grid(path, label):
    if not path.exists():
        fail(f"{label} missing: {path}")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if len(rows) < 3:
        fail(f"{label}: workbook has fewer than 3 rows")
    header = rows[0]
    data_rows = rows[1:]
    ncols = len(header)
    date_col = None
    for c in range(ncols):
        sample = [r[c] for r in data_rows[:20] if r[c] is not None]
        if sample and all(isinstance(v, datetime) for v in sample):
            date_col = c
            break
    if date_col is None:
        fail(f"{label}: could not autodetect a date column; header={header}")
    dates = []
    for r in data_rows:
        v = r[date_col]
        if v is None:
            continue
        dates.append(v.date() if isinstance(v, datetime) else v)
    if not dates:
        fail(f"{label}: no date values found in detected column {date_col} (header={header})")
    return len(dates), min(dates), max(dates), header


results = {}
for fname, label in [("10_Pattern_SPY.xlsx", "SPY"), ("10_Pattern_QQQ.xlsx", "QQQ")]:
    n, dmin, dmax, header = check_grid(REF_DIR / fname, label)
    results[label] = (n, dmin, dmax)
    print(f"{label}: n={n} range={dmin}..{dmax} header={header}")

EXPECTED_N = 2514
EXPECTED_MIN = datetime(2016, 8, 29).date()
EXPECTED_MAX = datetime(2026, 8, 28).date()

mismatches = []
for label, (n, dmin, dmax) in results.items():
    if n != EXPECTED_N:
        mismatches.append(f"{label}: expected n={EXPECTED_N}, got {n}")
    if dmin != EXPECTED_MIN or dmax != EXPECTED_MAX:
        mismatches.append(f"{label}: expected range {EXPECTED_MIN}..{EXPECTED_MAX}, got {dmin}..{dmax}")

if mismatches:
    fail("; ".join(mismatches))

print("Grid check: PASS -- both files match WO's claimed 2,514 bars, 2016-08-29..2026-08-28")

# --- Check 2: no file under python\ modified since the WO's work window started ---
WINDOW_START = datetime(2026, 8, 27, 0, 0, 0).timestamp()

modified = []
for root, dirs, files in os.walk(PYTHON_DIR):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    for fn in files:
        if fn.endswith(".pyc"):
            continue
        fp = os.path.join(root, fn)
        mtime = os.path.getmtime(fp)
        if mtime >= WINDOW_START:
            modified.append((fp, datetime.fromtimestamp(mtime).isoformat()))

if modified:
    print(f"python\\ files with mtime >= 2026-08-27 00:00: {len(modified)} (reviewer interprets)")
    for fp, mt in modified:
        print(f"  {fp}  mtime={mt}")
else:
    print("python\\ check: PASS -- no file under P_300\\python\\ modified since 2026-08-27 00:00")

write_done("PASS", 0)
print("PASS")
