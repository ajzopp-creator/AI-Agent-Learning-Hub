import sqlite3

# Absolute Path
db_path = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\catalog.db'

# Sample data to verify parity
# (In a real scenario, this would be your exported pattern data)
sample_data = [
    (1, 101, '2026-05-01', 150.25, 155.50, 155.50),
    (2, 102, '2026-05-02', 152.00, 151.00, 151.00),
    (3, 103, '2026-05-03', 148.50, 160.00, 160.00)
]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert Data
    cursor.executemany('''
        INSERT OR IGNORE INTO pattern_instances 
        (pattern_instance_id, symbol_id, anchor_date, open_0, close_0, close_price) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    print("Database hydrated with sample data successfully.")
    
    # Verify count
    count = conn.execute('SELECT count(*) FROM pattern_instances').fetchone()[0]
    print(f"Total rows in pattern_instances: {count}")
    
    conn.close()
except Exception as e:
    print(f"Error during hydration: {e}")