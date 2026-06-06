import sqlite3
from pathlib import Path

# Project paths
DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db")

def patch_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- Applying Schema Patch to 050326geminicatalog.db ---")
    
    # Create the trade_outcomes table safely
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_outcomes (
            instance_id INTEGER PRIMARY KEY,
            win_loss INTEGER,
            FOREIGN KEY(instance_id) REFERENCES pattern_instances(pattern_instance_id)
        )
    """)
    
    conn.commit()
    print("[+] 'trade_outcomes' table created or already exists.")
    conn.close()

if __name__ == "__main__":
    patch_db()