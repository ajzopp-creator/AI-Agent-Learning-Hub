# MANUAL PENDING RECORD -- NOT A SCHEMA-VALIDATED P400 VAULT RECORD

**This file is a stopgap.** It exists because WO-P400-E3.004 (scope item 5,
opened 2026-06-29) found there is no CLI-wired options spec command and no
options-aware fields in `P400Record` / `obsidian_writers` write path. The
schema has no fields for order_id, contracts, strike, expiration, premium,
or delta -- forcing this trade's data into the stock-shaped fields
(entry_price/stop_price/target_1/position_size) would silently misrepresent
option premium as stock share price. Claude declined to do that.

**Action required when WO-P400-E3.004 ships:** migrate this trade into a
real P400Record via the corrected write path, then delete this file.

---

## Trade Detail

- **Symbol:** ADBE
- **Asset class:** Option (single-leg call)
- **Order ID (Schwab):** 5362890896
- **Contract:** ADBE 215C 17JUL26 (strike $215.00, exp 2026-07-17)
- **Council verdict:** APPROVED_BY_OVERRIDE
  - Override phrase given verbatim by Tony: "OVERRIDE BLOCK ON ADBE -- I ACCEPT RESPONSIBILITY"
  - Override reason: option sized to 0 contracts under Chart-Based gate math
    (risk_per_contract $384.00 vs HALF-posture budget $367.53 at evaluation
    time; posture was OFF, budget $245.02, at original 205C evaluation).
    Tony's standing rule this session: override if risk_per_contract < $500.
- **Contracts:** 1
- **Entry premium (paid):** $4.00 (ask, limit)
- **Defined max loss:** $400.00 (premium paid -- the only real risk cap on a long call)
- **Delta-translated target (informational only):** ~$27.38 (off stock T1 $275.44;
  static estimate, not a live re-check)
- **Stop / exit mechanism:** MANUAL -- delta-translated stop computed to $0.01
  (degenerate). Per P_000 Options Rule, management trigger is underlying STOCK
  price, not option Mark. Exit ADBE 215C manually if ADBE stock trades through
  $192.23 (the original P_300 packet's guideline_stop). No resting option stop
  order placed.
- **Underlying at evaluation:** $204.815 (live, TOS, Tony-supplied screenshot)
- **Replaces:** stock bracket order for ADBE (3-5 shares depending on posture
  snapshot at evaluation time) -- stock order was NOT submitted; Tony chose
  override-into-option as a full replacement, not an addition.
- **Posture at override decision:** HALF (intraday upgrade from morning OFF;
  P_010_RiskConfig.json intraday_signal=UPGRADE, "Market stronger than
  predicted, prices above PRANGE")
- **Signal origin:** P_300 pattern-analog BUY, 2026-06-26_ADBE.md,
  signal_id P300-2026-06-26-ADBE-001, 75% WR / 20 matches at h=5
- **Date/time logged:** 2026-06-29

## Lifecycle Log

- 2026-06-29: SUBMITTED. Order ID 5362890896 reported by Tony. Logged here
  pending WO-P400-E3.004 (no schema-validated write path exists for this
  trade type as of this date).