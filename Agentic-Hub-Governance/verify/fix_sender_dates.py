import csv
from pathlib import Path
from datetime import datetime

path = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\data\sender_sheet.csv")

with open(path, newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
    fieldnames = rows[0].keys()

fixed = 0
for row in rows:
    v = row["date_added"]
    try:
        datetime.strptime(v, "%Y-%m-%d")
        continue  # already ISO
    except ValueError:
        pass
    d = datetime.strptime(v, "%m/%d/%Y").date()
    row["date_added"] = d.isoformat()
    fixed += 1

with open(path, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Fixed {fixed} of {len(rows)} rows")
