# P_400 Trade Log & Simulation Notes

**Purpose:** Running record of P_400 Council reviews, sizing decisions, and any gate overrides for trades submitted through the P_400 Trade Management System. Append new entries at the bottom, most-recent-last.

**Maintained By:** Anthony Zoppi
**Format:** One entry per trade decision/override, chronological.

---

## 2026-09-05 — EVERPURE (P) 105 Call, exp 09/18/26 — Gate 1 Override

```
=== P_400 OVERRIDE LOG ===
Ticket:            EVERPURE (P), 105 Call, exp 09/18/26
Order Structure:    BUY +3 P 100 18 SEP 26 105 CALL @2.50 LMT [TO OPEN]
                    OCO exits:
                      SELL -2 contracts MKT GTC, TRG when mark >= $112.10 (Take-Profit Target, partial)
                      SELL -3 contracts MKT GTC, TRG when mark <= $93.00 (Stop, full exit)
Account:            10606348SCHW (AJZ Strategies LLC)

Gate Violated:      Gate 1 — Risk-Based Sizing
Approved Size:      2 contracts (FULL mode, Risk Capital $410.34 ÷ $1.80/contract)
Actual Size:        3 contracts (as submitted on live order ticket)
Overshoot:
  Decay-adjusted model ($1.80/contract): Risk = $540.00 vs $410.34 budget → +31.6%
  Worst-case model ($2.50/contract, full premium): Risk = $750.00 vs $410.34 budget → +82.8%

Account Snapshot (at time of review):
  Net Liq:                      $27,355.85
  Option Buying Power:          $16,140.32
  Available Funds For Trading:  $16,140.32
  Cash Balance:                 $3,144.75
  Cash & Sweep Vehicle:         $1,144.75
  Intraday Buying Power:        $81,573.12 (margin — not used for sizing basis)

Risk Mode at Time:  FULL (P_010_RiskConfig.json, timestamp 2026-09-05T06:48:09)
  spy_posture: 1.835236 | qqq_posture: 1.456329 | avg_posture: 1.645782
  vxx_signal: NEUTRAL (stable/flat volatility, no directional signal)
  Note: avg_posture exceeds the 1.08 HOT-mode threshold referenced in P_400 docs, but the
  risk_mode field explicitly reads "FULL" and is treated as authoritative per standing rule.

Other Gates:        Gate 2 (cash) and Gate 3 (concentration) both clear at 3 contracts — not violated
                      Gate 2 (conservative, Cash Balance $3,144.75 ÷ $245): 12 contracts
                      Gate 2 (Available Funds $16,140.32 ÷ $245, margin — flagged): 65 contracts
                      Gate 3 (Concentration $1,367.79 ÷ $245): 5 contracts

R:R Check:          PASS — using intended entry range (99.1–99.9):
                      ~2.0:1 to Take-Profit Target ($112.10)
                      ~3.3:1 to Primary Target ($119.10)
                      Note: live quote at ticket time (Last 99.51 / Bid 101.00 / Ask 101.49) was at/above
                      the top of intended Entry Range — R:R degrades if filled above $99.9.

Macro/Vol Backdrop: VXX neutral/stable, avg_posture elevated but risk_mode field authoritative at FULL

Authorization:      Manual override by Tony (account owner), issued directly in P_400 session
Justification:      Explicit instruction to hold size at 3 contracts despite Gate 1 cap; R:R and
                    macro/tape checks all pass — only the risk-based position-size gate is overridden.
Behavioral Judge Note: Override issued deliberately and in real time, not as a reactive/emotional
                    adjustment after entry — consistent with override-discipline requirement.

Final Council Status: APPROVED (with logged override)
```

---
