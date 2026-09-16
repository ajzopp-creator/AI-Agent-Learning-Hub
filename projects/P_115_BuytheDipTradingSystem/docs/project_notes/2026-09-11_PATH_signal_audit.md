# PATH Signal Audit — 2026-09-11

**Batch:** P_115 STEPS 1-2, explicit SOURCE:P_910 tag (scan-sourced candidate, P_115 engine scores it)
**Chart source:** P_115_BuyTheDipChart_V16 LogEntry: PATH | 4 | 3 | 2 | 3 | -2 | - | BUY
**Diagnostics:** Fund=4, Anal=3, Candle=2, Setup=3, STR=-2
**HybridTier:** 3 + 4 = 7 (>=6, BUY confirmed). STR=-2 does not trigger Cause A auto-reject (requires Fund=0, and Fund=4 here).
**Entry (submitted):** 13.93
**PA Stop (chart, Structure):** 13.15
**T1 Exit (chart):** 15.40 (Tch:4)
**T2 Exit (chart):** 16.88 (Tch:4)
**ATR:** 0.98
**200-MA:** Price $13.92 above 200-SMA $12.90 (+8%, NORMAL, no penalty). Note: separate top-overlay study (D_130_BounceTrade_OIL_V23) shows Daily/4H Downtrend at the same time -- mixed context, flagged to Tony, confirmed no open/active position exists (Tony confirmed "nothing on PATH" 2026-09-11).
**Close at signal:** 13.93
**VolumeAvg(20):** 8,008,719

**Fund Verification (V111, mandatory P_115 BUY, Fund>=2):**
- ROE: ~18% (most recent 10-Q, Q1'26 per opencapital.sh/SEC filing) -- above 15% threshold
- Debt/Cap: ~3-4% (well under 60% threshold)
- FCF: positive (~$129M TTM)
- Recomputed tier: consistent with submitted Fund=4, within 1 tier -- verified, proceed

**Result:** Fund verification passed. Tony confirmed no existing position on PATH before authorizing emission. Signal emitted to P_400 via cli.py, signal_source=P_115 (packet convention, regardless of P_910 tracker origin).
