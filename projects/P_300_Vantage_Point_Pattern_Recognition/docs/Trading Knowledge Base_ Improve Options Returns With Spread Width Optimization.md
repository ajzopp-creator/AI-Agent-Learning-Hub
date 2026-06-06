# Trading Knowledge Base: Improve Options Returns With Spread Width Optimization

**Source:** SMB Capital — YouTube  
**Video Title:** Improve Your Options Returns Hugely With This Simple Tweak (Counterintuitive)  
**Duration:** 13:20  
**Published:** July 29, 2023  
**URL:** https://www.youtube.com/watch?v=66lbCWsfnyA  

---

## The Core Concept: Spread Width Determines Your Return on Capital

The "counterintuitive tweak" is this: **using a narrower spread width generates a significantly higher return on capital (ROC) than a wider spread** — even though the wider spread collects more total premium in dollar terms.

Most traders assume wider spreads are better because they collect more money. The video proves mathematically that the opposite is true when you measure **return on capital at risk**.

---

## The Key Moments Broken Down

### Timestamp 4:35 — 50-Wide Put Credit Spread

- Sell put at strike X, Buy put at strike X-50
- Max risk = **$5,000** per spread (50 × $100 SPX multiplier)
- Credit collected = ~$5.00 = **$500** per spread
- **Return on Capital = $500 ÷ $5,000 = 10% ROC**

### Timestamp 9:08 — 25-Wide Put Credit Spread

- Sell the **same short put strike**, Buy put at strike X-25 (closer in)
- Max risk = **$2,500** per spread (25 × $100 multiplier)
- Credit collected = ~$4.00 = **$400** per spread (slightly less)
- **Return on Capital = $400 ÷ $2,500 = 16% ROC**

> The narrower spread collects slightly less in dollars but generates **60% more return on capital** because it ties up far less money.

### Timestamp 12:01 — Three-Case Comparison

| Case | Structure | Credit | Capital at Risk | ROC |
|---|---|---|---|---|
| Case 1 | One 50-wide spread | $500 | $5,000 | 10% |
| Case 2 | One 25-wide spread | $400 | $2,500 | 16% |
| Case 3 | Two 25-wide spreads | $800 | $5,000 | 16% |

**Winner: Case 3 — Two 25-wide spreads**  
Same capital as one 50-wide spread, but collects $800 vs. $500 in credit AND delivers 16% ROC vs. 10%.

---

## Why This Is Counterintuitive

Most traders focus on the **dollar amount of premium collected** rather than the **return on capital**. A 50-wide spread collects $500 vs. $400 for a 25-wide — but it requires twice the capital at risk.

When you normalize for capital used, the narrower spread wins every time. This is the same logic professional traders apply: it's not about how much you make per trade, it's about **how efficiently your capital works**.

The credit difference is also smaller than expected — the outer long put adds very little value to the buyer, so you give up minimal premium by moving it closer. This is the mathematical key to why the tweak works.

---

## The ROC Formula
```
Return on Capital (ROC) = Credit Received ÷ Max Risk × 100

Where: Max Risk = (Spread Width - Credit Received) × Multiplier
```

**Example:**
- 25-wide spread, credit = $4.00
- Max risk = ($25 - $4.00) × $100 = $2,100
- ROC = $400 ÷ $2,100 = **19% ROC**

Always calculate ROC before entering — not just the dollar credit amount.

---

## Practical Application Rules

- **Never automatically choose the widest spread** — always calculate and compare ROC across widths first
- The **short strike stays the same** — only the long strike (hedge) moves closer to the short strike
- Narrower spreads carry **less absolute dollar risk per contract** — easier position sizing for smaller accounts
- **Two narrow spreads > one wide spread** on the same capital, in both ROC and total dollar profit
- Use this framework for both put credit spreads and call credit spreads

---

## Additional Key Insights

**Capital efficiency compounds over time.** A 16% ROC strategy consistently outperforms a 10% ROC strategy over months and years, even if individual trade dollar amounts look similar.

**Narrower spreads = lower max loss per contract.** Losing less on individual bad trades makes it psychologically easier to follow your plan and stay disciplined.

**More positions, more diversification.** Freed-up capital from narrower spreads can be deployed into additional trades on different underlyings — reducing single-trade concentration risk.

**The long put (hedge) has diminishing marginal value.** As you move the long put further away from the short put, each additional dollar of width adds less and less protection value — meaning you're paying disproportionately high capital cost for very little additional premium on wide spreads.

---

## Quick Reference Checklist

- [ ] Calculate ROC for your default spread width before entering
- [ ] Calculate ROC for a narrower spread width (e.g., half the width)
- [ ] If narrower width gives better ROC, prefer it — even if dollar credit is slightly lower
- [ ] Consider running two narrower spreads instead of one wide spread when capital allows
- [ ] Track ROC on every trade alongside dollar P&L — it's the true measure of capital efficiency
- [ ] Keep a log: over time, compare actual ROC across different width choices

---

## Comparison Summary

| Spread Width | Dollar Credit | Capital at Risk | ROC | Verdict |
|---|---|---|---|---|
| Wide (50-wide) | Higher | Much Higher | Lower (~10%) | ❌ Less efficient |
| Narrow (25-wide) | Slightly Lower | Much Lower | Higher (~16%) | ✅ More efficient |
| 2× Narrow spreads | Higher than 1 wide | Same as 1 wide | Higher (~16%) | ✅✅ Best of both |

---

## Glossary

| Term | Definition |
|---|---|
| **Spread Width** | The dollar distance between the short strike and long strike in a credit spread |
| **Return on Capital (ROC)** | Credit received divided by max capital at risk; measures efficiency of capital use |
| **Short Strike** | The option you sell in a credit spread; generates the premium |
| **Long Strike** | The option you buy in a credit spread; defines your maximum loss |
| **Max Risk** | Maximum possible loss = spread width minus credit received (× multiplier) |
| **Capital Efficiency** | How much return you generate per dollar of capital deployed |
| **SPX Multiplier** | SPX options have a $100 multiplier — 1 point = $100 per contract |

---

*Document generated from: SMB Capital YouTube — "Improve Your Options Returns Hugely With This Simple Tweak (Counterintuitive)" (Jul 29, 2023)*  
*For educational purposes only. Not financial advice.*