# AGNC Signal Audit Note — 2026-07-24

**Source:** P_910 daily scan, evaluated via P_115 core engine (STEP 1)
**LogEntry parse:** AGNC | Fund 4 | Anal 2 | Candle 0 | Setup 2 | STR 0 | BUY
**HybridTier:** Anal(2) + Fund(4) = 6 -- meets BUY threshold

**Fund Verification (stockanalysis.com):** ROE 19.80% (pass, >15%), Debt/Cap ~88% (fail, >60% --
mortgage REIT, repo-financed leverage is the business model, not distress), FCF positive
(~$525M last quarter). 2 of 3 clear -- recomputed tier ~3 vs submitted 4, a 1-tier gap.
Inside tolerance (only >1-tier triggers hard stop).

**Post-Earnings check:** reported Mon 7/20/26 after close. Today (Fri 7/24) is the 4th trading
session since (Tue/Wed/Thu/Fri) -- just past the 3-session stabilization window. No auto-flag.

**Chart context:** Price $10.59, -0.7% below 200-SMA $10.66 (NORMAL zone, no penalty).
Pullback from recent swing high (~$11.45, 7/17 area) toward 200-SMA support -- classic
anticipatory dip pattern. Existing options position noted on chart (BULL ACTIVE, Days:3,
Strike 11.58, Delta 34.3%, P&L -4%) -- informational only, not part of this signal.
Classified strategy=dip_buy.

**Guideline levels (structural reference only, per P_400 architecture v2.0):**
- guideline_stop: $10.44 (PA Stop, Structure)
- guideline_target: $12.41 (T1 Exit, Tch:3)

**ATR14 (chart):** 0.23