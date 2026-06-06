"""
FILE: P_300_TradeLogger.py
VERSION: 1.2 (LEAN ARCHIVE)
DATE: 2026-05-11
DESCRIPTION: 
    Quick-log BUY signals for historical performance verification.
    Minimalist approach to avoid duplicating VantagePoint's work.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

P300_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
LOG_PATH = P300_ROOT / "data" / "trade_log.csv"

def quick_log(symbol, signal_type="BUY"):
    """Records the date and signal to verify against future DB outcomes."""
    new_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "symbol": symbol,
        "signal": signal_type,
        "market_posture": 12.30 # Current session state
    }
    
    df = pd.read_csv(LOG_PATH) if LOG_PATH.exists() else pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(LOG_PATH, index=False)
    print(f"[+] {symbol} Signal Archived in Trade Log.")

if __name__ == "__main__":
    # Log today's primary signal
    quick_log("NVDA", "BUY")