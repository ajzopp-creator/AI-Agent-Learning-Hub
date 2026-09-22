"""
FILE: alphalens_ic_quantile.py
VERSION: 1.0
DATE: 2026-09-21
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Read-only factor-validation diagnostic, adapted from the Alphalens
    methodology (Quant Scientist newsletter, Apr 2026) to P_300's real
    schema instead of the library itself. Tests whether topk_cache's
    composite_distance / rank predicts the matched neighbor's own
    forward_labels.return_pct -- do closer historical analogs actually
    out-earn farther ones, per horizon.

    POOLED statistic across every (anchor, neighbor) pair in the
    catalog, not a per-anchor IC -- 20 points per anchor is too thin
    for a meaningful per-anchor Spearman; pooling across the corpus is
    the statistically defensible version of the same test. A strong
    pooled IC confirms the existing wr>=0.70/z>0.0 BUY gate's premise;
    it is not an independent out-of-sample validation (same corpus
    both set the gate and is tested here).

    Quantile spread: topk_cache rows bucketed into quintiles by rank
    (1-4 closest .. 17-20 farthest), mean forward return_pct per
    bucket, per horizon.

    return_pct is a decimal fraction (M-020) -- x100 applied only at
    print, never inside the correlation/mean computation.

    Read-only against catalog: no Check-In/Check-Out bracketing needed.

CHANGELOG:
    - 2026-09-21 v1.0: Initial release.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PYTHON_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PYTHON_DIR))

from config import FORWARD_HORIZONS, TOP_K_MATCHES  # noqa: E402
from utilities.db_utils import get_latest_catalog  # noqa: E402

N_QUANTILES = 5


def _rankdata(values: list[float]) -> list[float]:
    """Average ranks, ties split evenly, 1-indexed."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_ic(x: list[float], y: list[float]) -> float:
    """Spearman rank correlation via Pearson-on-ranks. NaN if degenerate."""
    n = len(x)
    if n < 2:
        return float("nan")
    rx, ry = _rankdata(x), _rankdata(y)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        return float("nan")
    return cov / (vx * vy) ** 0.5


def fetch_pairs(
    conn: sqlite3.Connection, horizon: int
) -> list[tuple[int, float, float]]:
    """(rank, composite_distance, return_pct) for every topk_cache row
    with a forward_labels row at this horizon on the matched neighbor."""
    sql = """
        SELECT tc.rank, tc.composite_distance, fl.return_pct
          FROM topk_cache tc
          JOIN forward_labels fl
            ON fl.pattern_instance_id = tc.matched_pid
           AND fl.horizon_days = ?
    """
    return conn.execute(sql, (horizon,)).fetchall()


def quantile_bucket(rank: int) -> int:
    """1..N_QUANTILES, rank 1 (closest) -> bucket 1."""
    width = TOP_K_MATCHES / N_QUANTILES
    return min(N_QUANTILES, int((rank - 1) / width) + 1)


def report_horizon(conn: sqlite3.Connection, horizon: int) -> None:
    rows = fetch_pairs(conn, horizon)
    n = len(rows)
    print(f"\n--- horizon={horizon}d  n_pairs={n}")
    if n < 2:
        print("  too few pairs, skipped")
        return

    dists = [r[1] for r in rows]
    rets = [r[2] for r in rows]

    ic = spearman_ic(dists, rets)
    print(
        f"  Spearman IC (composite_distance vs return_pct): {ic:+.4f}"
        f"  (negative = closer analogs earn more, as hypothesized)"
    )

    buckets: dict[int, list[float]] = {}
    for rank, _dist, ret in rows:
        buckets.setdefault(quantile_bucket(rank), []).append(ret)

    print(f"  {'quantile':>10s} {'n':>6s} {'mean_return_%':>14s}")
    for q in range(1, N_QUANTILES + 1):
        vals = buckets.get(q, [])
        label = f"Q{q}"
        if q == 1:
            label += "(near)"
        elif q == N_QUANTILES:
            label += "(far)"
        mean_pct = (sum(vals) / len(vals) * 100) if vals else float("nan")
        print(f"  {label:>10s} {len(vals):>6d} {mean_pct:>13.3f}%")


def main() -> int:
    catalog_path = get_latest_catalog()
    print(f"Catalog: {catalog_path}")
    print("=" * 60)
    conn = sqlite3.connect(str(catalog_path))
    try:
        for h in FORWARD_HORIZONS:
            report_horizon(conn, h)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
