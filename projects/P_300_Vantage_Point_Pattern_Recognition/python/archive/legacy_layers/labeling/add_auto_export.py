import sqlite3
import pandas as pd
import os

# Assumes run right after your pipeline fills models/catalog.db
db_path = '../models/catalog.db'  # Relative from python/labeling/
conn = sqlite3.connect(db_path)

os.makedirs('../../output/validation', exist_ok=True)

# Full tables
tables = ['symbols', 'sourcefiles', 'pricebars', 'featuresets', 'patterninstances', 'patternfeatures', 'forwardlabels']
for table in tables:
    df = pd.read_sql(f'SELECT * FROM {table}', conn)
    df.to_csv(f'../../output/validation/{table}.csv', index=False)

# FR-5 QQQ 10d specific
qqq10d = pd.read_sql("""
    SELECT s.symbol, pi.anchordate, fl.holddays, fl.percentreturn, fl.profitable,
           COUNT(*) OVER() as total_qqq10d
    FROM forwardlabels fl 
    JOIN patterninstances pi ON fl.patterninstanceid = pi.patterninstanceid 
    JOIN symbols s ON pi.symbolid = s.symbolid 
    WHERE s.symbol='QQQ' AND fl.holddays=10
""", conn)
qqq10d.to_csv('../../output/validation/qqq_fr5_10d.csv', index=False)

conn.close()
print("Auto-exported to output/validation/. Ready for upload.")