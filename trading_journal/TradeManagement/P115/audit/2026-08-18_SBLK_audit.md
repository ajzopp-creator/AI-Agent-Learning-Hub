# SBLK Signal Audit Note -- 2026-08-18

**Source:** P_920 EOD scan, evaluated via P_115 core engine (STEP 1)
**LogEntry parse:** SBLK | Fund 2 | Anal 3 | Candle 2 | Setup 3 | STR 0 | PA -- | ASYM
**HybridTier:** Anal(3) + Fund(2) = 5 (below BUY threshold of 6)
**Verdict path:** AsymmetricSetup (Anal>=3, Fund>=2) -- matches chart's displayed ASYM verdict

**Fund Verification (stockanalysis.com, live pull 8/18/26):** ROE 11.68% (fail, <15%, 0pts),
Debt/Equity 0.47 -> Debt/Capital ~32.0% (pass, <60%, 15pts), FCF $287.04M positive (pass, 10pts).
Raw = 25pts -> base tier map 20-29 -> base Fund 2. 200-MA distance +27.2% (price above 200-SMA,
chart-labeled NORMAL) -> zero penalty. Recomputed adjustedFund = 2. Matches submitted Fund=2.
No flag.

**Post-Earnings Auto-Flag:** last reported 8/5/26 (Q2 EPS $1.21 actual vs $0.89 consensus,
beat). Today 8/18/26 = 9 trading sessions elapsed -- outside 3-session stabilization window.
No flag.

**Chart context:** Price $30.09, well above rising 200-SMA ($23.66, +27.2%, NORMAL zone, no
200-MA penalty). Daily bar 8/17/26 (O 29.05 H 30.18 L 29.00 C 30.09). Bull trend intact.
Regime Council: RANGE BOUND / Wait for Setup / WEAK / ABOVE AVG VOL, sumZZ -0.95 -- mixed/neutral
momentum backdrop, asymmetric setup relies on structure (PA Stop) not momentum confirmation.
Classified strategy=dip_buy (P_115 core mandate; ASYM is a reduced-confidence variant of the
same setup type, not a different one).

**Guideline levels (structural reference only, per P_400 architecture v1.3/1.4 -- P_115 does not
size):**
- guideline_stop: $27.06 (PA Stop, Structure label on chart -- Stop Derivation Rule v1.2)
- guideline_target: $38.79 (chart's T1/T2 Exit label, touched 4x -- first major resistance)

**ATR14 (chart):** 0.94
**Volume note:** chart's trailing unlabeled figure (1,387,510) used as day volume, distinct from
the chart's labeled VolumeAvg(20)=2,027,206 -- flagged to Tony as a chart-reading assumption.