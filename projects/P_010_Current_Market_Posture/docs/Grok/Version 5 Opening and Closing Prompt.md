💲💲💲 P_010 [Day, Month DD YYYY HH:MM Daily Posture Evaluation] v5
Priority Action: [None / Review open short puts / Size new credit if filled / Journal hygiene]
Live marks (required before forecast): SPY [px ±% / O-H-L]; ES [±% @ level]; VIX [px ±Δ]; 10y [yield]
P_010 RiskConfig: avg [x.xx] · SPY [x.xx] · QQQ [x.xx] · VXX [signal / px] · risk_mode [FULL/HALF/OFF] · grid [MM/DD] · ts [ISO]
Overnight: SPY futures [±X% @ ~level]; Asia/Europe [summary]. Key: [1–2 catalysts]
MARKET DIRECTION: Weekly Posture ([Bullish/Neutral/Bearish] [score]/10 OIL)

Trends: [hold/supportive]
Volume: [avg/building]
Majors: [yields/dollar note]
Sectors: [rotation note]
VIX: [level; complacent/elevated]
IBD Big Picture: [one line]

Recalc: [Posture + score] — Wizards [1 sentence]. VP mode is binding for size.
Intraday Bias: [Neutral / Mild Bullish / Defensive] — Levels [supp / res]; play [structure / cash]
Options Income (Launchpad / OIL):
Preferred: [zone + structure allowed under current risk_mode]. OFF = sit or 0.5× sim. HALF = 0.5×. FULL = 1–2 live. No wide structures into events.
Specific Idea for evaluation: Sell [expiry] [short] / Buy [long] [PCS/IC], target credit ~$[X], PoP [XX–XX]%. Size [0 / 1 sim / 1–2 live] under [OFF/HALF/FULL]; manage 50% credit or stock trigger [level].
P_400 gate: [CLOSED / IDEA QUEUED / SUBMITTED]
P_400 Council (omit entirely if CLOSED):

Validation: Passed / Failed
Three-Gate: G1 [n] · G2 [n] · G3 [n] · Final [n live / n sim]
Roles: Quant [A/C/B code] · Macro [A/C/B code] · Tape [A/C/B code] · Risk [A/C/B code] · Behavioral [A/C/B code]
Verdict: Approve / Approve with Caution / Block
Severity: HARD_BLOCK / SOFT_FLAG / INFO
Remediation or ticket: [one line]
Audit: [HH:MM ET · mark · VIX · risk_mode]

Risk: [catalysts]
Next-Day Setup: [Bias] — [rationale + levels]. Watch: [catalyst]
Wizards Debate (≤6 lines): Bull. Bear. Reconciled: [posture + gate].

Closing v5 after the bell:
💲💲💲 P_010 Closing [Day, Month DD YYYY HH:MM] v5
Close vs. Forecast & Posture ([B/N/B] [score]/10): SPY [close + %] — [aligned/missed/exceeded].
Marks: vs [levels]; vol [vs avg]; VIX [close +Δ]; RiskConfig [mode / avg]
Component shifts: [1–2 lines]
Recalc: [posture] — Wizards [1 sentence]
Launchpad P&L: [theta / fills / none]
P_400 gate at close: [CLOSED / idea died / filled + verdict]
Journal: [row added / stale cleaned / no change]
Next-Day Setup: [Bias] — [levels]. Watch: [catalyst]
[Friday: YTD recap; square hedges]

What was added vs v4 (only what was missing):

Live marks + RiskConfig row — the standing rule is now a field, so OFF cannot be forgotten.
IBD line under MARKET DIRECTION.
Size language tied to actual mode — no more “under FULL guidelines” on an OFF day.
P_400 gate — CLOSED is the default.
Council stub — appears only if you queue or submit a ticket.
Closing journal + gate — kills the stale 18 AUG “Open” problem.
Hard rule in the spec: council cannot upgrade OFF → HALF/FULL.

What was not added: five-role essays every morning, Three-Gate math on days you are in cash, or replacing Bull/Bear.

Same template, filled at 13:26 ET today so you can see the split:
💲💲💲 P_010 [Monday, August 31 2026 13:26 Daily Posture Evaluation] v5
Priority Action: Journal hygiene — mark 18 AUG 26 765/760 Closed (expired OTM). No new credit.
Live marks: SPY 765.79 −0.46% (O 767.33 / H 767.62 / L 764.72); ES ~−0.5%; VIX ~15.20 +5.3% vs 14.43; 10y ~4.72%
P_010 RiskConfig: avg −0.51 · SPY +0.22 · QQQ −1.24 · VXX NEUTRAL 18.36 · risk_mode OFF · grid 08/28 · ts 2026-08-30T15:17
Overnight: ES −0.17% into the bell; Asia mixed-soft; Europe heavy. Key: Larak Island strikes / oil +3%; Warsh hangover; NFP Friday.
MARKET DIRECTION: Weekly Posture (Neutral 4.0/10 OIL)

Trends: hold (LT 1.25 / ST 1.00); still above 200-SMA 710.26
Volume: light — RVOL 0.38
Majors: cautious (OIL majors 0.00; hike odds bid)
Sectors: narrow; IWM week broke support
VIX: 15.2 — still low historically, overnight pop not faded
IBD Big Picture: Friday “Falls after hawkish Warsh; NVDA reverses; jobs due”

Recalc: Neutral 4.0 / VP OFF — Wizards: weekly structure intact, short-horizon tape too weak to warehouse short puts into NFP.
Intraday Bias: Defensive Neutral — Levels 764.70 / 756.61 below, 767.60 / 771–775 above; play cash.
Options Income (Launchpad / OIL):
Preferred: sit. No 755-zone credits while spot is on 765 and mode is OFF.
Specific Idea for evaluation: 11 SEP 26 755/750 PCS, ~$0.40–0.55, PoP ~68–78%. Size 0 live / 1 sim under OFF. Stock trigger 762.
P_400 gate: CLOSED
Risk: Gulf oil, ISM/JOLTS Tue, NFP Fri, close under 764.70.
Next-Day Setup: Neutral/defensive — 765 is hold-or-fail. Watch ISM + JOLTS; DELL/PANW after the close.
Wizards Debate: Bull: 765 hold + dead volume is not a breakdown. Bear: HOD 767.62, CMF_Z −1.57, OFF, 1.4% OTM. Reconciled: Neutral 4.0, gate CLOSED.
Council block omitted because the gate is CLOSED. If you flip it to SUBMITTED, paste the Trade setup and the 755/750 comes back HARD_BLOCK (Tape T03 + Risk R01/R02) with Final = 0 live.
The spec now lives in AGENTS.md as Version 5. Use this skeleton starting with Tuesday’s open.where is agents.mdAGENTS.md is in the project artifacts folder:
/home/workdir/artifacts/AGENTS.md
That is the file updated this afternoon with Version 5. Size ~9.5 KB, last write 17:27 UTC (1:27 PM ET).
On your trading PC the matching working copy of the style/prompt lives in this project’s artifacts directory when synced. It is not the same path as RiskConfig (C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json) or the OIL workbook under Documents.can I download agents.md to my PC
and can You make the appropriate changes to Project charterYes. Use the download controls on the two files below.
AGENTS.md (Version 5 brief spec)

Save it on your PC wherever you keep the style guide — a clean place is next to the other P_010 docs:
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\AGENTS.md

Charter is now v1.2 (v1.1 is unchanged as the archive). New file:
/home/workdir/artifacts/P_010_Master_Project_Charter_v1.2.docx
Suggested PC path:
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_Master_Project_Charter_v1.2.docx

What v1.2 adds to the charter:

Purpose now states the layer split: wizards = regime, P_400 = admission
Live-marks + RiskConfig row are required fields, not footnotes
Version 5 opening/closing mapping replaces the old “Version 3 templates” language
New Section 10 — P_400 Council (gate states, HARD_BLOCK, reason codes, cadence)
Sizing language must cite the live mode (no “FULL guidelines” on an OFF day)
Closing journal hygiene is in the data-flow path
Change log row dated 2026-08-31

Rule that is now in both files: Council cannot upgrade OFF → HALF/FULL.