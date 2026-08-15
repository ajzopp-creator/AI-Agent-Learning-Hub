"""
FILE: Agentic-Hub-Governance/verify/run_this.py
PURPOSE: Archive the 20 mined-corpus XLSX files left in data\\bulk\\mine\\
         after the 2026-08-04 12:03 batch's archive-mined step failed on
         a full E: drive (ENOSPC). E: now has 682.82 GB free (Tony
         cleared space). The catalog promote itself already succeeded
         (080426catalog.db confirmed on disk) -- this only re-runs the
         archive step, nothing touches the catalog.

Calls utilities.archive_mined_file.run_archive() directly (same function
cli.py archive-mined --xlsx <path> calls) once per file, in the same
20-file order the original batch log showed. Each call is independently
safe: append to zip -> verify entry landed -> only then delete source.
A failure on one file does not affect the others or roll back prior
successes.

RUN:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe run_this.py
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
)
PYTHON_DIR = PROJECT_ROOT / "python"
sys.path.insert(0, str(PYTHON_DIR))

MINE_DIR = PROJECT_ROOT / "data" / "bulk" / "mine"

FILES = [
    "10_Pattern_AIQ.xlsx", "10_Pattern_ASTS.xlsx", "10_Pattern_BBAI.xlsx",
    "10_Pattern_BBBY.xlsx", "10_Pattern_ENPH.xlsx", "10_Pattern_EXP.xlsx",
    "10_Pattern_FLNC.xlsx", "10_Pattern_GGAL.xlsx", "10_Pattern_HRZN.xlsx",
    "10_Pattern_IREN.xlsx", "10_Pattern_JMIA.xlsx", "10_Pattern_KEY.xlsx",
    "10_Pattern_OCSL.xlsx", "10_Pattern_PAVE.xlsx", "10_Pattern_POOL.xlsx",
    "10_Pattern_PSEC.xlsx", "10_Pattern_RKLB.xlsx", "10_Pattern_RKT.xlsx",
    "10_Pattern_RY.xlsx", "10_Pattern_VUZI.xlsx",
]


def main() -> int:
    from utilities.archive_mined_file import run_archive

    ok = 0
    failed: list[str] = []
    for i, fname in enumerate(FILES, 1):
        fpath = MINE_DIR / fname
        print(f"[{i}/{len(FILES)}] {fname}")
        if not fpath.exists():
            print(f"  SKIP -- not found (already archived?): {fpath}")
            continue
        rc = run_archive(fpath)
        if rc == 0:
            ok += 1
        else:
            failed.append(fname)

    print(f"\n{'=' * 60}")
    print(f"Archived {ok} / {len(FILES)} files.")
    if failed:
        print(f"FAILED ({len(failed)}): {', '.join(failed)}")
    print("=" * 60)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
