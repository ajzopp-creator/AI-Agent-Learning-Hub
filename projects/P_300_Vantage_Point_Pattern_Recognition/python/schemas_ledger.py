"""
Ledger domain models.

Captures signal state at fire time (FiredSignal + PredictedStat) and
realized outcomes filled asynchronously (RealizedOutcome).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SignalClass(str, Enum):
    """Signal classification output from daily_evaluate_pipeline."""
    BUY = "BUY"
    WATCH = "WATCH"
    PASS = "PASS"


@dataclass
class FiredSignal:
    """
    Immutable snapshot of a signal at the moment it fires.
    Written immediately to ledger by ledger_record.py.
    
    Attrs:
        ticker: Stock symbol (e.g., "AAPL").
        signal_date: ISO calendar date YYYYMMDD (e.g., "20260603").
        signal_class: BUY, WATCH, or PASS.
        chosen_horizon: Forward-return window in trading days (5, 7, 10, 15, 20).
        pattern_id: Foreign key to catalog.pattern_id that triggered signal.
        pattern_source_file: Name of VP History Grid XLSX that contributed pattern.
        source_file_hash: MD5 hash of source file (detect re-ingestion).
        fired_at: Timestamp (UTC) when recorded.
    """
    ticker: str
    signal_date: str
    signal_class: SignalClass
    chosen_horizon: int
    pattern_id: int
    pattern_source_file: str
    source_file_hash: str
    fired_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PredictedStat:
    """
    Predicted statistics from catalog at fire time.
    Snapshot of AggregatedSignalPerHorizon.chosen_horizon at signal_date.
    
    Attrs:
        n_matches: Number of catalog patterns matched.
        win_rate_pct: Historical win rate (0.0–100.0).
        mean_return_pct: Average forward return.
        std_return_pct: Standard deviation of returns.
        z_score: Distance from threshold (used for confidence tier).
    """
    n_matches: int
    win_rate_pct: float
    mean_return_pct: float
    std_return_pct: float
    z_score: float


@dataclass
class RealizedOutcome:
    """
    Realized forward returns, filled asynchronously by ledger_fill.py.
    All return fields remain None until 20 trading bars elapse.
    
    Attrs:
        h5_return_pct: Realized return at +5 bars (None until filled).
        h7_return_pct: Realized return at +7 bars (None until filled).
        h10_return_pct: Realized return at +10 bars (None until filled).
        h15_return_pct: Realized return at +15 bars (None until filled).
        h20_return_pct: Realized return at +20 bars (None until filled).
        filled_date: Date ledger was filled YYYYMMDD (None until filled).
        filled_at: Timestamp when record was filled (None until filled).
    """
    h5_return_pct: Optional[float] = None
    h7_return_pct: Optional[float] = None
    h10_return_pct: Optional[float] = None
    h15_return_pct: Optional[float] = None
    h20_return_pct: Optional[float] = None
    filled_date: Optional[str] = None
    filled_at: Optional[datetime] = None

    def is_filled(self) -> bool:
        """True if all horizon returns are populated."""
        return all([
            self.h5_return_pct is not None,
            self.h7_return_pct is not None,
            self.h10_return_pct is not None,
            self.h15_return_pct is not None,
            self.h20_return_pct is not None,
        ])

    def fill_partial(self, returns: dict[int, float], fill_date: str) -> None:
        """
        Populate return columns from dict keyed by horizon.
        Called by ledger_fill.py.
        """
        if 5 in returns:
            self.h5_return_pct = returns[5]
        if 7 in returns:
            self.h7_return_pct = returns[7]
        if 10 in returns:
            self.h10_return_pct = returns[10]
        if 15 in returns:
            self.h15_return_pct = returns[15]
        if 20 in returns:
            self.h20_return_pct = returns[20]
        self.filled_date = fill_date
        self.filled_at = datetime.utcnow()
