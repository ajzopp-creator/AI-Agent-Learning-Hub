# SBLK Signal Audit Note — 2026-07-24

**Source:** P_920 EOD scan, evaluated via P_115 core engine (STEP 1)
**LogEntry parse:** SBLK | Fund 2 | Anal 3 | Candle 2 | Setup 3 | STR 0 | ASYM
**HybridTier:** Anal(3) + Fund(2) = 5 (below BUY threshold of 6)
**Verdict path:** AsymmetricSetup (Anal>=3, Fund>=2) — matches chart's displayed ASYM verdict

**Fund Verification (stockanalysis.com):** ROE 3.41% (fail, <15%), Debt/Cap ~33.3% (pass, <60%),
FCF $211.95M positive (pass). 2 of 3 criteria clear — matches submitted Fund=2, no tier-gap flag.

**Post-Earnings Auto-Flag:** last reported Q1 2026 on 5/20/26; next report ~8/5/26 — outside the
3-session stabilization window. No flag.

**Chart context:** Price $28.14, well above rising 200-SMA ($22.79, +23.4%, NORMAL zone, no
200-MA penalty). Multiple "Bull Signal (Rise)" markers (5/19, 6/19, 6/30, 7/17) across an
established uptrend — repeated shallow-pullback-and-bounce behavior rather than a single deep
anticipated dip. Classified strategy=dip_buy (P_115 core mandate; ASYM is a reduced-confidence
variant of the same setup type, not a different one).

**Guideline levels (structural reference only, per P_400 architecture v2.0 — P_115 does not size):**
- guideline_stop: $24.77 (PA Stop, Structure label on chart — Stop Derivation Rule v1.2)
- guideline_target: $35.26 (chart's first major resistance / T1 Exit label)

**ATR14 (chart):** 0.85