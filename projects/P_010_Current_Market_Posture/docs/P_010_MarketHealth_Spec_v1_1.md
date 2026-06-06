# P_010 Market Health -- Distribution Day Tracker Spec

**File:** P_010_MarketHealth_Spec_v1_1.md
**Project:** P_010_Current_Market_Posture
**Version:** 1.1 (Open questions resolved -- ready for Phase 1 implementation)
**Date:** April 25, 2026
**Status:** All design decisions locked. Implementation can begin.

---

## CHANGES FROM v1.0

All 5 open questions in Section 10 of v1.0 are now resolved (see Section 10 below).
No other content changes -- decisions in Sections 3-8 remain locked.

---

## 1. Purpose

Add IBD-style distribution day and follow-through day tracking to the P_010 daily pipeline so every trade gets logged with two pieces of market-internal context that today's system is missing:

- **DistributionDayCount** -- accumulated institutional selling pressure
- **FollowThroughDay** -- whether a confirmed rally bottom signal exists and how recent

Three columns already sit empty in the locked 27-column tracker schema (`DistributionDayCount`, `FollowThroughDay`, `MarketDirection`). This spec populates the first two from a new computed JSON without changing existing logic.

---

## 2. Background

(Unchanged from v1.0 -- see original spec for full context. Key points: 4-5 distribution days in 25 days historically precedes major tops; breakout success drops from ~70% to ~40% in correction; risk_mode and dist count are complementary lenses, not duplicative.)

---

## 3. Design Decisions (Locked)

(Unchanged from v1.0)

- **3.1** MarketDirection column stays as risk_mode value
- **3.2** Phase 1 is data capture only -- no sizing impact
- **3.3** SPY and QQQ counted independently, max wins
- **3.4** 6:30 PM data timing is acceptable (IBD acts on prior close anyway)
- **3.5** Risk Config rules unchanged

---

## 4. Definitions

(Unchanged from v1.0)

- **Distribution Day:** Close[t] < Close[t-1] AND Volume[t] > Volume[t-1] AND |%Change| >= 0.2%
- **Stalling Day:** DEFERRED to Phase 2
- **Follow-Through Day:** Day 4-7 of rally attempt AND %Change >= 1.5% AND Volume[t] > Volume[t-1]
- **Reset Rules:** Rolling 25-day window AND 5% rally reset (either trigger applies independently)

---

## 5. Rally State Machine

(Unchanged from v1.0)

States: NO_RALLY -> RALLY_LOW_SET -> RALLY_ATTEMPT -> {FTD_CONFIRMED | NO_RALLY | STALE_RALLY}
FTD_CONFIRMED persists until distribution count reaches >= 4.

---

## 6. JSON Output Contract

(Unchanged from v1.0)

**File:** `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_MarketHealth.json`

Schema includes per-index dist counts, dist_dates list, rally_state, follow_through_day, ftd_age_days, market_phase, phase_reason. See v1.0 for full JSON example.

---

## 7. Market Phase Derivation

(Unchanged from v1.0)

Six phases keyed on `max_dist_count`, FTD age, and rally state. Most-restrictive phase wins.

---

## 8. INIT Integration

(Unchanged from v1.0)

INIT reads `P_010_MarketHealth.json` and adds one-line market phase banner.
Tracker columns `DistributionDayCount` and `FollowThroughDay` populated from JSON.
`MarketDirection` unchanged (still `risk_mode`).

---

## 9. File Plan (Phase 1 Implementation)

**Project root:**
`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\python\market_health\`

| # | File | Subfolder | ~Lines | Purpose |
|---|------|-----------|--------|---------|
| 1 | `config.py`            | `market_health\`  | 60  | VP Excel paths, thresholds, output JSON path |
| 2 | `schemas.py`           | `market_health\`  | 80  | Pydantic: VPDailyRow, IndexHealth, MarketHealthOutput |
| 3 | `distribution_day.py`  | `domain\`         | 100 | is_distribution_day, is_stalling_day, is_follow_through_candidate |
| 4 | `rally_state.py`       | `domain\`         | 120 | Rally state machine class + helpers |
| 5 | `market_phase.py`      | `domain\`         | 60  | Rule table -> phase derivation |
| 6 | `vp_reader.py`         | `infrastructure\` | 100 | Read SPY+QQQ rows from Excel, validate, parse |
| 7 | `health_writer.py`     | `infrastructure\` | 50  | Atomic JSON write with backup |
| 8 | `health_runner.py`     | `application\`    | 120 | Orchestration: read -> compute -> derive -> write |
| 9 | `cli.py`               | `market_health\`  | 80  | argparse: --date, --dry-run, --verbose, exit codes |
| 10| `launcher.bat`         | `market_health\`  | 30  | Activates p140, calls cli.py, logs to logs\market_health\ |

Total ~800 lines. All under 300-line cap. All functions under 50 lines.
Conda env: p140.
Trigger chain: append a line to `P_010_daily_posture.bat` calling `launcher.bat` after VP pull completes.

---

## 10. Open Questions -- ALL RESOLVED

| # | Question | Resolution |
|---|----------|------------|
| 1 | VP feed location and format | **Same files we already use:** `data\excel_exports\History Grid (SPY)_v3.xlsx` and `History Grid (QQQ)_v3.xlsx` -- xlsx with VP indicator columns |
| 2 | Date column format | **`datetime64[us]`** -- pandas `read_excel` parses natively, no transform needed |
| 3 | Distribution day reset rule | **Both** -- rolling 25-day window AND 5% rally reset |
| 4 | Include stalling day in Phase 1? | **Defer to Phase 2** -- needs calibration first |
| 5 | Index disagreement -- max or both confirm? | **Max count** -- standard IBD methodology, conservative |

### Schema details from VP Excel files (verified 2026-04-25)

Confirmed columns present (using exact pandas-read names):
- `Date` (datetime64)
- `Open\nPrice`, `High\nPrice`, `Low\nPrice`, `Close\nPrice` (float64)
- `Volume` (float64) -- present in file, not currently read by v5
- VP indicators: Short/Medium/Long Term Difference, Predicted High/Low/Range, etc.

**File quirk:** Row 0 is a label/garbage row (NaT date, mostly NaN, some text labels in object columns). Real data starts row 1. The existing v5 reader handles this with `if pd.isna(df.iloc[0]['Date'])`. `vp_reader.py` must replicate this skip logic.

---

## 11. Phase Roadmap

(Unchanged from v1.0)

- **Phase 1 (May 2026):** Data capture, JSON write, INIT banner, tracker columns. Zero impact on sizing/scoring/verdict.
- **Phase 2 (June 2026):** Add stalling days, backtest, calibrate. 30+ day baseline minimum before any sizing change.
- **Phase 3 (July 2026, conditional):** Sizing multiplier by phase. Verdict gate for breakouts in deteriorating tape.

---

## 12. Success Metrics

(Unchanged from v1.0)

Phase 1: JSON written daily, tracker populated, banner displayed, sanity-check vs manual IBD count for 5 days.
Phase 2 decision gate: keep/wire-up if signal predicts >= 10% win rate delta.

---

## 13. Today's Example Case

(Unchanged from v1.0 -- April 24 AMZN/AMAT case)

---

## 14. Save Location for This Spec Doc

`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\docs\P_010_MarketHealth_Spec_v1_1.md`

(v1.0 archived at same folder.)

---

## 15. Version History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-04-24 | Tony + Claude | Initial draft -- design decisions locked, file plan defined, 5 open questions |
| 1.1 | 2026-04-25 | Tony + Claude | All 5 open questions resolved. VP Excel schema verified. Row-0 garbage quirk documented. Ready for Phase 1 implementation. |

---

*END OF SPEC*
