#!/usr/bin/env python3
"""
P_300 Intraday VP Band Check v2.6
Run anytime after 9:30 AM to validate SPY/QQQ prices against VP predictions

Uses grid_snapshot_latest.json created at 9:30 AM - no XML file needed!

Can run at:
  - 2:00 PM (intraday check during trading)
  - 3:00 PM (afternoon update)
  - 4:00 PM (close recheck)
  - 5:00 PM (after-hours)
  - Evening before 6:30 PM (final check before new Grid file)
"""

from pathlib import Path
from typing import Dict
import json
from datetime import datetime
import yfinance as yf
import sys
import logging

# Configure logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"P_300_Daily_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ---------- VP Band Validation ----------

def validate_vp_band(current_price: float, phigh: float, plow: float, tolerance_pct: float = 0.02) -> Dict:
    """Validate current price against VP predicted band"""
    
    midpoint = (phigh + plow) / 2.0
    inside_band = (plow <= current_price <= phigh)
    pct_from_mid = abs(current_price - midpoint) / midpoint if midpoint > 0 else 0.0
    
    if inside_band:
        status = "in_band"
        message = "Price inside VP predicted range (PLOW-PHIGH)"
    elif pct_from_mid <= tolerance_pct:
        status = "deviation_small"
        message = f"Price outside VP band but within {tolerance_pct*100:.1f}% of midpoint"
    else:
        status = "deviation_large"
        message = f"Price >{tolerance_pct*100:.1f}% outside VP band (material deviation)"
    
    if current_price < plow:
        edge_pressure = "PLOW_BREACH"
    elif current_price > phigh:
        edge_pressure = "PHIGH_BREACH"
    else:
        dist_to_plow = current_price - plow
        dist_to_phigh = phigh - current_price
        edge_pressure = "NEAR_PLOW" if dist_to_plow < dist_to_phigh else "NEAR_PHIGH"
    
    return {
        "current_price": round(current_price, 2),
        "phigh": round(phigh, 2),
        "plow": round(plow, 2),
        "midpoint": round(midpoint, 2),
        "inside_band": inside_band,
        "pct_from_mid": round(pct_from_mid * 100, 2),
        "band_status": status,
        "edge_pressure": edge_pressure,
        "message": message
    }

def load_grid_snapshot() -> Dict:
    """Load grid snapshot from 9:30 AM run"""
    script_dir = Path(__file__).parent
    snapshot_path = script_dir.parent / "grid_snapshot_latest.json"
    
    if not snapshot_path.exists():
        logger.error(f"✗ Grid snapshot not found: {snapshot_path}")
        logger.error("  Run 9:30 AM fresh posture check first (.\run_daily_posture.bat)")
        return None
    
    try:
        with open(snapshot_path, "r") as f:
            snapshot = json.load(f)
        logger.info(f"✓ Loaded grid snapshot from {snapshot['snapshot_created']}")
        return snapshot
    except Exception as e:
        logger.error(f"✗ Error loading grid snapshot: {e}")
        return None

def main():
    """Run intraday VP band validation"""
    
    logger.info("=" * 80)
    logger.info(f"P_300 INTRADAY VP BAND CHECK | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    logger.info("\n📦 Loading grid snapshot from 9:30 AM run...")
    snapshot = load_grid_snapshot()
    
    if not snapshot:
        return
    
    logger.info(f"  Grid date: {snapshot['grid_date']}")
    logger.info(f"  Snapshot created: {snapshot['snapshot_created']}")
    
    logger.info("\n📊 Fetching current prices from yfinance...")
    try:
        spy_data = yf.download("SPY", period="1d", progress=False)
        qqq_data = yf.download("QQQ", period="1d", progress=False)
        
        spy_price = float(spy_data['Close'].iloc[-1])
        qqq_price = float(qqq_data['Close'].iloc[-1])
        
        logger.info(f"  SPY: ${spy_price:.2f}")
        logger.info(f"  QQQ: ${qqq_price:.2f}")
    except Exception as e:
        logger.error(f"✗ Error fetching prices: {e}")
        return
    
    logger.info("\n🎯 VP BAND VALIDATION")
    logger.info("=" * 80)
    
    spy_validation = validate_vp_band(spy_price, snapshot['spy']['phigh'], snapshot['spy']['plow'])
    qqq_validation = validate_vp_band(qqq_price, snapshot['qqq']['phigh'], snapshot['qqq']['plow'])
    
    logger.info("\n📊 SPY:")
    logger.info(f"  Current Price:    ${spy_validation['current_price']}")
    logger.info(f"  VP Predicted:     ${spy_validation['plow']} - ${spy_validation['phigh']}")
    logger.info(f"  Status:           {spy_validation['band_status'].upper()}")
    logger.info(f"  Deviation:        {spy_validation['pct_from_mid']}%")
    
    logger.info("\n📊 QQQ:")
    logger.info(f"  Current Price:    ${qqq_validation['current_price']}")
    logger.info(f"  VP Predicted:     ${qqq_validation['plow']} - ${qqq_validation['phigh']}")
    logger.info(f"  Status:           {qqq_validation['band_status'].upper()}")
    logger.info(f"  Deviation:        {qqq_validation['pct_from_mid']}%")
    
    max_severity = max(
        0 if spy_validation['band_status'] == 'in_band' else (1 if spy_validation['band_status'] == 'deviation_small' else 2),
        0 if qqq_validation['band_status'] == 'in_band' else (1 if qqq_validation['band_status'] == 'deviation_small' else 2)
    )
    
    if max_severity == 0:
        adjustment = "NONE"
        note = "Both indices within VP bands. Keep 9:30 AM risk_mode."
    elif max_severity == 1:
        adjustment = "HALF"
        note = "One or both indices showing deviation. Use HALF sizing, favor spreads."
    else:
        adjustment = "REDUCED"
        note = "Material VP band breach. Use HALF sizing max, prefer spreads."
    
    logger.info("\n" + "=" * 80)
    logger.info("🎯 INTRADAY RISK ADJUSTMENT")
    logger.info("=" * 80)
    logger.info(f"  Adjustment: {adjustment}")
    logger.info(f"  Note: {note}")
    
    check_result = {
        "timestamp": datetime.now().isoformat(),
        "check_type": "intraday_vp_band",
        "grid_snapshot_date": snapshot['grid_date'],
        "grid_snapshot_created": snapshot['snapshot_created'],
        "spy_validation": spy_validation,
        "qqq_validation": qqq_validation,
        "intraday_adjustment": adjustment,
        "intraday_note": note
    }
    
    script_dir = Path(__file__).parent
    output_path = script_dir.parent / "outputs" / f"intraday_vp_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(check_result, f, indent=2)
    
    logger.info(f"\n✓ Saved check: {output_path}")
    logger.info("\n" + "=" * 80)
    logger.info("✓ Intraday check complete\n")

if __name__ == "__main__":
    main()
