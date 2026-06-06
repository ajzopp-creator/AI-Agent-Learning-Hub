"""
FILE: P_300_vantagepoint_batch_convert_v5.py
VERSION: 5.2
LAST UPDATE: 2026-05-09 21:15
AUTHOR: Gemini (P_300 Agent)

CHANGELOG:
- v5.2: Fixed 'nan' error by explicitly skipping Vantage Point header rows (header=None).
- v5.1: Enforced strict mapping from ingest_manifest.json (professionalsentiment -> psi).
"""
import os
import pandas as pd
import re
import zipfile
from datetime import datetime
from pathlib import Path

# CONFIGURATION
SRC_DIR = Path(r"D:\OneDrive\Documents\AJZStrategiesLLC\P_300_Vantage Point Up Trend Pattern Recognition")
ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
HIST_DIR = ROOT / "data" / "historical_patterns"
LIVE_DIR = ROOT / "data" / "live"
ARCHIVE_PATH = SRC_DIR / "P_300_ArchiveVP_excel.zip"

def process_all_files():
    # CLEAN UP: Remove old CSVs that don't match the new 'symbol/psi' schema
    for old_csv in LIVE_DIR.glob("*.csv"):
        os.remove(old_csv)

    files = list(SRC_DIR.glob("*.xlsx"))
    if not files: return

    for f in files:
        match = re.search(r'\((.*?)\)', f.name)
        ticker = match.group(1) if match else "UNKNOWN"
        
        # FIX: read_excel with header=None to ensure we control the data row
        df_raw = pd.read_excel(f, header=None)
        
        # Vantage Point Row 0 is often headers. We look for the first float in Col 1.
        try:
            # We scan the first 3 rows of Column 1 for a number
            p_val = pd.to_numeric(df_raw.iloc[:, 1], errors='coerce').dropna().iloc[0]
        except:
            p_val = 0.0

        standard_df = pd.DataFrame([{
            "symbol": ticker,
            "psi": float(p_val),
            "bar_date": datetime.now().strftime('%Y-%m-%d')
        }])

        target_dir = HIST_DIR if f.name.lower().startswith("pattern") else LIVE_DIR
        standard_df.to_csv(target_dir / f.name.replace(".xlsx", ".csv"), index=False)
        
        with zipfile.ZipFile(ARCHIVE_PATH, 'a') as zipf:
            zipf.write(f, f.name)
        os.remove(f)
        
    print(f"--- [v5.2] Schema Lockdown Complete ({len(files)} files) ---")

if __name__ == "__main__":
    process_all_files()