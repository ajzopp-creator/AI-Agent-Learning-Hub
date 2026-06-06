# Work Order — P_300 Session Required
**From:** P_800 (Note Standard v1.1 implementation)
**Date:** 2026-06-01
**Priority:** HIGH — P_300 vault writes will fail until this is done

---

## What Changed in P_800

The obsidian_writers engine was upgraded to schema v2.0 on 2026-06-01.
write_to_vault() now requires these additional fields in every data dict:

| Field | Type | Example |
|-------|------|---------|
| signal_date | YYYY-MM-DD string | "2026-05-29" |
| run_date | YYYY-MM-DD string | injected automatically by write_handler |
| run_ts | ISO 8601 string | injected automatically by write_handler |
| written_by | string | "P_300/daily_evaluate_pipeline" |

run_date and run_ts are injected automatically — the sending script does NOT
need to supply them.

signal_date and written_by MUST be supplied by write_signal_to_obsidian.py.

---

## Required Change to write_signal_to_obsidian.py

In the trade_data dict build (around line 85), add:

```python
trade_data = {
    "signal_date": anchor_date,      # ADD THIS LINE
    "written_by": "P_300/daily_evaluate_pipeline",   # ADD THIS LINE
    "date": anchor_date,             # keep for backward compat (deprecated)
    "ticker": symbol,
    "anchor_date": anchor_date,
    "signal": signal_class,
    "signal_horizon": horizon,
    "z_score": z_score,
    "vol_flag": "NONE",
}
```

No other changes required in P_300. write_handler injects run_date and run_ts
automatically. The verdict field is mapped automatically from signal.

---

## Test After Change

Run a single symbol through the pipeline and verify the Obsidian note contains:
- signal_date field
- run_date field
- run_ts field
- written_by field
- verdict field (BUY | WATCH | PASS)
- note_version: 1 (first write) or incremented (re-run)
- verdict_history: [] (first write) or populated list (re-run)

---

## Notes

- The double-division bug (lines 57-58) and overwrite=False bug (line 98)
  were already fixed in write_signal_to_obsidian.py v1.1 (2026-05-31).
  No further action on those items.
- Existing ~60 P_300 notes in the vault are unaffected — they stay at schema
  v1.0 frontmatter. Cross-system Dataview queries will only include notes
  written after this change.
- signal field is retained in P300Record for backward compat. Remove in v3.0.

---
*Work order written by P_800 session — 2026-06-01*