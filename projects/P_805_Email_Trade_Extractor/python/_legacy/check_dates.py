"""Phase 1 diagnostic — dumps the Date header distribution of MBOX_FILE.

One-off script to figure out why the 30-day scan returned 0 messages
when the file has 368. Delete after we diagnose.

Run:
    python check_dates.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from infrastructure.mbox_reader import iter_mbox_messages, parse_message_date

mbox_path = config.PROFILE_ROOT / config.MBOX_FILE
print(f"File: {mbox_path}\n")

total = 0
no_date_header = 0
unparseable = 0
parsed_dates = []

for msg in iter_mbox_messages(mbox_path):
    total += 1
    raw = msg.get("Date")
    if not raw:
        no_date_header += 1
        continue
    dt = parse_message_date(raw)
    if dt is None:
        unparseable += 1
        if unparseable <= 3:
            print(f"  UNPARSEABLE sample: {raw!r}")
        continue
    parsed_dates.append(dt)

print(f"\nTotal messages:    {total}")
print(f"No Date header:    {no_date_header}")
print(f"Unparseable dates: {unparseable}")
print(f"Parsed OK:         {len(parsed_dates)}")

if parsed_dates:
    parsed_dates.sort()
    print(f"\nOldest: {parsed_dates[0].isoformat()}")
    print(f"Newest: {parsed_dates[-1].isoformat()}")
    print(f"\nFirst 3 raw Date headers from the file:")
    count = 0
    for msg in iter_mbox_messages(mbox_path):
        print(f"  {msg.get('Date')!r}")
        count += 1
        if count >= 3:
            break
