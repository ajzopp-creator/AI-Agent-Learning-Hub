import sqlite3

# This assumes your sql file is named catalog.sql
with open('catalog.sql', 'r') as f:
    sql = f.read()

conn = sqlite3.connect('catalog.db')
conn.executescript(sql)
conn.commit()
conn.close()
print("Database catalog.db successfully created.")