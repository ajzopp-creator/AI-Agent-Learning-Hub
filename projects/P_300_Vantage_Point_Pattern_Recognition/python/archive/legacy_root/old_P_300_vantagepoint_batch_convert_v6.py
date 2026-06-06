"""
FILE: P_300_vantagepoint_batch_convert_v6.7 (DUAL-EXPORT)
DATE: 2026-05-12
DESCRIPTION: Converts D: Drive files and populates BOTH the Vault (historical) 
             and the Front Line (live) folders.
"""
import pandas as pd
from pathlib import Path
import os

# 1. PATH CONFIGURATION (Direct Bridge from OneDrive to Project)
SOURCE_DIR = Path(r"D:\OneDrive\Documents\AJZStrategiesLLC\P_300_Vantage Point Up Trend Pattern Recognition")
VAULT_DIR  = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical_patterns")
LIVE_DIR   = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\live")

def sanitize_data(df):
    """v6.7: Cleans VantagePoint column noise and keeps latest pattern data."""
    df.columns = [str(c).strip() for c in df.columns]
    return df.tail(5) 

def process_files():
    print(f"[*] SCANNING ONEDRIVE: {SOURCE_DIR}")
    
    # Ensure project folders exist
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    LIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Gather Excel and CSV files from D: Drive
    files = list(SOURCE_DIR.glob("*.xlsx")) + list(SOURCE_DIR.glob("*.csv"))
    
    if not files:
        print(f"[!] No files found. Check if D: drive is connected.")
        return

    count = 0
    for file in files:
        if file.name.startswith("~$"): continue

        print(f"[+] Processing: {file.name}")
        try:
            # Flexible reading for XLSX or CSV
            df = pd.read_excel(file) if file.suffix == '.xlsx' else pd.read_csv(file, encoding='cp1252')
            sanitized_df = sanitize_data(df)
            
            # --- DUAL EXPORT ---
            # 1. Drop in Vault (For Database Ingestion)
            sanitized_df.to_csv(VAULT_DIR / f"{file.stem}.csv", index=False)
            
            # 2. Drop in Live (For Daily Workflow Evaluation)
            sanitized_df.to_csv(LIVE_DIR / f"{file.stem}.csv", index=False)
            
            count += 1
        except Exception as e:
            print(f" [!] FAILED {file.name}: {e}")

    print(f"\n[SUCCESS] Distributed {count} files to both VAULT and LIVE folders.")

if __name__ == "__main__":
    process_files()
    os.system("pause")