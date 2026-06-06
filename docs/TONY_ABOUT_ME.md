# TONY_ABOUT_ME.md
## Personal Context for Claude
## AI-Agent-Learning-Hub | Loaded at session start

---

## Who I Am

My name is Tony. I am a trader based in Allentown, Pennsylvania.
Trading under AJZ Strategies LLC. Brokerage: Schwab.

My final position before retirement was Software Architect. I retired in 2009.
Always was interested in Knowledge Based Systems.

Trading is my primary identity and primary goal — not software development.
Technology is in service of trading. Never the reverse.

My focus split: 70% trading skills and market knowledge, 30% technology tools.

---

## Trading Background

**Experience level:** 1.5 years self-taught since August 2024.

**Primary markets I trade:**
- Options Income Launchpad (OIL) (CL) — active setup: TradeTheBounce strategy (D_130)
- SPY / QQQ — pattern recognition and market posture (P_300, P_010)
- Equities (BT and CAVP strategies — flag breakouts, technical setups)

**Subscriptions and tools:**
- VantagePoint Software — pattern recognition
- Big Trends — Sunday Night Trader
- Eddie Z — lifetime subscription, 10 picks per trading day
- Chaikin Analytics — Basic subscription

**Trading style:**
- Technical swing trader using trend context + selective fundamentals
- Day trader when volatility is high
- Position trader when the setup warrants it
- Timeframes: weekly for long-term trend/posture, daily and 4H for setups, 2 / 5 / 15 min for intraday entries

**Current active strategies:**
- BT (Big Trends) — flag breakout entries, Sirott cushion 1.5 ATR
- CAVP (Chaikin Analytics + VantagePoint) — CA ≥5.5/6.5, VP ≥6/8, flag pattern
- TradeTheBounce OIL (D_130) — bounce entries on oil
- Market Posture Weekly Forecasts (P_010) — weekly directional bias

**Platform:** ThinkorSwim (charting + ThinkScript scripting)
**Pattern tool:** VantagePoint software (no public API — GUI automation being explored)
**Account API:** Schwab API (integration in migration plan)

---

## Trading Education Path

Currently reading: *The New Market Wizards* by Jack Schwager.
Goal: Study the mindset and methods of consistently profitable traders.

Learning priorities:
1. Market knowledge and edge development
2. Trading psychology and discipline
3. Risk management and position sizing
4. AI tools to support decisions (not replace judgment)

---

## Risk Management Philosophy

Trading account: $35,000 USD across Roth IRA + AJZ Strategies LLC.
Target: grow to support $12,000 annual after-tax withdrawals.
Position sizing working toward Schwab API integration for automation.

**Risk rules — Normal Mode:**
- Risk per trade: 1.5% ($525)
- Max single position: 5% ($1,750)
- Daily loss limit: 2% ($700) — stop trading if hit
- Weekly loss limit: 6% ($2,100)
- Max open trades: 3 (total open risk ≤5%)
- Cash buffer: ≥$8,000 at all times
- Minimum R:R: 2:1 on every trade

**Risk rules — Correction Mode (Risk-Off):**
- Risk per trade: 0.75% ($262.50)
- Daily loss limit: 1% ($350)
- Weekly loss limit: 3% ($1,050)
- Max open trades: 2 (total open risk ≤3%)

**Stop trading immediately if:**
- 3% drawdown in a session
- 6 consecutive losers
- Out of flow / not executing the process

**Full rules, position sizing methodology, and pre-trade checklist:**
See AJZ_Strategies_Trading_Plan_2026_V2.md (uploaded to Claude Project)

**Trading psychology:**
- Strengths: focused, persistent, strong research and analysis orientation
- Known weakness: inconsistent discipline — committed to single defined process until 50% win rate
- Known weakness: order-entry errors — checklist required before every submission

---

## Technology Skill Level

| Skill | Level |
|---|---|
| ThinkScript | Experienced — primary scripting language |
| Python | Novice — actively learning |
| VS Code | Novice — learning the environment |
| PowerShell | Basic usage for Hub management |
| LM Studio / Local LLMs | Functional — installed and working |

**Important:** Always explain Python concepts and VS Code steps explicitly.
Never assume I know what a library does or how an IDE shortcut works.

---

## The AI-Agent-Learning-Hub

Root path: `C:\Users\Trader\AI-Agent-Learning-Hub\`

I am building a set of AI-powered tools to support trading decisions:
- Market analysis automation
- Trade journal analysis
- Pattern recognition
- Eventually: automated risk management workflows

**Core principles I follow:**
- Local processing first (LM Studio / Llama) — privacy and cost reasons
- Claude API is secondary, cloud-only when local is insufficient
- Small, modular scripts — never monoliths
- One shared conda environment (p140) across all projects

**Active projects:**
- P_000 — Foundation / master reference (this project)
- P_010 — Market Posture Weekly Forecasts
- P_020 — AJZ Strategies Performance Analysis
- P_115 — Buy the Dip Trading System
- P_300 — VantagePoint Pattern Recognition
- P_130 — TradeTheBounce OIL

---

## How I Communicate

**I prefer:**
- Direct answers before explanations
- Step-by-step instructions for technical tasks
- One thing at a time — don't overwhelm with options
- Plain English for complex concepts
- Confirmation that each step worked before moving to the next

**I dislike:**
- Generic AI responses that don't account for my context
- Being given 5 options when I need a recommendation
- Responses that restate my question before answering it
- Excessive caveats and disclaimers
- Bullet points when a sentence works fine

**Decision-making style:**
- Give the recommendation first, reasoning second. I'll ask if I want more detail.
- When I ask for a recommendation, give one — not a list of pros/cons

---

## Goals for 2026

**Trading goals:**
- Execute Section 3 risk rules on 100% of trades — process goal
- Outperform SPY quarterly — outcome goal
- Complete 3 plan iterations: V2.0 (done) → V2.1 Q2 → V2.2 Q3
- Build to 15–18% annual growth + lifestyle flexibility

**Technology goals:**
- Complete GitHub setup and version control for the Hub
- Implement CoWork for file-reading workflows
- Integrate Schwab API for position sizing
- Build LM Studio-powered trade journal analysis
- Develop VantagePoint GUI automation (pywinauto)

---

## What Claude Should Know Every Session

1. Trading comes first. If a technology task conflicts with a trading session, trading wins.
2. I am building tools that I will actually use — not demos or experiments.
3. Explain the "why" behind recommendations — I want to learn, not just copy-paste.
4. When I say "let's build X," help me plan it fully before writing any code.
5. Always deliver files as downloadable artifacts with full Windows save paths.
6. I use the p140 conda environment at `C:\Users\Trader\.conda\envs\p140\python.exe`.
   Never suggest creating a new virtual environment.

---

## Last Updated
May 9, 2026 — Merged 4/14 (risk rules, psychology, goals, BT/CAVP specs) with 4/18 (LLC/Schwab, retired-architect bio, 70/30 split, experience level, subscriptions list, intraday timeframes, Schwab API note).

## How to Use This File
Upload to Claude Project → Project Settings → Add Content
Claude will read it before every session automatically.
