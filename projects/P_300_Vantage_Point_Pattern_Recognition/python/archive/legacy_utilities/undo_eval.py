import sqlite3

# Pointing to your canonical database
DB_PATH = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db'

def clean_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Check how many bad rows exist
    cursor.execute("SELECT COUNT(*) FROM pattern_instances WHERE data_origin_type = 'EVAL_SET'")
    bad_rows = cursor.fetchone()[0]
    
    if bad_rows > 0:
        # 2. Delete the bad rows
        cursor.execute("DELETE FROM pattern_instances WHERE data_origin_type = 'EVAL_SET'")
        conn.commit()
        print(f"SUCCESS: Purged {bad_rows} bad evaluation rows from pattern_instances.")
    else:
        print("Database is already clean. No EVAL_SET rows found.")
        
    conn.close()

if __name__ == '__main__':
    clean_database()