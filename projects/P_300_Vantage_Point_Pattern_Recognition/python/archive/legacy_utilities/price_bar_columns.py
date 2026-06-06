import sqlite3
import pandas as pd

db_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db"
conn = sqlite3.connect(db_path)

# Verify column names in the price_bars table
df_sample = pd.read_sql("SELECT * FROM price_bars LIMIT 1", conn)
print("--- Columns found in price_bars table ---")
print(df_sample.columns.tolist())

conn.close()