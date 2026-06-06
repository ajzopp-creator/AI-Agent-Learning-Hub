"""
Ledger fill orchestration.

Reads unfilled ledger rows, fetches price history, computes realized returns,
updates ledger. Non-blocking: partial fills OK, errors logged.

Call: ledger_fill.fill_ledger()
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

from config import MODELS_DIR
from domain import realized_return
from infrastructure import price_history_reader
from infrastructure.ledger_db import LedgerDB
from schemas_ledger import RealizedOutcome

logger = logging.getLogger(__name__)


def fill_ledger(dry_run: bool = False) -> None:
    """
    Fill realized outcomes for unfilled ledger rows.
    
    Iterates unfilled signals, fetches price history, computes realized
    forward returns (5/7/10/15/20-day windows), and updates ledger.
    
    Non-blocking: partial fills OK (e.g., if only 10 trading days have
    passed, fill h5/h7/h10, leave h15/h20 NULL for next call).
    
    Args:
        dry_run: If True, log fills but don't write to DB.
    """
    ledger_db = LedgerDB()
    unfilled = ledger_db.query_unfilled()
    
    if not unfilled:
        logger.info("No unfilled ledger rows.")
        return
    
    logger.info(f"Processing {len(unfilled)} unfilled rows...")
    filled_count = 0
    
    for ledger_id, ticker, signal_date, chosen_horizon in unfilled:
        outcome = _try_fill_outcome(ticker, signal_date)
        
        if outcome.is_filled():
            logger.info(
                f"Ledger {ledger_id}: {ticker} {signal_date} "
                f"h20_return={outcome.h20_return_pct:.4f}"
            )
            if not dry_run:
                ledger_db.update_realized_outcome(ledger_id, outcome)
            filled_count += 1
        else:
            unfilled_horizons = [h for h in [5, 7, 10, 15, 20]
                                 if getattr(outcome, f"h{h}_return_pct") is None]
            if unfilled_horizons:
                logger.debug(
                    f"Ledger {ledger_id}: {ticker} {signal_date} "
                    f"incomplete (missing {unfilled_horizons})"
                )
    
    logger.info(f"Filled {filled_count} / {len(unfilled)} rows")


def _try_fill_outcome(
    ticker: str,
    signal_date: str,
) -> RealizedOutcome:
    """
    Attempt to compute realized returns for one signal.
    
    Fetches price history from signal_date through +25 calendar days.
    Maps trading-day offsets (5/7/10/15/20) to history entries.
    Returns partially-filled RealizedOutcome if some horizons unavailable.
    
    Args:
        ticker: Stock symbol.
        signal_date: Signal date in YYYYMMDD format.
    
    Returns:
        RealizedOutcome with populated return fields, or empty if
        insufficient price data.
    """
    try:
        # Compute fetch window: signal_date to +25 calendar days.
        # (25 days allows up to 20 trading days; weekends/holidays reduce count.)
        signal_dt = datetime.strptime(signal_date, "%Y%m%d")
        fetch_end_dt = signal_dt + timedelta(days=25)
        fetch_end_str = fetch_end_dt.strftime("%Y%m%d")
        
        # Fetch price history.
        history = price_history_reader.fetch_price_history(
            ticker, signal_date, fetch_end_str
        )
        
        if not history:
            logger.warning(
                f"No price history for {ticker} {signal_date}–{fetch_end_str}"
            )
            return RealizedOutcome()  # Empty, unfilled.
        
        # Extract anchor close (first entry should be signal_date or first available).
        anchor_date, anchor_close = history[0]
        if anchor_date != signal_date:
            logger.warning(
                f"Anchor mismatch: expected {signal_date}, "
                f"earliest history {anchor_date}. Using earliest."
            )
        
        # Map horizons (5, 7, 10, 15, 20 trading days) to history offsets.
        # history[0] = anchor, history[5] = +5 trading days, etc.
        # (yfinance returns sorted trading days; no weekends/holidays.)
        horizon_closes = {}
        for horizon in [5, 7, 10, 15, 20]:
            if horizon < len(history):
                _, close = history[horizon]
                horizon_closes[horizon] = close
        
        # If we have all horizons: compute returns.
        if len(horizon_closes) == 5:
            returns = realized_return.compute_realized_returns(
                anchor_close, horizon_closes
            )
            outcome = RealizedOutcome(
                h5_return_pct=returns[5],
                h7_return_pct=returns[7],
                h10_return_pct=returns[10],
                h15_return_pct=returns[15],
                h20_return_pct=returns[20],
                filled_date=datetime.now().strftime("%Y%m%d"),
                filled_at=datetime.utcnow(),
            )
            return outcome
        else:
            # Partial fill: populate available horizons, leave rest NULL.
            # (ledger_db.update_realized_outcome handles partial updates.)
            outcome = RealizedOutcome(filled_at=datetime.utcnow())
            if 5 in horizon_closes:
                outcome.h5_return_pct = realized_return.compute_realized_returns(
                    anchor_close, {5: horizon_closes[5]}
                )[5]
            if 7 in horizon_closes:
                outcome.h7_return_pct = realized_return.compute_realized_returns(
                    anchor_close, {7: horizon_closes[7]}
                )[7]
            if 10 in horizon_closes:
                outcome.h10_return_pct = realized_return.compute_realized_returns(
                    anchor_close, {10: horizon_closes[10]}
                )[10]
            if 15 in horizon_closes:
                outcome.h15_return_pct = realized_return.compute_realized_returns(
                    anchor_close, {15: horizon_closes[15]}
                )[15]
            if 20 in horizon_closes:
                outcome.h20_return_pct = realized_return.compute_realized_returns(
                    anchor_close, {20: horizon_closes[20]}
                )[20]
            outcome.filled_date = datetime.now().strftime("%Y%m%d")
            return outcome
    
    except Exception as e:
        logger.error(f"Failed to fill {ticker} {signal_date}: {e}", exc_info=True)
        return RealizedOutcome()


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    fill_ledger()
