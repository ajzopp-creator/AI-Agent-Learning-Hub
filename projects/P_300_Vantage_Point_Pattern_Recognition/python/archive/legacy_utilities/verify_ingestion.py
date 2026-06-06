import sqlite3
import pandas as pd
import os

# System of Record: Immutable Path
DB_PATH = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db'

def verify_ingestion():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        print("--- P_300 DATABASE VERIFICATION ---")
        
        tables = ['symbols', 'price_bars', 'pattern_instances', 'pattern_features', 'forward_labels']
        
        for table in tables:
            try:
                count = conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
                print(f"Total rows in {table}: {count}")
            except sqlite3.OperationalError:
                print(f"Table '{table}' does not exist yet.")
                
        print("\n--- SAMPLE: RECENT PATTERN INSTANCES ---")
        sample_df = pd.read_sql_query(
            "SELECT pattern_instance_id, symbol_id, anchor_date, close_0, data_origin_type FROM pattern_instances ORDER BY pattern_instance_id DESC LIMIT 5", 
            conn
        )
        print(sample_df.to_string(index=False))

        conn.close()
        print("\n--- VERIFICATION COMPLETE ---")
    except Exception as e:
        print(f"Error reading database: {e}")

if __name__ == "__main__":
    verify_ingestion()