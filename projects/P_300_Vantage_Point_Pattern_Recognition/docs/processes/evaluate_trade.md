# P_300 — Evaluate Trade Runbook

**File:** `docs/processes/evaluate_trade.md`
**Version:** 1.0
**Status:** Live operator runbook
**Last Updated:** 2026-05-20
**Audience:** Anthony Zoppi (sole operator until further notice)
**Pairs With:** `python/application/daily_evaluate_pipeline.py` v1.2 / `report_writer.py` v1.3 / `schemas_pipeline_b.py` v1.2

---

## Purpose

Per-candidate decision tree for running Pipeline B and turning the signal into a trading action. Not a fixed-time routine — run whenever a setup catches your eye, with the data-freshness rules below. Not a strategy book. Operator runbook only.

Section 4 (Decision Tree) is the meat. Sections 1-3 are the mechanics; section 5+ is post-trade housekeeping and failure recovery.

---

## 1. Prerequisites (One-Time / Per-Session)

- p140 conda env active in PowerShell ISE. Verify if you've opened a fresh session: `(Get-Command python).Source` must return `C:\Users\Trader\.conda\envs\p140\python.exe`. If not, M-016 / SKILL Workstation Resolution applies — fix the ISE profile before running anything.
- Catalog DB present and HEALTHY. Verify with `python python\cli.py catalog-summary` (currently 25 patterns at `models\051826catalog.db`). Heads-up: this command can hit the 4-min `windows-mcp:PowerShell` subprocess timeout when called via MCP, but runs fine when you invoke it yourself in ISE.
- VantagePoint open and signed in.
- `data\live\` directory exists at the project root (it does — created at Stage 3).
- (Optional, only if you want narrative commentary) LM Studio open with DeepSeek R1 14B loaded. Adds ~10-40s per evaluation and never affects signal class (NFR-1 hard rule).

---

## 2. Data Freshness Boundary — 18:30 ET

VantagePoint's History Grid export contains end-of-day bars only. Today's bar lands in the export AFTER ~18:30 ET when the daily build completes.

| Time of run | Most recent bar in export | Anchor date in report |
| :---- | :---- | :---- |
| Before 18:30 ET today | Yesterday's close | Yesterday |
| After 18:30 ET today | Today's close | Today |

**Implication for entries:**

- Run AFTER 18:30: signal anchors on TODAY's close; act at next open (tomorrow) per your sizing rules.
- Run BEFORE 18:30: signal anchors on YESTERDAY's close; today is already a "next-bar" forward bar relative to the signal. Today's intraday action is invisible to the analysis. Re-run after 18:30 to confirm the call still holds with today's bar in the window.

If a candidate is screaming for attention pre-18:30, the cleanest move is to glance at the pre-18:30 signal for direction, then re-run after the daily build before committing capital.

---

## 3. Per-Candidate Workflow (Mechanics)

### Step 3.1 — Export from VantagePoint

Pull up the candidate ticker in VP. Export the History Grid to `data\live\History Grid (<SYMBOL>).xlsx`. Filename rules:
- Uppercase symbol in parentheses, exact spacing — Pipeline B's regex (`vp_xlsx_reader.py`) requires it
- Overwrite any prior export for the same ticker; live exports are not preserved

### Step 3.2 — Run Pipeline B

From project root in PowerShell ISE:

```
cd "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
python python\application\daily_evaluate_pipeline.py --xlsx "data\live\History Grid (<SYMBOL>).xlsx" --no-narrator
```

Flag notes:
- Drop `--no-narrator` when LM Studio is loaded and you want commentary
- Add `--no-write-file` when you don't want a persisted report (default is to save at `outputs\reports\report_<SYMBOL>_<ANCHOR>_<TIMESTAMP>.txt`)
- Override `--top-k N` if you want a tighter or wider analog set (default 20)
- Override `--window-length N` if you want longer / shorter pattern context (default 20)

### Step 3.3 — Read the Report

Five blocks render top-to-bottom:

1. **Header** — ticker, anchor date, signal class, chosen horizon
2. **Per-horizon stats** — `n / win_rate / mean_ret / std_ret / z_score / class` for horizons 5/7/10/15/20
3. **Top 20 matches** — historical analogs sorted by composite distance ASCENDING (lower = more similar); returns at +5/+7/+10/+15/+20 days
4. **Volatility divergence** — appears ONLY when MILD or STRONG; absence = NONE = vol regime matches top-K
5. **Narrative** — LLM commentary if narrator enabled; `(unavailable)` otherwise

---

## 4. Decision Tree (THE Section)

**Two inputs drive the call: signal_class × volatility_severity.** Then operator judgment overlays catalog observations (which tickers in top-K, return patterns, etc.).

Current catalog reality (N=25, mixed-vol per Stage 7 design): expect BUY to be RARE — z > 1.0 thresholds are tight at this catalog size (M-028). Most candidates will land in WATCH or PASS. STRONG vol flag will be common for low-vol mega-caps and ETFs because the catalog includes high-vol names like TTD, GLP, AMD, PLTR.

### 4.1 — BUY Branch

**BUY + vol NONE (the gold case, rare today):**
- Clean BUY signal at vol-aligned analogs
- Action: enter at next open after the chosen horizon's signal direction; full size per P_000 risk rules (1.5% of $32,812 = $492.18 max risk; three-gate sizing per P_000)
- Set stop per your usual rule (volatility-trailing / fixed-percent / time-based — your choice; not enforced by P_300)
- Hold for the chosen_horizon's bar count unless invalidated

**BUY + vol MILD (decent but caveated):**
- Modest vol regime mismatch; top-K analogs trade slightly differently than candidate
- Action: enter, but size at ~75% of full (risk budget $369 instead of $492, matching the HALF risk mode in P_010 conceptually)
- Tighten stop one notch — the return magnitudes in top-K may overstate what to expect

**BUY + vol STRONG (treat with skepticism):**
- Top-K analogs are apples-to-oranges; the math says "shape similar" but they live in a different vol regime
- Default action: treat as WATCH — do NOT enter on this signal alone
- Override conditions for entering anyway (any one is sufficient):
  - At least 3 of top-5 matches are SAME-ticker or SAME-vol-class as candidate (you eyeball this on the matches table)
  - Independent confirmation (chart pattern, sector momentum, etc.) outside the system
  - You're willing to size at 25-50% of full to test the call
- If you do enter, journal the override reason for later calibration

### 4.2 — WATCH Branch

WATCH means: stats are constructive but not strong enough to commit. Default behavior: monitor, don't enter.

**WATCH + vol NONE:** Clean WATCH. Add ticker to a re-evaluate list. Re-run Pipeline B daily (after 18:30) until signal evolves to BUY (then enter per 4.1) or degrades to PASS (drop).

**WATCH + vol MILD:** Same monitoring posture, but note the caveat — the eventual BUY (if one comes) will inherit the MILD flag and you'll size at 75% per 4.1.

**WATCH + vol STRONG:** Lower-priority monitor; the analog cohort isn't great. Don't put much weight on a future BUY from this signal pathway unless the cohort improves. Check the top-K composition daily — if same-vol-class matches start displacing the high-vol outliers, the flag will drop.

### 4.3 — PASS Branch

PASS means: no actionable edge in the math.

**PASS at all three vol flags:** Skip. The vol flag adds nothing when you're not entering.

One exception worth flagging: if PASS comes with strongly NEGATIVE z-scores across multiple horizons (e.g., -1.5 or worse at 3+ horizons), that's not "no signal" — it's a potential AVOID / SHORT signal. P_300 doesn't currently emit a SHORT class (Stage 6 Decision F is one-sided BUY/WATCH/PASS), but the signature is visible in the per-horizon stats table. Note these candidates for the trade journal — repeated AVOIDs that play out negatively are evidence for adding a SHORT class downstream.

### 4.4 — When the Decision Tree Disagrees with You

If your gut says one thing and the system says another, the chart wins (core principle from project instructions). Pipeline B is a quantitative second opinion, not a veto. Journal the disagreement and what happened — those are the highest-information observations for calibrating the system.

---

## 5. Sizing Reference (Read-Only — Defined Elsewhere)

Position sizing rules are NOT in P_300. They live in:

- `P_000_Account_Parameters_Current.md` — account balance, 1.5% risk per trade, three-gate sizing (risk / cash / concentration)
- `P_010_RiskConfig.json` — current market posture and risk mode (OFF / HALF / STANDARD / FULL / HOT)

P_300 emits a signal class and a volatility flag. You apply sizing using those two artifacts plus P_000 / P_010 rules. The mapping suggested in section 4 (full / 75% / 25-50%) is a starting heuristic; calibrate from actual trade outcomes.

Milestone 6 (Trade Management Module, parked) will eventually formalize this mapping. Until then, manual judgment using the above documents.

---

## 6. Common Failure Modes & Recovery

| Failure | Symptom | Recovery |
| :---- | :---- | :---- |
| Wrong filename | `vp_xlsx_reader` regex error on parse_live_file | Rename to exact `History Grid (<SYMBOL>).xlsx` format |
| Python interpreter resolution | `ImportError` on pandas/openpyxl/pydantic | M-016 — check `(Get-Command python).Source`, fix ISE profile prepend |
| LM Studio not loaded but `--no-narrator` not set | Pipeline waits 60s then renders `NARRATIVE: (unavailable)` | Re-run with `--no-narrator` if you don't need narration |
| Catalog empty / unhealthy | Pipeline error or zero matches | Run `python python\cli.py catalog-summary` in ISE; ingest patterns via Pipeline A if needed |
| Stage 7 ingest typo in filename | Cosmetic only (e.g., TTD's `20260818` capture date — see M-024) | Ignore; pipeline math unaffected |
| Pre-18:30 signal looks great | Anchor is yesterday; today is already next-bar | Re-run after 18:30 with today's bar in the window before committing |
| PowerShell stdout shows red text | Some library writing to stderr | M-011 / M-019 — usually cosmetic warnings, check whether signal still emitted cleanly |
| File output is UTF-16 LE when piped via `>` | M-019 extension — PowerShell redirection default | Use `python ... \| Out-File -Encoding utf8 audit.txt` if grep/diff is needed |

---

## 7. Post-Trade Capture (For Future Calibration)

After every trade triggered by Pipeline B, capture in a trade journal:

- **Pre-trade snapshot:** ticker, anchor_date, signal_class, chosen_horizon, vol_severity, top-5 ticker mix, sample win-rate at chosen horizon, mean_ret at chosen horizon, position size, stop placement
- **Override flag:** did you trade against the default action in section 4? If so, why?
- **Outcome:** entry price, exit price, exit reason (target / stop / time / discretionary), realized return, holding period in bars, max favorable excursion, max adverse excursion
- **System-vs-actual gap:** did the system's expected return (mean_ret at chosen_horizon) match realized? Within 1 std_ret? Outside it?

These observations are the input for the eventual M-028 catalog-grow-and-re-sweep and Milestone 6 sizing calibration. The trade journal is the bridge between system output and operator learning. Format and storage is your call (Excel, markdown, dedicated DB) — this runbook doesn't prescribe.

---

## 8. Calibration Markers (Things in This Doc That Will Change)

These are v1.0 starting heuristics, NOT settled:

- **BUY + MILD → 75% size** — pulled from P_010's HALF risk mode conceptually; calibrate from real outcomes
- **BUY + STRONG → treat as WATCH** — conservative default; may relax once you have evidence the STRONG flag mis-fires on apples-to-apples matches
- **WATCH re-evaluate cadence** — daily after 18:30; tighten or loosen based on observed signal evolution speeds
- **Override conditions for BUY + STRONG entry** — operator-judgment based; document patterns when they work / when they don't
- **PASS with negative z-scores → AVOID** — currently informal; promote to a formal SHORT class if AVOIDs prove consistent

Update this doc whenever a calibration changes. Bump version, add CHANGELOG below.

---

## Maintenance

- **Owner:** Anthony Zoppi
- **Update trigger:** any time a section-4 default changes from real-trade evidence, any time a section-3 mechanics change (CLI flags, file paths, catalog ops), any time a section-6 failure mode is encountered + resolved that isn't already listed

## Changelog

### 2026-05-20 v1.0
- Initial release. Per-candidate workflow framing locked. Decision tree built around signal_class × volatility_severity matrix from `report_writer.py` v1.3 output. 18:30 data freshness boundary called out explicitly. Sizing rules deferred to P_000 / P_010. Section 8 (Calibration Markers) makes the starting-heuristic nature of section 4 explicit.

---

**End of Evaluate Trade Runbook**
