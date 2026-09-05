# P_400 Current State

## 2026-08-31 -- WO-P400-E7.001 (Extended-Hours Pricing Basis) build session

**Status: CODE BUILT, not OWNER_DONE.** Full build + fix landed same session; live-verified on real symbols, partially.

### Shipped this session (all read-back verified on disk)
- config.py +16 -- PRE_MARKET_OPEN_TIME_ET, AFTER_HOURS_CLOSE_TIME_ET,
  MAX_PLAUSIBLE_SPREAD_PCT_EXTENDED (provisional 5.0%, not yet backed by
  real spread samples)
- domain/market_hours.py -- new get_session_state() (regular/pre_market/
  after_hours/closed); is_market_open_now() now a thin wrapper over it
- infrastructure/schwab_market_data.py -- new get_extended_quote_data()
- application/fetch_snapshot.py -- 3-way session branch (was 2-way bool)
- domain/council.py -- tape_vote() extended branch, RC_USING_EXTENDED_DATA
- application/evaluate_signal.py -- spread-sanity threshold now differs by
  price_basis
- schemas.py, domain/council_codes.py -- supporting field/constant additions
- tests: test_market_hours.py, test_schwab_market_data.py,
  test_tape_price_basis.py, test_fetch_snapshot.py extended;
  test_evaluate_signal.py split (296->246 lines) into new
  test_evaluate_signal_spread.py (200 lines -- moved E4.004 tests + new
  extended-threshold tests)
- WO-P400-E7.001 filed and updated to CODE BUILT

### Regression check
Full suite twice this session: 384 passed/1 skipped (initial build), then
385 passed/1 skipped after the live-bug fix below (one new test added).
Exit 0 both times. Pre-existing warnings only.

### Live verification -- PARTIAL, and caught a real bug
2026-08-31 17:41 ET, after-hours: ran fetch-snapshot on CME/SPGI/WFC (the
three symbols batch-2b couldn't price earlier the same session, no cached
spread). All three returned [OK] with price_basis="extended" -- but
bid=0.0/ask=0.0 on all three. Root cause: Schwab's extended quote node
returns 0.0 (not null) when there's no active extended-session market for
a symbol, and the original get_extended_quote_data() only checked for
None, not <= 0 -- would have let a fake zero-spread snapshot through the
spread-sanity gate looking like a perfect fill. Fixed same session
(bid/ask <= 0 now treated as no-data, same as None), test added
(test_get_extended_quote_data_returns_none_on_zero_bid_ask), 3 bad
snapshot files deleted. Re-ran fetch-snapshot CME after the fix: correctly
fails loud now instead of writing garbage.

**Confirmed working:** session detection (correctly identified
after_hours at 17:41 ET), extended-quote HTTP call, price_basis="extended"
wiring end to end, the zero-bid/ask guard (post-fix).

**NOT YET exercised by a live run:**
- A symbol WITH real extended-hours liquidity (bid/ask > 0) -- CME/SPGI/WFC
  just had none available tonight.
- Pre-market window (only after-hours tested tonight).
- Real extended-hours spread sampling to replace the provisional 5.0%
  MAX_PLAUSIBLE_SPREAD_PCT_EXTENDED placeholder.

### CME/SPGI/WFC status
Still un-priceable as of session end -- no active extended market tonight,
no cached regular-session spread either. Resolves naturally at tomorrow's
9:30 ET open (first live fetch caches the spread for future closed-market
runs too). Manual/TOS entry is the only tonight-option if needed sooner.

### Do NOT
- Mark WO-P400-E7.001 OWNER_DONE until a real symbol with actual
  extended-hours liquidity has been fetched successfully (not just the
  fail-loud path) and pre-market has been tested at least once.
- Assume the 5.0% extended-spread threshold is calibrated -- it's a
  documented placeholder, not derived from data.

---

## 2026-08-07 -- WO-P400-E5.003 (Tier-2B Batch Runner) build session

**Status: IN_PROGRESS, not OWNER_DONE.** Build complete, live-verified partially.

### Shipped this session (all hash-verified on disk)
- `application/batch_2b.py` (201 lines) -- orchestration
- `application/batch_2b_scoring.py` (268 lines) -- per-symbol pipeline, vehicle
  comparison, ranking (split out of batch_2b.py to stay under 300-line cap)
- `config.py` +4 (BATCH_REPORT_DIR, BATCH_REPORT_FILE_PATTERN)
- `cli.py` +10 (batch-2b subcommand wiring)
- `application/fetch_chain.py` +19 (Scope 6 viability WARN at fetch time)
- SIP -> v2.6 (STEP 2/4 rewritten: options-first via `compare`, replaces the
  old stock-sizes-to-0/R:R<2:1/Tony-request fork -- applies to BOTH the manual
  flow and batch-2b, Tony confirmed 2026-08-07)
- `.claude\skills\p400-project-context\SKILL.md` disk copy -- new Must #13
  (options-first) + changelog entry. **Tony still needs to sync this into the
  live skill via Customize -> Skills -- disk edit alone doesn't propagate.**

### Regression check
Full suite: 318 passed / 1 skipped / 319 collected, exit 0 -- matches
established baseline exactly (WO-P000-E13.001). No regressions from the
config.py/cli.py/fetch_chain.py edits.

### Live verification -- PARTIAL
First real `batch-2b --cash 18894.78` run, 2026-08-07 09:31 ET, market open.
9 packets screened, 8 FAIL-disposed (RR_BELOW_MIN), 1 PASS (FSLR, the
2026-08-06 packet). FSLR BLOCKED at evaluate (ADVERSE_DRIFT, drift ~6.65%
collapsed R:R to 0.36). Report JSON read back and hand-verified field-by-field
against source data -- all correct (heat_cap = 12% of $31,348.39 balance
exactly, evaluated count math right, skip reason format right, ET timestamp
offset right).

**Confirmed working:** single-invocation orchestration, Tier-1 screen
reproduction, FAIL disposal, live Schwab fetch-snapshot, evaluate_signal()
reuse incl. drift/ENTRY_MISSED path, empty-candidate handling, Pydantic
report persistence.

**NOT YET exercised by a live run** (FSLR never reached this stage --
BLOCKED before vehicle comparison):
- `_vehicle_comparison()` / options-first compare_vehicles() integration
- `_build_candidate()` / `score_candidate()` / `order_by_score()` integration
  (the underlying functions are unit-tested in test_ranking.py and unchanged,
  but the NEW glue code connecting them in batch_2b_scoring.py is not)
- Cumulative heat warning (needs 2+ APPROVED candidates)
- fetch-chain Scope 6 viability WARN under a real bad-liquidity contract

### Earnings file
`python\earnings_2026-08-07.json` -- web-search-sourced entries for all 8
unique symbols in the 2026-08-07 inbox (FSLR, AVB, DX, LFCR, MAA, NVR, NVT,
PSKY). LFCR (Aug 5) and PSKY (Aug 4) both reported earnings within the last
3 days -- expect APPROVED_WITH_CAUTION (post-earnings stabilization, WO-P400-
E2.023), not BLOCK, if either resurfaces as PASS in a future screen.

### Next step (Tony's choice, offered, not yet answered)
1. Wait for a future PASS signal to survive to APPROVED naturally, or
2. Hand-check the vehicle-comparison path directly against a real symbol/
   chain, independent of the daily signal set.
Tony deferred -- has an Eddie Z (P_118) batch to evaluate first, will return
if nothing there.

### Do NOT
- Mark WO-P400-E5.003 OWNER_DONE until the vehicle-comparison/ranking path
  gets at least one real exercise.
- Re-derive any of the above -- read this entry first.