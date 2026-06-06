import sqlite3
from pathlib import Path

DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050426geminicatalog.db")

def cleanup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Keep only the first instance of each pattern based on Date and Symbol
    # This deletes rows where the same symbol/date combination appears multiple times
    query = """
    DELETE FROM pattern_instances 
    WHERE rowid NOT IN (
        SELECT MIN(rowid) 
        FROM pattern_instances 
        GROUP BY symbol_id, anchor_date
    )
    """
    cursor.execute(query)
    conn.commit()
    print(f"[SUCCESS] Cleaned up {cursor.rowcount} duplicate rows.")
    conn.close()

if __name__ == "__main__":
    cleanup()