import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db")
conn = sqlite3.connect(db_path)

# 1. Ingestion Integrity
total_rows = pd.read_sql("SELECT COUNT(*) FROM price_bars", conn).iloc[0,0]
unique_symbols = pd.read_sql("SELECT COUNT(DISTINCT symbol_id) FROM price_bars", conn).iloc[0,0]

# 2. Indicator Mapping Health (The critical test)
# If these counts are > 0, the manifest mapping is correctly aligned with the CSV columns.
indicators = ['triple_cross_short', 'triple_cross_medium', 'triple_cross_long', 'neuralx', 'psi']
health_report = []

for ind in indicators:
    count = pd.read_sql(f"SELECT COUNT(*) FROM price_bars WHERE {ind} IS NOT NULL", conn).iloc[0,0]
    health_report.append({"Indicator": ind, "Non-Null Count": count})

conn.close()

# Report Output
print(f"--- Database Integrity Report ---")
print(f"Total Rows: {total_rows}")
print(f"Unique Symbols: {unique_symbols}")
print("\n--- Indicator Data Mapping ---")
print(pd.DataFrame(health_report).to_string(index=False))