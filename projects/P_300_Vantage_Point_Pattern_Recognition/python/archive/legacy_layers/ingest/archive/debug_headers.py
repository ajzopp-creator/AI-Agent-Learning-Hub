import pandas as pd
from pathlib import Path

# Point to one of the files that actually ingested 15 rows
file_path = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical\History Grid 011725_012525 (SPY).csv")

df = pd.read_csv(file_path)

# Apply the exact cleaning logic from your ingestion script
cleaned_cols = [c.lower().strip().replace(' ', '').replace('\n', '') for c in df.columns]

print("--- Exact Column Headers Found After Cleaning ---")
for col in cleaned_cols:
    print(f"'{col}'")