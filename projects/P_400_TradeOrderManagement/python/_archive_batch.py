import zipfile
from pathlib import Path
from datetime import date

inbox = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\signals')
processed = inbox / 'processed'
processed.mkdir(exist_ok=True)
keep = {'2026-06-16_MU_v2.0.json', '2026-06-16_WDC_v2.0.json'}

yymm = date.today().strftime("%y%m")
zip_path = processed / f"{yymm}_ProcessedJson.zip"

files = [f for f in inbox.glob('*_v2.0.json') if f.name not in keep]
with zipfile.ZipFile(zip_path, 'a', compression=zipfile.ZIP_DEFLATED) as zf:
    for f in files:
        zf.write(f, arcname=f.name)
        f.unlink()
        print(f"Archived: {f.name}")
print(f"Done. {len(files)} files archived.")
