"""
P_010 Daily Note Writer -- External API Fetchers
Split from P_010_write_daily_note.py (WO-P010-E1.003 housekeeping, 2026-08-10).
Scripture / quote / joke fetches for the Obsidian daily note. All fail gracefully
inline -- never raise, always return a display-safe string.
"""

import json
import urllib.request


def fetch_scripture():
    try:
        req = urllib.request.Request(
            "https://labs.bible.org/api/?passage=random&type=json",
            headers={"User-Agent": "P_010"})
        with urllib.request.urlopen(req, timeout=5) as r:
            v = json.loads(r.read().decode())[0]
            return f'> *{v["bookname"]} {v["chapter"]}:{v["verse"]}*\n> "{v["text"]}"'
    except Exception as e:
        return f"> *Scripture unavailable -- check connection ({e})*"


def fetch_quote():
    try:
        req = urllib.request.Request(
            "https://zenquotes.io/api/random",
            headers={"User-Agent": "P_010"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode())
            return f'> "{d[0]["q"]}" -- *{d[0]["a"]}*'
    except Exception as e:
        return f"> *Quote unavailable -- check connection ({e})*"


def fetch_joke():
    try:
        url = "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single&blacklistFlags=nsfw,racist,sexist,explicit"
        req = urllib.request.Request(url, headers={"User-Agent": "P_010"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode())
            return f'> {d["joke"]}'
    except Exception as e:
        return f"> *Humor unavailable -- check connection ({e})*"
