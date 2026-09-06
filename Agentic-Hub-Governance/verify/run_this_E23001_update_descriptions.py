"""Manual live-DB fix: update P_910/P_920 descriptions to match db_seeder.py's
corrected seed text (Relative Strength scan / EOD scan), since seed_all()'s
INSERT OR IGNORE won't touch rows that already exist.

Safe to re-run -- plain UPDATE by primary key, no deletes, no schema changes.
Ref: WO-P000-E23.001.
"""

import sqlite3

DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"

UPDATES = [
    ("P_910", "Relative Strength Scan",
     "P_115 bucket - relative strength scan signals (WO-P000-E23.001)"),
    ("P_920", "EOD Scan",
     "P_115 bucket - end-of-day scan signals (WO-P000-E23.001)"),
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

print("--- before ---")
for row in cur.execute("SELECT system_id, system_name, description FROM systems WHERE system_id IN ('P_910','P_920')"):
    print(row)

for system_id, name, desc in UPDATES:
    cur.execute(
        "UPDATE systems SET system_name = ?, description = ? WHERE system_id = ?",
        (name, desc, system_id),
    )

conn.commit()

print()
print("--- after ---")
for row in cur.execute("SELECT system_id, system_name, description FROM systems WHERE system_id IN ('P_910','P_920')"):
    print(row)

conn.close()
