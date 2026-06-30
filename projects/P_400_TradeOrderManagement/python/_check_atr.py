import zipfile, json
zp = r'C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals\processed\2606_ProcessedJson.zip'
syms = ['CARG','DIS','FMCC','GOOGL','MSTR','PYPL']
with zipfile.ZipFile(zp) as z:
    for name in z.namelist():
        parts = name.split('_')
        sym = parts[1] if len(parts) > 1 else ''
        if sym in syms and '2026-06-15' in name:
            d = json.loads(z.read(name))
            print(f"{sym}: atm_at_signal={d['context']['atm_at_signal']}")
