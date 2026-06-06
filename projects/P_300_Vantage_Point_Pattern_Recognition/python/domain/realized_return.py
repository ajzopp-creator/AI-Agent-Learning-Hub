"""
Realized return computation.

Mirrors domain/labeler.py logic exactly:
    return_pct = (close_at_horizon - close_at_anchor) / close_at_anchor

Pure domain logic; no I/O, no DB.
"""


def compute_realized_returns(
    anchor_close: float,
    horizon_closes: dict[int, float],
) -> dict[int, float]:
    """
    Compute realized forward returns from anchor close + horizon closes.
    
    Mirrors labeler.py's compute_forward_labels logic for apples-to-apples
    comparison between predicted (catalog) and realized (market) returns.
    
    Args:
        anchor_close: Close price at signal_date (anchor bar).
        horizon_closes: Dict mapping horizon_days -> close_price.
            Keys are (5, 7, 10, 15, 20) typically.
    
    Returns:
        Dict mapping horizon_days -> return_pct (decimal fraction).
        Example: {5: 0.0342, 7: 0.0510, 10: 0.0621, 15: 0.0755, 20: 0.0891}
        This means +3.42% at 5 days, +5.10% at 7 days, etc.
    
    Raises:
        ValueError if anchor_close <= 0.
    """
    if anchor_close <= 0:
        raise ValueError(f"anchor_close must be positive; got {anchor_close}")
    
    realized = {}
    for horizon, close_at_horizon in horizon_closes.items():
        return_pct = (close_at_horizon - anchor_close) / anchor_close
        realized[horizon] = return_pct
    
    return realized


def is_profitable(
    return_pct: float,
    min_threshold: float = 0.0,
) -> bool:
    """
    Check if realized return exceeds a threshold.
    
    Args:
        return_pct: Decimal fraction (0.0342 = +3.42%).
        min_threshold: Minimum return to be considered profitable (default 0.0).
    
    Returns:
        True if return_pct >= min_threshold.
    """
    return return_pct >= min_threshold
