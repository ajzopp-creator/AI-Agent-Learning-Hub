# P_300 — Add Pattern Runbook

**File:** `docs/processes/add_pattern.md`
**Version:** 1.0
**Status:** Live operator runbook
**Last Updated:** 2026-05-20
**Audience:** Anthony Zoppi (sole operator until further notice)
**Pairs With:** `python/application/add_pattern_pipeline.py` v1.0 / `python/cli.py` v1.3 / `python/schemas.py` v2.1

---

## Purpose

Per-pattern workflow for growing the catalog. Capture a setup you've identified in VP, ingest it via Pipeline A, verify it landed clean. Lower frequency than Evaluate Trade (you'll do this in batches when you find new candidates worth adding), but the workflow is unforgiving — Pipeline A writes to the catalog via Lock + Temp-DB + Atomic Move, so a sloppy ingest either succeeds cleanly or rejects entirely without corrupting master.

Section 4 (Per-Pattern Workflow) is the meat. Section 5 captures what to do when the integrity-check fails or the verification rejects. Section 3 (Capture Mechanics) is where most operator errors actually originate.

---

## 1. Prerequisites (One-Time / Per-Session)

- p140 conda env active in PowerShell ISE. Verify with `(Get-Command python).Source` returning `C:\Users\Trader\.conda\envs\p140\python.exe`. If not, M-016 / SKILL Workstation Resolution applies — fix the ISE profile prepend before running anything.
- Catalog DB present and HEALTHY. Verify via `python python\cli.py catalog-summary` (currently 25 patterns at `models\051826catalog.db`).
- VantagePoint open and signed in. Confirm you have license access to the ticker you're about to capture (M-023 — healthcare sector is blocked; specific tickers may still be accessible individually).
- `data\historical_patterns\` directory exists at project root. Cosmetic gotcha: the legacy `data\historical\` directory may also exist from Gemini-era work — use `historical_patterns` (M-025).
- Optional: tracker Excel open (`P_300_Curated_Patterns.xlsx`) if you log captures externally. P_300 doesn't enforce this — it's operator hygiene.

---

## 2. The D+20 Rule

Pipeline A computes forward labels at +5/+7/+10/+15/+20 trading days from the launch/anchor date. The XLSX you export must contain enough bars AFTER the launch for all 5 horizons to land on a real bar.

| Launch date | Earliest valid capture date |
| :---- | :---- |
| Monday 2026-04-13 | Monday 2026-05-11 (20 trading days later) |
| Friday 2026-04-17 | Friday 2026-05-15 |
| Mid-week target N | N + 20 trading days, accounting for US market holidays |

If you capture too early, Pipeline A will fail at the labeler (insufficient forward bars) and reject the ingest cleanly. No catalog corruption, but you'll need to re-export after the D+20 window matures.

Practical rule: don't capture a launch younger than ~4 calendar weeks. Wait until the 20-day forward window has fully formed before pulling the XLSX out of VP.

---

## 3. Capture Mechanics (Where Most Errors Happen)

### 3.1 — Identify the launch date

The launch date is what you flag as interesting — the start of a move you want the system to learn from. Stage 7 SEAL locked this: **target = anchor**. In VP, you pick the launch date as the START of your grid range, capture 20 trading bars BACKWARDS for setup context, and the forward labels run 5/7/10/15/20 days FORWARD from there.

If you find yourself wondering "is the target the start or end of my window?" — the target is the LAUNCH, and the LAUNCH is the anchor (offset 0). Setup bars run -19 to 0. Forward labels run +5 through +20.

### 3.2 — Validate the launch date is a trading day

US market holiday + weekend pre-check (M-026): every date you pick should be a trading day. Sunday-date errors crept into Stage 7's initial pick list (AVGO 6/15 Sun, AMD 7/20 Sun, PFE 8/10 Sun, PLTR 10/25 Sat were all caught at review). If you're picking dates manually, eyeball them against a calendar; if you're scripting a pick list, use `datetime.weekday()` + a US federal holiday calendar.

### 3.3 — Export from VantagePoint

In VP, pull up the candidate ticker, set the grid to cover the launch date with at least 20 bars BEFORE and 20 trading days AFTER. Export the History Grid as XLSX.

### 3.4 — Filename and drop location

Save the export as:

```
Pattern_<TARGET_YYYYMMDD>_<CAPTURE_YYYYMMDD>_<SYMBOL>.xlsx
```

Components:
- `Pattern_` prefix — exact, case-sensitive
- `TARGET_YYYYMMDD` — the launch/anchor date in 8-digit format (e.g., `20251115`)
- `CAPTURE_YYYYMMDD` — today's date in 8-digit format (when you exported)
- `SYMBOL` — uppercase ticker (e.g., `NKE`, `GOOGL`, `BRK_A`)
- `.xlsx` — required extension

Drop location: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical_patterns\`

**M-024 gotcha:** Pipeline A's filename parser accepts ANY valid YYYYMMDD date — it doesn't sanity-check "capture date isn't future." TTD's Stage 7 ingest had `20260818` (transposed month-day) and parsed without error. The typo is cosmetic — stored in `source_files.filename` only, doesn't affect math — but it's worth a second-look at filename dates before saving.

**M-025 gotcha:** if you accidentally save to `data\historical\` (the legacy folder), Pipeline A will still read the file if you give it the full path, but you'll lose track of where things live. The DB only stores `filename`, not full path, so files saved to the wrong folder become harder to locate later. Use `windows-mcp:FileSystem` mode=move to relocate any drift catches.

---

## 4. Per-Pattern Workflow

### Step 4.1 — Integrity Check (Conditional)

**Run this ONCE after any VP version update, NOT before every ingest.**

```
cd "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
python python\cli.py integrity-check --xlsx "data\historical_patterns\Pattern_<TARGET>_<CAPTURE>_<SYMBOL>.xlsx"
```

What it does: validates the XLSX column layout against `parameters\ingest_manifest.json`. If VP changed an export column (added, removed, reordered, renamed), the manifest needs an edit before any ingest will work. Exit 0 = safe to proceed; exit 1 = stop and update the manifest first.

When to skip: if you've ingested another pattern with VP unchanged since, you can skip. The check is cheap (~1 sec) so running it doesn't hurt.

### Step 4.2 — Ingest

```
python python\cli.py add-pattern --xlsx "data\historical_patterns\Pattern_<TARGET>_<CAPTURE>_<SYMBOL>.xlsx"
```

What it does (architecture §8.2):
1. Parse the XLSX into Pydantic models
2. Locate the launch bar (the TARGET date from the filename)
3. Slice the 20-bar setup window ending at launch
4. Normalize via domain.normalization
5. Compute forward labels at 5/7/10/15/20 trading days
6. `shutil.copy2(master_db, temp_working.db)` — temp now mirrors master
7. Insert into temp in FK order (symbol → source_file → pattern_instance → bars batch → labels batch)
8. `verify_and_promote(temp, master, expected_delta, pre_counts)` — hollow-record scan + delta verification + atomic move

Expected stdout on success:

```
INGEST OK  -- master=<path to current catalog.db>
backup=<path>.bak
post_counts={'symbols': N, 'source_files': N, ...}
```

Master DB is now atomically updated. The `.bak` is the previous master (deleted on next successful ingest's atomic move; designed to be transient).

Expected stdout on failure:

```
INGEST FAILED -- master untouched
  - <failure reason>
  - <another reason>
```

When INGEST FAILED: master is UNTOUCHED. The temp DB at `models\temp_working.db` is preserved for forensic inspection. See section 5.

### Step 4.3 — Verify the catalog state

```
python python\cli.py catalog-summary
```

Look for:
- `OVERALL: HEALTHY` in the output
- `0 hollow` rows
- Total counts incremented by the expected delta (1 source_file, 1 pattern_instance, 20 pattern_bars, 5 forward_labels, +1 symbol if it was new)
- The new pattern showing in the recent-patterns list

Heads-up: `catalog-summary` can hit the 4-min `windows-mcp:PowerShell` subprocess timeout when called via MCP. Run it directly in ISE for the cleanest path.

### Step 4.4 — Hand-Compare (Optional but Recommended for Each New Symbol)

For at least the first ingest of any new symbol, hand-verify the math against the source XLSX:

```
python python\cli.py inspect-pattern --id N
```

Where `N` is the new pattern_instance_id (visible in the post_counts from Step 4.2 — it's the new top end of the range).

Verify in the output:
- Anchor close matches the launch-date close in source XLSX to 4 decimals
- All 5 forward closes (+5/+7/+10/+15/+20 trading days) match the corresponding bars in source XLSX to 4 decimals
- Each forward label's `return_pct` arithmetic matches (anchor close → future close)

This is the Stage 5 regression workflow — repeat for any new symbol or after any pipeline code change.

---

## 5. Decision Points

### 5.1 — Integrity Check Failed (Step 4.1 exit 1)

Don't ingest. The XLSX column layout doesn't match `ingest_manifest.json` — usually because VP updated an export field. Two paths:

- **You changed nothing intentional:** investigate what VP changed; the integrity-check output names the offending column. Update `parameters\ingest_manifest.json` to reflect the new layout, increment the manifest version, then re-run integrity-check.
- **You did change VP settings (added an indicator, reordered columns):** revert the VP-side change OR update the manifest as above. Don't paper over a real schema drift.

### 5.2 — Ingest Failed (Step 4.2 INGEST FAILED)

Master is untouched. Read the failure reasons listed in stdout. Common causes:
- **launch_date not found in bars** — the TARGET date in the filename isn't a date present in the XLSX. Either the filename is wrong (typo, wrong date) or you didn't capture enough history (the export's earliest bar is later than your target).
- **insufficient setup history** — the launch is too close to the start of the export (need 19+ bars before). Re-export from VP with a wider range.
- **insufficient forward bars** — the D+20 rule wasn't satisfied. Either wait longer (D+20 hasn't matured yet) or you captured too early.
- **Hollow records detected** — verify_and_promote caught a data integrity issue inside the temp DB. The temp at `models\temp_working.db` is preserved; inspect with sqlite tooling before deciding whether to reset or investigate.
- **Delta mismatch** — actual post-insert counts didn't match expected. Usually means an FK issue or a Pydantic validator fired late; check the temp DB.

Recovery rule: do NOT delete `temp_working.db` on a failed ingest until you've understood why it failed. Once understood, fix root cause and re-run Step 4.2.

### 5.3 — Catalog-Summary Shows Drift

If `OVERALL` isn't HEALTHY, or hollow > 0, or counts don't match expected delta — STOP. Don't run another ingest. The catalog is in a state the next ingest could compound. Investigate via `inspect-pattern` for the affected pattern, then decide whether to roll back to the `.bak` or live with the drift.

Rolling back: rename the current master to `<name>.broken`, rename `.bak` to the master name, re-verify. The `.bak` is the previous master from before the broken ingest.

### 5.4 — Hand-Compare Mismatch

If `inspect-pattern --id N` returns values that don't match the source XLSX to 4 decimals — STOP. Pipeline A math has regressed. Don't ingest more patterns. Capture the mismatch (what's off, by how much, at which horizon), then investigate the pipeline code. This is exactly what Stage 5's regression workflow is designed to catch.

---

## 6. Common Failure Modes & Recovery

| Failure | Symptom | Recovery |
| :---- | :---- | :---- |
| Filename regex doesn't match | parse_pattern_file ValueError | Rename to strict `Pattern_<YYYYMMDD>_<YYYYMMDD>_<UPPERSYMBOL>.xlsx` |
| Sunday/Saturday target date | launch_date not in bars (no bar for that date) | Pick a real trading day; M-026 |
| Capture too early (D+20 not matured) | insufficient forward bars | Wait until 20 trading days after target have elapsed |
| VP license blocked for ticker | Can't export from VP in the first place | M-023 substitution pattern — name a thesis-preserving alternative you do have access to |
| Wrong folder (`data\historical\`) | Pipeline A reads it fine via full path but file is hard to find later | Move to `data\historical_patterns\` via `windows-mcp:FileSystem` |
| Capture date typo in filename | None — cosmetic only (M-024) | Optional: rename for hygiene; `source_files.filename` will then mismatch the source file if you do |
| Python interpreter resolution | ImportError on pandas/openpyxl/pydantic | M-016 — fix ISE profile prepend before running anything |
| Manifest drift after VP update | integrity-check exit 1 | Update `parameters\ingest_manifest.json` to match the new VP layout |
| Hollow records caught | verify_and_promote rejects atomic move | Inspect `models\temp_working.db`; understand cause before retry |
| Master got promoted but inspect-pattern shows math mismatch | Worse — bad data in catalog | Roll back to `.bak`, investigate pipeline code, don't ingest more |

---

## 7. Post-Ingest Capture

After each successful ingest, log (in your tracker Excel or wherever):
- **Target date** (the launch/anchor)
- **Capture date** (when you exported from VP)
- **Symbol + pattern_instance_id**
- **Cap class / sector** (informal — used later when grading top-K diversity in Evaluate Trade)
- **Notes** (why you flagged this setup; what about the chart pattern caught your attention)

Catalog growth strategy reminder (from Stage 7 design): mix winners and losers intentionally. An all-winners catalog produces baseline win_rate=1.0 and degenerates the z-score math (ID-007, RESOLVED at Stage 7 SEAL by ingesting diverse outcomes). When picking the next batch of patterns to add, aim for roughly 60% likely winners and 40% mixed/losers — that's what kept the baseline informative.

---

## 8. Calibration Markers (Things in This Doc That Will Change)

- **D+20 rule** — currently 20 trading days is the max forward horizon. If you decide to extend Pipeline A to support longer horizons (60-day, 90-day labels for swing setups), this section changes.
- **`window_length = 20`** — the setup window size. Hard-coded at `MAX_WINDOW_LENGTH` in `add_pattern_pipeline.ingest_pattern_file` default. Could be parameterized later for short-window patterns (5-10 bars for breakout setups vs 20 for trend-continuation).
- **Hand-compare cadence** — currently "first ingest of any new symbol." Could relax to "first of each batch" once you trust the pipeline more, or tighten to "every ingest" if a regression appears.
- **Catalog mix targets (60/40 winner/loser)** — eyeballed Stage 7 heuristic. Calibrate as catalog grows and you see how baseline win_rates evolve.

Update this doc when calibration changes. Bump version, add CHANGELOG below.

---

## Maintenance

- **Owner:** Anthony Zoppi
- **Update trigger:** any time the four-step workflow changes (new CLI flag, new verification step), any time a section-6 failure mode surfaces that isn't already listed, any time a section-8 marker calibrates

## Changelog

### 2026-05-20 v1.0
- Initial release. Per-pattern workflow built around the four-step `integrity-check → add-pattern → catalog-summary → inspect-pattern` sequence (the operator workflow frozen at Stage 4 SEAL and confirmed at Stage 5/7). Section 3 expanded the capture mechanics with M-022 through M-026 inline callouts where the operator would actually trip on them. Section 5 made the failure decision points explicit. D+20 rule called out in its own section (analogous to the 18:30 boundary in evaluate_trade.md).

---

**End of Add Pattern Runbook**
