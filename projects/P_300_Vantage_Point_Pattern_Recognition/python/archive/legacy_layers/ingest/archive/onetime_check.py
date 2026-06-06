import sqlite3
import pandas as pd

conn = sqlite3.connect(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db")
# Check SPY (the most likely candidate for valid data)
df = pd.read_sql("SELECT * FROM price_bars WHERE symbol_id=1", conn)

print(f"Total rows: {len(df)}")
print("Non-null counts for key indicators:")
print(df[['triple_cross_long', 'neuralx', 'psi']].count())
conn.close()