import zipfile
from pathlib import Path

zp = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\processed\2026-06.zip')
live = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\live')
live.mkdir(parents=True, exist_ok=True)

syms = ['CARG','DIS','FMCC','GOOGL','MSTR','PYPL']
restored = 0

with zipfile.ZipFile(zp) as z:
    for name in z.namelist():
        for sym in syms:
            if f'20260615_History Grid ({sym})' in name:
                dest = live / f"History Grid ({sym}).xlsx"
                dest.write_bytes(z.read(name))
                print(f"Restored: {name} -> {dest.name}")
                restored += 1

print(f"Total restored: {restored}")
