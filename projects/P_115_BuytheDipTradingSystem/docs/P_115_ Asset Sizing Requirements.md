# SUPERSEDED 2026-07-24

This file is superseded. Position sizing, R:R validation, stop/target
authority, and order formatting are now P_400's job -- see P_400
architecture doc Section 3.3 (Three-Gate Position Sizing) and Section
3.1 (Authority Rule). P_115 emits a raw SIGNAL_V2 packet (entry, chart
PA Stop, first resistance target) via `cli.py` and P_400's own pipeline
(screen-all -> evaluate -> spec) does all sizing from there -- see
P_115_System_Architecture.v1.0.md Section 8.2 (v1.3, 2026-07-24).

The account figures below are also stale (superseded by
P_000_Account_Parameters_Current.md, read live) -- kept for historical
reference only, not to be used for any calculation.

---
Please  Note: This file is derived fron Sysem Initialization Prompt.md in  P-115_BuyYTheDiptradingSystem  


ACCOUNT PARAMETERS:
  Balance:      $35,000
  Base Risk:    1.5% = $525
  Max Position: 5%   = $1,750
  Next Review:  February 2026

MARKET POSTURE STATUS:
  [Display SPY posture, QQQ posture, avg posture, risk_mode]

TRADING MODE: [HOT MARKET / STANDARD / CORRECTION]

THREE-GATE POSITION SIZING:
  Gate 1: Risk-based (Risk$ / (Entry - Stop))
  Gate 2: Cash availability (per trade, user provides)
  Gate 3: Concentration limit ($1,750 max or premium paid for options)
  Final = SMALLEST of three gates

2-TRANCHE EXIT SYSTEM:
  T1: First major resistance (50% of position)
  T2: Trailing stop using weekly ATR (50% of position)
  Zone strength: Strong (3+ touches), Moderate (2), Weak (1)