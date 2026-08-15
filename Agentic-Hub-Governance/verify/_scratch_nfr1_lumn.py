"""
Scratch NFR-1 replay -- targets an XLSX actually present in data\\live today.
Not a permanent file, not part of WO-P000-E5.001's deliverable. Same
comparison logic as tasks\\nfr1_determinism_replay.py verbatim, only the
target file differs (CGBD isn't on disk right now; LUMN is).
Delete after use: Agentic-Hub-Governance\\verify\\_scratch_nfr1_lumn.py
"""

import sys
from pathlib import Path

_PYTHON_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python")
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import CE_GATE_ENABLED  # noqa: E402
from application.daily_evaluate_pipeline import run_daily_evaluate  # noqa: E402

_XLSX = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\live\History Grid (LUMN).xlsx")
_DECIMAL_PLACES = 6
_TOL = 10 ** -_DECIMAL_PLACES


def _fmt(val):
    if val is None:
        return "None"
    return f"{val:.{_DECIMAL_PLACES}f}"


def main() -> int:
    print("=" * 65)
    print("SCRATCH NFR-1 REPLAY -- LUMN (CGBD not on disk today)")
    print("=" * 65)

    if CE_GATE_ENABLED:
        print("FAIL -- CE_GATE_ENABLED is True.")
        return 1
    print(f"[OK] CE_GATE_ENABLED={CE_GATE_ENABLED}  (observe-only confirmed)")

    if not _XLSX.exists():
        print(f"FAIL -- XLSX not found: {_XLSX}")
        return 1
    print(f"[OK] XLSX: {_XLSX.name}")
    print()

    print("[RUN 1] Evaluating...")
    r1 = run_daily_evaluate(_XLSX, narrator_enabled=False, print_output=False, write_file=False)
    print(f"       signal={r1.signal_class.value}  horizon={r1.chosen_horizon}")

    print("[RUN 2] Evaluating...")
    r2 = run_daily_evaluate(_XLSX, narrator_enabled=False, print_output=False, write_file=False)
    print(f"       signal={r2.signal_class.value}  horizon={r2.chosen_horizon}")
    print()

    failures: list[str] = []

    if r1.signal_class != r2.signal_class:
        failures.append(f"signal_class mismatch: run1={r1.signal_class.value} run2={r2.signal_class.value}")

    if r1.chosen_horizon != r2.chosen_horizon:
        failures.append(f"chosen_horizon mismatch: run1={r1.chosen_horizon} run2={r2.chosen_horizon}")

    h_keys_1 = set(r1.per_horizon_stats.keys())
    h_keys_2 = set(r2.per_horizon_stats.keys())
    if h_keys_1 != h_keys_2:
        failures.append(f"per_horizon_stats key mismatch: {h_keys_1} vs {h_keys_2}")
    else:
        for h in sorted(h_keys_1):
            s1 = r1.per_horizon_stats[h]
            s2 = r2.per_horizon_stats[h]
            checks = [
                ("n_matches", s1.n_matches, s2.n_matches),
                ("win_rate", s1.win_rate, s2.win_rate),
                ("mean_return_pct", s1.mean_return_pct, s2.mean_return_pct),
                ("std_return_pct", s1.std_return_pct, s2.std_return_pct),
                ("z_score", s1.z_score, s2.z_score),
                ("certainty_equivalent", s1.certainty_equivalent, s2.certainty_equivalent),
            ]
            for field, v1, v2 in checks:
                if v1 is None and v2 is None:
                    continue
                if (v1 is None) != (v2 is None):
                    failures.append(f"h={h} {field}: None vs non-None ({_fmt(v1)} vs {_fmt(v2)})")
                    continue
                if abs(v1 - v2) > _TOL:
                    failures.append(f"h={h} {field}: {_fmt(v1)} vs {_fmt(v2)} (delta={abs(v1-v2):.2e})")

    print("-" * 65)
    if failures:
        print(f"FAIL -- {len(failures)} divergence(s) found:")
        for f in failures:
            print(f"  * {f}")
        print("-" * 65)
        return 1

    horizons = sorted(r1.per_horizon_stats.keys())
    print(f"PASS -- signal={r1.signal_class.value}  horizon={r1.chosen_horizon}")
    print(f"        horizons checked: {horizons}")
    print("        ALL IDENTICAL across both runs. NFR-1 OK (LUMN substitute).")
    print("-" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
