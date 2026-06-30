import zipfile
zp = r'C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals\processed\2606_ProcessedJson.zip'
with zipfile.ZipFile(zp) as z:
    names = z.namelist()
    print(f"Total entries: {len(names)}")
    for n in sorted(names):
        print(n)
