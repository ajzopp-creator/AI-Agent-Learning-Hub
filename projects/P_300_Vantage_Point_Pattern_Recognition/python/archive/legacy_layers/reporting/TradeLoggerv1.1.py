"""
FILE: P_300_TradeLogger.py
VERSION: 1.1 (REPORTING INTEGRATION)
DATE: 2026-05-11
DESCRIPTION: 
    Logs paper and live trades. Saved in reporting/ to avoid 
    unnecessary directory growth.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

# Path Configuration
P300_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
LOG_PATH = P300_ROOT / "data" / "trade_log.csv"

def log_trade(symbol, entry_price, contracts, strategy, trade_type="PAPER"):
    """Appends trade data to the persistent log."""
    new_trade = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "symbol": symbol,
        "entry_price": entry_price,
        "contracts": contracts,
        "strategy": strategy,
        "type": trade_type,
        "status": "OPEN",
        "exit_price": None,
        "pnl_pct": None
    }
    
    # Load or Create log
    if LOG_PATH.exists():
        df = pd.read_csv(LOG_PATH)
    else:
        df = pd.DataFrame(columns=new_trade.keys())
    
    # Append and Save
    df = pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True)
    df.to_csv(LOG_PATH, index=False)
    
    print("=" * 40)
    print(f" [+] TRADE LOGGED: {symbol} ({trade_type})")
    print(f" [+] STRATEGY: {strategy}")
    print(f" [+] COST BASIS: ${entry_price * contracts * 100:.2f}")
    print("=" * 40)

if __name__ == "__main__":
    # EXECUTE NVDA PAPER TRADE PILOT
    # Using the calculated $220/$230 Bull Call Spread
    log_trade(
        symbol="NVDA", 
        entry_price=4.50, # Net debit for the spread
        contracts=3, 
        strategy="Bull Call Spread 220/230",
        trade_type="PAPER"
    )