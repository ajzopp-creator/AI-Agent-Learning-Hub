import zipfile
from pathlib import Path

zp = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals\processed\2606_ProcessedJson.zip')
inbox = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals')
syms = {'CARG','DIS','FMCC','GOOGL','MSTR','PYPL'}

restored = 0
with zipfile.ZipFile(zp) as z:
    print(f"Entries with 2026-06-15:")
    for name in z.namelist():
        if '2026-06-15' in name:
            print(f"  {name}")
        parts = name.replace('.json','').split('_')
        # filename: 2026-06-15_SYMBOL_v2.0 -> parts[1] is symbol
        sym = parts[1] if len(parts) >= 2 else ''
        if sym in syms and '2026-06-15' in name:
            dest = inbox / name
            dest.write_bytes(z.read(name))
            print(f"Restored: {name}")
            restored += 1
print(f"Total restored: {restored}")
