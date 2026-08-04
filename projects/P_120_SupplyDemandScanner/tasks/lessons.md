# P_120 Supply & Demand Scanner — Lessons

Live working lessons. Loaded at INIT. Append only; never delete a lesson.

---

## L-001 — Source PDF diverges from the source trading lessons in four places (2026-08-03, High)

The `P_120_System_Architecture_and_Development_Plan.pdf` was written from the six supply/demand email lessons, but it drops or mangles four rules. Building Phase 2 from the PDF alone would ship a scanner that scores setups differently from how the strategy is actually taught.

**1. Target derivation is missing.** Lesson 3 sets the target from the opposing zone — supply above for a long, demand below for a short. The PDF states only `RRR >= 2.5` as a filter and never says where TP comes from.

*Architectural consequence:* `risk_levels.py` needs the full zone map to locate the opposing zone. The graph state must carry **every** detected zone through to the Selector, not just Evaluator-passing zones. The PDF state flow prunes rejected zones early — it cannot.

**2. "Time" was misread as base length.** Lesson 6 defines Time as how long price *dwells inside the zone on retest* — a live failure signal on an existing zone. The PDF converted this to "> 3 candles inside base," which is base construction, and which the Scanner already enforces as "< 4 candles." Result: one rule stated twice, and the actual Time failure factor absent.

*Architectural consequence:* zone persistence in SQLite with a status field, re-scored on each daily run. New domain module for retest evaluation (dwell + depth).

**3. Choppiness is not measured.** Lesson 4: candles with significant wicks lower zone quality — one candle moving 10% beats three candles totaling 10%. The PDF captures magnitude (2.5 ATR) and candle count (<= 2) but nothing about body-to-range ratio, so two full-bodied departure candles and two long-wicked doji score identically.

*Fix:* `body_fill_ratio` term in `quality_scoring.py`.

**4. Demand-zone top is ambiguous in the source and hard-coded in the PDF.** Lesson 2 allows the top at "the top of the wick or body" — trader discretion. The PDF fixes it at wick-top, which triggers entries on shallower pullbacks. Legitimate choice, wrong place for it.

*Fix:* `DEMAND_TOP_MODE = "wick" | "body"` in `config.py` so both can be tested.

**Rule going forward:** the six lessons are ground truth. The PDF is a derived document. On conflict, the lessons win.

---

## L-002 — Source lessons carry no numeric thresholds (2026-08-03, Medium)

Every quality and failure rule in the lessons is directional, not quantitative: "faster is better," "the longer price spends in the zone, the higher the chance it fails," "the deeper the retest, the worse." The numbers in the PDF (2.5 ATR, <= 2 candles, 50% retest depth, RRR >= 2.5) do not appear in any lesson — they were invented by whoever wrote the PDF.

Treat every one of them as a tunable in `config.py` with a comment marking it as unvalidated, not as a strategy constant. Phase 4 backtesting sets the real values. Nothing gets hardcoded outside `config.py`.

---

## L-003 — Schwab has no 4H candles and caps intraday history (2026-08-03, High)

`pricehistory` accepts minute frequencies of 1, 5, 10, 15, and 30 only; a `day` periodType accepts only minute frequency. There is no 4H. Intraday depth is capped at roughly 30-35 days at one-minute resolution and not much better at 30-minute.

Consequences: 4H would need resampling from 30-min bars, forcing a session-anchor decision (9:30 open vs midnight) that changes every base and every zone boundary. And a 12-month 4H backtest across the S&P 500 — Phase 4 in the source PDF — was never obtainable from Schwab.

Resolution: dropped 4H (D-002). Daily and Weekly pull full multi-year history, so Phase 4 works as written. If intraday is ever needed for fills, add 30-min at execution time only and cache forward from that day — never as a scan timeframe.

---

## L-004 — Refresh token expires every 7 days and needs a browser click (2026-08-03, High)

Schwab refresh tokens have a 7-day life and renewal requires a browser redirect. Any "fully autonomous daily batch" breaks weekly on its own.

Plan a Sunday re-auth runbook at `docs\processes\refresh_schwab_token.md`. The daily batch must fail loud when the token is dead — never skip a scan silently and never emit a success line without the API call returning.

---

## L-005 — Project ID collision with P_300 (2026-08-03, Medium)

The source PDF self-brands as "P300" throughout, including the database name `p300_trading.db`. P_300 is already VantagePoint Pattern Recognition. Every reference scrubbed to P_120; DB renamed `P_120_scanner.db`.

Check for residual "P300" strings in any document derived from that PDF before it enters the project folder.

---

## L-006 — Module naming (2026-08-03, Low)

Nothing in this project gets named `signal.py`. Stdlib collision; `sys.path[0]` prepend causes circular imports. Cost P_300 a debugging session (M-018). Use `trade_signal.py` or keep the model in `schemas.py`.
