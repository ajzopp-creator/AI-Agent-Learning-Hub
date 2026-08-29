import os

order_ids = ["5374405691","5384905992","5376687262","5384905948","5383701549","5384804461","5384807275"]
tickers = ["EMR","CPAY","WSM","SBLK"]

roots = [
    r"C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal",
    r"C:\Users\Trader\Documents\AJZStrategies_TradingJournal",
]

hits = []
for root in roots:
    if not os.path.exists(root):
        hits.append("ROOT NOT FOUND: " + root)
        continue
    for dirpath, dirnames, filenames in os.walk(root):
        if ".obsidian" in dirpath:
            continue
        for fn in filenames:
            if not fn.lower().endswith((".md", ".json")):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                continue
            for oid in order_ids:
                if oid in content:
                    hits.append("ORDER_ID " + oid + " FOUND IN: " + fp)

outp = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\order_id_results.txt"
with open(outp, "w", encoding="utf-8") as f:
    if hits:
        f.write(chr(10).join(hits))
    else:
        f.write("NO ORDER ID MATCHES FOUND ANYWHERE IN SCANNED ROOTS")
print("done", len(hits))
