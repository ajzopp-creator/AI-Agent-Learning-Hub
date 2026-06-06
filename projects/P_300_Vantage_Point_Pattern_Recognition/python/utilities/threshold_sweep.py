"""
FILE: threshold_sweep.py
VERSION: 1.1
DATE: 2026-05-19
AUTHOR: Anthony Zoppi + Claude
LAYER: utility
DESCRIPTION:
    Stage 9 BUY-only threshold sweep. Wraps utilities.loo_replay to
    grid-search over (BUY_MIN_MATCHES, BUY_MIN_WIN_RATE, BUY_MIN_Z_SCORE)
    against the live catalog via leave-one-out. Writes a CSV of metrics
    per (grid_point, horizon) for offline analysis.

    WATCH thresholds held at Stage 6 Decision F values (not swept).

    Performance trick: similarity ranking + aggregator stats depend only
    on (catalog, candidate, feature_mask) — NOT on classifier thresholds.
    So replay_all runs ONCE at config defaults to produce per-pattern
    HorizonResult records that already carry n_analogs / win_rate /
    z_score / actual_return / actual_is_profitable. The sweep then
    re-applies the threshold-overridable AND-gate to those cached
    stats per grid combo. 75 combos × 25 patterns × 5 horizons of
    re-classification is millisecond-scale; the costly LOO replay
    runs exactly once.

    Honest caveat (also in CSV header comment):
        At N=25, per-(combo, horizon) buy counts are small. A combo
        that fires 2 BUYs total can show "100% precision" by luck.
        Read precision in context of buy_count; combos with buy_count
        ≥ 5 are the only ones worth comparing.

    Entry points:
        sweep_buy_thresholds(...) -> Path   (library)
        main(argv) -> int                    (CLI)

CHANGELOG:
    - 2026-05-19 v1.1: DEFAULT_BUY_*_GRID pointed downward after
      first sweep (CSV outputs/threshold_sweep_buy_20260519_183459.csv)
      showed Stage 6 default thresholds (n=5, wr=0.70, z>1.0) are
      calibrated above where any BUY fires in the 25-pattern catalog.
      z_score is binding; n thresholds 3..7 don't bite at TOP_K=20.
      v1.0 grid: n=(3,4,5,6,7) wr=(0.55..0.75) z=(0.5,1.0,1.5).
      v1.1 grid: n=(3,5,7) wr=(0.50..0.70) z=(-0.5,0.0,0.5).
    - 2026-05-19 v1.0: Initial release. Stage 9 file #2 of 3.
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
from datetime import datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import FORWARD_HORIZONS  # noqa: E402
from schemas_pipeline_b import AggregatedSignalPerHorizon, SignalClass  # noqa: E402
from utilities.loo_replay import (  # noqa: E402
    HorizonResult, LooReplayResult, ThresholdOverrides,
    _classify_per_horizon_overridable, _label_correctness, replay_all,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s",
                    stream=sys.stdout)
logger = logging.getLogger(__name__)


# ─── Default grid (operator can override on CLI) ────────────────────────────

# v1.1 downward grid — see CHANGELOG. z is binding; first pass showed
# zero BUYs at z >= 1.0. n collapsed to (3,5,7) since 3..7 are all loose
# at TOP_K=20. Original v1.0 grid preserved in 20260519_183459 CSV.
DEFAULT_BUY_N_GRID: tuple[int, ...] = (3, 5, 7)
DEFAULT_BUY_WR_GRID: tuple[float, ...] = (0.50, 0.55, 0.60, 0.65, 0.70)
DEFAULT_BUY_Z_GRID: tuple[float, ...] = (-0.5, 0.0, 0.5)

CSV_FIELDNAMES = [
    "combo_id", "buy_min_n", "buy_min_win_rate", "buy_min_z_score",
    "horizon", "buy_count", "correct_buy", "false_positive",
    "buy_precision", "mean_return_on_buys",
    "pass_count", "correct_pass", "missed", "pass_specificity",
    "watch_count",
]


# ─── Re-classification of cached LOO results at new thresholds ──────────────

def _reapply(
    horizon_results: list[HorizonResult],
    overrides: ThresholdOverrides,
) -> list[tuple[int, SignalClass, str, float, bool]]:
    """Re-run AND-gate on cached stats. Returns rows of (h, signal, correctness, actual_ret, profitable)."""
    out = []
    for hr in horizon_results:
        stats = AggregatedSignalPerHorizon(
            horizon_days=hr.horizon_days,
            n_matches=hr.n_analogs,
            win_rate=hr.cluster_win_rate,
            mean_return_pct=hr.cluster_mean_return,
            std_return_pct=hr.cluster_std_return,
            z_score=hr.z_score,
        )
        new_signal = _classify_per_horizon_overridable(stats, overrides)
        new_correctness = _label_correctness(new_signal, hr.actual_is_profitable)
        out.append((hr.horizon_days, new_signal, new_correctness,
                    hr.actual_return, hr.actual_is_profitable))
    return out


def _score_combo(
    combo_id: int,
    overrides: ThresholdOverrides,
    cached_results: list[LooReplayResult],
) -> list[dict]:
    """Apply overrides across all cached patterns; emit one CSV row per horizon."""
    # Per-horizon accumulators
    acc = {h: {"buy_count": 0, "correct_buy": 0, "false_positive": 0,
               "correct_pass": 0, "missed": 0, "watch_count": 0,
               "buy_returns": []} for h in FORWARD_HORIZONS}

    for result in cached_results:
        for h, signal, correctness, actual_ret, _profit in _reapply(
            result.horizon_results, overrides,
        ):
            a = acc[h]
            if signal == SignalClass.BUY:
                a["buy_count"] += 1
                a["buy_returns"].append(actual_ret)
            elif signal == SignalClass.WATCH:
                a["watch_count"] += 1
            # correctness label increments
            if correctness == "correct_buy":
                a["correct_buy"] += 1
            elif correctness == "false_positive":
                a["false_positive"] += 1
            elif correctness == "correct_pass":
                a["correct_pass"] += 1
            elif correctness == "missed":
                a["missed"] += 1

    rows = []
    for h in FORWARD_HORIZONS:
        a = acc[h]
        pass_count = a["correct_pass"] + a["missed"]
        buy_precision = (a["correct_buy"] / a["buy_count"]
                         if a["buy_count"] > 0 else None)
        pass_specificity = (a["correct_pass"] / pass_count
                            if pass_count > 0 else None)
        mean_buy_ret = (sum(a["buy_returns"]) / len(a["buy_returns"])
                        if a["buy_returns"] else None)
        rows.append({
            "combo_id": combo_id,
            "buy_min_n": overrides.buy_min_n,
            "buy_min_win_rate": overrides.buy_min_win_rate,
            "buy_min_z_score": overrides.buy_min_z_score,
            "horizon": h,
            "buy_count": a["buy_count"],
            "correct_buy": a["correct_buy"],
            "false_positive": a["false_positive"],
            "buy_precision": buy_precision,
            "mean_return_on_buys": mean_buy_ret,
            "pass_count": pass_count,
            "correct_pass": a["correct_pass"],
            "missed": a["missed"],
            "pass_specificity": pass_specificity,
            "watch_count": a["watch_count"],
        })
    return rows


# ─── Main sweep ─────────────────────────────────────────────────────────────

def sweep_buy_thresholds(
    buy_n_grid: tuple[int, ...] = DEFAULT_BUY_N_GRID,
    buy_wr_grid: tuple[float, ...] = DEFAULT_BUY_WR_GRID,
    buy_z_grid: tuple[float, ...] = DEFAULT_BUY_Z_GRID,
    out_csv: Path | None = None,
) -> Path:
    """Grid sweep over BUY thresholds; writes CSV; returns its path.

    Runs replay_all once at config defaults (one expensive LOO pass),
    then re-classifies cached results against every grid point.
    """
    logger.info(
        "Sweep grid: n=%d wr=%d z=%d  (%d combos)",
        len(buy_n_grid), len(buy_wr_grid), len(buy_z_grid),
        len(buy_n_grid) * len(buy_wr_grid) * len(buy_z_grid),
    )

    # One expensive LOO pass — produces per-pattern HorizonResults with
    # actual returns and ground-truth profitability.
    logger.info("Running baseline LOO replay (one pass)...")
    base_batch = replay_all()
    logger.info("LOO baseline complete: %d patterns", base_batch.n_patterns)

    all_rows = []
    combo_id = 0
    for bn in buy_n_grid:
        for bwr in buy_wr_grid:
            for bz in buy_z_grid:
                combo_id += 1
                overrides = ThresholdOverrides(
                    buy_min_n=bn,
                    buy_min_win_rate=bwr,
                    buy_min_z_score=bz,
                )
                all_rows.extend(_score_combo(combo_id, overrides, base_batch.results))

    if out_csv is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_csv = Path("outputs") / f"threshold_sweep_buy_{ts}.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        f.write(
            f"# P_300 Stage 9 BUY-threshold sweep · {datetime.now().isoformat()}\n"
            f"# Catalog: {base_batch.catalog_path}\n"
            f"# N patterns: {base_batch.n_patterns} · "
            f"Grid size: {combo_id} combos · "
            f"Rows: {len(all_rows)} (combo x horizon)\n"
            f"# WATCH thresholds held at Stage 6 Decision F (not swept).\n"
            f"# Honest caveat: small-N — read buy_precision in context of "
            f"buy_count; combos with buy_count < 5 are noisy.\n"
        )
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    logger.info("Wrote sweep CSV: %s (%d rows)", out_csv, len(all_rows))

    # Quick stdout summary: top 5 combos by buy_precision among
    # buy_count >= 5 (filter out small-sample noise).
    qualifying = [r for r in all_rows
                  if r["buy_count"] >= 5 and r["buy_precision"] is not None]
    qualifying.sort(key=lambda r: r["buy_precision"], reverse=True)
    print("\nTop 5 (combo, horizon) by buy_precision among buy_count >= 5:")
    print(f"{'rank':4s} {'n':3s} {'wr':5s} {'z':4s} {'h':3s} "
          f"{'buys':5s} {'prec':6s} {'mean_ret':9s}")
    for i, r in enumerate(qualifying[:5], 1):
        print(f"{i:4d} {r['buy_min_n']:3d} {r['buy_min_win_rate']:5.2f} "
              f"{r['buy_min_z_score']:4.1f} {r['horizon']:3d} "
              f"{r['buy_count']:5d} {r['buy_precision']:6.3f} "
              f"{r['mean_return_on_buys']:9.4f}")
    if not qualifying:
        print("  (no combos cleared buy_count >= 5 — grid may be too tight)")
    return out_csv


# ─── CLI ────────────────────────────────────────────────────────────────────

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage 9 BUY-only threshold sweep against catalog LOO.",
    )
    parser.add_argument("--out", type=Path, default=None,
                        help="Output CSV path (default: outputs/threshold_sweep_buy_<ts>.csv)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        sweep_buy_thresholds(out_csv=args.out)
    except Exception as e:
        logger.error("Sweep failed: %s: %s", type(e).__name__, e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
