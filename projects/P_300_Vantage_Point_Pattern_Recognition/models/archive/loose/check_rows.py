import sqlite3
import os

db_path = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\catalog.db'

try:
    conn = sqlite3.connect(db_path)
    count = conn.execute('SELECT count(*) FROM pattern_instances').fetchone()[0]
    print(f"Rows in pattern_instances: {count}")
    conn.close()
except Exception as e:
    print(f"Error accessing database: {e}")