import sqlite3

# Path to your catalog
db_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to count total patterns
    cursor.execute("SELECT COUNT(*) FROM pattern_instances")
    total_patterns = cursor.fetchone()[0]
    
    print(f"Total pattern instances in catalog: {total_patterns}")
    
    # Breakdown by symbol_id
    print("\nBreakdown by symbol_id:")
    cursor.execute("SELECT symbol_id, COUNT(*) FROM pattern_instances GROUP BY symbol_id")
    for row in cursor.fetchall():
        print(f"Symbol ID {row[0]}: {row[1]} patterns")
        
    conn.close()
except Exception as e:
    print(f"Error accessing catalog: {e}")