import sqlite3
import pandas as pd
import os

db_path = 'models/catalog.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

conn = sqlite3.connect(db_path)
tables = ['symbols', 'sourcefiles', 'pricebars', 'featuresets', 'patterninstances', 'patternfeatures', 'forwardlabels']

os.makedirs('output/validation', exist_ok=True)
for table in tables:
    df = pd.read_sql(f'SELECT * FROM {table}', conn)
    df.to_csv(f'output/validation/{table}.csv', index=False)
    print(f'Exported {table}.csv ({len(df)} rows)')

conn.close()
print('Full catalog dumped to output/validation/. Upload CSVs for analysis.')