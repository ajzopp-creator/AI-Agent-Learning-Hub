import sqlite3
import pandas as pd

DB_PATH = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db'
conn = sqlite3.connect(DB_PATH)

def audit_features(instance_ids):
    for pid in instance_ids:
        df = pd.read_sql(f"SELECT feature_name, feature_value FROM pattern_features WHERE pattern_instance_id = {pid}", conn)
        print(f"\n--- Features for Instance {pid} ---")
        print(df.to_string(index=False))

audit_features([394, 1])
conn.close()