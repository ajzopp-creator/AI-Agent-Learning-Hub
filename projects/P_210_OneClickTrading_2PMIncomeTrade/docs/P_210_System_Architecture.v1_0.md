# P_210 System Architecture — One Click Trading 2PM Income Trade

**Version:** 1.0
**Created:** 2026-09-05
**Owner:** Tony (review), Claude (drafting)
**Status:** Initial capture — service just onboarded, no live trades logged yet

---

## Purpose

P_210 is a paid subscription signal service (One Click Trading — 2PM Income Trade), same category as P_110 (Trade the Bounce). Tony does not build or maintain the signal logic; the provider delivers it via a ThinkOrSwim indicator and a same-day Telegram alert. This project's job is to hold the reference material for interpreting those alerts and, later, to log trades taken from them.

- Subscription page: https://app.oneclicktrading.com/product/44bb1db3-39ad-49bb-aca5-c98de8109782
- Publisher: Graham Lindman, editor of the "2pm Income Trade" financial service; distributed via One Click Trading (48bytesNorth Inc.), which acts only as technical conduit and does not endorse or execute the publisher's trade ideas
- Underlying: signal computed off QQQ (price) and VIX; trade instrument is NDX options (per-strike net-credit spreads)
- Delivery: Telegram alert once per day at 2:00 PM ET

---

## Critical Paths

| Path | Resolution |
| :---- | :---- |
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_210_OneClickTrading_2PMIncomeTrade\` |
| ThinkScript source | `tos_scripts\P_210_2PM_StrategyRouter.ts` — provider's chart indicator, reproduced verbatim |
| This doc | `docs\P_210_System_Architecture.v1_0.md` |
| Obsidian KB reference | `trading_journal\KnowledgeBase\2026-09-05_One Click Trading 2 pm Income Trade Guide.md` — read and reviewed 2026-09-05; frontmatter tagged review_status: reviewed-relevant |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` (shared conda env, no new venv) |

Only what's needed exists so far: `docs\` and `tos_scripts\`. No `data\`, `outputs\`, or `python\` yet — add them when a real need shows up (e.g. a trade log or an automated alert parser), following P_110's layout as the template.

---

## Signal Logic (from the ThinkScript router)

The indicator locks QQQ and VIX readings at 9:30 AM ET (session open) and again at 2:00 PM ET (entry decision point), plus the overnight gap (prior close to today's 9:30 open). From those three inputs it walks a fixed if/else cascade to select one of 14 rule codes, which map to 11 named strategy buckets and a size tier (1, 2, 4, or 8):

| Direction since 9:30 | VIX band (2PM) | Other condition | Strategy | Size |
| :---- | :---- | :---- | :---- | :---- |
| Down | 18–19 | — | Bear Call | 4 |
| Down | 19–20 | gap < 1% down | Bull Put | 1 |
| Down | ≥20 | — | Bear Call | 2 |
| Down | 16–18 | gap ≥1% down | Bear Call | 1 |
| Down | 16–18 | Tuesday, gap <1% down | Bear Call | 1 |
| Down | 16–18 | not Tuesday, gap <1% down | Bull Put | 1 |
| Down | <16 | not Tuesday, move > -0.5% | Bear Call | 2 |
| Up | ≥18 | gap ≥1% down | Bonus Butterfly | 4 |
| Up | ≥18 | VIX drop OK, gap <1% down, not Monday | Bull Put | 8 |
| Up | ≥18 | VIX drop OK, gap <1% down, Monday | Bear Call | 2 |
| Up | 16–18 | gap ≥1% down | Bear Call | 1 |
| Up | 16–18 | VIX drop OK, gap <1% down | Bull Put | 4 |
| Up | <16 | VIX drop OK, Tue/Thu | Bull Put | 8 |
| Up | <16 | VIX drop OK, Wed/Fri | Bear Call | 2 |
| Up | <16 | gap ≥1% down | Bear Call | 1 |
| (no match) | — | — | SKIP — no trade | 0 |

"VIX drop OK" = VIX has not fallen more than 5% since 9:30. All thresholds, bands, and the cascade order are the provider's — treat this table as a read of their indicator, not a strategy Tony designed or can freely edit.

A separate "live" version of the same cascade runs continuously before 2PM as an unconfirmed preview; only the 2:00 PM lock is the real signal.

---

## Alert Format (example, captured 2026-09-05)

```
Bearish 2 PM Entry - Position Size 2
Ticker: NDX
Buy to Open: 4 SEP 26 29530 NDX CALL
Sell to Open: 4 SEP 26 29520 NDX CALL
Reminder: Enter this trade as a net credit (not a debit).
Make sure to use a limit order.
Suggested Net Credit: $1.10 - $1.30 or higher
Max Profit: NDX Closes Below 29520
```

This is a bear call credit spread: sell the lower strike, buy the higher strike as protection, collect the credit, limit order only, max profit if NDX settles below the short strike. A "Bullish" alert would be the mirror-image bull put spread. Size 2 in this example corresponds to one of the DOWN-side / VIX-band-2 buckets in the table above (ruleCode 3, 7, or 13, depending on that day's actual gap/direction reading).

---

## Open Items

- No trade log yet. When Tony starts logging P_210 fills, follow the P_800 vault-write convention (`write_to_vault()`) rather than hand-building frontmatter — P_210 itself should never own vault-write logic, same rule as every other strategy project.
- No automated Telegram-to-log pipeline yet. Build only if/when Tony asks — not assumed as a next step here.

---

## Changelog

### 2026-09-05
Initial creation. Project folder, this doc, and the provider's ThinkScript router file added after Tony's first P_210 alert and confirmation this is a subscription service (same category as P_110/OIL).

**Same-day update:** Obsidian Local REST API key mismatch found and fixed (config had a stale key unrelated to the actual plugin key) -- KB article read successfully, reviewed per kb-review-convention (reviewed-relevant, frontmatter patched), and publisher attribution (Graham Lindman / 48bytesNorth Inc.) folded into Purpose section. Open Items entry for the unreadable KB article removed since it's now resolved.
