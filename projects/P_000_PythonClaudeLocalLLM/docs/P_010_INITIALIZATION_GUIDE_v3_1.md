# P_010 INITIALIZATION GUIDE v3.1

**Project:** P_010 Current Market Posture  
**Version:** 3.1  
**Updated:** 2026-06-04  
**Type:** Daily workflow guide (batch + governance)

---

## DAILY INITIALIZATION SEQUENCE

### Pre-Market (Before 9:30 AM)

**STEP 0.5: Work Order Review**

Query shared work order ledger at `C:\Users\Trader\AI-Agent-Learning-Hub\04-Shared-Resources\work_orders\`:
- **Owner=P_010, status not CLOSED** → Display; **HALT** if action required
- **P_010 in Affects, Ack pending** → Display; **ACTION REQUIRED** post-session to Ack

If ledger unavailable, proceed with inline note.

**STEP 1: Verify Grid XML Files**

Location: `data/excel_exports/`

Required:
- `History Grid (SPY)_v3.xlsx`
- `History Grid (QQQ)_v3.xlsx`

If missing: export fresh from ThinkorSwim (export at 6:30 PM previous evening).

### Market Open (9:30 AM)

**STEP 2: Morning Initialization**

```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture
.\P_010_daily_posture.bat
```

Verify output:
- `P_010_RiskConfig.json` created
- Check: `risk_mode` ∈ {FULL, HALF, OFF}
- Check: `spy_posture`, `qqq_posture` populated
- Backup in `data/snapshots/`

**Integration:** P_115, P_118, P_300, P_400 read `P_010_RiskConfig.json` for position sizing.
- FULL = 100% of base risk
- HALF = 50% of base risk
- OFF = 0% (correction mode)

Morning Initialization: ✓ COMPLETE

### Intraday (2:00 PM or Later)

**STEP 3: Intraday Validation (Optional)**

```powershell
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture
.\P_010_run_intraday_vp_check.bat
```

Verify output:
- `outputs/intraday_vp_check_[timestamp].json` created
- Check: `intraday_adjustment` ∈ {NONE, HALF, REDUCED}
- Check: `prange_status` (CONFIRM, DIVERGE, etc.)

**Integration:** Apply MIN(morning_risk_mode, intraday_adjustment) for position sizing.
- Example: FULL + HALF = use HALF sizing

Can run multiple times (2 PM, 3 PM, 4 PM, etc.); each creates timestamped file. Downstream systems read latest.

Intraday Validation: ✓ COMPLETE

---

## QUICK COMMANDS

| Time | Command | Purpose |
|------|---------|---------|
| 9:30 AM | `INIT daily` | Run morning initialization batch |
| 2+ PM | `INIT intraday` | Run intraday validation (optional) |
| Anytime | `type P_010_RiskConfig.json` | Check current risk mode |
| Anytime | `dir outputs\*.json /o-d` | List latest intraday checks |

---

## INITIALIZATION CHECKLIST

**Pre-Market:**
- [ ] Grid XML files exported from TOS (previous 6:30 PM)
- [ ] Files in `data/excel_exports/`
- [ ] Previous day's logs reviewed

**At 9:30 AM:**
- [ ] Run `INIT daily`
- [ ] Verify `P_010_RiskConfig.json` created
- [ ] Check `risk_mode` (FULL/HALF/OFF)
- [ ] Confirm downstream systems reading config

**At 2 PM (if running intraday):**
- [ ] Run `INIT intraday`
- [ ] Verify `intraday_vp_check_*.json` created
- [ ] Apply MIN(morning_risk, intraday_adj)

**At 4 PM:**
- [ ] Review `logs/P_010_Daily_*.log`
- [ ] Verify no errors or warnings
- [ ] Archive snapshots if needed

---

## TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| Grid XML not found | Verify filenames match exactly; export fresh from TOS |
| Python/yfinance error | Check internet; run `pip list \| findstr yfinance` |
| Intraday can't load snapshot | Run morning system first (`INIT daily`) |

---

## DAILY WORKFLOW SUMMARY

```
6:30 PM (prev day):   Export Grid XML from TOS
9:30 AM (market open): INIT daily → risk_mode set
2:00 PM (intraday):    INIT intraday → adjustment determined (optional)
4:00 PM (close):       Review logs

Position Sizing = MIN(risk_mode, intraday_adjustment)
```

---

## CHANGELOG

### v3.1 — 2026-06-04
- Added STEP 0.5 Work Order Review (governance).
- Compressed from 179 → 110 lines: condensed steps, removed verbose output listings, collapsed troubleshooting, simplified checklist.
- Essential workflow retained: morning batch, intraday batch, quick reference.

### v3.0 — 2026-02-04
- Original daily initialization guide. Batch-driven workflow, grid-based posture calculation.

---

**End of P_010 Initialization Guide v3.1**
