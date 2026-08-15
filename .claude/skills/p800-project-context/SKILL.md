---
name: p800-project-context
description: >
  P_800 Automation / Interface Layer — project-specific operating rules,
  critical paths, vault schema, and anti-patterns. Load at the start of ANY
  session involving P_800 work. Triggers on any reference to P_800,
  obsidian_writers, vault_interface.py, write_to_vault, TradeManagement,
  TradeOrderManagement, KnowledgeBase, Bases, Dashboard.md, Obsidian MCP
  bridge, or any .base file. Always read BEFORE writing any code, file path,
  or vault edit.
---

# P_800 Project Context

## Purpose & Pairs With

Auto-loading protection layer — rules, critical paths, vault schema, anti-patterns. Full architecture on demand.

| File | Role |
| :---- | :---- |
| `docs\P_800_SYSTEM_DOCUMENTATION.md` | Full spec — on demand. Section 7.1 folder tree and Section 5 Phase 5F status are known stale as of 2026-08-12 (WO-P800-E4.004 session) — do not trust either without a live disk/WO check first. |
| `docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md` | Vault folder structure, per-project data schemas — canonical |
| `docs\P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` | Six Bases definitions, Dashboard design, Python writers |
| `python-project-architecture` SKILL (Hub) | Layer boundary standard — domain/infrastructure/application |
| `tasks\todo.md` | Active task queue — loaded by INIT (Protocol F2) |
| **THIS FILE** | Always-active protection rules |

---

## Critical Paths

| Path | Resolution |
| :---- | :---- |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Vault root | `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\` |
| `obsidian_writers` package (canonical) | `C:\Users\Trader\AI-Agent-Learning-Hub\obsidian_writers\` — Hub root, since WO-P800-E2.005 (2026-06-16). Any copy found elsewhere is stale/dead. |
| Public write API | `shared_resources\python_utils\vault_interface.py` — `write_to_vault(schema_name, data_dict)` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` (never a new venv) |
| Bases folder | `trading_journal\Bases\` — six `.base` files |
| Work order ledger | `Agentic-Hub-Governance\work_orders\` |
| Obsidian MCP bridge config | `%APPDATA%\Claude\claude_desktop_config.json` — `mcp_obsidian` package via p140 python; restart Claude Desktop fully (tray → Quit) after any `OBSIDIAN_API_KEY` change |
| Obsidian Local REST API | `127.0.0.1:27124` (HTTPS) — bridge is dead without Obsidian running |

### TradeManagement vs TradeOrderManagement — the confusion that hid EC-P800-E4.004

Two folders, easy to conflate, real disk state governs, not the doc:

| Folder | Holds | Live status (2026-08-12) |
| :---- | :---- | :---- |
| `trading_journal\TradeManagement\` | Legacy — per-project frontmatter notes, pre-rename | Empty shell, confirmed dead (WO-P800-E3.003) |
| `trading_journal\TradeOrderManagement\<P115\|P300\|P400\|P020>\` | Live frontmatter notes, one `.md` per record | Confirmed live — P300 subfolder alone held 582 files at last check |

**Never trust the system doc's folder tree over a live `Test-Path` / `Get-ChildItem` count.** Section 7.1 still shows the pre-rename tree as of this skill's creation — a doc fix is filed but not yet done. If a `.base` filter or a project's `config.py` references `TradeManagement\<project>`, that is the dead path — flag it, don't build on it.

---

## Vault Folder Map (live, confirmed 2026-08-12)

```
trading_journal\
├── Templates\P_800_Daily_Flow.md      ← master template, P_800-owned, only one
├── Bases\                             ← six .base files, real Obsidian Bases YAML
│   ├── P115_Evaluations.base          ← owner P_115
│   ├── P300_Signals.base              ← owner P_300
│   ├── P400_Trades.base               ← owner P_400
│   ├── P020_Performance.base          ← owner P_020
│   ├── Open_Positions.base            ← P_800-internal
│   └── KB_Articles.base               ← P_800-internal
├── TradeOrderManagement\
│   ├── P115\ P300\ P400\ P020\        ← one frontmatter .md per record, live
│   └── signals\                       ← raw JSON signal packets, P400SIG schema
├── KnowledgeBase\                     ← articles, clipped content, AI summaries
└── Dashboard.md                       ← daily entry point, vault root
```

### Public API contract

```python
from shared_resources.python_utils.vault_interface import write_to_vault
write_to_vault("P115", {"date": "2026-06-07", "symbol": "AAPL", ...})
```

`vault_interface.py` validates against `obsidian_writers\schemas.py`, routes to the correct `TradeOrderManagement\<schema>\` subfolder, writes frontmatter `.md`. **No upstream project (P_115/P_300/P_400/P_020) has Obsidian knowledge of its own** — P_800 owns 100% of vault-write logic. A cross-project session touching vault content is a boundary violation unless it goes through a work order.

---

## Anti-Patterns (Forbidden by Construction)

1. **Trusting a `.base` file's rendered UI row count as proof its filter works.** An unfiltered base and a correctly-filtered one both render without error — Obsidian's Bases plugin silently ignores unrecognized top-level keys instead of erroring. WO-P800-E4.004 (2026-08-12): every `.base` file used a fabricated schema (`filter:`/`conditions:`/`conjunction:` — none are real Bases keys) since creation; P400_Trades silently showed the entire vault (3,002 rows) instead of 405. **Always read raw YAML via `obsidian_get_file_contents` or disk, check against `help.obsidian.md/bases/syntax`, before AND after any edit** — then get a human to confirm the row count against the folder's known file count.
2. **Real Bases syntax, for reference** — top-level `filters:` (plural) with `and`/`or`/`not` lists of function-call expression strings (`file.inFolder("path")`), `properties:` for cosmetic column display names, per-view `order:`/`sort:` under `views:`. NOT `filter:` (singular), NOT `conditions:`, NOT `conjunction:`, NOT top-level `columns:`.
3. **Adding `extra="forbid"` to a shared Pydantic model without checking the writer's injected fields.** EC-004 (2026-06-30): broke every P_400 vault write for ~90 min because `write_handler.py` injects a source key the caller's payload never carries. Test against the actual writer path, not just the caller's explicit dict.
4. **Editing a template or vault schema from outside P_800.** P_800 owns all Obsidian templates and all vault-write logic. Boundary violations go through a work order, never a direct edit from another project's session.
5. **Treating the Excel tracker sync as two-way.** `TradeOrderManagement\` is a one-way mirror (upstream → vault). Never write vault content back to Excel.
6. **Generating or modifying P_010 market posture data from P_800.** P_800 displays P_010 output only (EC-002, 2026-03-08).
7. **`tp.web.request()` in Templater.** Doesn't exist. Use `tp.obsidian.requestUrl({url: "..."})` (EC-009).
8. **Assuming the vault lives under OneDrive.** It doesn't — `trading_journal\` is on C: outside OneDrive by design (EC-007, 2026-03-16); the OneDrive Documents redirect caused a real historical path confusion.

---

## Layer Architecture (obsidian_writers, Hub Standard)

```
obsidian_writers\                      ← Hub root, canonical
├── config.py                          ← VAULT_FOLDER_MAP, all constants
├── schemas.py                         ← Pydantic models — per-project payload contracts
├── domain\
│   ├── validator.py
│   ├── vault_schemas.py               ← EC-004 site — check injected fields before extra="forbid"
│   ├── signal_schemas.py
│   ├── frontmatter_builder.py
│   └── filename_builder.py
├── infrastructure\
│   ├── vault_writer.py
│   └── json_writer.py
└── application\
    └── write_handler.py               ← injects source key — the field callers never send
```

**Hard rules:** `domain\` no file I/O. `infrastructure\` no business logic. `application\` orchestrates only. `config.py` is the single source of truth for folder routing — never hardcode `TradeOrderManagement\<x>` paths elsewhere.

---

## AI Behavioral Rules

**Must:**
1. Verify live disk state (`Test-Path`, file counts) before trusting any doc's folder tree or path claim
2. Read raw `.base` YAML and check against `help.obsidian.md/bases/syntax` before AND after any Bases edit — never trust rendered row count alone
3. Archive-before-modify on every `.base`, WO, or source file edit (`{name}.bak_{YYYY-MM-DD}` or descriptive suffix)
4. Route all vault writes through `write_to_vault()` — never construct a frontmatter `.md` by hand for a live project
5. Treat cross-project `.base` edits (P115/P300/P400/P020-owned) as needing that project's Ack per WO_COMPLETION_GATE caller propagation, even though P_800 owns the edit
6. Plan all files with line counts before writing any code (Hub standard)
7. Write UTF-8 no-BOM, LF-only

**Must Not:**
1. Trust `P_800_SYSTEM_DOCUMENTATION.md` Section 7.1 or Section 5 without a live cross-check (both known stale as of 2026-08-12)
2. Reference `TradeManagement\<project>` as a live path — confirmed dead, `TradeOrderManagement\<project>` is current
3. Let another project's session edit a vault template, schema, or `.base` file directly — P_800 owns all of it
4. Add `extra="forbid"` to a shared vault Pydantic model without testing against the writer's injected fields
5. Generate or modify P_010 posture data
6. Write vault content back to the Excel tracker

---

## Naming Conventions

| Element | Convention |
| :---- | :---- |
| Vault frontmatter note | one `.md` per record, routed by `write_to_vault()` — never hand-built |
| Bases backup | `{filename}.bak_{YYYY-MM-DD}` before any edit |
| WO backup | `WO-{ID}_backup_{YYYY-MM-DD}.md` (numeric suffix same-day) |
| Daily note | `YYYY-MM-DD.md` |
| Master template | `P_800_Daily_Flow.md` — the only template, P_800-owned |

---

## Session-Start Checklist

- [ ] Call `tool_search` first — confirm Windows-MCP / filesystem availability, never assume
- [ ] Acknowledge SKILL loaded by citing one rule
- [ ] If touching a `.base` file: read raw YAML first, confirm live folder path via `Test-Path`/`Get-ChildItem`, archive before edit
- [ ] If touching `obsidian_writers`: confirm which layer (domain/infrastructure/application) before writing — never mix
- [ ] If the edit affects a P115/P300/P400/P020-owned `.base` or schema: flag that project's Ack is needed per WO_COMPLETION_GATE, don't self-close
- [ ] Never propose vault-schema or template work from another project's session — redirect to P_800 via work order

---

## When to Consult the Full Architecture Doc

Load `docs\P_800_SYSTEM_DOCUMENTATION.md` (with the Section 7.1 / Section 5 staleness caveat above) for:
- Full daily flow reference, tool inventory, build roadmap (Sections 3–5)
- MCP bridge configuration detail (Section 5.2)
- Full Error Corrections Log (Section 9)
- Session log history (Section 10)

Load `docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md` and `Part2_Bases_Dashboard_v1_0.md` for:
- Full per-project payload schemas (P115/P300/P400/P020)
- Original six-Bases design intent (predates the WO-P800-E4.004 fabricated-schema finding — treat filter syntax examples there as unverified until cross-checked)

Do NOT load reflexively — this SKILL covers most operations.

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** New EC log entry requiring structural protection, vault folder map change, or obsidian_writers layer contract change
- **Created:** 2026-08-12 — first always-loaded context layer for P_800, gap flagged during WO-P800-E4.004 (fabricated Bases schema sat undetected across every `.base` file since creation partly for lack of this layer)

## Changelog

### 2026-08-12
Initial creation. Anti-Pattern #1/#2 and Critical Paths' TradeManagement-vs-TradeOrderManagement section sourced directly from WO-P800-E4.004's live findings (same session). EC-004 (Pydantic `extra="forbid"`) and EC-002/007/009 (P_010 scope, OneDrive path, Templater function) folded in from `P_800_SYSTEM_DOCUMENTATION.md` Section 9.

---

**End of P_800 Project Context SKILL**
