\# P_400 Trade Order Management Guidelines

\#\# Purpose

P_400 is the authoritative trade order management layer for the AI-Agent-Learning-Hub trading system. It governs position sizing, target setting, stop placement, options translation, and broker-ready order formatting across active strategy systems. Strategy documents such as P_115 may still define entry logic or setup context, but they no longer control order management once a trade reaches the P_400 workflow.

\#\# Decision Boundary

The evaluating or analyzing project may propose a candidate order block, candidate target, or candidate risk structure, but it must not make the final portfolio money-management decision. P_400 owns the final decision on sizing, target acceptance, stop placement, stock-only versus options routing, and broker-ready execution formatting. The system-of-record for the executable order is the P_400 output, not the upstream analytical signal.

\#\# Authority Rule

All order management decisions must default to P_400. This includes stock sizing, options sizing, stop methodology, target hierarchy, risk-to-reward validation, fallback rules, override handling, and final Thinkorswim-ready order formatting. Any legacy document that references P_115 for sizing or order handling should be interpreted as historical or strategy-origin context unless that rule is explicitly restated inside P_400.

\#\# System Scope

P_400 applies across active strategies including P_115, P_116, P_117, P_118 and P_300. The current framework defines P_400 as the cross-system trade management layer and states that P_115 integration exists inside P_400 rather than beside it as a separate authority.

\#\# Council Governance

Before any new order is submitted or any management override is approved, the council framework must evaluate technical validity, risk structure, macro backdrop, tape confirmation, and plan adherence. A trade should not proceed when a critical risk, macro, tape, or behavioral failure is present, because blocking authority exists within the council decision structure used by the P_400 space.

\#\# Core Workflow

1\. Entry signal logic comes from the source strategy or setup prompt.

2\. The source strategy may provide a baseline target, but P_400 decides whether that target is accepted, adjusted, replaced, or rejected.

3\. Once a candidate trade is valid, P_400 takes control of sizing, stop placement, target selection, options translation, and execution formatting.

4\. The final order package must reflect the council state of Approve, Approve with Caution, Block, or Override Required before broker submission.

\#\# Position Sizing Standard

Every position must pass the three-gate sizing system, and the smallest gate result is the final position size. The three gates are risk-based sizing, user-provided cash availability, and concentration cap, with options using premium paid rather than notional exposure for concentration calculations. No exception is allowed without explicit override and documented justification.

\#\# Risk Mode Standard

Risk mode from P010RiskConfig.json is authoritative and must be re-read before each STEP 2 evaluation. P_400 defines adjusted risk capital and concentration values by risk mode, so older fixed sizing values from P_115-derived references should not be treated as the active control set unless they match current P_400 values.

\#\# Target Selection Standard

P_400 controls target selection. Standard setups use resistance-based targets, while price-discovery setups with no visible overhead resistance use the Confluence-Based Target Framework built from ATR extension, round-number alignment, measured move when visually confirmed, and prior structure when available. ATR alone is not sufficient; confluence governs target choice. If the source strategy provides a target, P_400 may use it as a strict baseline, then normalize it into the final executable target.

\#\# Reward-to-Risk Rule

T1 must produce at least 2:1 reward to risk from entry or the setup is not valid. When T1 passes, T2 becomes the continuation objective, and after price reaches T1 the stop should move to breakeven with trailing logic applied for T2 management. Fabricating a target only to satisfy the 2:1 rule is prohibited. A source-provided target that does not satisfy the rule should be retained only as a candidate or baseline, not as the final executable target.

\#\# Stop Architecture

P_400 controls stop placement for both stocks and options. The stock stop is determined from the more conservative of ATR-based or chart-structure logic when required by the framework, and option stops are translated from underlying stock movement through delta-aware methodology under the approved options process.

\#\# Options Management

P_400 is the governing authority for options order management. Options must pass viability gates for spread, open interest, and reward-to-risk parity versus the stock setup, then use either the chart-based primary method or risk-budget-first secondary method depending on the technical quality of the setup. If gate math yields zero contracts, fallback to stock or explicit override is required.

\#\# Options Data Priority

Before any options trade is finalized, live chain data should be pulled from Thinkorswim first, then ChartExchange, then Yahoo Finance, then Barchart or Nasdaq as later fallbacks. Data sourcing should stop at the first usable source, and sources should not be aggregated.

\#\# Execution Formatting

The final order output must be broker-ready and concise. The master P_400 trade setup prompt requires the response to include council status, stock order format, and option order format when applicable, with option management tied to the underlying stock trigger by default unless the trade plan explicitly says otherwise. If no option contract data is supplied, P_400 must make the explicit decision that the order is stock-only or that options are not applicable.

\#\# Replacement Guidance for Legacy P_115 References

The following replacements should govern any future edits:

\| Legacy reference pattern \| Replacement rule \|

\|---\|---\|

\| “P_115 asset sizing requirements” \| Replace with “P_400 three-gate sizing framework.” \|

\| “P_115 execution decision logic” \| Replace with “P_400 trade order management workflow.” \|

\| “P_115 options handling” \| Replace with “P_400 options translation and hybrid risk methodology.” \|

\| “P_115 order notes / TOS logic” \| Replace with “P_400 broker-ready Thinkorswim order format.” \|

\| “P_115 manages exits” \| Replace with “P_400 manages stops, T1/T2 logic, breakeven transitions, and trailing logic after entry approval.” \|

\#\# Applies-To Rule

P_115 remains a strategy-origin document for entry logic and contextual setup information only where P_400 explicitly references it. P_400 now owns all downstream trade order management functions, including sizing, target logic, stop logic, options translation, override documentation, and order submission formatting. The evaluating project may provide a recommended baseline, but P_400 determines the final executable order and the final money-management decision.

\#\# Document Use Rule

This guideline should be used as the normalization layer whenever older files, quick references, or prompts contain P_115-based execution language. In any conflict between a P_115-derived order-management rule and a P_400 rule, P_400 controls. The final order notes should describe P_400 decisions, not unlabeled analytical-layer fallbacks.
