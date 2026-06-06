# P_010 Session Handoff -- 2026-04-25

**Purpose:** Carry context from this Saturday debug + spec session into the next chat where the obsidian MCP tools are live and Phase 1 implementation begins.

---

## 1. Where things stand

- **P_010 production:** Running normally. Friday 4/24 INIT happened. No code changes touched the production pipeline today.
- **Distribution Day Tracker spec:** v1.1 saved to `docs\P_010_MarketHealth_Spec_v1_1.md`. All 5 open questions resolved. Ready to write code.
- **Obsidian MCP integration:** Now installed in p140 conda env, Claude Desktop config updated, server connecting cleanly. Tools didn't surface in *this* chat because Claude Desktop doesn't refresh tool surfaces mid-session -- they will be live in the next new chat.

---

## 2. Today's debug story (so we don't relearn it)

### Aura antivirus broke uvx-based MCP installs

**Symptom:** `uvx mcp-obsidian` failed with `os error -2147024786` (ERROR_OPEN_FAILED) on random package extracts (httpx, python-dotenv, pywin32). uv reports the failure against the first-resolved package, not the actual one failing -- looked like httpx, was actually pywin32.

**Cause:** Aura's real-time scanner intercepting newly-extracted .exe / .pyd files in uv's tool install directory.

**Fix attempted:**
1. Excluded `C:\Users\Trader\AppData\Local\uv` (uv cache) in Aura -- not enough
2. Excluded `C:\Users\Trader\AppData\Roaming\uv` (uv tools) in Aura -- still not enough; Aura scans new .exe creations system-wide regardless of folder exclusion

**Fix actually used:** Bypass uvx entirely. Install `mcp-obsidian` into the existing `p140` conda env (pip install). Update `claude_desktop_config.json` `obsidian` server to launch via:
- `command`: `C:\Users\Trader\.conda\envs\p140\python.exe`
- `args`: `["-m", "mcp_obsidian"]`
- env unchanged

Backup of original config saved as `claude_desktop_config.json.backup_20260425`.

### Windows-MCP cannot reliably spawn p140 python.exe

**Symptom:** Calling `Windows-MCP:PowerShell` with anything that runs python.exe and waits for output (e.g. `python -c "..."` or `Start-Process python ... -Wait`) hangs Windows-MCP itself for 4+ minutes, eventually timing out and wedging the MCP server until Claude Desktop is restarted.

**Note:** The same python invocation runs fine from a normal PowerShell window. Issue is specifically with the Windows-MCP -> child python process handle/IO chain.

**Workaround used today (works):**
1. Write the python code to a `.py` file with `Set-Content`
2. Use `Start-Process` WITHOUT `-Wait` and WITHOUT `-PassThru`, with `-RedirectStandardOutput` to a file
3. `Start-Sleep` long enough for the script to finish
4. `Get-Content` the output file

**Future fix to investigate:** May be related to pywin32 import interaction with Windows-MCP's own Python process. Worth filing upstream, but not blocking.

### MCP tool surface doesn't refresh mid-session

After updating `claude_desktop_config.json` and restarting Claude Desktop, the obsidian MCP tools registered successfully (verified in `mcp-server-obsidian.log`: server connected, 12 tools listed). But they didn't appear in this conversation's tool surface because the chat was already open.

**Lesson:** After any `claude_desktop_config.json` change, test in a *new* Claude Desktop chat, not the existing one.

---

## 3. VP Excel schema (verified today)

For `History Grid (SPY)_v3.xlsx` and `History Grid (QQQ)_v3.xlsx` in `data\excel_exports\`:

- `Date` -- datetime64[us], parsed natively by `pd.read_excel`
- `Open\nPrice`, `High\nPrice`, `Low\nPrice`, `Close\nPrice` -- float64 (note literal newlines in column names)
- `Volume` -- float64 (present in file; v5 doesn't currently read it)
- VP indicators: Short/Medium/Long Term Difference, Predicted High/Low/Range, Williams EMAI, Professional Sentiment, Neural Index, Triple Cross, etc.

**Quirk:** Row 0 is a header-garbage row (NaT date, mostly NaN, some text labels). Real data starts row 1. The existing v5 reader handles this with `if pd.isna(df.iloc[0]['Date']): df = df.iloc[1:]`. New `vp_reader.py` must replicate.

---

## 4. Next session pickup

Start a new Claude Desktop chat. Confirm obsidian MCP tools are live by listing TradingJournal files. Then reference the spec at `docs\P_010_MarketHealth_Spec_v1_1.md` and begin Phase 1 implementation in delivery order:

1. `python\market_health\config.py` (~60 lines)
2. `python\market_health\schemas.py` (~80 lines)
3. `python\domain\distribution_day.py` (~100 lines)
4. `python\domain\rally_state.py` (~120 lines)
5. `python\domain\market_phase.py` (~60 lines)
6. `python\infrastructure\vp_reader.py` (~100 lines)
7. `python\infrastructure\health_writer.py` (~50 lines)
8. `python\application\health_runner.py` (~120 lines)
9. `python\market_health\cli.py` (~80 lines)
10. `python\market_health\launcher.bat` (~30 lines)

All files: p140 env, < 300 lines, < 50 lines per function. One file per code block. Hub architecture rules apply.

---

## 5. Memory items for the new chat

To carry into Claude memory in the next session:

- Aura blocks uvx-based MCP installs at .exe extraction time even with both `Local\uv` and `Roaming\uv` excluded. **Standing rule: install MCP servers into p140 conda env, not via uvx, when on this machine.**
- Windows-MCP hangs when spawning p140 python.exe and waiting for output. **Workaround: write .py file, fire-and-poll output file via Start-Process without -Wait.**
- VP Excel schema verified: row 0 is garbage, real data row 1. `Volume` column exists. Date is datetime64.
- claude_desktop_config.json `obsidian` server now points at `p140\python.exe -m mcp_obsidian` (not uvx).
