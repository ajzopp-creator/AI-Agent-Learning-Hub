import sqlite3

db_path = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables found in catalog.db:")
for table in tables:
    print(f"- {table[0]}")

conn.close()