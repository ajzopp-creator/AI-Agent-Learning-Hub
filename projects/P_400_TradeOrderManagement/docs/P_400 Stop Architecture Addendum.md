# P_400 Stop Architecture Addendum — Underlying-Condition Requirement for Option Stop Legs

**Applies to:** P_400 Trade Order Management Guidelines — "Stop Architecture" section
**Trigger incident:** P_118 MA, 2026-08-21 → 2026-08-24 → flagged 2026-09-02
**Action:** Insert the rule and checklist below into the existing "Stop Architecture" section. Add the incident entry to your Error Corrections / Incident Log (create that section in the P_400 doc if it doesn't exist yet — the P_000 doc's `Section 6` format is shown as a template below).

---

## 1. New rule — insert directly after the existing Stop Architecture paragraph

> **Mandatory Underlying-Condition Rule for Option Stop Legs**
>
> Every option order leg that functions as a stop (`STP`, `STP-LMT`, or `TRAILSTOP`) MUST carry an explicit condition clause:
>
> `Submit Condition: MARK of underlying <SYMBOL> <operator> <price>`
>
> A bare numeric price or trigger level attached directly to an option leg (e.g., `SELL -1 .XYZ260101C100 STP 534`) with **no** underlying-MARK condition is **not a valid stop** and must be rejected at Council review, regardless of how the number was derived.
>
> **Rationale:** Option premium does not move 1:1 with the underlying's price scale. A raw stock-plan price copied onto an option leg either (a) sits at a level the option's real price can never reach — so the stop never fires — or (b) fires at an underlying level that no longer matches the originally-approved dollar risk. All stop translation from a stock plan to an option plan must go through delta-aware conversion **and** be expressed as an underlying condition — never as a literal price carried over from the stock leg.
>
> **Every bracket leg gets this, not just the ones that happen to include it.** If Bracket A and Bracket B are part of the same order package, both must carry underlying-MARK conditions on every stop/target leg where the intent is underlying-driven — inconsistency between brackets (one conditioned, one not) is itself a red flag.

## 2. New pre-submission checklist item — Council / Quant Strategist gate

> Before any option bracket order is approved for submission:
> - [ ] Every leg tagged as a stop (S1, S2, trailing stop, or equivalent) includes a `Submit Condition: MARK of underlying` clause.
> - [ ] The underlying trigger level in that condition reflects a delta-aware translation of the approved dollar-risk budget — not a number copied verbatim from a prior stock-only plan.
> - [ ] If switching an approved stock plan to an option plan mid-workflow, Gate 1 (risk capital) is re-run against premium paid, per the Position Sizing Standard — the stock plan's dollar-risk figure does not automatically carry over.
>
> **Any missing checkbox = automatic Block, not "approve with caution."** This is a structural stop-architecture failure, not a judgment call.

## 3. Incident log entry (add to Error Corrections Log / Incident Log)

```
### EC-[NEXT] — Naked Option-Price Stop Leg Approved Without Underlying Condition (2026-09-02)

Severity: High
Category: Stop Architecture / Council Gate Failure
Strategy: P_118, Symbol: MA

What happened:
Stock plan (entry 579.96, stop 554.98, $24.98/share risk, R:R 4.75 to 699.45)
was converted into an OTM call position (.MA261016C640). Bracket A's stop leg
(S1: SELL -1 @ 534 STP) was submitted with no underlying MARK condition, while
Bracket B's T2/S2 legs correctly carried "Submit Condition: MARK of underlying
MA > 730". The bare 534 level was a stock-price-derived figure, not a reachable
option price, so the stop never triggered against real option pricing. Position
rode to a loss close to the full premium paid (~$450) instead of a bounded,
pre-defined risk.

Root cause:
Stock-plan stop level (554.98) was inherited as a literal price on the option
leg instead of being translated into a delta-aware underlying MARK condition.
No Council stop-architecture check caught the missing/inconsistent condition
before submission.

Correct rule:
Mandatory Underlying-Condition Rule for Option Stop Legs (Stop Architecture
section) + pre-submission checklist above.

Fix applied:
Added mandatory underlying-condition requirement and Council checklist item
to the Stop Architecture section; documented here so recurrence is checked
against this log before every option bracket approval.
```

---

## Where this goes / how to apply it

I don't have local filesystem access in this session, so I can't edit the live file directly. Copy the two blocks above into your working copy of the guidelines doc, then bump the version number.

```powershell
$projectRoot  = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_Trade_Management_System"
$targetFolder = Join-Path $projectRoot "docs"

if (-not (Test-Path $targetFolder)) {
    New-Item -ItemType Directory -Path $targetFolder -Force | Out-Null
}

# After you've merged the addendum into your working copy and saved the new
# version file to Downloads, copy it into place:
Copy-Item -Path (Join-Path $HOME "Downloads\P_400TradeOrderManagementGuidelines_vNEXT.md") `
          -Destination (Join-Path $targetFolder "P_400TradeOrderManagementGuidelines_vNEXT.md") -Force
```

Let me know the current version number of your live guidelines file and I can merge this addendum directly into a full, ready-to-save vNEXT copy instead of a standalone patch.
