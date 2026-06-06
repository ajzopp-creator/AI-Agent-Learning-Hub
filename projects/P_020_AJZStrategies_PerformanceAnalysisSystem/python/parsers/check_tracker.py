import openpyxl
from datetime import datetime

wb = openpyxl.load_workbook(
    r'C:\Users\Trader\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx',
    data_only=True
)
ws = wb.active
rows = list(ws.iter_rows(min_row=2, values_only=True))
non_empty = [r for r in rows if any(r)]
has_all   = [r for r in non_empty if r[0] and r[1] and r[2]]

print(f"Total rows     : {len(rows)}")
print(f"Non-empty      : {len(non_empty)}")
print(f"Has date+sym+sig: {len(has_all)}")
print(f"First row      : {has_all[0][:3] if has_all else None}")
print(f"Last row       : {has_all[-1][:3] if has_all else None}")
