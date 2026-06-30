import zipfile
from pathlib import Path
zp = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\processed\2026-06.zip')
with zipfile.ZipFile(zp) as z:
    print(f"Total entries: {len(z.namelist())}")
    for name in sorted(z.namelist()):
        print(name)
