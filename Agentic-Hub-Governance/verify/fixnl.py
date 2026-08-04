from pathlib import Path
p = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\params_aug_2026.py")
s = p.read_text(encoding="utf-8")
a = "            return raw.decode(enc), enc"
b = '            d = raw.decode(enc)\n            return d.replace("\\r\\n", "\\n"), enc, b"\\r\\n" in raw'
assert s.count(a) == 1, "anchor A"
s = s.replace(a, b, 1)
a2 = "    text, enc = load()"
b2 = "    text, enc, crlf = load()"
assert s.count(a2) == 1, "anchor B"
s = s.replace(a2, b2, 1)
a3 = "        FILE.write_text(text, encoding=enc)"
b3 = ('        body = text.replace("\\n", "\\r\\n") if crlf else text\n'
      "        FILE.write_bytes(body.encode(enc))")
assert s.count(a3) == 1, "anchor C"
s = s.replace(a3, b3, 1)
p.write_text(s, encoding="utf-8")
print("PATCHED newline handling OK")
