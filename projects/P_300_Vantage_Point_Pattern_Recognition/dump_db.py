
import sqlite3

def dump_db(db_path, output_path):
    conn = sqlite3.connect(db_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    conn.close()
    print(f"Dump complete: {output_path}")

dump_db('models/catalog.db', 'catalog_dump.sql')
