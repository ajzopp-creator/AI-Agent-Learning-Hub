"""
P_010 Intraday VP Check -- Risk Logic
Split from P_010_intraday_vp_check_v4.py (WO-P010-E1.003 housekeeping, 2026-08-10).
PRANGE validation and the morning-baseline + intraday-signal risk mode decision.
Pure logic -- no I/O, no network calls.
"""


def validate_against_prange(grid_close, current_price, pred_high, pred_low):
    """Validate current price against predicted range (PRANGE)."""
    price_change = current_price - grid_close
    price_move_pct = (price_change / grid_close) * 100

    if current_price > pred_high:
        band_status = "above_band"
        deviation_pct = ((current_price - pred_high) / pred_high) * 100
        deviation_from = "pred_high"
    elif current_price < pred_low:
        band_status = "below_band"
        deviation_pct = ((pred_low - current_price) / pred_low) * 100
        deviation_from = "pred_low"
    else:
        band_status = "in_band"
        deviation_pct = 0.0
        deviation_from = None

    return {
        'grid_close': grid_close,
        'current': current_price,
        'price_change': price_change,
        'price_move_pct': round(price_move_pct, 2),
        'pred_high': pred_high,
        'pred_low': pred_low,
        'band_status': band_status,
        'deviation_pct': round(abs(deviation_pct), 2),
        'deviation_from': deviation_from
    }


def determine_final_risk_mode(morning_risk_mode, spy_validation, qqq_validation):
    """
    Determine final risk mode based on morning baseline and intraday price action.

    Three-State System: OFF (0%), HALF (50%), FULL (100%)

    Logic:
    - ABOVE PRANGE = Market stronger than predicted = UPGRADE
    - IN PRANGE = Market as predicted = CONFIRM
    - BELOW PRANGE = Market weaker than predicted = DOWNGRADE
    """

    spy_status = spy_validation['band_status']
    qqq_status = qqq_validation['band_status']

    # Determine market signal based on both symbols
    if spy_status == 'above_band' and qqq_status == 'above_band':
        signal = "UPGRADE"
    elif spy_status == 'below_band' and qqq_status == 'below_band':
        signal = "DOWNGRADE"
    elif spy_status == 'in_band' and qqq_status == 'in_band':
        signal = "CONFIRM"
    else:
        # Mixed signals - be conservative
        if spy_status == 'below_band' or qqq_status == 'below_band':
            signal = "DOWNGRADE"
        else:
            signal = "CONFIRM"

    # Apply directional adjustment to morning baseline
    if signal == "UPGRADE":
        if morning_risk_mode == "OFF":
            final_mode = "HALF"
            reason = "Intraday upgrade: Market stronger than predicted (prices above PRANGE)"
        elif morning_risk_mode == "HALF":
            final_mode = "FULL"
            reason = "Intraday upgrade: Market stronger than predicted (prices above PRANGE)"
        else:  # FULL
            final_mode = "FULL"
            reason = "Intraday confirm: Market strength confirmed (prices above PRANGE)"

    elif signal == "DOWNGRADE":
        if morning_risk_mode == "FULL":
            final_mode = "HALF"
            reason = "Intraday downgrade: Market weaker than predicted (prices below PRANGE)"
        elif morning_risk_mode == "HALF":
            final_mode = "OFF"
            reason = "Intraday downgrade: Market weaker than predicted (prices below PRANGE)"
        else:  # OFF
            final_mode = "OFF"
            reason = "Intraday confirm: Market weakness confirmed (prices below PRANGE)"

    else:  # CONFIRM
        final_mode = morning_risk_mode
        reason = "Intraday confirm: Prices within predicted range (PRANGE)"

    return final_mode, signal, reason
