import json
from pathlib import Path
from datetime import datetime

print("Testing intraday check...")

# Load snapshot
snap = json.load(open("grid_snapshot_latest.json"))
print(f"Loaded snapshot: SPY={snap['spy']['phigh']}, QQQ={snap['qqq']['phigh']}")

# Simulate prices (we'll use actual yfinance)
import yfinance as yf
spy = yf.download("SPY", period="1d", progress=False)['Close'].iloc[-1]
qqq = yf.download("QQQ", period="1d", progress=False)['Close'].iloc[-1]

print(f"Prices: SPY={spy:.2f}, QQQ={qqq:.2f}")

# Validate
def check_band(p, high, low):
    mid = (high + low) / 2
    dev = abs(p - mid) / mid * 100
    if low <= p <= high:
        return "in_band", dev
    elif dev <= 2:
        return "small_dev", dev
    else:
        return "large_dev", dev

spy_st, spy_dev = check_band(spy, snap['spy']['phigh'], snap['spy']['plow'])
qqq_st, qqq_dev = check_band(qqq, snap['qqq']['phigh'], snap['qqq']['plow'])

print(f"SPY: {spy_st} ({spy_dev:.2f}%)")
print(f"QQQ: {qqq_st} ({qqq_dev:.2f}%)")

# Determine adjustment
max_sev = max(
    0 if spy_st == "in_band" else (1 if spy_st == "small_dev" else 2),
    0 if qqq_st == "in_band" else (1 if qqq_st == "small_dev" else 2)
)

if max_sev == 0:
    adj = "NONE"
elif max_sev == 1:
    adj = "HALF"
else:
    adj = "REDUCED"

# Save
result = {
    "timestamp": datetime.now().isoformat(),
    "spy_validation": {
        "current_price": round(spy, 2),
        "phigh": snap['spy']['phigh'],
        "plow": snap['spy']['plow'],
        "midpoint": round((snap['spy']['phigh'] + snap['spy']['plow']) / 2, 2),
        "band_status": spy_st,
        "pct_from_mid": round(spy_dev, 2),
        "edge_pressure": "N/A"
    },
    "qqq_validation": {
        "current_price": round(qqq, 2),
        "phigh": snap['qqq']['phigh'],
        "plow": snap['qqq']['plow'],
        "midpoint": round((snap['qqq']['phigh'] + snap['qqq']['plow']) / 2, 2),
        "band_status": qqq_st,
        "pct_from_mid": round(qqq_dev, 2),
        "edge_pressure": "N/A"
    },
    "intraday_adjustment": adj,
    "intraday_note": f"Check complete: {adj}"
}

Path("outputs").mkdir(exist_ok=True)
fname = f"outputs/intraday_vp_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
json.dump(result, open(fname, "w"), indent=2)
print(f"Saved: {fname}")
print("DONE")
