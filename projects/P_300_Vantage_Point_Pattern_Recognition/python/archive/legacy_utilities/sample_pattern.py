import sqlite3
import pandas as pd

db_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db"
conn = sqlite3.connect(db_path)

# Fetch one sample pattern
sample = pd.read_sql("SELECT * FROM pattern_instances LIMIT 1", conn)
print("--- Sample Pattern Instance ---")
print(sample.T) # Transpose for readability

conn.close()