#!/usr/bin/env python3
"""
P_010 Intraday VP Check V5.0
Validates current market prices against VP Grid predictions
Updates P_010_RiskConfig.json with three-state logic

V5.0: Three-state logic (OFF/HALF/FULL) with directional adjustment
"""

import sys
import json
import yfinance as yf
from pathlib import Path
from datetime import datetime


def load_grid_snapshot(snapshot_file):
    """Load the morning Grid snapshot created by daily posture script."""
    if not snapshot_file.exists():
        raise FileNotFoundError(
            f"Grid snapshot not found at {snapshot_file}. "
            "Run morning daily posture script first!"
        )
    
    with open(snapshot_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def fetch_current_price(symbol):
    """Fetch current market price for a symbol using yfinance."""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d", interval="1m")
    
    if hist.empty:
        raise ValueError(f"No price data available for {symbol}")
    
    close_data = hist['Close']
    if hasattr(close_data, 'iloc'):
        current_price = float(close_data.iloc[-1])
    else:
        current_price = float(close_data)
    
    return current_price


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


def main():
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    snapshot_file = project_root / "grid_snapshot_latest.json"
    config_file = project_root / "P_010_RiskConfig.json"
    output_dir = project_root / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("P_010 INTRADAY VP VALIDATION V5.0")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load morning Grid snapshot
    try:
        snapshot = load_grid_snapshot(snapshot_file)
    except Exception as e:
        print(f"ERROR loading Grid snapshot: {e}")
        return 1
    
    print(f"Loaded Grid snapshot from: {snapshot['timestamp']}")
    print(f"SPY Grid Date: {snapshot['spy']['date']}")
    print(f"QQQ Grid Date: {snapshot['qqq']['date']}")
    print()
    
    # Fetch current market prices
    print("Fetching current market prices...")
    try:
        spy_current = fetch_current_price("SPY")
        qqq_current = fetch_current_price("QQQ")
    except Exception as e:
        print(f"ERROR fetching current prices: {e}")
        return 1
    
    print(f"SPY Current: ${spy_current:.2f}")
    print(f"QQQ Current: ${qqq_current:.2f}")
    print()
    
    # Validate against PRANGE
    spy_validation = validate_against_prange(
        snapshot['spy']['close'],
        spy_current,
        snapshot['spy']['pred_high'],
        snapshot['spy']['pred_low']
    )
    spy_validation['symbol'] = 'SPY'
    
    qqq_validation = validate_against_prange(
        snapshot['qqq']['close'],
        qqq_current,
        snapshot['qqq']['pred_high'],
        snapshot['qqq']['pred_low']
    )
    qqq_validation['symbol'] = 'QQQ'
    
    # Display validation results
    print("SPY Validation:")
    print(f"  Grid Close -> Current: ${spy_validation['grid_close']:.2f} -> ${spy_validation['current']:.2f} ({spy_validation['price_move_pct']:+.2f}%)")
    print(f"  PRANGE: ${spy_validation['pred_low']:.2f} - ${spy_validation['pred_high']:.2f}")
    print(f"  Status: {spy_validation['band_status'].upper()}")
    if spy_validation['deviation_from']:
        print(f"  Deviation: {spy_validation['deviation_pct']:.2f}% from {spy_validation['deviation_from']}")
    print()
    
    print("QQQ Validation:")
    print(f"  Grid Close -> Current: ${qqq_validation['grid_close']:.2f} -> ${qqq_validation['current']:.2f} ({qqq_validation['price_move_pct']:+.2f}%)")
    print(f"  PRANGE: ${qqq_validation['pred_low']:.2f} - ${qqq_validation['pred_high']:.2f}")
    print(f"  Status: {qqq_validation['band_status'].upper()}")
    if qqq_validation['deviation_from']:
        print(f"  Deviation: {qqq_validation['deviation_pct']:.2f}% from {qqq_validation['deviation_from']}")
    print()
    
    # Load config to get morning baseline
    # CRITICAL: Always read from morning_risk_mode (preserved field), never risk_mode
    # risk_mode gets overwritten by each intraday run causing cascading upgrades
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            risk_config = json.load(f)
        # Use morning_risk_mode if it exists (set by first intraday run of the day)
        # If not present, this is the first intraday run -- capture and preserve it
        if 'morning_risk_mode' not in risk_config:
            risk_config['morning_risk_mode'] = risk_config['risk_mode']
            print(f"  Capturing morning baseline: {risk_config['morning_risk_mode']}")
        morning_baseline = risk_config['morning_risk_mode']
    except Exception as e:
        print(f"ERROR loading config: {e}")
        return 1
    
    # Determine final risk mode based on morning + intraday
    final_mode, signal, reason = determine_final_risk_mode(morning_baseline, spy_validation, qqq_validation)
    
    # Create DETAILED audit file
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'snapshot_timestamp': snapshot['timestamp'],
        'spy_validation': spy_validation,
        'qqq_validation': qqq_validation,
        'morning_baseline': morning_baseline,
        'intraday_signal': signal,
        'intraday_final_mode': final_mode,
        'reason': reason
    }
    
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"intraday_vp_check_{timestamp_str}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    # Update P_010_RiskConfig.json with FINAL risk mode
    print("Updating P_010_RiskConfig.json...")
    
    try:
        # Update risk_mode based on intraday validation
        risk_config['risk_mode'] = final_mode
        risk_config['intraday_signal'] = signal
        risk_config['intraday_reason'] = reason
        
        print(f"  Morning baseline: {morning_baseline}")
        print(f"  Intraday signal: {signal}")
        print(f"  Final risk_mode: {final_mode}")
        print(f"  Reason: {reason}")
        
        # OVERWRITE the master config file with UTF-8 encoding
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(risk_config, f, indent=2, ensure_ascii=False)
            f.flush()  # Force write to disk
        
        # VERIFY the write succeeded
        with open(config_file, 'r', encoding='utf-8') as f:
            verify = json.load(f)
        
        if 'intraday_signal' in verify and verify['risk_mode'] == final_mode:
            print(f"  [SUCCESS] VERIFIED: File updated successfully")
        else:
            print(f"  [ERROR]: File update failed - fields not present after write!")
            return 1
            
    except Exception as e:
        print(f"  [ERROR] updating config file: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("=" * 70)
    print("INTRADAY VP VALIDATION COMPLETE")
    print("=" * 70)
    print(f"Morning Baseline: {morning_baseline}")
    print(f"Intraday Signal: {signal}")
    print(f"FINAL Risk Mode: {final_mode}")
    print(f"Reason: {reason}")
    print()
    print(f"Detailed audit: {output_file.name}")
    print(f"UPDATED: P_010_RiskConfig.json")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

