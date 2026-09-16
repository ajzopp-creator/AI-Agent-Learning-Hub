"""
FILE: ledger_calibration.py
VERSION: 1.1
DATE: 2026-07-02
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Compares predicted (catalog) vs realized (market) forward returns for
    fired ledger signals, grouped by each signal's own chosen_horizon.

    Confidence factor = realized_win_rate / predicted_win_rate
    Values > 1.0 indicate signal edge stronger than predicted.

CHANGELOG:
    - 2026-07-02 v1.1: Two bugs fixed (todo.md open item, M-046 gate).
      (1) Query required h20_return_pct IS NOT NULL on every row before
      it counted at all -- with the catalog this young, that limited the
      report to 2 rows (DE, COHR) regardless of how many signals had
      their OWN chosen_horizon already filled. Now each row only needs
      its own chosen_horizon column filled.
      (2) predicted_win_rate/mean_return are computed by the classifier
      for a signal's chosen_horizon specifically (one prediction, one
      horizon -- confirmed in ledger_db.py's insert_fired_signal). The
      old code paired that single value against realized returns at ALL
      5 horizon columns, comparing e.g. a 5-day prediction against a
      20-day realized outcome. Now a row is grouped into exactly one
      horizon bucket (its own chosen_horizon) and compared only there.
    - Pre-1.1: Initial version. Filtered on h20_return_pct IS NOT NULL;
      broadcast every row's prediction across all 5 horizon buckets.
"""

import logging
import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from infrastructure.ledger_db import LedgerDB

logger = logging.getLogger(__name__)

_HORIZON_COLUMNS: Dict[int, str] = {
    5: "h5_return_pct",
    7: "h7_return_pct",
    10: "h10_return_pct",
    15: "h15_return_pct",
    20: "h20_return_pct",
}


@dataclass
class HorizonCalibration:
    """Per-horizon calibration metrics -- only rows fired AT this horizon."""
    horizon_days: int
    sample_count: int
    predicted_win_rate: float
    realized_win_rate: float
    confidence_factor: float
    avg_predicted_return: float
    avg_realized_return: float

    def __str__(self) -> str:
        return (
            f"h{self.horizon_days:2d} | "
            f"n={self.sample_count:3d} | "
            f"pred_wr={self.predicted_win_rate:.1%} | "
            f"real_wr={self.realized_win_rate:.1%} | "
            f"conf={self.confidence_factor:.2f} | "
            f"ret={self.avg_realized_return:+.2%}"
        )


@dataclass
class LedgerCalibrationReport:
    """Overall calibration report."""
    total_signals: int
    total_usable: int
    usable_pct: float
    per_horizon: Dict[int, HorizonCalibration]
    overall_confidence: float

    def __str__(self) -> str:
        lines = [
            "Ledger Calibration Report",
            "========================",
            f"Total signals: {self.total_signals}",
            f"Usable (own chosen_horizon filled): {self.total_usable} "
            f"({self.usable_pct:.1%})",
            "",
            "Per-Horizon Metrics (each row compared only at its own",
            "chosen_horizon -- not broadcast across all 5 columns):",
            "-" * 90,
        ]
        for h in (5, 7, 10, 15, 20):
            if h in self.per_horizon:
                lines.append(str(self.per_horizon[h]))
        lines.extend([
            "-" * 90,
            f"Overall confidence factor: {self.overall_confidence:.2f}",
        ])
        return "\n".join(lines)


def calibrate_ledger() -> LedgerCalibrationReport:
    """
    Generate calibration report from ledger.

    Each fired signal is compared only against the realized return at its
    OWN chosen_horizon -- a row with chosen_horizon=5 contributes to the
    h5 bucket only, using h5_return_pct, regardless of whether h15/h20
    have filled yet.

    Returns:
        LedgerCalibrationReport with per-horizon and overall metrics.
    """
    ledger_db = LedgerDB()

    with sqlite3.connect(ledger_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM fired_signals")
        total_signals = cursor.fetchone()[0]

        cursor.execute("""
            SELECT chosen_horizon, win_rate_pct, mean_return_pct,
                   h5_return_pct, h7_return_pct, h10_return_pct,
                   h15_return_pct, h20_return_pct
            FROM fired_signals
            ORDER BY signal_date ASC
        """)
        rows = cursor.fetchall()

    horizons_data: Dict[int, List[Tuple[float, float, float]]] = {
        h: [] for h in _HORIZON_COLUMNS
    }
    usable_count = 0

    for row in rows:
        chosen_horizon, win_rate_pct, mean_ret, h5, h7, h10, h15, h20 = row
        realized_by_col = {5: h5, 7: h7, 10: h10, 15: h15, 20: h20}
        realized_ret: Optional[float] = realized_by_col.get(chosen_horizon)

        if realized_ret is None or chosen_horizon not in horizons_data:
            continue  # This signal's own horizon hasn't landed yet.

        usable_count += 1
        horizons_data[chosen_horizon].append(
            (realized_ret, win_rate_pct / 100.0, mean_ret)
        )

    per_horizon: Dict[int, HorizonCalibration] = {}
    all_predicted_wrs: List[float] = []
    all_realized_wins: List[int] = []

    for horizon, data in horizons_data.items():
        if not data:
            continue

        realized_returns = [d[0] for d in data]
        predicted_wrs = [d[1] for d in data]
        predicted_returns = [d[2] for d in data]

        realized_wr = sum(1 for r in realized_returns if r > 0.0) / len(data)
        predicted_wr = sum(predicted_wrs) / len(predicted_wrs)
        confidence = realized_wr / predicted_wr if predicted_wr > 0 else 0.0

        per_horizon[horizon] = HorizonCalibration(
            horizon_days=horizon,
            sample_count=len(data),
            predicted_win_rate=predicted_wr,
            realized_win_rate=realized_wr,
            confidence_factor=confidence,
            avg_predicted_return=sum(predicted_returns) / len(predicted_returns),
            avg_realized_return=sum(realized_returns) / len(realized_returns),
        )
        logger.info("h%s: %s", horizon, per_horizon[horizon])

        all_predicted_wrs.extend(predicted_wrs)
        all_realized_wins.extend(1 if r > 0.0 else 0 for r in realized_returns)

    overall_predicted = (
        sum(all_predicted_wrs) / len(all_predicted_wrs) if all_predicted_wrs else 0.0
    )
    overall_realized = (
        sum(all_realized_wins) / len(all_realized_wins) if all_realized_wins else 0.0
    )
    overall_confidence = (
        overall_realized / overall_predicted if overall_predicted > 0 else 0.0
    )

    return LedgerCalibrationReport(
        total_signals=total_signals,
        total_usable=usable_count,
        usable_pct=usable_count / total_signals if total_signals > 0 else 0.0,
        per_horizon=per_horizon,
        overall_confidence=overall_confidence,
    )
