"""
FILE: cap_sensitivity_audit.py
VERSION: 1.0
DATE: 2026-05-20
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Read-only audit of per-symbol distributional structure across all 17 raw
    VP fields and 10 normalized derivatives on pattern_bars.

    Purpose: identify which fields carry residual cap-class signal AFTER the
    normalization layer. Output is per-field cross-symbol dispersion of
    per-symbol medians plus coefficient of variation. High dispersion on a
    NORMALIZED field = normalization did not kill cap-sensitivity for that
    field, making it a candidate for the post-filter cap-divergence flag in
    Pipeline B report metadata (Thread B / Stage 6 Decision B addendum).

    Read-only against catalog: no Check-In/Check-Out bracketing required.
    Cap class is inferred at interpretation time via median close as a
    rough proxy (cleanest available without a cap-class column on symbols).

CHANGELOG:
    - 2026-05-20 v1.0: Initial Thread B audit utility.
"""
from __future__ import annotations

import sqlite3
import statistics
import sys
from pathlib import Path

# Add python/ to sys.path so 'from utilities.db_utils import ...' resolves
# when invoked from project root as:
#   python python/utilities/cap_sensitivity_audit.py
SCRIPT_DIR = Path(__file__).parent
PYTHON_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(PYTHON_DIR))

from utilities.db_utils import get_latest_catalog  # noqa: E402


RAW_FIELDS: list[str] = [
    "open", "high", "low", "close", "volume",
    "stdiff", "mtdiff", "ltdiff",
    "pred_high", "pred_low", "pred_range",
    "williams_emai", "psi", "neural_index",
    "triple_cross_short", "triple_cross_medium", "triple_cross_long",
]

NORM_FIELDS: list[str] = [
    "close_pct_from_anchor", "range_pct", "body_pct", "volume_zscore",
    "stdiff_pct", "mtdiff_pct", "ltdiff_pct",
    "pred_high_pct", "pred_low_pct", "pred_range_pct",
]


def per_symbol_median(conn: sqlite3.Connection, field: str) -> dict[str, float]:
    """Return per-symbol median of `field` across all pattern_bars rows."""
    sql = f"""
        SELECT s.ticker, pb.{field}
          FROM pattern_bars pb
          JOIN pattern_instances pi
            ON pi.pattern_instance_id = pb.pattern_instance_id
          JOIN symbols s
            ON s.symbol_id = pi.symbol_id
         ORDER BY s.ticker
    """
    cur = conn.cursor()
    cur.execute(sql)
    by_symbol: dict[str, list[float]] = {}
    for ticker, value in cur:
        by_symbol.setdefault(ticker, []).append(value)
    return {t: statistics.median(vs) for t, vs in by_symbol.items()}


def dispersion(per_symbol: dict[str, float]) -> tuple[float, float, float]:
    """Return (median_of_medians, stdev_of_medians, coeff_of_variation)."""
    vals = list(per_symbol.values())
    med = statistics.median(vals)
    sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
    cv = sd / abs(med) if med != 0 else float("inf")
    return med, sd, cv


def print_field_block(
    field: str,
    per_symbol: dict[str, float],
    sort_by: list[str],
) -> None:
    """Print per-symbol table sorted by `sort_by` (ascending cap proxy)."""
    print(f"\n--- {field}")
    print(f"  {'ticker':<8s} {'median':>14s}")
    for ticker in sort_by:
        if ticker in per_symbol:
            print(f"  {ticker:<8s} {per_symbol[ticker]:>14.6f}")
    med, sd, cv = dispersion(per_symbol)
    print(
        f"  -> dispersion: median_of_medians={med:.4f}"
        f"  stdev_of_medians={sd:.4f}  cv={cv:.4f}"
    )


def audit_field_group(
    conn: sqlite3.Connection,
    label: str,
    fields: list[str],
    sort_by: list[str],
) -> list[tuple[str, float]]:
    """Run audit on a field group; return [(field, stdev_of_medians), ...]."""
    print(f"\n{'=' * 76}\n{label}\n{'=' * 76}")
    dispersions: list[tuple[str, float]] = []
    for field in fields:
        per = per_symbol_median(conn, field)
        print_field_block(field, per, sort_by)
        _, sd, _ = dispersion(per)
        dispersions.append((field, sd))
    return dispersions


def main() -> int:
    catalog_path = get_latest_catalog()
    print(f"Catalog: {catalog_path}")
    print("=" * 76)

    conn = sqlite3.connect(str(catalog_path))
    try:
        # Sort symbols by median close (cap proxy ascending)
        close_med = per_symbol_median(conn, "close")
        sort_by = sorted(close_med, key=lambda t: close_med[t])
        print("Symbols sorted by median close (cap proxy ascending):")
        for ticker in sort_by:
            print(f"  {ticker:<8s} median_close={close_med[ticker]:>10.2f}")

        raw_disp = audit_field_group(conn, "RAW FIELDS", RAW_FIELDS, sort_by)
        norm_disp = audit_field_group(
            conn, "NORMALIZED FIELDS", NORM_FIELDS, sort_by
        )

        print(
            f"\n{'=' * 76}"
            f"\nSUMMARY: stdev_of_per_symbol_medians (HIGH = more cap-coded)"
            f"\n{'=' * 76}"
        )
        print("\nRaw fields ranked:")
        for f, sd in sorted(raw_disp, key=lambda x: -x[1]):
            print(f"  {f:<25s} {sd:>14.6f}")
        print("\nNormalized fields ranked:")
        for f, sd in sorted(norm_disp, key=lambda x: -x[1]):
            print(f"  {f:<25s} {sd:>14.6f}")

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
