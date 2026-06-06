import sqlite3
import pandas as pd

# 1. Connect to the master record (in the sandbox)
conn = sqlite3.connect('catalog.db')

# 2. Extract the data
df = pd.read_sql_query("SELECT * FROM pattern_instances", conn)

# 3. Export to CSV for you to download
df.to_csv('pattern_data.csv', index=False)
conn.close()