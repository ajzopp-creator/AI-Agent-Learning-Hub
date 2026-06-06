# P_010 Market Health — Distribution Day Tracker Spec

**File:** P_010_MarketHealth_Spec_v1_0.md
**Project:** P_010_Current_Market_Posture
**Version:** 1.0 (Draft)
**Date:** April 24, 2026
**Status:** Awaiting answers to 5 open questions before implementation

---

## 1. Purpose

Add IBD-style distribution day and follow-through day tracking to the P_010 daily pipeline so every trade gets logged with two pieces of market-internal context that today's system is missing:

- **DistributionDayCount** — how much institutional selling pressure has accumulated
- **FollowThroughDay** — whether a confirmed rally bottom signal exists and how recent

Three columns already sit empty in the locked 27-column tracker schema (`DistributionDayCount`, `FollowThroughDay`, `MarketDirection`). This spec populates the first two from a new computed JSON without changing existing logic.

---

## 2. Background

### Why this matters

- 4–5 distribution days inside a 25-day window historically precedes major market tops
- Breakout success rate drops from ~70% (rally) to ~40% (correction)
- Follow-through days are the only reliable bottom signal — no major bottom occurs without one
- Today's trade decisions on AMZN and AMAT (both BUY signals into a tape with `avg_posture` 14.03 / `risk_mode` FULL) lacked this context. Bunched targets in a "no-distribution" tape ≠ bunched targets in a "4 distribution days in 3 weeks" tape

### What's already in place

- VantagePoint pulls SPY and QQQ daily OHLCV at 6:30 PM
- VP feed columns include: Date, Open, High, Low, Close, Volume — all required inputs
- `P_010_RiskConfig.json` is read at every INIT and populates `MarketDirection` column with `risk_mode` value
- `risk_mode` (quant momentum from `avg_posture`) is **complementary** to distribution days (institutional selling pressure), not duplicative

---

## 3. Design Decisions (Locked)

### 3.1 MarketDirection column stays as-is

**Decision:** `MarketDirection` continues to carry the `risk_mode` value (FULL / STANDARD / HOT / OFF / CORRECTION). No schema change.

**Reasoning:** Memory rule says `MarketDirection = risk_mode`. Original roadmap proposed Rally/Correction/Neutral but that conflicts. The two empty columns (`DistributionDayCount` and `FollowThroughDay`) carry the IBD signal independently. Both lenses logged on every row.

### 3.2 No sizing impact in Phase 1

**Decision:** Phase 1 is data capture only. No position sizing multiplier. No scoring change. No verdict adjustment.

**Reasoning:** Validation rule — log first, measure for 30+ days, then decide if the signal predicts breakout failure before wiring it into sizing logic.

### 3.3 Both indexes counted independently, max wins

**Decision:** SPY and QQQ each get their own distribution day count. The reported `max_dist_count` = `max(spy_count, qqq_count)`.

**Reasoning:** Standard IBD methodology. More conservative — when leadership rotates between indexes, distribution can hide in one while the other looks clean.

### 3.4 6:30 PM data timing is a feature, not a constraint

**Decision:** Compute runs after the existing VP pull completes. JSON sits ready for the next morning's INIT.

**Reasoning:** IBD methodology acts on prior-close signals anyway. No intraday refresh needed. No new data feed required.

### 3.5 Memory rule preservation

**Decision:** Risk Config rules unchanged. `risk_mode` remains authoritative for sizing. Distribution day count is informational only in Phase 1.

---

## 4. Definitions

### 4.1 Distribution Day

```
Distribution Day = Close[t] < Close[t-1] AND Volume[t] > Volume[t-1] AND |%Change| ≥ 0.2%
```

The 0.2% threshold filters noise-level closes that technically qualify but carry no meaning.

### 4.2 Stalling Day (Phase 2 — DEFERRED)

```
Stalling Day = Volume[t] > Volume[t-1] AND |%Change| < 0.2% AND (Close-Low)/(High-Low) < 0.5
```

Captures churn / no-progress days where the index closes in the lower half of its range on heavy volume. Deferred to Phase 2 — needs calibration data before going live.

### 4.3 Follow-Through Day (FTD)

```
FTD = Day 4-7 of an active rally attempt
      AND %Change ≥ 1.5%
      AND Volume[t] > Volume[t-1]
```

Requires state tracking — see section 5.

### 4.4 Reset Rules

- **Rolling window:** Days older than 25 trading days roll off
- **5% rally reset:** If the index closes ≥5% above the lowest close in the current window, distribution count resets to zero (clean slate confirmed)
- **Either trigger applies independently**

---

## 5. Rally State Machine (FTD Detection)

```
STATE: NO_RALLY
  └── Index hits new 25-day low → STATE: RALLY_LOW_SET, day_counter = 0

STATE: RALLY_LOW_SET
  └── Index closes higher than rally_low close → STATE: RALLY_ATTEMPT, day_counter = 1
  └── Index closes lower → update rally_low, day_counter stays 0

STATE: RALLY_ATTEMPT
  └── Day 4-7 AND %Change ≥ 1.5% AND Vol[t] > Vol[t-1] → STATE: FTD_CONFIRMED
  └── Index closes below rally_low → STATE: NO_RALLY (failed attempt)
  └── Day > 10 without FTD → STATE: STALE_RALLY (count but flag)

STATE: FTD_CONFIRMED
  └── Persists until distribution count reaches ≥4 → STATE: NO_RALLY (FTD invalidated)
```

State persists in the JSON between runs.

---

## 6. JSON Output Contract

**File:** `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_MarketHealth.json`

**Schema:**

```json
{
  "as_of": "2026-04-23",
  "computed_at": "2026-04-23T18:42:11",
  "spy": {
    "dist_count_25d": 2,
    "stalling_count_25d": 0,
    "dist_dates": ["2026-04-15", "2026-04-21"],
    "last_close": 568.42,
    "last_volume": 78421300
  },
  "qqq": {
    "dist_count_25d": 1,
    "stalling_count_25d": 0,
    "dist_dates": ["2026-04-15"],
    "last_close": 491.18,
    "last_volume": 41872100
  },
  "max_dist_count": 2,
  "rally_state": "FTD_CONFIRMED",
  "rally_low_date": "2026-03-04",
  "rally_low_close": 542.10,
  "rally_day_count": null,
  "follow_through_day": "2026-03-12",
  "ftd_age_days": 30,
  "market_phase": "Confirmed Uptrend",
  "phase_reason": "FTD active within 30 days, max_dist_count ≤ 2"
}
```

---

## 7. Market Phase Derivation

| Condition | Phase | INIT Banner |
|-----------|-------|-------------|
| FTD active (≤30 days old) AND `max_dist_count` ≤ 2 | Confirmed Uptrend | 🟢 |
| `max_dist_count` = 3 | Uptrend Under Pressure | 🟡 |
| `max_dist_count` = 4 | Distribution Cluster Warning | 🟠 |
| `max_dist_count` ≥ 5 OR major index breaks 50-day MA | Market in Correction | 🔴 |
| Rally attempt active, no FTD yet | Rally Attempt | ⚪ |
| FTD age > 30 days AND `max_dist_count` 0-2 | Aging Uptrend | 🟢 |

Single most-restrictive phase wins (e.g., `max_dist_count = 5` always shows Correction even if FTD is recent).

---

## 8. INIT Integration

**Current INIT reads:**
- `P_000_Account_Parameters_Current.md`
- `P_010_RiskConfig.json`

**New INIT step:**
- Add read of `P_010_MarketHealth.json`
- Add one-line market phase banner to session dashboard:
  ```
  Market Phase: 🟢 Confirmed Uptrend | SPY dist 2/25d | QQQ dist 1/25d | FTD 3/12 (30d ago)
  ```

**Tracker logging:**
- `DistributionDayCount` ← `max_dist_count` from JSON
- `FollowThroughDay` ← `Yes` if `ftd_age_days` ≤ 30 else `No`
- `MarketDirection` ← unchanged (still `risk_mode`)
- Optional Comments addition: `Market Phase: <phase>` when phase ≠ Confirmed Uptrend

---

## 9. File Plan (Phase 1 Implementation)

**Project root:**
`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\python\market_health\`

| # | File | Subfolder | ~Lines | Purpose |
|---|------|-----------|--------|---------|
| 1 | `config.py` | `market_health\` | 60 | VP feed paths, thresholds (0.2% noise filter, 25-day window, FTD day 4-7), output JSON path |
| 2 | `schemas.py` | `market_health\` | 80 | Pydantic: `VPDailyRow`, `IndexHealth`, `MarketHealthOutput` |
| 3 | `distribution_day.py` | `domain\` | 100 | Pure logic: `is_distribution_day()`, `is_stalling_day()`, `is_follow_through_candidate()` |
| 4 | `rally_state.py` | `domain\` | 120 | Rally state machine class + helpers |
| 5 | `market_phase.py` | `domain\` | 60 | Rule table → phase derivation |
| 6 | `vp_reader.py` | `infrastructure\` | 100 | Read SPY+QQQ rows from VP feed, validate, parse to schemas |
| 7 | `health_writer.py` | `infrastructure\` | 50 | Atomic JSON write with backup |
| 8 | `health_runner.py` | `application\` | 120 | Orchestration: read → compute per index → derive phase → write |
| 9 | `cli.py` | `market_health\` | 80 | argparse: `--date`, `--dry-run`, `--verbose`, exit codes |
| 10 | `launcher.bat` | `market_health\` | 30 | Activates p140 env, calls cli.py, logs to `logs\market_health\` |

**Total:** ~800 lines across 10 files. All under 300-line cap. All functions under 50 lines.

**Conda env:** `p140` (`C:\Users\Trader\.conda\envs\p140\python.exe`)

**Trigger chain:** Append a line to existing `P_010_daily_posture.bat` calling `launcher.bat` after the VP pull completes (post-6:30 PM).

---

## 10. Open Questions (Must Resolve Before Coding)

| # | Question | My Recommendation |
|---|----------|-------------------|
| 1 | VP feed file location and format — one CSV per index, or combined? What folder? | _Need answer from Tony_ |
| 2 | Date column format in VP feed — `M/D/YYYY`, `YYYY-MM-DD`, Excel serial? | _Need answer from Tony_ |
| 3 | Distribution day reset rule — rolling 25-day, or 25-day AND 5% rally reset? | **Both** — rolling window AND 5% reset |
| 4 | Include stalling day in Phase 1? | **Defer to Phase 2** — needs calibration first |
| 5 | Index disagreement — max count or require both to confirm? | **Max count** — IBD methodology, conservative |

---

## 11. Phase Roadmap

### Phase 1 — Data Capture (Target: May 2026)
- Compute and log distribution / FTD per index daily
- Write `P_010_MarketHealth.json` after VP pull
- INIT reads and reports market phase
- Tracker columns populated automatically
- **Zero impact on scoring, sizing, or verdict logic**

### Phase 2 — Calibration & Stalling Days (Target: June 2026)
- Add stalling day detection
- Backtest against logged trades — does `max_dist_count` predict breakout failure?
- Calibrate phase thresholds against actual win rates
- 30+ day baseline minimum before any sizing change

### Phase 3 — Active Risk Adjustment (Target: July 2026, conditional on Phase 2 results)
- Sizing multiplier by phase: Confirmed Uptrend 1.0x / Under Pressure 0.75x / Cluster Warning 0.50x / Correction 0.25x or simulation-only
- Verdict gate: BUY signals in Cluster Warning or Correction require explicit override
- Documented in updated `P_010_System_Documentation_v3.md`

---

## 12. Success Metrics

**Phase 1 (30-day baseline):**
- ✅ JSON written successfully every trading day
- ✅ Zero column misalignment in tracker
- ✅ INIT banner displays correctly
- ✅ Distribution day counts reconcile with manual IBD verification (sanity check 5 days)

**Phase 2 (post 30-day):**
- Does `max_dist_count` ≥ 3 predict breakout failure? (target: 60%+ correlation)
- Does FTD presence improve breakout success? (target: 10%+ delta)
- Does phase signal flag at least one near-top before drawdown?

**Decision gate end of Phase 2:**
- KEEP and proceed to Phase 3 if signal predicts ≥10% win rate delta
- KEEP without sizing wire-up if signal is informative but not predictive
- DROP if signal is noise

---

## 13. Today's Example Case

**Date:** April 24, 2026
**Trades evaluated:** AMZN, AMAT (both Eddie Z BUY signals)
**Current context:** `risk_mode` FULL, `avg_posture` 14.03 (deep HOT)
**Missing context:** No distribution day count

Both trades held due to bunched R:R targets. With this enhancement:
- If `max_dist_count` = 0–2: bunched targets in a clean tape — current decision (hold) reasonable, alternatives (wait for pullback) have less urgency
- If `max_dist_count` = 3–4: bunched targets in a deteriorating tape — current decision (hold) strongly correct, breakouts likely to fail
- If FTD = recent: bunched targets early in confirmed rally — alternative entry (wait for second-stage breakout) has higher conviction

This is exactly the gap the tracker fills.

---

## 14. Save Location for This Spec Doc

`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\docs\P_010_MarketHealth_Spec_v1_0.md`

---

## 15. Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-04-24 | Tony + Claude | Initial draft — design decisions locked, file plan defined, awaiting answers to 5 open questions |

---

*END OF SPEC*
