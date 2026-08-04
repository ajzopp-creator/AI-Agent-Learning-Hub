"""
FILE: smoke_loo_replay.py
VERSION: 1.0
DATE: 2026-05-19
AUTHOR: Anthony Zoppi + Claude
PURPOSE: Parity smoke for utilities.loo_replay. Verifies the harness's
         threshold-overridable AND-gate produces bit-identical output to
         domain.signal_classifier.classify_per_horizon at config defaults
         (overrides=None). No DB dependency.

RUN (from project root, with ISE profile's p140 PATH prepend active):
    python tests/smoke_loo_replay.py

Expected output: 6 parity lines all "OK"; final line "parity check: 6/6 OK".
Exit code 0 = full pass, 1 = any failure.

Per M-016: verify `(Get-Command python).Source` returns p140 python.exe
BEFORE running.

CHANGELOG:
    - 2026-05-19 v1.0: Initial release. Split out of loo_replay.py to
      hold that file under the 300-line standard.
"""
import sys
from pathlib import Path

# Put project's python/ folder on sys.path so domain, schemas_pipeline_b,
# and utilities resolve regardless of CWD.
_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from domain import signal_classifier  # noqa: E402
from schemas_pipeline_b import AggregatedSignalPerHorizon  # noqa: E402
from utilities.loo_replay import _classify_per_horizon_overridable  # noqa: E402


def _s(h, n, wr, mr, sr, z):
    return AggregatedSignalPerHorizon(
        horizon_days=h, n_matches=n, win_rate=wr,
        mean_return_pct=mr, std_return_pct=sr, z_score=z)


FIXTURES = [
    ("clear BUY (10, 0.80, z=1.5)",         _s(7, 10, 0.80, 3.5, 1.2, 1.5)),
    ("clear WATCH (5, 0.65, z=0.5)",        _s(7,  5, 0.65, 2.0, 1.0, 0.5)),
    ("clear PASS (3, 0.50, z=0.4)",         _s(7,  3, 0.50, 1.0, 0.5, 0.4)),
    ("BUY wr OK but z=1.0 strict-gt fails", _s(7, 10, 0.80, 3.5, 1.0, 1.0)),
    ("WATCH n=3 boundary OK",               _s(7,  3, 0.60, 1.5, 0.8, 0.1)),
    ("PASS wr just under WATCH",            _s(7,  5, 0.59, 1.2, 0.8, 0.3)),
]


def main() -> int:
    failures = 0
    for label, s in FIXTURES:
        ref = signal_classifier.classify_per_horizon(s)
        mine = _classify_per_horizon_overridable(s, None)
        ok = (ref == mine)
        print(f"parity {label:42s} ref={ref.value:5s} mine={mine.value:5s} {'OK' if ok else 'FAIL'}")
        if not ok:
            failures += 1
    print(f"\nparity check: {len(FIXTURES) - failures}/{len(FIXTURES)} OK")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
