# EXPD Signal Audit — 2026-09-11

**Batch:** P_118 STEP 1 (Eddie Z Breakouts), SignalSource=P_118 per batch header
**Chart source:** P_115_BuyTheDipChart_V16 LogEntry: EXPD | 4 | 3 | 2 | 3 | 0 | - | BUY
**Diagnostics:** Fund=4, Anal=3, Candle=2, Setup=3, STR=0
**HybridTier:** 3 + 4 = 7 (>=6, BUY confirmed)
**PatternType (chart read):** Flat Base — tight horizontal range near recent highs, RANGE_BOUND/LOW VOL/Wait-for-Setup flags active on D_200_RegimeCounsel_V10, no cup depth or W-shape visible
**Entry (submitted):** 191.82
**PA Stop (chart, Structure):** 183.93
**T1 Exit (chart):** 247.48 (Tch:11)
**T2 Exit (chart):** 247.48 (Tch:7)
**ATR:** 3.64
**200-MA:** +19.8% (NORMAL, no penalty)
**Close at signal:** 191.27
**VolumeAvg(20):** 127,499

**Fund Verification (V111, mandatory P_118 BUY, Fund>=2):**
- ROE: 26-37% across sources checked (well above 15% threshold)
- Debt/Cap: ~20% (well under 60% threshold)
- FCF: positive (~$900M+ TTM)
- Recomputed tier: consistent with submitted Fund=4, within 1 tier — verified, proceed

**Result:** Fund verification passed. Signal emitted to P_400 via cli.py, signal_source=P_115 (packet convention, regardless of P_118 tracker origin).
