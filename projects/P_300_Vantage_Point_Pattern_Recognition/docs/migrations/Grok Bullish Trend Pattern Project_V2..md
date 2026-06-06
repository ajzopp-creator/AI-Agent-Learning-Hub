Bullish Trend Pattern Project - V2.5 Pattern Matching Guide

What is "Pattern Matching"?

We look for repeatable setups in VantagePoint history grids that have produced winning bullish trades in the past. When most checklist conditions are met, we get a strong Pattern-Match signal.

Key Elements of the Bullish Trend Pattern (V2.5)

Short-Term Crossover

Definition: Short_Term_Difference flips from negative to positive.

Why it matters: Shows short-term trend turning bullish.

Rule: Must be > 0 today and < 0 yesterday.

Short-Term Strength

Definition: Short_Term_Difference stays positive for 3+ days.

Why it matters: Confirms momentum.

Rule: 3+ consecutive positive days.

Medium & Long-Term Momentum

Definition: MT and LT differences.

Why it matters: Confirms bigger trend.

Rule: MT ≥ 1.5 OR LT ≥ 1.5.

Williams EMAI Slope

Definition: EMAI rising over last 5–10 days.

Why it matters: Institutional buying pressure.

Rule: Upward slope (+0.30 bonus).

Inverse PSI/EMAI

Definition: PSI flat/declining while EMAI rises.

Why it matters: Smart money buying.

Rule: PSI ROC ≤ 0 + EMAI rising (+0.15–0.20 bonus).

Neural Index

Definition: NeuralX = "up" on 2 of last 3 days + NeuralXMax.

Why it matters: AI predicts near-term upside.

Rule: ≥ 2/3 "up" + NIMAX ≥ 35–40.

Triple Cross Alignment

Definition: Short > Medium > Long.

Why it matters: All timeframes aligned.

Rule: +0.10 bonus.

Volume Confirmation

Definition: Up-day volume > 20-day average.

Why it matters: Real buying pressure.

Rule: > 30% above average (+0.25 bonus).

Price vs 50-day SMA

Definition: Close > 50-day SMA.

Rule: Required.

DL Score (Decision Layer)

Definition: Combined score from all elements.

Rule: DL ≥ 0.74 = Pattern-Match candidate.

Relaxed Visibility Mode

Even when market risk = OFF, catalog any stock with:

DL ≥ 0.74

Strong EMAI slope

Inverse PSI/EMAI

Execution only occurs when Posture Gate allows.

Python Program Specification

File: p301_pattern_matcher.py

Goal: Load any VantagePoint History Grid XML, scan for the pattern, and output a clear report + DL score.

Key Components

Load XML grid

Convert to DataFrame

Compute DL score

Scan entire grid

Output CSV of matches

DL Score Logic (Simplified)

Short-term crossover → +0.25

Short-term strength → +0.15

MT/LT momentum → +0.20

EMAI upward slope → +0.30

Neural Index → +0.15

Volume surge → +0.25

Triple cross / bonuses → TBD

Final DL score capped at 1.0.

Output

Date

Close price

DL score

Signal (Strong Buy / Buy / Hold / Pass)

Key reasons

How to Use

Save as p301_pattern_matcher.py.

Run: python p301_pattern_matcher.py "History Grid.xml"

Outputs matches + CSV.

Next Steps

Add Triple Cross logic

Add inverse PSI logic

Add posture gate check

Integrate V2.5 trigger phrases

This Markdown file preserves the structure and clarity of the original PDF while making it fully Obsidian-ready.