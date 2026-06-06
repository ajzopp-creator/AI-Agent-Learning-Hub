# P_805 KB Integration Specification

**Version:** 1.1  
**Date:** 2026-05-25  
**Owner:** Tony  
**Status:** Specification phase (ready to build)

---

## Scope

Extend P_805 to convert approved Thunderbird emails to KB notes in Obsidian's `KnowledgeBase/` folder using the unified interface defined in `HUB_Obsidian_Interface_Architecture.md`.

**Reference:** All schemas and write interface calls use `KBRecord` from the Hub Interface Architecture.

---

## P_805-Specific Requirements

### 1 Input Source

**Manually-saved emails** from Thunderbird (approved senders: `data\sender_sheet.csv`)  
**Path:** `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\data\inbox\`  
**Format:** `.eml` files (Thunderbird export format)  
**Trigger:** If folder is non-empty, process all `.eml` files. If empty, exit gracefully.  
**Lookback:** configurable window (default: 7 days, for metadata/filtering only)

---

### 2 Processing Mode (Dual Control)

#### Global Mode (CLI Flag, Default)
```bash
python cli.py --kb-mode full        # all .eml files → full content
python cli.py --kb-mode summary     # all .eml files → LM Studio summary
```

#### Per-File Override (Filename Pattern)
Files matching these patterns override the CLI flag:

- `*--full.eml` → always use **full content**, ignore CLI flag
- `*--summarize.eml` → always use **LM Studio summary**, ignore CLI flag
- `*.eml` (no suffix) → use CLI flag mode (default)

**Example:**
```
data\inbox\
├── earnings_report.eml              (uses CLI flag mode)
├── newsletter--summarize.eml        (always summarized)
├── earnings_deep_dive--full.eml     (always full)
```

---

### 3 Mode A: Full Content

- Extract plain-text email body as-is
- No modification or summarization
- `ai_summarized` flag: `false`

---

### 4 Mode B: Summarized

- Extract plain-text email body
- Call LM Studio at `http://127.0.0.1:1234/v1` for 2-3 sentence summary
- Max 300 tokens
- **Fallback to Mode A if LM Studio unreachable**
- `ai_summarized` flag: `true`

---

### 5 Schema Usage

Use `KBRecord` from Hub Interface. P_805 populates:

```python
{
  "date": extract_date(email),
  "title": email.subject,
  "kb_type": "Article",
  "origin": "Email",
  "from": email.sender,
  "ai_summarized": (is_mode_b),
  "tags": [],
  "ticker_relevance": [],
  "sector": None,
  "market_regime": None,
  "linked_trades": []
}
```

**Body:** email text (Mode A) or LM Studio summary (Mode B)

---

### 6 LM Studio Summarization

**Endpoint:** `http://127.0.0.1:1234/v1/completions`  
**Model:** `mistral` (or config value)  
**Temp:** 0.3  
**Max tokens:** 300  
**Timeout:** 10 seconds

**System prompt:**
```
You are a financial research assistant. Summarize this email in 2-3 sentences.
Focus: thesis, data points, action insights. Omit: greetings, signatures, marketing.
```

---

### 7 Write Interface Call

**Import:** `from obsidian_writers.application.write_handler import handle_write`

**Call:**
```python
success = handle_write(
    schema_name="KB",
    data=kb_data,
    body=body,
    overwrite=False
)

if success:
    delete_eml_file(eml_path)
else:
    log_error(f"KB write failed: {eml_path}")
```

See `HUB_Obsidian_Interface_Architecture.md` for full handler behavior.

---

### 8 Configuration

Add to `python\config.py`:

```python
import sys
import os

# Path wiring for Hub interface
P800_SCRIPTS = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts"
if P800_SCRIPTS not in sys.path:
    sys.path.insert(0, P800_SCRIPTS)

# KB integration
KB_MODE = os.getenv("KB_MODE", "full")  # "full" or "summary"
KB_LOOKBACK_DAYS = int(os.getenv("KB_LOOKBACK_DAYS", "7"))
KB_MODE_PATTERN_FULL = r"--full\.eml$"
KB_MODE_PATTERN_SUMMARIZE = r"--summarize\.eml$"
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"
LM_STUDIO_MODEL = "mistral"
LM_STUDIO_TEMP = 0.3
LM_STUDIO_MAX_TOKENS = 300
LM_STUDIO_TIMEOUT = 10
```

---

### 9 New Files

- `python\application\p805_kb_writer.py` (~120 lines) — scan `data\inbox\`, parse filename patterns, orchestrate write
- `python\infrastructure\lm_studio_caller.py` (~60 lines) — LM Studio API wrapper with retry + fallback

**Updates:**
- `python\config.py` — add KB_MODE, KB_LOOKBACK_DAYS, KB_MODE_PATTERN_*, LM_STUDIO_* constants
- `python\cli.py` — add `--kb-mode` and `--kb-lookback` args

---

### 10 CLI

```bash
python cli.py --kb-mode full --kb-lookback 7
python cli.py --kb-mode summary --kb-lookback 7
```

**Behavior:**
1. Check if `data\inbox\` has `.eml` files
2. If empty, log and exit
3. For each `.eml` file:
   - Parse filename for `--full` or `--summarize` suffix
   - If found, use that mode; else use CLI default
   - Extract `.eml` body (plain text)
   - If summarize mode: call LM Studio (fall back to full if unreachable)
   - Build KBRecord
   - Call `handle_write("KB", ...)`
   - On success: delete `.eml` file
   - Log per-file outcome
4. Output: "Wrote X KB notes (Y summarized, Z full)"

---

### 11 Error Handling

| Scenario | Action |
|----------|--------|
| `data\inbox\` is empty | Log "No `.eml` files to process", exit normally |
| LM Studio offline (Mode B) | Log warning, fall back to Mode A for that file |
| `.eml` undecodable | Log error, skip file, continue |
| KBRecord validation fails | Log error, skip file, continue |
| handle_write fails | Log error, skip file, do NOT delete `.eml` |
| `.eml` delete fails after write | Log warning (file stays in drop zone for manual retry) |
| P800_SCRIPTS path missing | Fail at startup with clear error message |

---

### 12 File Lifecycle

1. Tony manually saves `.eml` file to `data\inbox\` from Thunderbird
2. `python cli.py --kb-mode X [--kb-lookback Y]` runs
3. P_805 reads file, determines mode (filename pattern or CLI default)
4. Extract body, (optionally) summarize via LM Studio
5. Write to KB via P_800 `handle_write()` interface
6. On success: delete `.eml` from `data\inbox\`
7. On failure: file remains for manual review / retry

---

### 13 Testing Checklist

- [ ] `data\inbox\` folder exists and is readable
- [ ] sys.path import succeeds (`P800_SCRIPTS` accessible)
- [ ] LM Studio connectivity check (or fallback works)
- [ ] Filename pattern matching works (`*--full.eml`, `*--summarize.eml`, `*.eml`)
- [ ] Mode A writes full email body to KB
- [ ] Mode B writes LM Studio summary to KB
- [ ] Title, date, `ai_summarized` flag correct in KBRecord
- [ ] File saved to `KnowledgeBase/YYYY-MM-DD_title.md`
- [ ] Fallback to Mode A works if LM Studio offline
- [ ] `.eml` file deleted after successful write
- [ ] `.eml` file remains if write fails

---

**Reference:** `HUB_Obsidian_Interface_Architecture.md`

*P_805 KB Integration Spec v1.1 — Dual-mode control (global CLI + per-file patterns)*
