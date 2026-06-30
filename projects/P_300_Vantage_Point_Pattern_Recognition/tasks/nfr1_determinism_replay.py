"""
NFR-1 Determinism Replay -- CE observe-mode (Enhancement 2)
============================================================
Proves that CE_GATE_ENABLED=False (observe-only) produces byte-identical
BUY/WATCH/PASS signals across two independent runs on the same XLSX.

Usage (from project root in p140):
    python tasks/nfr1_determinism_replay.py

Requires NARRATOR_ENABLED=False or LM Studio running. The script forces
narrator_enabled=False to avoid any LLM dependency.

Pass criteria:
  - signal_class identical (run 1 == run 2)
  - chosen_horizon identical
  - per_horizon_stats: all numeric fields identical to 6 decimal places
    (n_matches, win_rate, mean_return_pct, std_return_pct, z_score,
     certainty_equivalent if present)
  - CE_GATE_ENABLED confirmed False at test time (gate must be observe-only)

Exit codes:
  0 = PASS (all checks green)
  1 = FAIL (divergence found or gate not observe-only)
"""

import sys
from pathlib import Path

# Bootstrap so this runs from project root
_PYTHON_DIR = Path(__file__).resolve().parent.parent / "python"
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import CE_GATE_ENABLED  # noqa: E402
from application.daily_evaluate_pipeline import run_daily_evaluate  # noqa: E402

# ---------------------------------------------------------------------------
# Target XLSX -- smallest live file; PASS classification won't emit packets
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_XLSX = _PROJECT_ROOT / "data" / "live" / "History Grid (CGBD).xlsx"

_DECIMAL_PLACES = 6
_TOL = 10 ** -_DECIMAL_PLACES


def _fmt(val):
    if val is None:
        return "None"
    return f"{val:.{_DECIMAL_PLACES}f}"


def main() -> int:
    print("=" * 65)
    print("NFR-1 DETERMINISM REPLAY -- CE observe-mode (Enhancement 2)")
    print("=" * 65)

    # Gate check: must be observe-only
    if CE_GATE_ENABLED:
        print("FAIL -- CE_GATE_ENABLED is True.")
        print("       This replay tests observe-mode (gate off).")
        print("       Flip gate back to False before running.")
        return 1
    print(f"[OK] CE_GATE_ENABLED={CE_GATE_ENABLED}  (observe-only confirmed)")

    if not _XLSX.exists():
        print(f"FAIL -- XLSX not found: {_XLSX}")
        return 1
    print(f"[OK] XLSX: {_XLSX.name}")
    print()

    # Run 1
    print("[RUN 1] Evaluating...")
    r1 = run_daily_evaluate(
        _XLSX,
        narrator_enabled=False,
        print_output=False,
        write_file=False,
    )
    print(f"       signal={r1.signal_class.value}  horizon={r1.chosen_horizon}")

    # Run 2
    print("[RUN 2] Evaluating...")
    r2 = run_daily_evaluate(
        _XLSX,
        narrator_enabled=False,
        print_output=False,
        write_file=False,
    )
    print(f"       signal={r2.signal_class.value}  horizon={r2.chosen_horizon}")
    print()

    # Compare
    failures: list[str] = []

    # Signal class
    if r1.signal_class != r2.signal_class:
        failures.append(
            f"signal_class mismatch: run1={r1.signal_class.value} "
            f"run2={r2.signal_class.value}"
        )

    # Chosen horizon
    if r1.chosen_horizon != r2.chosen_horizon:
        failures.append(
            f"chosen_horizon mismatch: run1={r1.chosen_horizon} "
            f"run2={r2.chosen_horizon}"
        )

    # Per-horizon stats
    h_keys_1 = set(r1.per_horizon_stats.keys())
    h_keys_2 = set(r2.per_horizon_stats.keys())
    if h_keys_1 != h_keys_2:
        failures.append(
            f"per_horizon_stats key mismatch: {h_keys_1} vs {h_keys_2}"
        )
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
                ("certainty_equivalent", s1.certainty_equivalent,
                 s2.certainty_equivalent),
            ]
            for field, v1, v2 in checks:
                # None vs None is fine; None vs float is a mismatch
                if v1 is None and v2 is None:
                    continue
                if (v1 is None) != (v2 is None):
                    failures.append(
                        f"h={h} {field}: None vs non-None "
                        f"({_fmt(v1)} vs {_fmt(v2)})"
                    )
                    continue
                if abs(v1 - v2) > _TOL:
                    failures.append(
                        f"h={h} {field}: {_fmt(v1)} vs {_fmt(v2)} "
                        f"(delta={abs(v1-v2):.2e})"
                    )

    # Result
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
    print("        signal_class, chosen_horizon, n_matches, win_rate,")
    print("        mean_return_pct, std_return_pct, z_score,")
    print("        certainty_equivalent -- ALL IDENTICAL across both runs.")
    print("        CE observe-mode does NOT alter BUY/WATCH/PASS. NFR-1 OK.")
    print("-" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())
