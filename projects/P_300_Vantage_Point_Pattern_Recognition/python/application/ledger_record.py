"""
Ledger record hook.

Called by daily_evaluate_pipeline.py after classify_signal() to snapshot
predicted stats and fire a ledger row. Best-effort: non-blocking on error.
"""

import logging
import sqlite3
from datetime import datetime
from typing import Optional

from config import MODELS_DIR
from domain.signal_classifier import AggregatedSignalPerHorizon
from infrastructure.ledger_db import LedgerDB
from schemas_ledger import FiredSignal, PredictedStat, SignalClass

logger = logging.getLogger(__name__)


def record_fired_signal(
    ticker: str,
    signal_date: str,
    signal_class: SignalClass,
    chosen_horizon: int,
    pattern_id: int,
    aggregated_horizon: AggregatedSignalPerHorizon
) -> Optional[int]:
    """
    Record a fired signal to ledger (best-effort, non-blocking).
    
    Called immediately after classify_signal() returns a BUY or WATCH.
    Snapshots predicted stats for later confidence calibration against realized returns.
    Errors are logged but do NOT block the signal from firing.
    
    Args:
        ticker: Stock symbol (e.g., "AAPL").
        signal_date: ISO date YYYYMMDD.
        signal_class: BUY, WATCH, or PASS.
        chosen_horizon: Forward-return window (5, 7, 10, 15, 20 trading days).
        pattern_id: Catalog pattern_id that matched.
        aggregated_horizon: AggregatedSignalPerHorizon for chosen_horizon.
    
    Returns:
        ledger_id if successful, None if write failed (logged, non-fatal).
    """
    try:
        # Fetch pattern metadata from catalog.
        # We need source_file and source_file_hash for the fired_signal snapshot.
        from pathlib import Path
        from glob import glob
        
        # Find latest catalog DB by modification time (glob *.db, sort by mtime).
        catalog_pattern = str(MODELS_DIR / "*catalog.db")
        catalog_files = glob(catalog_pattern)
        if not catalog_files:
            logger.warning(f"No catalog found at {catalog_pattern}, skipping ledger record")
            return None
        
        catalog_path = max(catalog_files, key=lambda p: Path(p).stat().st_mtime)
        
        # Query catalog for the source file name and ID.
        # We'll use source_file name as identifier (no hash in catalog schema).
        with sqlite3.connect(catalog_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sf.filename
                FROM pattern_instances pi
                JOIN source_files sf ON pi.source_file_id = sf.source_file_id
                WHERE pi.pattern_instance_id = ?
            """, (pattern_id,))
            row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Pattern {pattern_id} not found in catalog, skipping ledger record.")
            return None
        
        source_file = row[0]
        source_file_hash = source_file  # Use filename as identifier (no hash available)
        
        # Construct domain objects.
        fired_signal = FiredSignal(
            ticker=ticker,
            signal_date=signal_date,
            signal_class=signal_class,
            chosen_horizon=chosen_horizon,
            pattern_id=pattern_id,
            pattern_source_file=source_file,
            source_file_hash=source_file_hash,
            fired_at=datetime.utcnow()
        )
        
        predicted_stat = PredictedStat(
            n_matches=aggregated_horizon.n_matches,
            win_rate_pct=aggregated_horizon.win_rate * 100.0,
            mean_return_pct=aggregated_horizon.mean_return_pct,
            std_return_pct=aggregated_horizon.std_return_pct,
            z_score=aggregated_horizon.z_score
        )
        
        # Write to ledger.
        ledger_db = LedgerDB()
        ledger_id = ledger_db.insert_fired_signal(fired_signal, predicted_stat)
        logger.info(f"Ledger record: {ticker} {signal_date} {signal_class.value} → ledger_id={ledger_id}")
        return ledger_id
    
    except Exception as e:
        logger.warning(f"Ledger record FAILED for {ticker} {signal_date}: {e}", exc_info=False)
        return None
