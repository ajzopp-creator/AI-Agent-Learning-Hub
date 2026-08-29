# P_300 Feature Specification — Drift-Regime Gate

**Status:** DRAFT — requires operator review/approval before implementation (structural decision, 3+ files)
**Source:** Adapted from Singha (2025), "Discovery of a 13-Sharpe OOS Factor: Drift Regimes Unlock Hidden Cross-Sectional Predictability," [arXiv:2511.12490](https://arxiv.org/abs/2511.12490)
**Author:** Claude (drafting) / Anthony Zoppi (review) — per SKILL Maintenance convention
**Aligned with:** P_300 Schema Shorthand + Architecture v2.7 (as loaded in this session)

---

## 1. Concept Being Translated

The paper's edge isn't the value/reversal signal itself — it's the **gate**: a stock only "counts" when it has shown a persistent up-day frequency over a long lookback, distinct from ordinary price momentum. Translated to P_300 terms, this is a **regime-context feature attached to an anchor date**, not a per-bar shape feature. That distinction drives every schema decision below.

Paper notation → P_300 translation:

| Paper | Formula | P_300 equivalent |
|---|---|---|
| `UpFraction_{i,t}` | `(1/63) * Σ_{k=1}^{63} I[r_{i,t-k} > 0]` | `drift_up_fraction_63` — decimal fraction, e.g. 0.6349 |
| `REGIME_{i,t}` | `I[UpFraction_{i,t} > 0.60]` | `drift_regime_active` — 1.0/0.0 |
| `EDGE = BASE × REGIME` | signal gated to zero outside regime | pre-filter/early-PASS gate (see §6), **not** folded into DTW similarity distance |

---

## 2. Schema Placement

**No DDL migration required.** `pattern_features` is EAV-style (`feature_name`/`feature_value`), so this adds rows, not columns:

```
pattern_features (pattern_feature_id PK, pattern_instance_id FK, feature_name, feature_value)
  + ('drift_up_fraction_63', 0.6349)
  + ('drift_regime_active',  1.0)
```

Consistent with the `return_pct` convention (M-020): store as **decimal fraction**, multiply by 100 only at the display boundary. `drift_regime_active` stored as REAL 1.0/0.0, not TEXT — avoids the TEXT-into-INTEGER-FK class of bug (EC-061) by never touching an FK column at all.

These are **derived** features (computed from raw price history, not raw VP export fields) — correctly excluded from `pattern_bars`' 17 raw + 10 normalized columns per the existing raw/derived split.

---

## 3. Open Structural Question — Data Availability for Pipeline A

This is the part that needs your decision before any code gets written.

`UpFraction` needs **63 trading days strictly before `anchor_date`**. P_300's two pipelines have asymmetric access to that history:

- **Pipeline B (Daily Evaluate):** `History Grid (<symbol>).xlsx` is a rolling grid — almost certainly already contains ≥63 prior bars. Low risk, no new data source needed.
- **Pipeline A (Add Pattern):** source is `Pattern_<startdate>_<enddate>_<symbol>.xlsx`, scoped to the pattern's own `window_length` (5–20 bars). That is **not enough history** to compute a 63-day trailing fraction at ingestion time for historical patterns.

Three options — pick one before I draft any infrastructure code:

| Option | Description | Tradeoff |
|---|---|---|
| A | Extend Pattern XLSX export to include 63+ pre-anchor bars as context-only rows | Touches your existing export process outside Claude's control |
| B | New lightweight `price_history_cache` (per-symbol daily close series, independent of `window_length`) | New table/file — a real schema addition, needs its own migration + Check-Out/Check-In discipline |
| C | Compute the feature only where trailing history happens to be available; store `NULL`/omit the row otherwise, flagged via a data-quality marker | No new dependency, but leaves historical catalog patterns with partial coverage |

I'd lean toward **B** for correctness (matches the paper's design intent and stays reusable for future long-lookback features like regime-by-VIX-bucket), but it's your schema call.

**Anti-pattern guard:** whatever option, never silently truncate to whatever history is available and compute anyway — that's exactly the `df.tail(N)` class of bug (EC-060). Insufficient history must raise/flag, not degrade quietly.

---

## 4. Layer Placement

```
domain/drift_regime.py          ← pure calc: up_fraction(), is_regime_active()  — no I/O, no DB
infrastructure/price_history_reader.py  ← NEW: fetch trailing N closes ending strictly before anchor_date
application/                    ← orchestrates: call reader, pass to domain calc, attach result to pattern_instance / live candidate
```

- Module name `drift_regime.py` — no stdlib collision (M-018 clear; avoid generic names like `regime.py` alone if that risks ambiguity with other modules, but no Python stdlib conflict either way).
- `domain/drift_regime.py` takes a `list[float]` of prior daily returns — never touches `sqlite3`, `requests`, or `infrastructure/` (Hub hard rule).
- `infrastructure/price_history_reader.py` is the only place that queries source data (Pattern XLSX / History Grid / new cache, depending on §3 decision).

```python
# domain/drift_regime.py (illustrative signature only — not for direct use, pending §3 decision)
def up_fraction(prior_returns: list[float], window: int = 63) -> float:
    """window must be exactly satisfied; raise on insufficient history (no EC-060 truncation)."""
    if len(prior_returns) < window:
        raise InsufficientHistoryError(f"need {window} prior bars, got {len(prior_returns)}")
    return sum(1 for r in prior_returns[-window:] if r > 0) / window

def is_regime_active(up_frac: float, threshold: float = 0.60) -> bool:
    return up_frac > threshold
```

---

## 5. Config Additions

Following the existing feature-flag pattern already in `config.py` (`CE_GATE_ENABLED`, `RISK_AVERSION_LAMBDA`, `CE_MIN_THRESHOLD`, `NARRATOR_ENABLED`):

```
DRIFT_WINDOW_DAYS   = 63     # trailing lookback, trading days
DRIFT_UP_THRESHOLD  = 0.60   # up-day fraction required to activate regime
DRIFT_GATE_ENABLED  = False  # off by default — additive, opt-in
```

If added, `DRIFT_GATE_ENABLED` should also be grepped and surfaced in the INIT Step 6 `Decision flags:` summary line, same as the other flags — a silent flip on this gate would change which candidates ever reach BUY/WATCH classification.

---

## 6. Pipeline Integration — Recommended: Pre-Filter, Not Similarity Dimension

Two ways to fold this in; recommending the first as the faithful translation:

**Option A — Pre-filter / early-PASS gate (recommended).** Mirrors the paper's `EDGE = BASE × REGIME` exactly: if the live candidate isn't in a drift regime, Pipeline B returns PASS *before* running DTW similarity ranking — reusing the existing "fail to PASS, never silently produce a BUY" failure mode. Does not touch the locked Stage-6 BUY/WATCH thresholds (n≥5+wr≥0.70+z>0 / n≥3+wr≥0.60+z>0) — it only narrows which candidates reach that logic. Symmetrically, when adding historical patterns via Pipeline A, tag whether that pattern's anchor was itself in a drift regime, so regime-matched comparisons are possible later.

**Option B — 11th similarity dimension in DTW composite distance.** Folds `drift_up_fraction_63` into the existing 10 normalized `pattern_bars` columns (equal-weight DTW, Decision B). Rejected as the primary approach: DTW is designed for normalized price-bar *shape*, and drift regime is a binary/scalar *context* variable, not a shape feature — mixing them dilutes both.

**Flag for your approval:** Option A changes what enters the classification path, which is adjacent to the Stage-6-locked decision logic even though it doesn't alter the thresholds themselves. Per the Hub rule on structural changes, this needs explicit sign-off before implementation, not silent inclusion.

---

## 7. Anti-Pattern Compliance Checklist

| Anti-pattern | Handled how |
|---|---|
| EC-060 (silent window truncation) | `up_fraction()` raises on insufficient history, never truncates |
| EC-061 (TEXT into INTEGER FK) | New feature never touches FK columns, EAV value is REAL |
| EC-046/048/022 (raw dollars in similarity) | Drift feature is a fraction/boolean, not a dollar value; kept out of DTW distance entirely (Option A) |
| EC-064 (mock data in decision engines) | Requires real trailing price history (§3) — no synthetic fallback |
| EC-049/058 (hardcoded paths) | New `infrastructure/price_history_reader.py` sources path via `config.py` / `db_utils.get_latest_catalog()`, same as existing readers |
| EC-067 (merging Pipeline A/B) | Feature computed independently in each pipeline; gate applied only in Pipeline B, storage only in Pipeline A — pipelines still never merge |
| EC-022/ID-005 (LLM in decision path) | Purely deterministic Python calc, no LLM involvement |
| M-018 (stdlib collision) | `drift_regime.py` — no conflict |

---

## 8. Open Decisions Before Implementation

1. **§3 — data source for Pipeline A's 63-day lookback:** Option A (extend export), B (new price cache table), or C (partial coverage with flagging)?
2. **§6 — is the pre-filter gate approved** to sit ahead of the locked Stage-6 BUY/WATCH logic, or do you want it evaluated separately from the classification path?
3. Threshold tuning: keep the paper's 63-day / 60% as defaults, or backtest against your own catalog before fixing `DRIFT_UP_THRESHOLD`? (The paper's own sensitivity table showed Sharpe swinging from 3.2 to 13.2 depending on this single threshold — it is not a robust constant to import blindly.)
4. Should `drift_regime_active` at the historical pattern's own anchor date be stored too (so Pipeline B can restrict matches to regime-consistent historical patterns, not just gate the live candidate)?

No files touch the Hub from this session — this is a design document for your review inside your own INIT'd session.
