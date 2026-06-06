**ONE unified, consolidated, architecture‑grade document**  
that merges:

- Your **P_800 Vault Rebuild Plan**
- Your **Obsidian Strategy / AJZ Knowledge OS**
- The **Bases architecture**
- The **Dataview dashboard architecture**
- The **P_115 + P_300 integration**
- The **Tracker Log (Excel → Obsidian) pipeline**
- The **P_300 processed‑log ingestion spec**
- The **LLM‑agnostic automation spec** (Claude, Grok, Gemini, Perplexity)

---

# **P_800 Unified Obsidian Architecture Specification**  
### *Version 1.0 — Consolidated from P_800 Rebuild Plan + AJZ Strategy + Bases + Dataview + P_115 + P_300*

---

# **0. PURPOSE**
This document defines the **single, unified architecture** for:

- The **P_800 Trading Journal Vault**
- The **AJZ Knowledge Operating System**
- The **P_115 Buy‑the‑Dip System**
- The **P_300 Pattern‑Match System**
- The **Excel Tracker Log → Obsidian pipeline**
- The **Bases + Dataview dual‑layer query system**
- The **LLM automation layer** (Claude, Grok, Gemini, Perplexity)

This is the **canonical reference** for all agents and all workflows.

---

# **1. VAULT LOCATION & STRUCTURE**

### **Vault Path (Locked)**
```
C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\
```

### **Top‑Level Folders**
| Folder | Purpose |
|-------|---------|
| `00_Inbox/` | Temporary landing for PDFs, transcripts, screenshots. |
| `10_Sources/` | Read‑only archive (“The Hoard”). AI reads only during ingest. |
| `20_Wiki/` | Evergreen knowledge base (Market Regimes, Indicators, Concepts). |
| `30_Analysis/` | P_115 checks, P_300 logs, risk logs, trade analysis. |
| `40_Operations/` | SOPs, Identity.md, Memory.md, project trackers. |
| `Trades/` | One `.md` per trade (Excel → Markdown export). |
| `Bases/` | `.base` files for Obsidian Bases views. |
| `Templates/` | All templates (Daily, Trade, Setup, Client, Project). |
| `System/` | CLAUDE.md, automation rules, environment detection skill. |

---

# **2. CORE PRINCIPLES**

### **2.1 Single Source of Truth**
- **Excel Tracker Log** (27 locked columns) remains canonical for trades.
- Obsidian is a **one‑way mirror** for trade notes.
- P_300 processed logs are **read‑only** inside Obsidian.

### **2.2 Dual Query Architecture**
- **Bases = Interface Layer**  
  Structured, Notion‑style views for Trades, Setups, Clients, Projects.

- **Dataview = Logic Layer**  
  Dashboards, cross‑folder analytics, daily/weekly summaries.

### **2.3 AI Automation Layer**
All LLMs (Claude, Grok, Gemini, Perplexity) follow the same rules:

- Read dashboard → generate briefing  
- Read daily note → update properties  
- Read P_300 logs → create/update setup notes  
- Never modify Excel  
- Never modify trade notes except via export pipeline

---

# **3. FILE NAMING RULES**

### **Daily Notes**
```
trading_journal/YYYY-MM-DD.md
```

### **Trade Notes**
```
Trades/YYYY-MM-DD_SYMBOL_P115.md
```

### **P_300 Processed Logs**
```
30_Analysis/P300/YYYY-MM-DD_TICKER_P300.md
```

### **Templates**
```
Templates/*.md
```

### **Bases**
```
Bases/*.base
```

---

# **4. YAML SCHEMA (UNIFIED)**

### **4.1 Global Properties**
```yaml
type: project | task | client | daily | ticker | setup | trade | p300
status: active | complete | pending | watch | asym | pass
created: YYYY-MM-DD
updated: YYYY-MM-DD
priority: high | medium | low
tags: []
```

---

### **4.2 Trade Note Schema (27 Columns → YAML)**  
*(Locked — do not modify)*

```yaml
---
date: 2026-05-09
symbol: MOD
signal_source: P_115
step1_verdict: BUY
pattern_type: "--"
breakout_verdict: "--"
breakout_volume_multiple: null
distribution_day_count: null
follow_through_day: null
market_direction: STANDARD
rs_vs_spy: null
fundamentals_tier: 3
analysis_tier: 3
candle_tier: 2
setup_score: 3
liquidity_tier: null
traded: N
entry_price: null
tp_level: null
sl_level: null
stop_level: null
risk_pct: null
account_balance: 32812
outcome: null
recheck_status: null
simulation_notes: ""
comments: "HybridTier=6"
---
```

---

### **4.3 P_300 Processed Log Schema (Minimal Required Fields)**  
*(We intentionally **strip** the CSV to only what Obsidian needs)*

```yaml
---
type: p300
date: 2026-05-19
ticker: VZ
signal: WATCH
horizon: 7
win_rate: 0.65
mean_return: 1.19
z_score: 0.456
volatility_regime: normal | divergent
top_matches: 20
---
```

**We do NOT store the full CSV.**  
Only the fields needed for:

- Bases filtering  
- Dataview dashboards  
- Linking to setups  

---

### **4.4 Setup Note Schema (P_115 + P_300 merged)**

```yaml
---
type: setup
ticker: VZ
setup_date: 2026-05-19
p115_step1: BUY | ASYM | PASS
p115_step2: null
dl_score: 0.82
p300_signal: WATCH
p300_horizon: 7
p300_win_rate: 0.65
recheck_date: 2026-05-26
structure_tier: 2
notes: ""
---
```

---

# **5. BASES CONFIGURATION**

### **5.1 `daily_trades.base`**
```
filter: file.inFolder("Trades")
sort: date desc
columns:
  - date
  - symbol
  - signal_source
  - step1_verdict
  - fundamentals_tier
  - analysis_tier
  - candle_tier
  - setup_score
  - traded
  - outcome
```

---

### **5.2 `open_positions.base`**
```
filter: traded == "Y" AND outcome == null
sort: date asc
columns:
  - date
  - symbol
  - entry_price
  - tp_level
  - sl_level
  - risk_pct
  - account_balance
formula:
  days_held = today - date
```

---

### **5.3 `performance_by_strategy.base`**
```
filter: file.inFolder("Trades") AND outcome != null
groupBy: signal_source
columns:
  - signal_source
  - count
  - count(outcome="TP Hit")
  - win_rate
```

---

### **5.4 `p300_signals.base`**
```
filter: type == "p300"
sort: date desc
columns:
  - date
  - ticker
  - signal
  - horizon
  - win_rate
  - z_score
```

---

# **6. DATAVIEW DASHBOARD (Cyril‑Style + Trading Panel)**

### **Dashboard.md**
Includes:

1. Today’s Priorities  
2. Active Projects  
3. Next 7 Days  
4. Client Health  
5. Open Loops  
6. Revenue Pulse  
7. **Trading Panel**  
   - Today’s Setups  
   - Recheck Queue  
   - Open Trades  
   - P_300 Signals  

All queries are Dataview TABLE/LIST blocks.

*(I will generate the full dashboard when you say “Generate the Dashboard.md file.”)*

---

# **7. EXCEL → MARKDOWN EXPORT PIPELINE**

### **Files**
```
excel_reader.py
frontmatter_writer.py
config.py
logger_setup.py
main.py
```

### **Rules**
- Reads Excel  
- Converts each row → YAML frontmatter  
- Writes `.md` to `Trades/`  
- Never overwrites manually edited notes  
- Logs all writes  

---

# **8. P_300 LOG INGESTION PIPELINE**

### **Input**
CSV from P_300 engine.

### **Output**
One `.md` per ticker per day:

```
30_Analysis/P300/YYYY-MM-DD_TICKER_P300.md
```

### **Fields kept**
- date  
- ticker  
- signal  
- horizon  
- win_rate  
- mean_return  
- z_score  
- volatility_regime  

### **Fields discarded**
- full analog table  
- full horizon table  
- narrative text  
- raw returns  

---

# **9. AI AUTOMATION LAYER (MODEL‑AGNOSTIC)**

### **9.1 Morning Briefing Prompt**
```
Read my Dashboard.md and every file it references.

Produce a 200–300 word briefing that tells me:
1. The single most important thing today
2. What must be done before noon and why
3. What is at risk if ignored
4. The client that needs attention most
5. One decision I should make now

Do not describe tables. Tell me what the data means.
```

---

### **9.2 Property Update Prompt**
```
Read today's daily note.

For each line:
- DONE: [project] — [deliverable]
- UPDATE: [project] — completion: 65
- OPEN: [item]

Update the corresponding project/task/setup/trade files.
Write changes to a changelog.
```

---

### **9.3 P_300 → Setup Integration Prompt**
```
When a new P_300 log appears:
- Create or update a setup note for that ticker
- Merge P_115 and P_300 fields
- Set recheck_date = setup_date + 7 days
- Add to Bases views automatically via YAML
```

---

# **10. BUILD SEQUENCE (FINAL)**

### **Phase 1 — Vault Build**
Steps 1–11 from your rebuild plan (unchanged).

### **Phase 2 — Export Pipeline**
Build Excel → Markdown script.

### **Phase 3 — P_300 Ingestion**
Add P_300 pipeline + `.base` views.

### **Phase 4 — Dashboard**
Generate Dashboard.md.

### **Phase 5 — AI Automation**
Add morning briefing + property update + P_300 integration.

---

