"""
FILE: P_300_vantagepoint_batch_convert_v6.8
VERSION: 6.8 (ONEDRIVE_BRIDGE_PROTOCOL)
DATE: 2026-05-12
AUTHOR: Gemini Collaboration
DESCRIPTION: 
    Bridges D: Drive (OneDrive) to C: Drive (Project). 
    Extracts 16 core features and distributes to BOTH:
    1. VAULT: For permanent DB ingestion.
    2. LIVE: For daily workflow evaluation.
"""
import pandas as pd
from pathlib import Path
import os

# 1. FIXED PATH CONFIGURATION
SOURCE_DIR = Path(r"D:\OneDrive\Documents\AJZStrategiesLLC\P_300_Vantage Point Up Trend Pattern Recognition")
VAULT_DIR  = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical_patterns")
LIVE_DIR   = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\live")

def sanitize_data(df):
    """v6.8: Standardizes headers and retains tailing 5-day pattern window."""
    df.columns = [str(c).strip() for c in df.columns]
    return df.tail(5) 

def process_files():
    print(f"--- [START] ONEDRIVE BRIDGE v6.8 ---")
    print(f"SOURCE: {SOURCE_DIR}")
    
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    LIVE_DIR.mkdir(parents=True, exist_ok=True)

    files = list(SOURCE_DIR.glob("*.xlsx")) + list(SOURCE_DIR.glob("*.csv"))
    
    if not files:
        print(f"[!] ALERT: No files found in SOURCE_DIR. Check D: drive connection.")
        return

    count = 0
    for file in files:
        if file.name.startswith("~$"): continue

        print(f"[+] Processing: {file.name}")
        try:
            df = pd.read_excel(file) if file.suffix == '.xlsx' else pd.read_csv(file, encoding='cp1252')
            sanitized_df = sanitize_data(df)
            
            # --- DUAL DISTRIBUTION ---
            sanitized_df.to_csv(VAULT_DIR / f"{file.stem}.csv", index=False)
            sanitized_df.to_csv(LIVE_DIR / f"{file.stem}.csv", index=False)
            
            count += 1
        except Exception as e:
            print(f" [!] ERROR processing {file.name}: {e}")

    print(f"\n[SUCCESS] {count} files distributed to VAULT and LIVE.")

if __name__ == "__main__":
    process_files()
    print("\n--- [PROCESS COMPLETE] ---")
    os.system("pause")