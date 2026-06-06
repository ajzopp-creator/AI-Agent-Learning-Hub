"""
Ledger calibration utility.

Computes confidence factors by comparing predicted (catalog) vs realized (market) 
forward returns for all filled ledger rows.

Confidence factor = realized_win_rate / predicted_win_rate
Values > 1.0 indicate signal edge stronger than predicted.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

from infrastructure.ledger_db import LedgerDB

logger = logging.getLogger(__name__)


@dataclass
class HorizonCalibration:
    """Per-horizon calibration metrics."""
    horizon_days: int
    sample_count: int
    predicted_win_rate: float  # Mean of n_matches predictions (0.0–1.0)
    realized_win_rate: float   # Fraction of signals with positive return
    confidence_factor: float   # realized_win_rate / predicted_win_rate
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
    total_filled: int
    filled_pct: float
    per_horizon: Dict[int, HorizonCalibration]
    overall_confidence: float
    
    def __str__(self) -> str:
        lines = [
            f"Ledger Calibration Report",
            f"========================",
            f"Total signals: {self.total_signals}",
            f"Filled: {self.total_filled} ({self.filled_pct:.1%})",
            f"",
            "Per-Horizon Metrics:",
            "-" * 90,
        ]
        for h in [5, 7, 10, 15, 20]:
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
    
    Compares predicted forward returns (catalog) against realized returns (market)
    for all filled ledger rows. Computes per-horizon and overall confidence factors.
    
    Returns:
        LedgerCalibrationReport with detailed metrics.
    """
    ledger_db = LedgerDB()
    
    import sqlite3
    with sqlite3.connect(ledger_db.db_path) as conn:
        cursor = conn.cursor()
        
        # Get total count.
        cursor.execute("SELECT COUNT(*) FROM fired_signals")
        total_signals = cursor.fetchone()[0]
        
        # Get filled count.
        cursor.execute("SELECT COUNT(*) FROM fired_signals WHERE h20_return_pct IS NOT NULL")
        total_filled = cursor.fetchone()[0]
        
        # Get all filled rows.
        cursor.execute("""
            SELECT 
                h5_return_pct, h7_return_pct, h10_return_pct, h15_return_pct, h20_return_pct,
                n_matches, win_rate_pct, mean_return_pct
            FROM fired_signals
            WHERE h20_return_pct IS NOT NULL
            ORDER BY signal_date ASC
        """)
        rows = cursor.fetchall()
    
    if not rows:
        logger.warning("No filled ledger rows found.")
        return LedgerCalibrationReport(
            total_signals=total_signals,
            total_filled=0,
            filled_pct=0.0,
            per_horizon={},
            overall_confidence=0.0,
        )
    
    # Group by horizon and compute metrics.
    horizons_data: Dict[int, List[Tuple]] = {5: [], 7: [], 10: [], 15: [], 20: []}
    all_predictions = []
    
    for row in rows:
        h5_ret, h7_ret, h10_ret, h15_ret, h20_ret, n_matches, win_rate_pct, mean_ret = row
        
        all_predictions.append(win_rate_pct / 100.0)  # Convert to fraction
        
        horizons_data[5].append((h5_ret, win_rate_pct / 100.0, mean_ret))
        horizons_data[7].append((h7_ret, win_rate_pct / 100.0, mean_ret))
        horizons_data[10].append((h10_ret, win_rate_pct / 100.0, mean_ret))
        horizons_data[15].append((h15_ret, win_rate_pct / 100.0, mean_ret))
        horizons_data[20].append((h20_ret, win_rate_pct / 100.0, mean_ret))
    
    # Compute per-horizon calibration.
    per_horizon = {}
    for horizon, data in horizons_data.items():
        if not data:
            continue
        
        realized_returns = [d[0] for d in data]
        predicted_wrs = [d[1] for d in data]
        predicted_returns = [d[2] for d in data]
        
        # Win rate = fraction with positive return.
        realized_wr = sum(1 for r in realized_returns if r > 0.0) / len(realized_returns)
        predicted_wr = sum(predicted_wrs) / len(predicted_wrs)  # Average predicted WR
        
        # Confidence = realized / predicted (avoid division by zero).
        confidence = realized_wr / predicted_wr if predicted_wr > 0 else 0.0
        
        avg_realized = sum(realized_returns) / len(realized_returns)
        avg_predicted = sum(predicted_returns) / len(predicted_returns)
        
        per_horizon[horizon] = HorizonCalibration(
            horizon_days=horizon,
            sample_count=len(data),
            predicted_win_rate=predicted_wr,
            realized_win_rate=realized_wr,
            confidence_factor=confidence,
            avg_predicted_return=avg_predicted,
            avg_realized_return=avg_realized,
        )
        
        logger.info(f"h{horizon}: {per_horizon[horizon]}")
    
    # Overall confidence.
    overall_predicted = sum(all_predictions) / len(all_predictions) if all_predictions else 0.0
    overall_realized = sum(1 for p in all_predictions if p > 0.0) / len(all_predictions) if all_predictions else 0.0
    overall_confidence = overall_realized / overall_predicted if overall_predicted > 0 else 0.0
    
    filled_pct = total_filled / total_signals if total_signals > 0 else 0.0
    
    report = LedgerCalibrationReport(
        total_signals=total_signals,
        total_filled=total_filled,
        filled_pct=filled_pct,
        per_horizon=per_horizon,
        overall_confidence=overall_confidence,
    )
    
    return report
