#!/usr/bin/env python3
from pathlib import Path
import json

# Load snapshot
snap_path = Path("grid_snapshot_latest.json")
if snap_path.exists():
    with open(snap_path) as f:
        snapshot = json.load(f)
    print(f"✓ Snapshot loaded")
    print(f"  SPY PHIGH: {snapshot['spy']['phigh']}")
    print(f"  QQQ PHIGH: {snapshot['qqq']['phigh']}")
else:
    print("✗ Snapshot not found")

# Try to import and test
try:
    import yfinance as yf
    print("✓ yfinance imported")
    
    spy = yf.download("SPY", period="1d", progress=False)
    spy_price = spy['Close'].iloc[-1]
    print(f"✓ SPY price: {spy_price}")
    
except Exception as e:
    print(f"✗ Error: {e}")
