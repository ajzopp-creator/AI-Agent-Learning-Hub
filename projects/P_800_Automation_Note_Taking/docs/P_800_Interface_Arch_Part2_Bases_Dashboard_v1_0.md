# P_800 Obsidian Interface Layer — Part 2: Bases, Dashboard & Build Plan
**Companion to:** P_800_Interface_Arch_Part1_Schemas_v1_0.md
**Version:** 1.2
**Created:** 2026-05-22
**Updated:** 2026-07-24 — roadmap corrected: 5E/5F/5H marked Done against live vault state (were stale session placeholders). Prior: 2026-05-22 — 5A/5B/5C/5D complete; 5E/5F reframed; README added

---
## 4. BASES CONFIGURATION

### 4.1 P115_Evaluations.base

```
filter:   file.inFolder("TradeManagement/P115")
sort:     date desc
columns:  date, symbol, step1_verdict, setup_score, traded, outcome, why_code
```

### 4.2 P300_Signals.base

```
filter:   file.inFolder("TradeManagement/P300")
sort:     date desc
columns:  date, ticker, signal, signal_horizon, h5_win_rate, h10_win_rate, h5_mean_ret, n_matches
```

### 4.3 P400_Trades.base

```
filter:   file.inFolder("TradeManagement/P400")
sort:     date desc
columns:  date, ticker, account_id, council_verdict, lifecycle_status, realized_pnl, why_code
```

### 4.4 P020_Performance.base

```
filter:   file.inFolder("TradeManagement/P020")
sort:     close_date desc
columns:  close_date, symbol, account_id, system, realized_pnl, realized_R, outcome, sig_code
```

### 4.5 Open_Positions.base

```
filter:   lifecycle_status == "OPEN" OR (traded == "Y" AND outcome IS NULL)
sort:     date asc
columns:  date, ticker, source, entry_price, stop_price, target_1, account_id, days_held
```

### 4.6 KB_Articles.base

```
filter:   file.inFolder("KnowledgeBase")
sort:     date desc
columns:  date, title, kb_type, origin, tags, ticker_relevance, sector
```

---

## 5. DASHBOARD DESIGN

### 5.1 Current Implementation — Link-Only (v1.0)

Dashboard.md is a simple navigation note. Each view is a clickable `[[link]]`
that opens the corresponding `.base` file. No plugin required. Works today.

**Why link-only:** Obsidian Bases does not support live `![[embed]]` rendering
inside regular notes. A Dataview-powered embedded dashboard requires the
Dataview plugin — deferred to Phase 6 checkpoint.

```markdown
# AJZ Strategies Dashboard

## Trade Views
| View | Open |
|------|------|
| P_115 Evaluations   | [[Bases/P115_Evaluations]] |
| P_300 Signals       | [[Bases/P300_Signals]] |
| P_400 Trades        | [[Bases/P400_Trades]] |
| P_020 Performance   | [[Bases/P020_Performance]] |
| Open Positions      | [[Bases/Open_Positions]] |

## Knowledge Base
| View | Open |
|------|------|
| Articles & Research | [[Bases/KB_Articles]] |

## Market Notes
<!-- Manual entry — TOS + VantagePoint observations -->
```

### 5.2 Phase 6 Checkpoint — Dataview Embedded Dashboard

When data is flowing and Tony knows what he wants to see daily, upgrade to a
Dataview-powered Dashboard.md with inline query tables.

**Requires:** Dataview community plugin (free, widely used, stable)
**Trigger:** At least two sending projects live and producing notes consistently
**Decision gate:** Tony reviews what queries are actually useful before building

---

## 6. PYTHON WRITER LAYER

### 6.1 Architecture Note — API Model (confirmed 2026-05-22)

The interface layer operates as an internal API. Sending projects (P_115, P_300,
P_020, P_400) import `write_to_vault()` and pass field data. P_800 handles all
Obsidian logic. Sending projects have zero vault knowledge.

```python
from shared_resources.python_utils.vault_interface import write_to_vault
write_to_vault("P115", {"date": "2026-05-22", "symbol": "AAPL", ...})
```

### 6.2 P_800 Engine Files (all written and tested)

Save path: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts\obsidian_writers\`

| File | Layer | Lines | Status |
|------|-------|-------|--------|
| `__init__.py` | — | 2 | ✅ Done |
| `logger_setup.py` | — | 43 | ✅ Done |
| `config.py` | config | 46 | ✅ Done |
| `schemas.py` | schema | 148 | ✅ Done |
| `domain/validator.py` | domain | 58 | ✅ Done |
| `domain/frontmatter_builder.py` | domain | 70 | ✅ Done |
| `domain/filename_builder.py` | domain | 80 | ✅ Done |
| `infrastructure/vault_writer.py` | infra | 55 | ✅ Done |
| `application/write_handler.py` | app | 55 | ✅ Done |

### 6.3 Public API (shared_resources)

| File | Path | Status |
|------|------|--------|
| `vault_interface.py` | `shared_resources\python_utils\` | ✅ Done |
| `VAULT_INTERFACE_README.md` | `shared_resources\python_utils\` | ✅ Done |

---

## 7. BUILD ROADMAP

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 5A | Vault subfolders (P115/, P300/, P400/, P020/, KnowledgeBase/) | ✅ Done 2026-05-22 |
| 5B | Six .base files | ✅ Done 2026-05-22 |
| 5C | Dashboard.md — link-only v1.0 | ✅ Done 2026-05-22 |
| 5D | Vault interface engine + public API + README | ✅ Done 2026-05-22 |
| 5E | P_300 integration — call write_to_vault() from P_300 project | ✅ Done — live since 2026-05-18 (earliest P300 vault note; 403 notes as of 2026-07-24) |
| 5F | P_020 integration — call write_to_vault() from P_020 project | ✅ Done 2026-07-21 (WO-P020-E1.005 + WO-P800-E3.002; 201 notes) |
| 5G | KB Templater template + Web Clipper config | Planned |
| 5H | P_400 integration — after P_400 schema locked | ✅ Done — live since 2026-06-08 (earliest P400 vault note; 190 notes + paper/ routing per WO-P400-E2.019) |
| 6 | ⚑ CHECKPOINT — Dataview embedded dashboard | Planned (trigger: 2+ projects live) |

---

## 8. OPEN ITEMS

| # | Item | Owner | Notes |
|---|------|-------|-------|
| 1 | P_115 schema — additional fields beyond 27 cols | Tony + P_115 | Add as discovered |
| 2 | P_400 schema v1 — finalize TXT input fields | P_400 session | Draft exists in P_400 doc |
| 3 | Dashboard update trigger — auto vs manual | Tony | Start automatic; revisit if cumbersome |
| 4 | KB capture workflow — Templater template needed | P_800 | Design in Phase 5G |
| 5 | P_020 WHY/SIG vocabulary lock (NEXT-1 in P_020 backlog) | Tony | Needed before P_020 integration tags work |
| 6 | Phase 6 Dataview decision — what queries are useful | Tony | Decide after 2+ projects producing notes |
| 7 | Delete smoke test note 2026-05-22_AAPL.md from vault | Tony | Safe to delete — test only |

---

*P_800 Obsidian Interface Layer Architecture v1.2 — 2026-05-22*
*Owner: P_800 — feeds from P_115, P_300, P_400, P_020 (read-only relative to all)*
