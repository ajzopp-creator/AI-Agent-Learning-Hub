#!/usr/bin/env python3
"""
V2.5_MCP_Launcher.py - Master Control Program for Bullish Trend Pattern Project V2.5
CSV priority + robust auto-archive + NaN-safe Date + Schema Support

Version: 1.10
Last Updated: 05/07/2026

Changelog:
- 05/07/26 (v1.10): Skips header rows and reads the first ACTUAL data row
- 05/07/26 (v1.9): Explicit 'Date' column priority
- Previous versions tracked above
"""

import pandas as pd
import shutil
import json
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_301_Bullish_Trend_Pattern_V2.5")
DATA_LIVE = PROJECT_ROOT / "data" / "live"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

SCHEMA_PATHS = [
    PROJECT_ROOT / "models" / "schema" / "vp_standard_schema.json",
    Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\schema\vp_standard_schema.json"),
    PROJECT_ROOT.parent / "P_300_Vantage_Point_Pattern_Recognition" / "models" / "schema" / "vp_standard_schema.json",
]

DATA_LIVE.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

class V25MCP:
    def __init__(self):
        self.MIN_DL = 0.74

    def parse_file(self, file_path):
        try:
            if file_path.suffix.lower() == '.csv':
                # Read full file but skip potential header rows
                df = pd.read_csv(file_path, skiprows=0)  # try 0 first
                if len(df) < 1:
                    return None
                
                # Find the first row that has a real date in first column
                data_row = None
                for i in range(min(5, len(df))):  # check first 5 rows
                    row = df.iloc[i].to_dict()
                    date_str = str(row.get('Date', '')).strip()
                    if date_str and any(c.isdigit() for c in date_str) and ('/' in date_str or '-' in date_str):
                        data_row = row
                        break
                
                if data_row is None:
                    data_row = df.iloc[0].to_dict()  # fallback
                
                row = data_row
            else:
                # XML fallback (unchanged)
                import xml.etree.ElementTree as ET
                tree = ET.parse(file_path)
                root = tree.getroot()
                records = list(root.findall('.//Stride')) or list(root.findall('.//The_x0020_Trade_x0020_Desk')) or []
                if not records:
                    return None
                row = {child.tag.replace('x0020_', ' ').strip(): child.text for child in records[0]}

            # === EXPLICIT DATE FROM YOUR HEADER ===
            date_val = 'N/A'
            if 'Date' in row:
                val = str(row['Date']).strip()
                if val and any(c.isdigit() for c in val):
                    date_val = val

            # Normalize numeric fields
            numeric_keys = ['Short_Term_Difference', 'Medium_Term_Difference', 'Long_Term_Difference',
                            'Close_Price', 'Neural_Index_NeuralXMax', 'Williams_EMAI',
                            'Professional_Sentiment_PSI', 'Professional_Sentiment_ROC', 'Volume']
            for k in numeric_keys:
                if k in row and row[k]:
                    try:
                        row[k] = float(row[k])
                    except:
                        row[k] = 0.0

            ticker = file_path.stem.split('(')[-1].split(')')[0].strip() if '(' in file_path.stem else file_path.stem[:5]
            row['ticker'] = ticker
            row['file'] = file_path.name
            row['Date'] = date_val
            return row
        except Exception as e:
            print(f"Error parsing {file_path.name}: {e}")
            return None

    def v25_score(self, row):
        st = float(row.get('Short_Term_Difference', 0))
        mt = float(row.get('Medium_Term_Difference', 0))
        lt = float(row.get('Long_Term_Difference', 0))
        nimax = float(row.get('Neural_Index_NeuralXMax', 0))
        emai = float(row.get('Williams_EMAI', 0))
        psi = float(row.get('Professional_Sentiment_PSI', 0))
        psi_roc = float(row.get('Professional_Sentiment_ROC', 0))

        dl = 0.50
        if st > 0 and (mt >= 1.5 or lt >= 1.5): dl += 0.25
        if nimax >= 90 and st > 0 and mt > 0 and lt > 0: dl += 0.15
        if emai > 0: dl += 0.30
        if psi < 30 and psi_roc < 0: dl += 0.20
        if nimax >= 35: dl += 0.10

        if dl >= 0.90: return "Strong Buy", round(dl, 2)
        if dl >= 0.75: return "Buy", round(dl, 2)
        if dl >= 0.60: return "Hold/Watch", round(dl, 2)
        return "Pass/Reject", round(dl, 2)

    def run(self):
        results = []
        csv_files = list(DATA_LIVE.glob("*.csv"))

        for f in csv_files:
            row = self.parse_file(f)
            if row:
                signal, score = self.v25_score(row)
                results.append({
                    "Ticker": row['ticker'],
                    "Signal": signal,
                    "DL_Score": score,
                    "Date": row.get('Date', 'N/A'),
                    "File": row['file']
                })

        df = pd.DataFrame(results)
        print("\n=== BULLISH TREND PATTERN PROJECT V2.5 MCP REPORT (CSV + XML) ===")
        print(df.to_string(index=False))
        print(f"\nProcessed {len(df)} files from data/live/. CSV priority active.")

        if csv_files:
            for f in csv_files:
                try:
                    dest = DATA_PROCESSED / f.name
                    if dest.exists():
                        dest.unlink()
                    shutil.move(str(f), str(dest))
                    print(f"-> Archived: {f.name}")
                except Exception as e:
                    print(f"-> Archive failed for {f.name}: {e}")

        print("\nMCP run completed successfully.")
        return df


if __name__ == "__main__":
    mcp = V25MCP()
    mcp.run()