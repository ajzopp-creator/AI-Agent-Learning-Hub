import sqlite3
import pandas as pd
import os

db_path = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\catalog.db'
csv_path = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\pattern_data.csv'

# Load CSV and insert into DB
df = pd.read_csv(csv_path)
conn = sqlite3.connect(db_path)
df.to_sql('pattern_instances', conn, if_exists='append', index=False)
conn.close()
print("Database hydrated successfully.")