# Work Order — P_115 Session Required
**From:** P_800 (Note Standard v1.1 implementation)
**Date:** 2026-06-01
**Priority:** MEDIUM — tracker writer does not exist yet; this work order
defines what it must produce when built.

---

## Context

The obsidian_writers engine was upgraded to schema v2.0 on 2026-06-01.
All vault notes now require a set of standard provenance fields (Note
Standard v1.1). The P_115 tracker writer (`tracker_writer.py`) does not
yet exist as a Python module. When it is built in a P_115 session, it
must conform to this specification.

---

## What the P_115 Tracker Writer Must Do

Read rows from the Excel tracker:
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\data\P_115_TrackerDashboard_V3.xlsx

For each row, call write_to_vault() via the Hub interface:
  C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python_utils\vault_interface.py

Output: one frontmatter-only .md per row in:
  C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeManagement\P115\

---

## Required Fields in Every data Dict Passed to write_to_vault()

| Field | Value | Notes |
|-------|-------|-------|
| signal_date | YYYY-MM-DD string | The evaluation date from the tracker row |
| written_by | "P_115/tracker_writer" | Hardcoded string — identifies the module |
| symbol | Uppercase ticker | From tracker column |
| step1_verdict | BUY or ASYM or PASS | From tracker column — auto-mapped to verdict |

run_date and run_ts are injected automatically by write_handler.
verdict is mapped automatically: BUY→BUY, ASYM→WATCH, PASS→PASS.

All 27 tracker columns should be passed where available. See
P_800_Interface_Arch_Part1_Schemas_v1_0.md Section 3.1 for the full
P115Record field list.

---

## Call Pattern

```python
from vault_interface import write_to_vault

write_to_vault(
    schema_name="P115",
    data={
        "signal_date": "2026-05-22",      # evaluation date from tracker
        "written_by": "P_115/tracker_writer",
        "symbol": "AAPL",
        "step1_verdict": "BUY",           # maps to verdict: BUY automatically
        # ... all other 27-column fields ...
    },
    overwrite=True,
)
```

---

## File Plan for tracker_writer.py

Save path:
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python\tracker_writer.py

Estimated ~120 lines. Layers:
  - Read Excel tracker via openpyxl (p140 conda has it installed)
  - Normalize each row to the P115Record field names (snake_case)
  - Call write_to_vault() for each row
  - Log skipped rows (missing date or symbol)

---

## Notes

- Do NOT write tracker_writer.py in a P_800 session. It belongs to P_115.
- The Hub interface (vault_interface.py) is the only import path for
  cross-project vault writes. Never import obsidian_writers internals directly.
- P_115 existing notes in TradeManagement/P115/ (1,462 files as of 2026-06-01)
  were written under schema v1.0. They will not have the new required fields.
  Cross-system Dataview queries will only include notes written after
  tracker_writer.py is built and run.
- Backfill of existing 1,462 notes is a separate decision — not in scope here.

---
*Work order written by P_800 session — 2026-06-01*