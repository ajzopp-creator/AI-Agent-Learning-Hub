# HUB_Obsidian_Interface_Architecture

**Version:** 1.0  
**Date:** 2026-05-24  
**Owner:** P_800 (Automation, Note-Taking & Knowledge Building)  
**Status:** Active — production interface for all vault-writing projects

---

## Governance

**Owner:** P_800 maintains and evolves this interface.  
**Scope:** All projects (P_115, P_300, P_400, P_020, KB) that write to Obsidian vault must conform to this schema.  
**Changes:** Any schema modification requires P_800 approval. Projects discover new field requirements → notify P_800 → schema updated → all projects adopt.

---

## Schema Registry

One unified schema per data type. All projects write to the same schema.

### TradeManagementRecord

All trade/signal records (P_115, P_300, P_400, P_020) use this schema.

**Core fields:**
- `date: date` (required)
- `symbol: str` (required)
- `source: str` (optional — P_115 | P_300 | P_400 | P_020)

**P_115 fields:** step1_verdict, pattern_type, setup_score, traded, entry_price, outcome, etc.  
**P_300 fields:** anchor_date, signal, signal_horizon, h5_win_rate, h7_mean_ret, top_analog_1, etc.  
**P_020 fields:** open_date, close_date, exit_price, realized_pnl, days_held, etc.  
**P_400 fields:** council_verdict, risk_mode, lifecycle_status, p115_linked, p300_linked, etc.

**All fields except `date` and `symbol` are optional.** Projects provide only their own data; other fields default to `null`.

**Location:** `P_800_Automation_Note_Taking\scripts\obsidian_writers\schemas.py` → `TradeManagementRecord`

---

### KBRecord

Knowledge base articles, research, summaries.

**Fields:**
- `date: date` (required)
- `title: str` (required)
- `kb_type: str` (Article | Research | AI Summary | Transcript)
- `origin: str` (Web Clipper | Email | Document | Manual)
- `from: str` (optional — source name)
- `ai_summarized: bool`
- `tags: list[str]`
- `ticker_relevance: list[str]`
- `sector: str` (optional)
- `market_regime: str` (optional)
- `linked_trades: list[str]` (optional — trade dates to link)

**Location:** `P_800_Automation_Note_Taking\scripts\obsidian_writers\schemas.py` → `KBRecord`

---

## Write Interface

**Handler:** `handle_write(schema_name, data, body="", overwrite=True)`  
**Location:** `P_800_Automation_Note_Taking\scripts\obsidian_writers\application\write_handler.py`

**Flow:**
1. Validate `data` dict against schema
2. Build filename from `schema_name` + `date` + `title`
3. Build YAML frontmatter from schema fields
4. Write note to vault subfolder (TradeManagement/ or KnowledgeBase/)

**Example call:**
```python
from obsidian_writers.application.write_handler import handle_write

kb_data = {
    "date": "2026-05-24",
    "title": "Email: Market Analysis",
    "kb_type": "Article",
    "origin": "Email",
    "from": "analyst@example.com",
    "ai_summarized": False
}

handle_write(
    schema_name="KB",
    data=kb_data,
    body="Full email text here...",
    overwrite=False
)
```

---

## Vault Folder Structure

```
trading_journal/
├── Templates/
│   └── P_800_Daily_Flow.md          (P_800 owns all templates)
├── Bases/
│   ├── KB_Articles.base
│   ├── Open_Positions.base
│   ├── P115_Evaluations.base
│   ├── P300_Signals.base
│   ├── P400_Trades.base
│   └── P020_Performance.base
├── Trades/
│   └── YYYY-MM-DD_SYMBOL_SOURCE.md  (one per trade)
├── TradeManagement/
│   ├── P115/                        (P_115 trade notes)
│   ├── P300/                        (P_300 signal notes)
│   ├── P400/                        (P_400 lifecycle notes)
│   └── P020/                        (P_020 performance notes)
├── KnowledgeBase/
│   └── YYYY-MM-DD_title.md          (KB articles)
└── YYYY-MM-DD.md                    (daily notes at root)
```

---

## Project Integration Pattern

Any project writing to the vault should:

1. **Reference this document** in project spec
2. **Use `handle_write()`** to write records
3. **Conform to schema** (provide only fields relevant to project)
4. **Add sys.path** to P_800 scripts if not already loaded
5. **Notify P_800** if new fields needed

---

## Ownership & Maintenance

**P_800 responsibility:**
- Maintain schemas in `schemas.py`
- Maintain write handler
- Review schema extension requests
- Update this document with changes

**Project responsibility:**
- Follow the schema
- Use the write interface
- Report issues or new requirements to P_800

---

*HUB_Obsidian_Interface_Architecture v1.0 — Owner: P_800*