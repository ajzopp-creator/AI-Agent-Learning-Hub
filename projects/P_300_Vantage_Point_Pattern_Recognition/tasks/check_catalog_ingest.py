import sqlite3, glob, os

DB_DIR = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models"
db = max(glob.glob(os.path.join(DB_DIR, "*catalog.db")), key=os.path.getmtime)
print(f"Catalog: {os.path.basename(db)}")

files = [
    "Pattern_20260107_20260205_PYPL.xlsx",
    "Pattern_20260109_20260115_BEAM.xlsx",
    "Pattern_20260128_20260205_MSTR.xlsx",
    "Pattern_20260205_20260212_ZBRA.xlsx",
    "Pattern_20260218_20260302_TORXF.xlsx",
    "Pattern_20260312_20260319_TORXF.xlsx",
    "Pattern_20260318_20260330_GOOGL.xlsx",
    "Pattern_20260326_20260401_FMCC.xlsx",
    "Pattern_20260407_20260417_BEAM.xlsx",
    "Pattern_20260407_20260423_GEV.xlsx",
    "Pattern_20260410_20260421_PYPL.xlsx",
    "Pattern_20260413_20260422_MSTR.xlsx",
    "Pattern_20260429_20260506_MTZ.xlsx",
]

conn = sqlite3.connect(db)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()
for f in files:
    cur.execute("SELECT COUNT(*) FROM source_files WHERE filename = ?", (f,))
    (n,) = cur.fetchone()
    print(f"{'IN_CATALOG  ' if n > 0 else 'NOT_INGESTED'} {f}")
conn.close()
