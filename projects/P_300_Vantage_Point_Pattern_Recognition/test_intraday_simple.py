#!/usr/bin/env python3
from pathlib import Path
import json
from datetime import datetime
import yfinance as yf

# Load snapshot
snap_path = Path("grid_snapshot_latest.json")
if not snap_path.exists():
    print("ERROR: grid_snapshot_latest.json not found")
    exit(1)

print("="*80)
print(f"P_300 INTRADAY VP CHECK | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

with open(snap_path) as f:
    snapshot = json.load(f)

print("\nLoaded snapshot:", snapshot.get('snapshot_created'))
print(f"SPY VP: \ - \")
print(f"QQQ VP: \ - \")

# Fetch prices
print("\nFetching live prices...")
spy = yf.download("SPY", period="1d", progress=False)
qqq = yf.download("QQQ", period="1d", progress=False)

spy_price = spy['Close'].iloc[-1]
qqq_price = qqq['Close'].iloc[-1]

print(f"SPY Price: \")
print(f"QQQ Price: \")

# Validate bands
def validate_band(price, phigh, plow):
    mid = (phigh + plow) / 2.0
    dev = abs(price - mid) / mid * 100
    
    if plow <= price <= phigh:
        status = "IN_BAND"
    elif dev <= 2.0:
        status = "DEVIATION_SMALL"
    else:
        status = "DEVIATION_LARGE"
    
    return status, round(dev, 2)

spy_status, spy_dev = validate_band(spy_price, snapshot['spy']['phigh'], snapshot['spy']['plow'])
qqq_status, qqq_dev = validate_band(qqq_price, snapshot['qqq']['phigh'], snapshot['qqq']['plow'])

print(f"\nSPY: {spy_status} (deviation: {spy_dev}%)")
print(f"QQQ: {qqq_status} (deviation: {qqq_dev}%)")

# Determine adjustment
max_dev = max(
    0 if spy_status == "IN_BAND" else (1 if spy_status == "DEVIATION_SMALL" else 2),
    0 if qqq_status == "IN_BAND" else (1 if qqq_status == "DEVIATION_SMALL" else 2)
)

if max_dev == 0:
    adj = "NONE"
    note = "Both in band"
elif max_dev == 1:
    adj = "HALF"
    note = "Small deviation"
else:
    adj = "REDUCED"
    note = "Large deviation"

print(f"\n🎯 ADJUSTMENT: {adj}")
print(f"   {note}")

# Save result
result = {
    "timestamp": datetime.now().isoformat(),
    "spy_validation": {
        "current_price": round(spy_price, 2),
        "phigh": snapshot['spy']['phigh'],
        "plow": snapshot['spy']['plow'],
        "band_status": spy_status,
        "pct_from_mid": spy_dev
    },
    "qqq_validation": {
        "current_price": round(qqq_price, 2),
        "phigh": snapshot['qqq']['phigh'],
        "plow": snapshot['qqq']['plow'],
        "band_status": qqq_status,
        "pct_from_mid": qqq_dev
    },
    "intraday_adjustment": adj,
    "intraday_note": note
}

out_dir = Path("outputs")
out_dir.mkdir(exist_ok=True)
out_file = out_dir / f"intraday_vp_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(out_file, "w") as f:
    json.dump(result, f, indent=2)

print(f"\n✅ Saved: {out_file}")
print("="*80)
