# P_010 Market Health — Phase 2 Plan
**Version:** 1.1
**Created:** April 25, 2026
**Target window:** May 1 – June 30, 2026
**Spec reference:** docs\P_010_MarketHealth_Spec_v1_1.md

---

## Architectural Boundary (read this first)

**P_010 = sensors.** Measures the market. Writes JSON. Knows nothing about trades, sizing, or verdicts.

**P_115 / P_118 = actuators.** Read P_010 JSON. Decide what to do with it.

This boundary governs the entire Phase 2 / Phase 3 split:

| Concern | Lives in |
|---|---|
| Distribution day count | P_010 |
| Stalling day count | P_010 |
| Follow-through day detection | P_010 |
| Market phase classification | P_010 |
| Backtest of phase signal vs forward index returns | P_010 |
| Trade-bucket analysis (research) | P_010 |
| Sizing multiplier by phase | **P_115 / P_118** |
| Verdict gate based on phase | **P_115 / P_118** |

**All Phase 2 work is measurement and research — it stays in P_010.** Phase 3 (when/if green-lit) is sizing logic that gets written into P_115 and P_118 directly. P_010's role in Phase 3 is unchanged: keep publishing `market_phase` in JSON. The strategies read it.

---

## Goal

Determine whether the `market_phase` signal predicts a meaningful win-rate edge in P_115 / P_118 trades. The Phase 2 → Phase 3 decision is binary and measurable.

**Decision gate:** ≥10 percentage-point win-rate delta between best and worst phase buckets in real trade history.

- ≥10pp delta → green-light Phase 3 (sizing multiplier work begins in P_115 / P_118)
- <10pp delta → ship Phase 2 as monitor-only; Phase 3 shelved

---

## Timeline

| Block | Dates | Work | Project |
|---|---|---|---|
| A | May 1 – May 31 | Passive baseline accumulation (22 trading days) | P_010 |
| B | Jun 1 – Jun 14 | Stalling day implementation | P_010 |
| C | Jun 15 – Jun 21 | Backtest harness | P_010 |
| D | Jun 22 – Jun 28 | Trade-bucketed analysis (decision gate) | P_010 |
| E | Jun 29 – Jun 30 | Go / no-go decision + spec v1.2 | P_010 |
| **F** | **Jul 1+** | **Sizing multiplier implementation (conditional)** | **P_115 / P_118** |

---

## Workstream A — Baseline accumulation (P_010)

**Purpose:** Capture 22 trading days of `P_010_MarketHealth.json` so Workstream D has real history to bucket trades against.

**Tasks:**
1. Modify launcher to copy each day's JSON to `data\snapshots\market_health\YYYYMMDD.json` after write (~10 lines added to launcher.py).
2. Verify Task Scheduler keeps firing the launcher daily.
3. Spot-check 5 random days against IBD Big Picture distribution count.

**Measurable objectives:**
- 22 daily archives in `data\snapshots\market_health\` by June 1
- IBD-vs-tracker dist count agreement within ±1 on all 5 spot-check days
- Zero days with empty or corrupted JSON

**Effort:** ~30 minutes of work time. Wall-clock time is the calendar.

---

## Workstream B — Stalling day implementation (P_010)

**Purpose:** Replace the Phase 1 stub `is_stalling_day()` with the real IBD definition.

**Why this is P_010, not P_115:** A stalling day is a property of the index, not the trade. P_118 will need it too. Putting it in P_115 forces duplication.

**Tasks:**
1. **Lock definition (1 day).** IBD stalling day = close > prior close AND volume[t] > volume[t-1] AND %gain ≤ 50% of prior up-day's gain AND close in lower half of day's range. Validate by hand against 10 known stalling days from 2025 SPY data.
2. **Implement function** (~30 lines) in `python\market_health\domain\distribution_day.py`. Pure function, no IO. Replaces existing stub.
3. **Unit tests** (~50 lines) in `python\market_health\tests\test_stalling.py`. Cover 10 positives and 5 negatives.
4. **Update `count_distribution_days()`** to fold stalling days into the dist count. Phase logic uses combined count.
5. **Re-run launcher on 30 days of VP data**, validate counts vs manual count.

**Measurable objectives:**
- All 15 unit tests pass
- Combined dist+stalling count reconciles to manual count within ±1 across 30 sample days
- No launcher exit-code changes for 5 consecutive production days post-deploy
- File line counts stay under 300 (split if approaching 250)

**Effort:** 2–3 days. Riskiest piece is the definition lock.

---

## Workstream C — Backtest harness (P_010)

**Purpose:** Measure whether the phase signal predicts forward returns on the indices themselves. Sanity check before the trade-bucket analysis.

**Why this is P_010, not P_115:** Backtest is on SPY/QQQ index returns, not on strategy trades. Pure market-state research.

**Tasks:**
1. Build `python\market_health\backtest\historical_phases.py` (~120 lines). Walks 12 months of VP data, computes phase for each day.
2. Build `python\market_health\backtest\forward_returns.py` (~80 lines). Joins 1/5/10/20-day forward SPY returns.
3. Build `python\market_health\backtest\report_generator.py` (~80 lines). Writes `outputs\phase_calibration_report.md`.
4. Run on May 2025 – April 2026 data (~250 trading days).

**Measurable objectives:**
- Report covers ≥250 trading days
- Phase distribution table: % of days in each of the 6 phases
- Forward-return stats per phase across 4 horizons (mean, median, win rate)
- Visible separation between CONFIRMED_UPTREND and CORRECTION buckets (eyeball check, not pass/fail)

**Effort:** 5–7 days. Bulk of Phase 2 coding.

---

## Workstream D — Trade-bucketed analysis (P_010, the actual gate)

**Purpose:** Forward returns on indices are suggestive. Win rate on real P_115/P_118 trades is what governs the Phase 3 decision.

**Why this is P_010, not P_115:** This is research, not strategy logic. Output is a report, not a sizing change. P_010 owns the analysis because the question is "does the P_010 signal have predictive value?" — that's a P_010 self-evaluation. The trade data is read-only input from P_020.

**Tasks:**
1. Pull P_020 trade database (already exists, no new infra).
2. For each closed trade, look up `market_phase` on entry date from the Workstream A archive.
3. Bucket trades by phase. Compute win rate, average R, median R per bucket.
4. Compare CONFIRMED_UPTREND bucket vs CORRECTION / DETERIORATING bucket.
5. Write `outputs\trade_bucket_report.md`.

**Measurable objectives:**
- ≥50 closed trades analyzed (target: ≥100)
- Win rate computed per phase bucket with sample size shown
- Win-rate delta between best and worst bucket reported as a single number
- Caveat flag if any bucket has fewer than 10 trades

**Decision gate (binary):**
- Best bucket WR − worst bucket WR ≥ 10pp → green light Phase 3
- Delta < 10pp → Phase 3 shelved, Phase 2 ships as monitor-only banner

**Effort:** 2–3 days.

---

## Workstream E — Decision and spec v1.2 (P_010)

**Tasks:**
1. Write `docs\P_010_MarketHealth_Phase2_Decision_2026-06-30.md` summarizing both report findings and the go/no-go call.
2. Write `docs\P_010_MarketHealth_Spec_v1_2.md`. Either path produces this doc:
   - Green light: locks Phase 1+2 as final P_010 scope. Hands off Phase 3 sizing work to P_115 / P_118 with a clear interface contract (which JSON fields to read, what they mean, semver guarantees).
   - Shelved: locks Phase 1+2 as final P_010 scope. Documents why Phase 3 was shelved.

**Measurable objectives:**
- Decision logged with explicit numbers from Workstream D
- Spec v1.2 written either way before July 1
- If green-lit: interface contract explicitly defines what P_115 and P_118 will consume

---

## Workstream F — Sizing multiplier (P_115 / P_118, conditional)

**This is Phase 3, listed here only to make the handoff explicit.**

**Trigger:** Workstream D decision gate green-lights Phase 3.

**Project:** P_115 first, then P_118 (both consume the same `market_phase` field).

**P_010's role:** Zero code changes. Continue publishing `market_phase` in `P_010_MarketHealth.json`. Treat the JSON schema as a stable interface — any breaking change requires coordinated P_115 / P_118 update.

**P_115 / P_118 work (out of scope for this plan):**
- Read `P_010_MarketHealth.json` alongside existing `P_010_RiskConfig.json`
- Apply phase-based sizing multiplier per the calibration numbers from Workstream D
- Optional verdict gate: block breakouts in DETERIORATING / CORRECTION phase
- Each strategy owns its own implementation

This split keeps P_010 doing one thing well (measure the market) and lets each strategy decide its own response.

---

## Risks

1. **Insufficient trade sample.** P_115/P_118 may not have 50 closed trades during the analysis window, especially in low-frequency phase buckets like CORRECTION. Mitigation: extend window backward, or accept lower confidence with documented caveat.
2. **Stalling day definition disputes.** IBD's exact rule isn't fully published. If manual reconciliation fails, document the chosen rule, ship it, refine later.
3. **Interface drift between P_010 and strategies.** If Phase 3 ships, any future change to `P_010_MarketHealth.json` schema risks breaking P_115 / P_118. Mitigation: lock the schema in spec v1.2 and treat additions as non-breaking, removals/renames as breaking.
4. **Backtest survivorship not applicable** to SPY/QQQ but Phase 3 sizing would apply to all trades regardless of underlying. Flag as known tail risk in the decision memo.

---

## Out of scope for Phase 2

- Sizing logic changes — that's P_115 / P_118 in Phase 3
- Verdict gate changes — that's P_115 / P_118 in Phase 3
- VXX integration into `market_phase` (separate enhancement, not on roadmap)
- Multi-timeframe (Phase 3+ if at all)

---

## Definition of Done for Phase 2

All five items must be true:

1. 22+ daily JSON archives in `data\snapshots\market_health\`
2. Stalling day function shipped and reconciling to manual counts within ±1
3. Backtest report exists with 12 months of phase classifications and forward returns
4. Trade bucket report exists with explicit win-rate delta number
5. Decision memo and spec v1.2 saved to `docs\` — including interface contract for P_115 / P_118 if green-lit

---

## Version History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-04-25 | Initial plan written same day Phase 1 shipped |
| 1.1 | 2026-04-25 | Added explicit P_010 vs P_115/P_118 ownership boundary at top. Added Workstream F to make Phase 3 handoff visible. Annotated each workstream with project ownership. |
