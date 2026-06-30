"""
Ledger database interface.

Manages schema initialization, signal capture (insert), and outcome filling (query/update).
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

from config import BUY_LEDGER_DB, LEDGER_DIR
from schemas_ledger import FiredSignal, PredictedStat, RealizedOutcome, SignalClass


class LedgerDB:
    """SQLite ledger for fired signals and realized outcomes."""

    def __init__(self, db_path: Path = BUY_LEDGER_DB):
        """Initialize ledger DB, creating directory and table if needed."""
        self.db_path = db_path
        
        # Ensure ledger directory exists.
        LEDGER_DIR.mkdir(parents=True, exist_ok=True)
        
        # Create table if not exists.
        self._init_schema()

    def _init_schema(self) -> None:
        """Create fired_signals table if not present."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fired_signals (
                    ledger_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    signal_date TEXT NOT NULL,
                    signal_class TEXT NOT NULL,
                    chosen_horizon INTEGER NOT NULL,
                    pattern_id INTEGER NOT NULL,
                    pattern_source_file TEXT NOT NULL,
                    source_file_hash TEXT NOT NULL,
                    n_matches INTEGER NOT NULL,
                    win_rate_pct REAL NOT NULL,
                    mean_return_pct REAL NOT NULL,
                    std_return_pct REAL NOT NULL,
                    z_score REAL NOT NULL,
                    h5_return_pct REAL,
                    h7_return_pct REAL,
                    h10_return_pct REAL,
                    h15_return_pct REAL,
                    h20_return_pct REAL,
                    filled_date TEXT,
                    fired_at TEXT NOT NULL,
                    filled_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def insert_fired_signal(
        self,
        fired_signal: FiredSignal,
        predicted_stat: PredictedStat
    ) -> int:
        """
        Insert a fired signal + predicted stats snapshot.
        Returns ledger_id for later outcome fill.
        
        Args:
            fired_signal: Immutable snapshot at fire time.
            predicted_stat: Predicted stats from catalog.
        
        Returns:
            ledger_id (auto-incremented).
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO fired_signals (
                    ticker, signal_date, signal_class, chosen_horizon,
                    pattern_id, pattern_source_file, source_file_hash,
                    n_matches, win_rate_pct, mean_return_pct, std_return_pct, z_score,
                    fired_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fired_signal.ticker,
                fired_signal.signal_date,
                fired_signal.signal_class.value,
                fired_signal.chosen_horizon,
                fired_signal.pattern_id,
                fired_signal.pattern_source_file,
                fired_signal.source_file_hash,
                predicted_stat.n_matches,
                predicted_stat.win_rate_pct,
                predicted_stat.mean_return_pct,
                predicted_stat.std_return_pct,
                predicted_stat.z_score,
                fired_signal.fired_at.isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    def query_unfilled(self) -> List[Tuple]:
        """
        Retrieve all rows with unfilled realized returns.
        For ledger_fill.py to process.
        
        M-062: checks h20_return_pct (the LAST horizon to fill), not
        h5_return_pct. The original h5 check meant any row that got even
        a partial fill (h5 only) would drop out of this query forever,
        permanently freezing h7/h10/h15/h20 as NULL with no way to ever
        revisit and complete them.
        
        Returns:
            List of (ledger_id, ticker, signal_date, chosen_horizon) tuples.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ledger_id, ticker, signal_date, chosen_horizon
                FROM fired_signals
                WHERE h20_return_pct IS NULL
                ORDER BY signal_date ASC
            """)
            return cursor.fetchall()

    def update_realized_outcome(
        self,
        ledger_id: int,
        outcome: RealizedOutcome
    ) -> None:
        """
        Update realized outcome for a ledger row.
        Called by ledger_fill.py after computing forward returns.
        
        M-064: uses COALESCE so a None field in `outcome` (a horizon not
        yet reachable -- e.g. h20 before 20 trading days have elapsed)
        preserves whatever is already in the DB rather than overwriting
        a previously-filled value with NULL. Safe to call repeatedly as
        more horizons become available across multiple runs.
        
        Args:
            ledger_id: Primary key in fired_signals.
            outcome: RealizedOutcome with any subset of h5/h7/h10/h15/h20
                populated; None fields are left untouched in the DB.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE fired_signals
                SET h5_return_pct = COALESCE(?, h5_return_pct),
                    h7_return_pct = COALESCE(?, h7_return_pct),
                    h10_return_pct = COALESCE(?, h10_return_pct),
                    h15_return_pct = COALESCE(?, h15_return_pct),
                    h20_return_pct = COALESCE(?, h20_return_pct),
                    filled_date = COALESCE(?, filled_date),
                    filled_at = COALESCE(?, filled_at)
                WHERE ledger_id = ?
            """, (
                outcome.h5_return_pct,
                outcome.h7_return_pct,
                outcome.h10_return_pct,
                outcome.h15_return_pct,
                outcome.h20_return_pct,
                outcome.filled_date,
                outcome.filled_at.isoformat() if outcome.filled_at else None,
                ledger_id
            ))
            conn.commit()

    def count_filled(self) -> int:
        """Number of fully-filled ledger rows."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM fired_signals
                WHERE h20_return_pct IS NOT NULL
            """)
            return cursor.fetchone()[0]

    def count_unfilled(self) -> int:
        """Number of unfilled ledger rows."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM fired_signals
                WHERE h5_return_pct IS NULL
            """)
            return cursor.fetchone()[0]
