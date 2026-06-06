"""
FILE: feature_ablation.py
VERSION: 1.1
DATE: 2026-05-19
AUTHOR: Anthony Zoppi + Claude
LAYER: utility
DESCRIPTION:
    Stage 9 per-feature ablation. For each of the 10 normalized features
    in SIMILARITY_FEATURES: mask that feature OFF, re-run LOO replay,
    score BUY/PASS performance against baseline (all features active).
    Surfaces which features carry signal vs noise.

    Unlike threshold_sweep.py, ablation requires one full LOO per masked
    feature — masking changes the composite distance, which changes the
    top-K ranking, which changes the per-horizon stats. No caching
    shortcut. Cost: 11 LOO passes (baseline + 10 ablations).

    Honest caveat: at N=25 absolute BUY counts are small (~8 across the
    5 horizons at Stage 6 default thresholds). Ablation measures
    RELATIVE change across the same 25 patterns under different masks —
    apples-to-apples within this run — but the underlying counts are
    still noisy. Read rankings directionally.

    Entry points:
        ablate_features(...) -> Path   (library)
        main(argv) -> int               (CLI)

CHANGELOG:
    - 2026-05-19 v1.1: Default thresholds set to Stage 7 sweep's firing
      corner (n=3, wr=0.55, z>0.5) so ablation produces a non-zero
      baseline against the 25-pattern catalog. At Stage 6 defaults
      (n=5, wr=0.70, z>1.0) the catalog yields zero BUYs and ablation
      surfaces no signal — see sweep CSV 20260519_183459 for the data
      showing why z is the binding constraint at this catalog size.
    - 2026-05-19 v1.0: Initial release. Stage 9 file #3 of 3.
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

from config import FORWARD_HORIZONS, SIMILARITY_FEATURES  # noqa: E402
from schemas_pipeline_b import SignalClass  # noqa: E402
from utilities.loo_replay import (  # noqa: E402
    FeatureMask, LooReplayBatch, ThresholdOverrides, replay_all,
)

# v1.1: Stage 7 sweep (CSV 20260519_183459) found BUYs fire only at
# z>=0.5 with wr<=0.70; n=3..7 all loose at TOP_K=20. Run ablation in
# that firing regime so feature deltas are measurable instead of all-zero.
STAGE9_LOOSE_OVERRIDES = ThresholdOverrides(
    buy_min_n=3, buy_min_win_rate=0.55, buy_min_z_score=0.5,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s",
                    stream=sys.stdout)
logger = logging.getLogger(__name__)


CSV_FIELDNAMES = [
    "ablated_feature", "horizon",
    "buy_count", "correct_buy", "false_positive", "buy_precision",
    "mean_return_on_buys",
    "pass_count", "correct_pass", "missed", "pass_specificity",
    "watch_count",
]


# ─── Helpers ────────────────────────────────────────────────────────────────

def _mask_without(feat: str) -> FeatureMask:
    """FeatureMask with all features True except `feat` set False."""
    kwargs = {f: True for f in SIMILARITY_FEATURES}
    kwargs[feat] = False
    return FeatureMask(**kwargs)


def _aggregate_batch(
    batch: LooReplayBatch, ablated_feature: str | None,
) -> list[dict]:
    """One LOO batch -> per-horizon CSV rows."""
    acc = {h: {"buy_count": 0, "correct_buy": 0, "false_positive": 0,
               "correct_pass": 0, "missed": 0, "watch_count": 0,
               "buy_returns": []} for h in FORWARD_HORIZONS}
    for result in batch.results:
        for hr in result.horizon_results:
            a = acc[hr.horizon_days]
            if hr.signal_class == SignalClass.BUY:
                a["buy_count"] += 1
                a["buy_returns"].append(hr.actual_return)
            elif hr.signal_class == SignalClass.WATCH:
                a["watch_count"] += 1
            if hr.correctness == "correct_buy":
                a["correct_buy"] += 1
            elif hr.correctness == "false_positive":
                a["false_positive"] += 1
            elif hr.correctness == "correct_pass":
                a["correct_pass"] += 1
            elif hr.correctness == "missed":
                a["missed"] += 1

    label = ablated_feature if ablated_feature else "(baseline)"
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
            "ablated_feature": label, "horizon": h,
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


def _print_summary(all_rows: list[dict]) -> None:
    """Aggregate-across-horizons stdout table. ASCII-only per M-019."""
    by_feat: dict[str, dict] = {}
    for r in all_rows:
        feat = r["ablated_feature"]
        if feat not in by_feat:
            by_feat[feat] = {"buys": 0, "correct": 0, "fp": 0}
        by_feat[feat]["buys"] += r["buy_count"]
        by_feat[feat]["correct"] += r["correct_buy"]
        by_feat[feat]["fp"] += r["false_positive"]

    baseline = by_feat["(baseline)"]
    base_prec = (baseline["correct"] / baseline["buys"]
                 if baseline["buys"] > 0 else 0.0)

    print(f"\nAblation summary (sum across 5 horizons):")
    print(f"  {'feature':32s} {'buys':>5s} {'correct':>8s} {'fp':>3s} "
          f"{'prec':>6s} {'d_buys':>7s} {'d_prec':>7s}")
    print(f"  {'(baseline, all features on)':32s} "
          f"{baseline['buys']:>5d} {baseline['correct']:>8d} "
          f"{baseline['fp']:>3d} {base_prec:>6.3f} "
          f"{'--':>7s} {'--':>7s}")

    feat_rows = []
    for feat in SIMILARITY_FEATURES:
        d = by_feat.get(feat, {"buys": 0, "correct": 0, "fp": 0})
        prec = d["correct"] / d["buys"] if d["buys"] > 0 else 0.0
        feat_rows.append({
            "feature": feat, "buys": d["buys"], "correct": d["correct"],
            "fp": d["fp"], "prec": prec,
            "d_buys": d["buys"] - baseline["buys"],
            "d_prec": prec - base_prec,
        })
    feat_rows.sort(key=lambda r: r["d_prec"], reverse=True)

    for r in feat_rows:
        print(f"  - {r['feature']:30s} {r['buys']:>5d} {r['correct']:>8d} "
              f"{r['fp']:>3d} {r['prec']:>6.3f} "
              f"{r['d_buys']:>+7d} {r['d_prec']:>+7.3f}")
    print("\n  Sorted by d_prec descending. Positive d_prec = removing the")
    print("  feature IMPROVES BUY precision (i.e., the feature was adding noise).")
    print("  Negative d_prec = the feature was contributing signal.")


# ─── Main ablation entry ────────────────────────────────────────────────────

def ablate_features(out_csv: Path | None = None) -> Path:
    """Run per-feature ablation; write CSV; print summary; return path."""
    logger.info("Baseline LOO (all 10 features active; v1.1 loose thresholds)...")
    baseline_batch = replay_all(threshold_overrides=STAGE9_LOOSE_OVERRIDES)
    all_rows = _aggregate_batch(baseline_batch, ablated_feature=None)

    for i, feat in enumerate(SIMILARITY_FEATURES, 1):
        logger.info("Ablating feature %d/%d: %s",
                    i, len(SIMILARITY_FEATURES), feat)
        mask = _mask_without(feat)
        ablated_batch = replay_all(
            threshold_overrides=STAGE9_LOOSE_OVERRIDES, feature_mask=mask,
        )
        all_rows.extend(_aggregate_batch(ablated_batch, ablated_feature=feat))

    if out_csv is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_csv = Path("outputs") / f"feature_ablation_{ts}.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        f.write(
            f"# P_300 Stage 9 per-feature ablation - {datetime.now().isoformat()}\n"
            f"# Catalog: {baseline_batch.catalog_path}\n"
            f"# N patterns: {baseline_batch.n_patterns} - "
            f"Features: {len(SIMILARITY_FEATURES)} + baseline = "
            f"{len(SIMILARITY_FEATURES) + 1} LOO passes\n"
            f"# Thresholds: BUY n>=3, wr>=0.55, z>0.5 (Stage 7 firing corner;\n"
            f"#   v1.1 default - see CHANGELOG). WATCH at Stage 6 Decision F.\n"
            f"# Honest caveat: small-N - read directionally; rankings are\n"
            f"# more reliable than absolute precisions at this catalog size.\n"
        )
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    logger.info("Wrote ablation CSV: %s (%d rows)", out_csv, len(all_rows))
    _print_summary(all_rows)
    return out_csv


# ─── CLI ────────────────────────────────────────────────────────────────────

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stage 9 per-feature ablation against catalog LOO.",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help="Output CSV path (default: outputs/feature_ablation_<ts>.csv)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        ablate_features(out_csv=args.out)
    except Exception as e:
        logger.error("Ablation failed: %s: %s", type(e).__name__, e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
