#!/usr/bin/env python3
"""
P_010 Intraday VP Check V3.0
Validates current market price against morning Grid predictions

Intraday Workflow:
  1. Load grid_snapshot_latest.json (Grid close + PRANGE from 9:30 AM)
  2. Fetch current live price from yfinance
  3. Compare: Grid Close ? Current Price movement
  4. Validate: Current Price vs Grid PRANGE (pred_high/pred_low)
  5. Calculate deviation and determine risk adjustment
  6. Create timestamped output in outputs/
"""

import sys
import json
from pathlib import Path
from datetime import datetime


def fetch_current_price(symbol):
    """Fetch current price from yfinance."""
    try:
        import yfinance as yf
        data = yf.download(symbol, period="1d", progress=False)
        
        # Handle multi-level columns
        close_data = data['Close']
        if hasattr(close_data, 'columns'):
            close_data = close_data.squeeze()
        
        # If it's already a scalar after squeeze, use it directly
        if hasattr(close_data, 'iloc'):
            current_price = float(close_data.iloc[-1])
        else:
            current_price = float(close_data)
        
        return current_price
    
    except Exception as e:
        raise Exception(f"Error fetching {symbol} price: {e}")


def validate_price_vs_prange(current, grid_close, pred_high, pred_low, symbol):
    """
    Validate current price against Grid predictions.
    
    Returns:
        dict with validation results including:
        - price_move_pct: % change from Grid close to current
        - band_status: in_band, above_band, or below_band
        - deviation_pct: % deviation from band if outside
    """
    # Calculate price movement from Grid close to current
    price_change = current - grid_close
    price_move_pct = (price_change / grid_close) * 100 if grid_close > 0 else 0.0
    
    # Check if current price is within PRANGE
    if current <= pred_high and current >= pred_low:
        band_status = "in_band"
        deviation_pct = 0.0
        deviation_from = None
    elif current > pred_high:
        band_status = "above_band"
        deviation_pct = ((current - pred_high) / pred_high) * 100
        deviation_from = "pred_high"
    else:  # current < pred_low
        band_status = "below_band"
        deviation_pct = ((pred_low - current) / pred_low) * 100
        deviation_from = "pred_low"
    
    return {
        'symbol': symbol,
        'grid_close': round(grid_close, 2),
        'current': round(current, 2),
        'price_change': round(price_change, 2),
        'price_move_pct': round(price_move_pct, 2),
        'pred_high': round(pred_high, 2),
        'pred_low': round(pred_low, 2),
        'band_status': band_status,
        'deviation_pct': round(deviation_pct, 2),
        'deviation_from': deviation_from
    }


def determine_intraday_adjustment(spy_result, qqq_result):
    """
    Determine intraday risk adjustment based on price validations.
    
    Rules:
    - Both in band ? NONE
    - One out of band with >2% deviation ? HALF
    - Both out of band OR any >5% deviation ? REDUCED
    """
    spy_out = spy_result['band_status'] != 'in_band'
    qqq_out = qqq_result['band_status'] != 'in_band'
    spy_dev = spy_result['deviation_pct']
    qqq_dev = qqq_result['deviation_pct']
    
    # Check for severe deviations
    if spy_dev > 5.0 or qqq_dev > 5.0:
        return "REDUCED", "Severe deviation from PRANGE (>5%)"
    
    # Both out of band
    if spy_out and qqq_out:
        return "REDUCED", "Both symbols outside PRANGE"
    
    # One out with significant deviation
    if (spy_out and spy_dev > 2.0) or (qqq_out and qqq_dev > 2.0):
        return "HALF", "One symbol outside PRANGE with >2% deviation"
    
    # All good
    return "NONE", "Prices within expected PRANGE"


def main():
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    outputs_dir = project_root / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    
    snapshot_file = project_root / "grid_snapshot_latest.json"
    
    print("=" * 70)
    print("P_010 INTRADAY VP VALIDATION V3.0")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load Grid snapshot
    if not snapshot_file.exists():
        print(f"ERROR: Grid snapshot not found at: {snapshot_file}")
        print("Run P_010_daily_posture.bat first at 9:30 AM")
        return 1
    
    with open(snapshot_file, 'r') as f:
        snapshot = json.load(f)
    
    print(f"Loaded Grid snapshot from: {snapshot.get('timestamp', 'unknown')}")
    print(f"SPY Grid Date: {snapshot['spy']['date']}")
    print(f"QQQ Grid Date: {snapshot['qqq']['date']}")
    print()
    
    # Fetch current prices
    print("Fetching current market prices...")
    try:
        spy_current = fetch_current_price("SPY")
        qqq_current = fetch_current_price("QQQ")
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    
    print(f"SPY Current: ${spy_current:.2f}")
    print(f"QQQ Current: ${qqq_current:.2f}")
    print()
    
    # Validate prices against PRANGE
    spy_result = validate_price_vs_prange(
        current=spy_current,
        grid_close=snapshot['spy']['close'],
        pred_high=snapshot['spy']['pred_high'],
        pred_low=snapshot['spy']['pred_low'],
        symbol='SPY'
    )
    
    qqq_result = validate_price_vs_prange(
        current=qqq_current,
        grid_close=snapshot['qqq']['close'],
        pred_high=snapshot['qqq']['pred_high'],
        pred_low=snapshot['qqq']['pred_low'],
        symbol='QQQ'
    )
    
    # Display validation results
    print("SPY Validation:")
    print(f"  Grid Close ? Current: ${spy_result['grid_close']:.2f} ? ${spy_result['current']:.2f} ({spy_result['price_move_pct']:+.2f}%)")
    print(f"  PRANGE: ${spy_result['pred_low']:.2f} - ${spy_result['pred_high']:.2f}")
    print(f"  Status: {spy_result['band_status'].upper()}")
    if spy_result['band_status'] != 'in_band':
        print(f"  Deviation: {spy_result['deviation_pct']:.2f}% from {spy_result['deviation_from']}")
    print()
    
    print("QQQ Validation:")
    print(f"  Grid Close ? Current: ${qqq_result['grid_close']:.2f} ? ${qqq_result['current']:.2f} ({qqq_result['price_move_pct']:+.2f}%)")
    print(f"  PRANGE: ${qqq_result['pred_low']:.2f} - ${qqq_result['pred_high']:.2f}")
    print(f"  Status: {qqq_result['band_status'].upper()}")
    if qqq_result['band_status'] != 'in_band':
        print(f"  Deviation: {qqq_result['deviation_pct']:.2f}% from {qqq_result['deviation_from']}")
    print()
    
    # Determine intraday adjustment
    adjustment, reason = determine_intraday_adjustment(spy_result, qqq_result)
    
    # Create output
    output = {
        'timestamp': datetime.now().isoformat(),
        'snapshot_timestamp': snapshot.get('timestamp'),
        'spy_validation': spy_result,
        'qqq_validation': qqq_result,
        'intraday_adjustment': adjustment,
        'reason': reason
    }
    
    # Write output file
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = outputs_dir / f"intraday_vp_check_{timestamp_str}.json"
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print("=" * 70)
    print("INTRADAY VP VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Adjustment: {adjustment}")
    print(f"Reason: {reason}")
    print(f"Output: {output_file.name}")
    print("=" * 70)
    print()
    
    if adjustment != "NONE":
        print(f"??  Apply risk adjustment: Use {adjustment} mode")
        print(f"   Combine with morning risk_mode: MIN(morning_mode, {adjustment})")
    else:
        print(f"?  No adjustment needed - prices within PRANGE")
    
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

