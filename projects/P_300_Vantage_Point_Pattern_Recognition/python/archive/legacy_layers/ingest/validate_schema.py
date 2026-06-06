import sqlite3
from pathlib import Path

# Target the restored backup specifically
DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050426geminicatalog.db")

def validate():
    if not DB_PATH.exists():
        print(f"[ERROR] Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch column details for the target table
    cursor.execute("PRAGMA table_info(pattern_instances)")
    columns = cursor.fetchall()
    
    print(f"--- SCHEMA VALIDATION: pattern_instances ---")
    print(f"{'CID':<5} {'Name':<20} {'Type':<10} {'NotNull':<10}")
    print("-" * 50)
    
    for col in columns:
        print(f"{col[0]:<5} {col[1]:<20} {col[2]:<10} {col[3]:<10}")
        
    conn.close()

if __name__ == "__main__":
    validate()