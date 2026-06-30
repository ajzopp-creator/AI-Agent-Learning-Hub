"""
Ledger fill orchestration.

Reads unfilled ledger rows, fetches price history, computes realized returns,
updates ledger. Non-blocking: partial fills OK, errors logged.

VERSION: 1.3
DATE: 2026-06-29
CHANGELOG:
    - 2026-06-29 v1.3: M-064 fix -- the persist call (update_realized_outcome)
      was only ever reached inside the is_filled() branch (all 5 horizons
      present). Every partial outcome (h5/h7/h10/h15 ready, h20 pending --
      i.e. every single row given the project's age) was computed and then
      silently discarded, never written. Now persists on ANY new horizon
      data, paired with a COALESCE-based update_realized_outcome() (M-064
      in ledger_db.py) so a None field never clobbers an already-saved
      value. This was the 3rd of 3 stacked bugs (M-060/M-061/M-064) found
      in succession while trying to get a single ledger-fill run to
      actually write anything.
    - 2026-06-29 v1.2: M-063 fix -- fetch window widened from +25 to +35
      calendar days. 25 days only yields ~17-18 trading days (5/7 ratio),
      but h20 needs at least 21 (anchor + 20 forward) -- the window was
      structurally incapable of ever reaching h20 regardless of how much
      time had elapsed. Caught immediately after the M-060/M-061 fixes
      both landed clean but "Filled 0/142" persisted with no errors.
    - 2026-06-29 v1.1: M-060 fix -- signal_date arrives from fired_signals as
      YYYY-MM-DD (catalog/ISO convention); _try_fill_outcome() was parsing it
      as YYYYMMDD (AddPattern filename convention), throwing on every single
      row since the ledger system was built (2026-06-03). Normalized once at
      function entry via signal_date_norm; zero rows had ever filled before
      this fix.

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
        
        # M-064: persist whenever ANY horizon was newly computed, not only
        # when all 5 are present. Previously this block only called
        # update_realized_outcome() inside the is_filled() branch, so a
        # partial outcome (e.g. h5/h7/h10/h15 ready, h20 still pending)
        # was computed in memory and then silently discarded every time --
        # nothing was ever written for a partial fill. Combined with
        # update_realized_outcome()'s COALESCE (M-064 in ledger_db.py),
        # this is now safe to call on every run as more horizons mature.
        has_new_data = any([
            outcome.h5_return_pct is not None,
            outcome.h7_return_pct is not None,
            outcome.h10_return_pct is not None,
            outcome.h15_return_pct is not None,
            outcome.h20_return_pct is not None,
        ])
        
        if has_new_data:
            logger.info(
                f"Ledger {ledger_id}: {ticker} {signal_date} "
                f"h5={outcome.h5_return_pct} h7={outcome.h7_return_pct} "
                f"h10={outcome.h10_return_pct} h15={outcome.h15_return_pct} "
                f"h20={outcome.h20_return_pct}"
            )
            if not dry_run:
                ledger_db.update_realized_outcome(ledger_id, outcome)
            if outcome.is_filled():
                filled_count += 1
        else:
            logger.debug(
                f"Ledger {ledger_id}: {ticker} {signal_date} "
                f"no new data available yet"
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
        signal_date: Signal date as stored in fired_signals (YYYY-MM-DD,
            ISO/catalog convention). Normalized internally to YYYYMMDD.
    
    Returns:
        RealizedOutcome with populated return fields, or empty if
        insufficient price data.
    """
    try:
        # Compute fetch window: signal_date to +35 calendar days.
        # M-063: 25 days was insufficient -- 25 calendar days yields only
        # ~17-18 trading days (5/7 ratio), but h20 needs history[20], i.e.
        # at least 21 trading days of data (anchor + 20 forward). 35
        # calendar days yields ~25 trading days even with US holidays in
        # the window, giving comfortable margin past the h20 requirement.
        # M-060: signal_date is stored in fired_signals as YYYY-MM-DD (catalog/
        # ISO convention), NOT YYYYMMDD (AddPattern filename convention).
        # Normalize once here; everything downstream in this function uses
        # signal_date_norm (YYYYMMDD), matching fetch_price_history() and its
        # returned anchor_date.
        signal_date_norm = signal_date.replace("-", "")
        signal_dt = datetime.strptime(signal_date_norm, "%Y%m%d")
        fetch_end_dt = signal_dt + timedelta(days=35)
        fetch_end_str = fetch_end_dt.strftime("%Y%m%d")
        
        # Fetch price history.
        history = price_history_reader.fetch_price_history(
            ticker, signal_date_norm, fetch_end_str
        )
        
        if not history:
            logger.warning(
                f"No price history for {ticker} {signal_date_norm}–{fetch_end_str}"
            )
            return RealizedOutcome()  # Empty, unfilled.
        
        # Extract anchor close (first entry should be signal_date or first available).
        anchor_date, anchor_close = history[0]
        if anchor_date != signal_date_norm:
            logger.warning(
                f"Anchor mismatch: expected {signal_date_norm}, "
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
