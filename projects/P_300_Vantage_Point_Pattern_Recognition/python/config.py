"""
FILE: config.py
VERSION: 1.20
DATE: 2026-07-19
AUTHOR: Anthony Zoppi + Claude
LAYER: config
DESCRIPTION:
    Single source of truth for all paths, constants, and thresholds in P_300.
    Every layer (domain, infrastructure, application) imports values from here.
    No hardcoded paths exist anywhere else in the codebase.

    Per architecture v2.4 §2.4: HUB_ROOT is the only hardcoded path; catalog
    DB resolution flows through db_utils.get_latest_catalog().

CHANGELOG:
    - 2026-07-19 v1.20 (WO-P300-E4.005 Phase 2c): EVAL_PARALLEL_ENABLED
      flipped True -> False. Post-JIT (Phase 2a/2b, similarity.py's DTW
      kernel), Phase 2c empirically re-tested parallel scoring against
      the real staging catalog and found it SLOWER than serial at every
      tested worker count (2-24) and batch size (50-400) -- e.g. default-
      worker-count parallel measured 2.8-3.1x slower than serial at
      typical batch sizes, only approaching (not beating) parity at
      batch=400. Each score_one() task got ~12x cheaper post-JIT, so
      ProcessPoolExecutor's per-worker startup cost (numba cache load +
      Windows-spawn re-import, confirmed one-time via a pool-reuse test)
      now exceeds the task itself. Pure performance flag -- parallel and
      serial are proven byte-identical in output (test_eval_scoring.py
      + every Phase 2a/2b/2c regression check), so this flip cannot
      change any BUY/WATCH/PASS signal, only wall-clock time. Full
      evidence in WO-P300-E4.005.md PHASE 2c RESULTS. EVAL_PARALLEL_
      WORKERS left in place (dormant while ENABLED=False) rather than
      removed -- cheap to re-enable if a future catalog scale or a
      redesigned (persistent, session-scoped) pool changes the verdict.
    - 2026-07-18 v1.19 (WO-P300-E4.004 v1.2): Added
      INCREMENTAL_MIN_REUSE_FRACTION. Consumed by application/
      incremental_post_batch.py's "worth it" threshold check --
      below this reuse fraction, skips the incremental path and
      calls the full parallel run_walk_forward() directly.
    - 2026-07-17 v1.18 (M-102): MINE_MIN_ANCHOR_DATE changed from a frozen
      literal to a computed first-safe date (calendar today-5yr + 2 days).
      VP's backfill boundary is a ROLLING 5-year window from export date.
      date(2021,7,14) set 2026-07-12 was already stale by 2026-07-17.
      First formula draft (today - (5*365+2)) landed ON the last zero-
      pred bar and still crashed the CNK batch; corrected to calendar
      5yr + 2 so it matches the original 2021-07-14 calibration and
      real data (first_nz=2021-07-19 on 2026-07-17).
    - 2026-07-16 v1.17: Added EVAL_PARALLEL_ENABLED + EVAL_PARALLEL_WORKERS
      (WO-P300-E4.003, M-096, file #4 of 5). Purely additive. Consumed by
      domain/eval_scoring.py's run_walk_forward() parallel path and wired
      through application/ingest_mined_pipeline.py's pre/post M-079 calls.
    - 2026-07-14 v1.16: Added MINE_ARCHIVE_DIR + MINE_ARCHIVE_SUFFIX
      ("BulkAddPattern" process, file #2 of 4). Purely additive. Auto-
      archive after ingest-mined was deliberately deferred in v1.13's
      DATA_BULK_MINE comment ("no auto-archive in v1") -- this is that
      v2. Reuses Scanner Loop's E:\\ drive but a separate constant +
      naming convention (date-first, no per-entry rename) per Tony's
      explicit call the same session.
    - 2026-07-13 v1.15: Added MINE_XOVER_MAX_BARS=20 + MINE_IGNITION_MAX_BARS=3
      (pattern_miner.py v2.0 -- crossover-gated eligibility replaces
      outcome-only screening; see that file's changelog). MINE_XOVER_MAX_BARS
      reuses _MAX_STANDARD_HORIZON's value deliberately, not coincidentally --
      measured from 66 real ground-truth picks (2026-07-13 diagnostic): 95%
      land within 20 bars of their own most-recent same-direction MT
      crossover. MINE_IGNITION_MAX_BARS splits that population into two
      labeled entry tiers (ignition vs continuation) per the same diagnostic
      (median 4, 50% within 3 bars).
    - 2026-07-12 v1.14: Added MINE_MAX_SCREEN_DAYS=180 (pattern_miner.py
      v1.2 -- screening no longer capped at 20 trading days; see that
      file's changelog for why the earlier cap was wrong, not just
      conservative).
    - 2026-07-12 v1.13: Added OUTCOME-FIRST PATTERN MINER section
      (WO-P300-E3.002, file #1 of 9). Purely additive. Reuses
      BULK_SIGNIFICANT_MOVE_PCT's existing 15.0 threshold via
      bulk_labeler.py's significant_move_15 -- MINE_MOVE_THRESHOLD is a
      separate constant so the two can diverge later without coupling.
      MINE_MIN_ANCHOR_DATE encodes the 2021-07-14 backfill boundary as a
      real constant for the first time (previously Phase 0 prose only).
    - 2026-07-12 v1.12: Added SCANNER LOOP section (WO-P300-E3.001, file #0
      of 5). Purely additive -- no existing constant changed. New
      DATA_BULK_NIGHTLY_SCAN subfolder deliberately isolated from
      BULK_INPUT_GLOB's non-recursive resolution (same isolation pattern
      as BULK_RESEARCH_DB in v1.9). SCANNER_ARCHIVE_DIR points off-disk to
      E:\\ -- confirmed existing, already holds an unrelated one-time
      backup this WO's monthly-suffixed archives never touch.
    - 2026-07-10 v1.11: Added SECTOR ANALYSIS section (WO-P300-E2.002,
      file #1 of 11). Purely additive -- no existing constant changed.
      ASSET_CLASS_STOCK/ETF mirror Decision 5 (ETF rows never get a
      fabricated sector). SECTOR_MIN_N_THRESHOLD=30 is a flat per-cell
      (sector x tier x horizon) floor -- NOT the ~384 whole-catalog CI
      figure from WO-P300-E2.001, which would over-flag at this grain;
      30 is the standard normal-approximation floor for a win-rate/mean
      statistic. See WO-P300-E2.002 Decision 6.
    - 2026-07-08 v1.10: Widened BULK_INPUT_GLOB from a hardcoded 10-year-
      only pattern to accept any export window length. Verified against
      real VP exports (10/5/3/1-year and 6-month SPY/BP files, both
      VP-direct and IntelliScan-routed) that column layout, header
      structure, and field semantics are IDENTICAL regardless of window
      length or export path -- only the row count and, inconsistently,
      the Triple Cross sub-header wording ("Short" vs "Triple Cross
      Short", confirmed symbol/window-independent) vary. A real pattern
      detection is not less valid because the source file is shorter;
      deliberately no minimum-window gate. Naming convention locked:
      <years>[I]_Pattern_<SYMBOL>.xlsx -- operator renames at export
      time (VP defaults to "History Grid (SYMBOL).xlsx"); the optional
      I flag records IntelliScan-routed exports for provenance only
      (confirmed byte-identical content to VP-direct at matched windows).
    - 2026-07-08 v1.9: Added BULK EXTRACTION section (WO-P300-E2.001).
      Purely additive -- no existing constant changed; Pipeline A/B behavior
      and INIT decision-flag grep unaffected. Research DB deliberately
      triple-isolated from get_latest_catalog() resolution: lives in a
      subfolder (glob is non-recursive on MODELS_DIR), filename does not
      match *catalog.db, and has no digit prefix.
    - 2026-06-28 v1.8: Re-tightened BUY_MIN_Z_SCORE from 0.0 to 1.0.
      M-034's 2026-06-18+ re-evaluation trigger ("re-tighten toward 1.0 when
      z becomes a meaningful separator") fires at N=331 (062326catalog.db).
      A walk-forward eval (not LOO) comparing the two thresholds across the
      full date-filtered catalog showed z>1.0 raises BUY accuracy 60.0%->
      62.9% (93/155 -> 61/97 correct) at the cost of a 37% cut in BUY
      volume; the 58 demoted patterns ran 55.2% (32W/26L), below the BUY
      pool's 60% average, so the cut is a real if modest edge, not noise.
      WATCH and PASS classification are mathematically unaffected (PASS
      identical 106/44/62 across both runs -- confirms the gate change is
      isolated to the BUY threshold only). See tasks/lessons.md M-034
      addendum (2026-06-28) for full walk-forward numbers.
    - 2026-06-09 v1.7: Added Certainty-Equivalent (CE) BUY-gate constants
      (RISK_AVERSION_LAMBDA, CE_MIN_THRESHOLD, CE_GATE_ENABLED). Risk-adjusted
      reasoning per Kochenderfer "Algorithms for Decision Making" Ch. 6
      (maximum expected utility). CARA exponential utility scores each top-K
      analog's forward return; the inverted mean utility is a certainty-
      equivalent return that sits below the raw mean for a risk-averse trader.
      CE_GATE_ENABLED defaults False -- CE is computed and displayed but does
      NOT alter any signal until flipped on after lambda tuning (NARRATOR_ENABLED
      precedent; determinism regression stays byte-identical while off).
      CRITICAL: RISK_AVERSION_LAMBDA is applied to DECIMAL-FRACTION returns
      (0.06 = 6%), NOT percentages. Any change to lambda is a calibration-
      affecting event: log it to tasks/lessons.md and note that fired BUY/WATCH
      signals are only comparable across runs at the same lambda. Lambda is
      stamped into every ledger record and report header for this reason.
    - 2026-05-30 v1.6: Raised LM_STUDIO_TIMEOUT_SECONDS from 60 to 120.
      DeepSeek R1 14B reasoning traces were hitting the timeout at 47-52s
      (DOX, DD) causing `Client disconnected. Stopping generation.`
      120s provides headroom for long reasoning chains without being
      unbounded.
    - 2026-05-28 v1.5: Lowered BUY_MIN_Z_SCORE from 1.0 to 0.0.
      Threshold sweep at N=116 (9-feature similarity, post-volume_zscore
      removal) confirmed z_score is not a discriminating gate at this
      catalog size. Every combo at wr=0.70 produced identical results
      across z=-0.5, 0.0, and 0.5 (buy_count=49, precision=79.6%,
      mean_ret=+6.4% at h=5). With baseline WR of 58%, top-K cluster
      z-scores rarely exceed 0.5 even for strong matches -- z>1.0 was
      suppressing valid BUY signals without improving precision.
      z=0.0 keeps the semantic intent (cluster must be above baseline)
      without blocking signals the wr gate already validated.
      Re-tighten toward z=1.0 as catalog grows to N=300+.
      BUY_MIN_WIN_RATE and BUY_MIN_MATCHES unchanged at 0.70 and 5.
    - 2026-05-28 v1.4: Removed volume_zscore from SIMILARITY_FEATURES.
      Feature ablation at N=116 showed removing it raised BUY precision
      from 54.0% to 70.5% (+16.5 pp). 9 features remain.
    - 2026-05-19 v1.3: Added Stage 8 Local LLM (LM Studio) constants.
    - 2026-05-16 v1.2: Added Pipeline B section; defined SIMILARITY_FEATURES.
    - 2026-05-15 v1.1: Removed ONEDRIVE_ROOT.
    - 2026-05-13 v1.0: Initial Stage 3 foundation.
"""

from datetime import date, timedelta  # noqa: E402
from pathlib import Path

# ---------------------------------------------------------------------------
# ROOT PATHS
# ---------------------------------------------------------------------------
HUB_ROOT: Path = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
PROJECT_ROOT: Path = HUB_ROOT / "projects" / "P_300_Vantage_Point_Pattern_Recognition"

# ---------------------------------------------------------------------------
# PROJECT SUB-FOLDERS
# ---------------------------------------------------------------------------
DATA_DIR: Path = PROJECT_ROOT / "data"
DOCS_DIR: Path = PROJECT_ROOT / "docs"
MODELS_DIR: Path = PROJECT_ROOT / "models"
PARAMETERS_DIR: Path = PROJECT_ROOT / "parameters"
PYTHON_DIR: Path = PROJECT_ROOT / "python"
TESTS_DIR: Path = PROJECT_ROOT / "tests"
TASKS_DIR: Path = PROJECT_ROOT / "tasks"
OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"

# ---------------------------------------------------------------------------
# DATA SUB-FOLDERS (Pipeline A & B file flow)
# ---------------------------------------------------------------------------
DATA_LIVE: Path = DATA_DIR / "live"
DATA_PROCESSED: Path = DATA_DIR / "processed"
DATA_HISTORICAL_PATTERNS: Path = DATA_DIR / "historical_patterns"
DATA_HISTORICAL: Path = DATA_DIR / "historical"
DATA_ARCHIVE: Path = DATA_DIR / "archive"

# ---------------------------------------------------------------------------
# CATALOG DB RESOLUTION
# ---------------------------------------------------------------------------
CATALOG_GLOB_PATTERN: str = "*catalog.db"
TEMP_WORKING_DB: Path = MODELS_DIR / "temp_working.db"
MODELS_ARCHIVE_DIR: Path = MODELS_DIR / "archive"

# ---------------------------------------------------------------------------
# STAGE 3 DELIVERABLE PATHS
# ---------------------------------------------------------------------------
STAGE_3_LEDGER: Path = DOCS_DIR / "migrations" / "STAGE_3_MIGRATION_LEDGER.md"

# ---------------------------------------------------------------------------
# PATTERN CONSTRAINTS (architecture §1.5, §9)
# ---------------------------------------------------------------------------
MIN_WINDOW_LENGTH: int = 5
MAX_WINDOW_LENGTH: int = 20
FORWARD_HORIZONS: tuple[int, ...] = (5, 7, 10, 15, 20)

# ---------------------------------------------------------------------------
# data_origin_type VALUES (architecture §9.4)
# ---------------------------------------------------------------------------
ORIGIN_PATTERN_IDENT: str = "PATTERN_IDENT"
ORIGIN_EVAL_SET: str = "EVAL_SET"

# ---------------------------------------------------------------------------
# DEFAULT FEATURE SET (Stage 4 ingest baseline)
# ---------------------------------------------------------------------------
DEFAULT_FEATURE_VERSION: str = "baseline_v1"
DEFAULT_FEATURE_DESCRIPTION: str = (
    "Stage 4 baseline feature engineering. Window-agnostic -- applies to "
    "all patterns regardless of 5-20 bar length. Full normalized columns "
    "on pattern_bars; scalar derived features per domain/feature_engineering."
)

# ---------------------------------------------------------------------------
# PIPELINE B -- DAILY EVALUATE
# ---------------------------------------------------------------------------
HISTORY_GRID_GLOB_PATTERN: str = "History Grid (*).xlsx"

# Decision C: top-K historical analogs returned per candidate.
TOP_K_MATCHES: int = 20

# Decision B: DTW per-feature, equal-weight summed across normalized
# pattern_bars columns (architecture §9.3). Single source of truth --
# domain/similarity.py imports this list rather than re-declaring it.
#
# v1.4 change: volume_zscore REMOVED. Feature ablation at N=116
# (outputs/feature_ablation_20260528_*.csv) showed it was pure noise:
# removing it raised BUY precision +16.5 pp (0.540 -> 0.705) with +42
# BUY count. Volume is noisy cross-symbol; matching on volume regime
# forces similarity toward volume profile instead of price structure.
# 9 features remain; all others within +-1.3 pp of baseline.
SIMILARITY_FEATURES: tuple[str, ...] = (
    "close_pct_from_anchor",
    "range_pct",
    "body_pct",
    "stdiff_pct",
    "mtdiff_pct",
    "ltdiff_pct",
    "pred_high_pct",
    "pred_low_pct",
    "pred_range_pct",
)

# Decision F: BUY / WATCH / PASS classification thresholds.
# AND-gate semantics -- all three conditions must hold for the class.
# Failure to meet WATCH thresholds drops the signal to PASS.
#
# Z-score interpretation: standardized excess win-rate of the candidate's
# top-K analogs vs. the catalog's baseline win-rate at the same horizon.
# Z > 0 = cluster wins more often than typical catalog patterns.
# Z > 1.0 = significantly above baseline.
#
# BUY_MIN_Z_SCORE history:
#   Stage 6 Decision F: 1.0 (calibrated for larger future catalog)
#   v1.5 (2026-05-28): lowered to 0.0. Threshold sweep at N=116
#   (outputs/threshold_sweep_buy_20260528_174716.csv) confirmed z is not
#   discriminating at this catalog size -- z=-0.5/0.0/0.5 all produced
#   identical results at wr=0.70 (buy_count=49, precision=79.6%). With
#   58% baseline WR, cluster z rarely exceeds 0.5 even for strong
#   matches; z>1.0 was suppressing valid BUY signals without improving
#   precision. Re-tighten toward 1.0 as catalog grows to N=300+.
#   v1.8 (2026-06-28): re-tightened to 1.0. N=331 walk-forward eval
#   (tasks/lessons.md M-034 addendum) confirmed z is now a real, if
#   modest, separator -- BUY accuracy 60.0%->62.9%, -37% BUY volume,
#   demoted patterns ran below the original pool's average win rate.
BUY_MIN_MATCHES: int = 5
BUY_MIN_WIN_RATE: float = 0.70
BUY_MIN_Z_SCORE: float = 1.0

WATCH_MIN_MATCHES: int = 3
WATCH_MIN_WIN_RATE: float = 0.60
WATCH_MIN_Z_SCORE: float = 0.0

# ---------------------------------------------------------------------------
# M-079 WALK-FORWARD EVAL -- PARALLEL EXECUTION (WO-P300-E4.003, M-096)
# ---------------------------------------------------------------------------
# domain/eval_scoring.py's run_walk_forward() fans out across a
# ProcessPoolExecutor when EVAL_PARALLEL_ENABLED. Added after a real
# BulkAddPattern run (2026-07-15) took 40+ minutes and looked hung to the
# operator -- an uncapped, single-process, O(n_patterns x corpus_size) eval
# with no visible progress inside a promotion gate. False -> unchanged
# serial path (debug/parity fallback). EVAL_PARALLEL_WORKERS=None defers to
# ProcessPoolExecutor's own default (os.cpu_count()); set an int to cap
# worker count on a shared/loaded machine.
# WO-P300-E4.005 Phase 2c (2026-07-19): flipped True -> False. Post-JIT,
# parallel is SLOWER than serial at every tested config (2-24 workers,
# batch 50-400) -- per-worker startup cost now exceeds each ~200ms task.
# Pure perf flag; parallel/serial proven byte-identical, so this cannot
# change any signal output. See WO-P300-E4.005.md PHASE 2c RESULTS.
EVAL_PARALLEL_ENABLED: bool = False
EVAL_PARALLEL_WORKERS: int | None = None

# ---------------------------------------------------------------------------
# FULL SERIAL RESCORE -- MEASURED COST ESTIMATE (WO-P300-E5.004)
# ---------------------------------------------------------------------------
# A cold M-079 "pre" (live-catalog) walk-forward cache falls back to a full,
# uncached, serial run_walk_forward() over the ENTIRE catalog -- the same
# O(n^2)-integrated cost EVAL_PARALLEL_ENABLED/topk_state_cache exist to
# avoid on the paths they cover, but this fallback is not one of those paths.
# WO-P300-E4.005 (2026-07-19) measured the true post-JIT serial rate against
# the real staging catalog: wall_ms = 0.7836 x corpus_size, fit through the
# origin, corpus_size range 19-10,656. domain/eval_scoring.py's
# estimate_full_rescore_seconds() integrates this over N patterns (corpus
# growing ~1:1 with index) to estimate a full rescore's total wall time.
# APPROXIMATION, not re-measured for WO-P300-E5.004 -- may drift as catalog
# composition (window lengths, symbol mix) changes. Good enough for the
# WO-P300-E5.004 confirm-before-rescore gate; not a promised SLA.
WALK_FORWARD_SERIAL_MS_PER_PAIR: float = 0.7836

# ---------------------------------------------------------------------------
# INCREMENTAL POST-BATCH -- MINIMUM REUSE FRACTION (WO-P300-E4.004 v1.2)
# ---------------------------------------------------------------------------
# application/incremental_post_batch.py's run_incremental_post_batch() checks
# the safe-reuse fraction (existing pids provably unaffected by this batch,
# per domain/eval_incremental.py's min-new-date partition) BEFORE attempting
# the incremental path. Below this cutoff, the incremental machinery isn't
# worth its own overhead vs. just calling run_walk_forward(parallel=True)
# directly on the whole staging catalog -- reuses E4.003's already-proven
# parallel path instead of building a second rescore path from scratch.
# Both real BulkAddPattern batches to date (2026-07-17) had a 0% reuse
# fraction (min_new_date near MINE_MIN_ANCHOR_DATE, ~10 years back), so the
# threshold has not yet been exercised against a real high-reuse batch.
# Tune against the ledger once enough real batches show what reuse fractions
# actually occur; not a calibration-affecting event like RISK_AVERSION_LAMBDA
# (this only picks which code path runs, never changes a signal).
INCREMENTAL_MIN_REUSE_FRACTION: float = 0.5

# ---------------------------------------------------------------------------
# CERTAINTY-EQUIVALENT (CE) BUY GATE -- risk-adjusted reasoning (v1.7)
# ---------------------------------------------------------------------------
# Source: Kochenderfer, "Algorithms for Decision Making", Ch. 6 (maximum
# expected utility). The current gate reasons on the EXPECTED forward return
# of the top-K analog cluster. The CE gate instead scores each analog's
# forward return through a concave (risk-averse) CARA utility function,
# averages the utilities, and inverts back to a certainty-equivalent return.
#
# CARA exponential utility:   u(r) = -exp(-lambda * r)
# Certainty equivalent:       CE   = -(1/lambda) * ln( mean_i( exp(-lambda * r_i) ) )
#
# For any non-degenerate spread of returns, CE < arithmetic mean. The gap
# (mean - CE) IS the risk penalty: fat-tailed / dispersed analog distributions
# are penalized INSIDE the decision rather than merely flagged afterward.
#
# *** DECIMAL SPACE -- READ BEFORE TUNING LAMBDA ***
# RISK_AVERSION_LAMBDA is applied to DECIMAL-FRACTION returns (0.06 = 6%),
# consistent with forward_labels.return_pct storage (M-020). At decimal
# magnitudes (~0.06), lambda must be large to bite: lambda=1 barely penalizes
# anything (exp(-0.06) ~ 0.94). Meaningful CE gaps live in the lambda=10-40
# band. DO NOT calibrate lambda as if returns were in percent (6.0) -- that
# collapses every CE toward the worst-case analog and nukes every BUY.
# Default 20.0 chosen as a moderate starting point; tune against the ledger.
#
# *** LAMBDA IS PROVENANCE ***
# A BUY made at lambda=20 means something different from a BUY at lambda=5.
# Any change to RISK_AVERSION_LAMBDA is a calibration-affecting event:
#   (1) log the change + rationale to tasks/lessons.md
#   (2) fired signals are only comparable across runs at the SAME lambda
# Lambda is therefore stamped into every ledger record and report header.
#
# CE_GATE_ENABLED defaults False (NARRATOR_ENABLED precedent): the first runs
# COMPUTE and DISPLAY CE without altering any signal, so the determinism
# regression stays byte-identical until you flip it on after lambda tuning.
RISK_AVERSION_LAMBDA: float = 20.0
CE_MIN_THRESHOLD: float = 0.0
CE_GATE_ENABLED: bool = False

REPORTS_DIR: Path = OUTPUTS_DIR / "reports"

# ---------------------------------------------------------------------------
# EXTERNAL P_000 / P_010 REFERENCES
# ---------------------------------------------------------------------------
P_000_ACCOUNT_PARAMS: Path = (
    HUB_ROOT / "projects" / "P_000_PythonClaudeLocalLLM"
    / "config" / "P_000_Account_Parameters_Current.md"
)
P_010_RISK_CONFIG: Path = (
    HUB_ROOT / "projects" / "P_010_Current_Market_Posture"
    / "P_010_RiskConfig.json"
)

# ---------------------------------------------------------------------------
# LM STUDIO -- LOCAL LLM (Stage 8: post-decision narrator only)
# ---------------------------------------------------------------------------
# Hard rule (NFR-1): the LLM is NEVER in the BUY/WATCH/PASS decision path.
# Narrator runs AFTER classify_signal() emits the structured SignalReport.
# Failure to reach LM Studio leaves SignalReport.narration = None; signal
# emits clean and the report writer renders `NARRATIVE: unavailable`.
LM_STUDIO_BASE_URL: str = "http://localhost:1234/v1"
LM_STUDIO_MODEL: str = "deepseek-r1-distill-qwen-14b"
LM_STUDIO_TIMEOUT_SECONDS: int = 120
LM_STUDIO_MAX_TOKENS: int = 1500
LM_STUDIO_TEMPERATURE: float = 0.7
NARRATOR_ENABLED: bool = True

# ---------------------------------------------------------------------------
# LEDGER -- BUY OUTCOME TRACKING (Phase 1: Capture / Phase 2: Fill)
# ---------------------------------------------------------------------------
LEDGER_DIR: Path = MODELS_DIR / "ledger"
BUY_LEDGER_DB: Path = LEDGER_DIR / "buy_ledger.db"

# Minimum trading bars after signal_date required before fill is attempted.
# Must support longest horizon (20 days).
LEDGER_REALIZED_FILL_MIN_BARS: int = 20

# Signal classes to log to the ledger (confidence measurement covers these).
LEDGER_LOG_CLASSES: tuple[str, ...] = ("BUY", "WATCH")

# Price data source for counterfactual forward returns (Phase 2).
# "yfinance" = automated daily-close pull; swappable to "vp_export" or other.
LEDGER_PRICE_SOURCE: str = "yfinance"

# ---------------------------------------------------------------------------
# CHAIKIN ANALYTICS -- POWER GAUGE RATING (read-only, supplementary)
# ---------------------------------------------------------------------------
# Not part of the BUY/WATCH/PASS decision path (NFR-1). Attached to the
# P300 Obsidian note for P_400 context only.
CHAIKIN_BASE_URL: str = "https://members.chaikinanalytics.com"
CHAIKIN_SESSION_FILE: Path = MODELS_DIR / "chaikin_session.json"

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# ---------------------------------------------------------------------------
# BULK EXTRACTION (WO-P300-E2.001) -- Pipeline A-Bulk research pool
# ---------------------------------------------------------------------------
# Writes ONLY to models/research/bulk_research.db. Deliberately isolated
# from live catalog resolution three ways: subfolder (get_latest_catalog
# globs MODELS_DIR non-recursively), suffix does not match *catalog.db,
# and no digit prefix. Pipeline B NEVER reads this DB under WO-P300-E2.001.
DATA_BULK: Path = DATA_DIR / "bulk"
DATA_REFERENCE: Path = DATA_DIR / "reference"
RESEARCH_DIR: Path = MODELS_DIR / "research"
BULK_RESEARCH_DB: Path = RESEARCH_DIR / "bulk_research.db"
BULK_TEMP_DB: Path = RESEARCH_DIR / "temp_bulk_working.db"
BULK_CHECKPOINT_FILE: Path = RESEARCH_DIR / "bulk_extract_checkpoint.json"
SECTOR_MAP_CSV: Path = DATA_REFERENCE / "sector_map.csv"

# Input naming: <years>[I]_Pattern_<SYMBOL>.xlsx, sheet name = symbol, in
# data/bulk/. Window length is arbitrary (VP export lookback the operator
# chose at export time) -- glob accepts any digit-led filename; the reader's
# filename regex is the real validator. No minimum window length: column
# layout, header structure, and field semantics are verified identical
# across every window length tested (10/5/3/1-year, 6-month), so a shorter
# export is not lower-confidence data, just less history behind it.
BULK_INPUT_GLOB: str = "*_Pattern_*.xlsx"

# data_origin_type for bulk-scan instances (joins PATTERN_IDENT / EVAL_SET)
ORIGIN_BULK_SCAN: str = "BULK_SCAN"

# Detection tiers. STRICT = full decoded Potential Crossover v12 (minus the
# IntelliScan-proprietary Verified Resistance Zone, approximated via
# swing-high). RELAXED = STRICT minus the triple-cross-down reversal
# condition (continuation variant). Every detection is tagged with its tier.
BULK_TIER_STRICT: str = "STRICT"
BULK_TIER_RELAXED: str = "RELAXED"

# Spacing rule: suppress a detection within N bars of a prior detection on
# the same symbol + tier (prevents overlapping-window n inflation).
BULK_MIN_DETECTION_SPACING_BARS: int = 5

# Swing-high resistance approximation (Verified Resistance Zone stand-in):
# nearest pivot high above close within the lookback; a pivot high is a bar
# whose high exceeds the highs of PIVOT_BARS bars on each side.
BULK_SWING_HIGH_LOOKBACK_BARS: int = 60
BULK_SWING_HIGH_PIVOT_BARS: int = 3

# Bars per bulk pattern instance window (incl. anchor) -- matches the
# curated catalog's maximum window so bar-level rows stay comparable.
BULK_WINDOW_LENGTH: int = 20

# Trend-direction check depth (mirrors the scan's CheckTrendDays=2).
BULK_TREND_CHECK_BARS: int = 2

# Significant-move tag: forward_labels.significant_move_15 = 1 when
# abs(percent return) >= this threshold. Threshold is in PERCENT space;
# return_pct storage stays decimal-fraction (M-020) -- comparison converts.
BULK_SIGNIFICANT_MOVE_PCT: float = 15.0

# Feature version stamped on bulk instances (never reuses baseline_v1).
BULK_FEATURE_VERSION: str = "bulk_scan_v1"

# ---------------------------------------------------------------------------
# SECTOR ANALYSIS (WO-P300-E2.002) -- Phase 5, research catalog only
# ---------------------------------------------------------------------------
ASSET_CLASS_STOCK: str = "STOCK"
ASSET_CLASS_ETF: str = "ETF"
SECTOR_STATS_TABLE: str = "sector_stats"
SECTOR_ETF_LABEL: str = "Index/Diversified"
SECTOR_MIN_N_THRESHOLD: int = 30

# ---------------------------------------------------------------------------
# SCANNER LOOP (WO-P300-E3.001) -- nightly detector watchlist, report-only
# ---------------------------------------------------------------------------
# Tony runs IntelliScan's native crossover screen (whole universe, one
# action), bulk-exports the resulting candidates in the SAME format as the
# research-corpus bulk exports (<years>[I]_Pattern_<SYMBOL>.xlsx,
# BulkBarRaw shape -- reuses bulk_grid_reader.parse_bulk_file() and
# bulk_pattern_detector.detect_bulk_pattern() unchanged, no new parsing or
# detection logic). This WO re-applies the full 9-condition STRICT test to
# narrow VP's cruder native crossover call down to the same bar the
# research catalog uses. Point-in-time only (last bar per file) -- not a
# historical sweep.
#
# Deliberately a SUBFOLDER of DATA_BULK, not DATA_BULK itself:
# bulk_extract_pipeline's file discovery (input_dir.glob(BULK_INPUT_GLOB))
# is non-recursive, so nightly candidate files are structurally invisible
# to a future research-corpus bulk-extract run, and the permanent 126-file
# corpus can never get swept into a nightly scan.
DATA_BULK_NIGHTLY_SCAN: Path = DATA_BULK / "nightly_scan"

# Report-only output -- no DB write of any kind (keeps this WO out of
# WO-P300-E2.003's rejected-merge territory; the detector's opinion never
# enters the analog pool automatically).
SCANNER_REPORTS_DIR: Path = REPORTS_DIR / "scanner"

# Every file the scanner processes -- STRICT hit or not -- gets archived
# off the local disk into a monthly zip on the external backup drive.
# Naming: 10_Pattern_BulkCreate<MMMYY>.zip (e.g. ...BulkCreateJul26.zip).
# Confirmed 2026-07-12: this directory already holds an unrelated,
# unsuffixed one-time backup (10_Pattern_BulkCreate.zip, the original
# research-corpus source files) -- monthly-suffixed archives are additive,
# this WO's own stream, and never touch that file.
SCANNER_ARCHIVE_DIR: Path = Path(r"E:\AI-Agent-Learning-Hub_BackupFiles")
SCANNER_ARCHIVE_BASENAME: str = "10_Pattern_BulkCreate"

# ---------------------------------------------------------------------------
# OUTCOME-FIRST PATTERN MINER (WO-P300-E3.002) -- grid -> >=15% move screen
# -> operator approve -> catalog ingest
# ---------------------------------------------------------------------------
# Reuses bulk_labeler.compute_bulk_forward_labels() and its existing
# significant_move_15 flag UNCHANGED -- BULK_SIGNIFICANT_MOVE_PCT (15.0,
# set 2026-07-08) already IS this WO's threshold. MINE_MOVE_THRESHOLD is
# kept as a separate named constant (not a re-read of the bulk one) so a
# future change to one doesn't silently retune the other -- they answer
# different questions (bulk: is this move flag-worthy at all; mine: is
# this anchor a catalog candidate) even though today they're the same
# number by design.
MINE_MOVE_THRESHOLD: float = 0.15  # decimal fraction (M-020), not percent

# Deliberately separate from DATA_BULK_NIGHTLY_SCAN (WO-P300-E3.001) --
# different lifecycle purpose (files stay until phase 2 ingest completes)
# and a subfolder of DATA_BULK for the same reason nightly_scan is:
# bulk_extract_pipeline's glob is non-recursive, so this is structurally
# invisible to a future research-corpus extraction run.
DATA_BULK_MINE: Path = DATA_BULK / "mine"

MINE_REPORTS_DIR: Path = REPORTS_DIR / "mine"
MINE_CANDIDATES_CSV: str = "mine_candidates.csv"

# v2 (2026-07-14, "BulkAddPattern" process): auto-archive after a
# successful ingest-mined run -- Tony's explicit call, same E:\ drive as
# Scanner Loop's archive but a SEPARATE named constant + naming
# convention (date-first: <MMMYY>BULKPattern.zip, e.g. Jul26BULKPattern.
# zip -- vs Scanner Loop's basename-first 10_Pattern_BulkCreate<MMMYY>.
# zip). No per-entry rename (archive_mined_file.py uses xlsx_path.name
# as-is) -- unlike Scanner Loop's date-prefixed entries, these don't
# need per-entry disambiguation. Mined files are NOT one-shot like
# Pipeline A's -- archiving-and-deleting means a future re-mine of that
# symbol requires re-exporting from VP, a known, accepted tradeoff.
MINE_ARCHIVE_DIR: Path = Path(r"E:\AI-Agent-Learning-Hub_BackupFiles")
MINE_ARCHIVE_SUFFIX: str = "BULKPattern"

# WO-P300-E2.001 Phase 0 finding: VP backfills predictive columns only
# 5 years back from the EXPORT DATE -- a ROLLING window, not a fixed
# calendar date. M-102 (2026-07-17): previously frozen as date(2021,7,14)
# at v1.13 (2026-07-12); 5 days later that boundary was already stale,
# letting genuinely-still-backfilled bars pass this check and crash
# catalog_merge_io.py's PatternBarRecord validation on a real run.
# Computed fresh at import time -- every real run is a fresh process
# (PEH convention). FIRST-SAFE-DATE semantics (M-093): window start
# on/after this date is accepted (strict < rejects earlier). Original
# 2021-07-14 on 2026-07-12 = calendar 5yr + 2 days. Do NOT use
# today - (5*365+2): that lands ON the last zero-pred bar (confirmed
# 2026-07-17 CNK/GURE/LCID/NNDM/TWST: last_zero=2021-07-16,
# first_nz=2021-07-19) and the < gate lets it through.
_today = date.today()
try:
    _vp_backfill_edge = date(_today.year - 5, _today.month, _today.day)
except ValueError:
    # Feb 29 when target year is non-leap
    _vp_backfill_edge = date(_today.year - 5, 2, 28)
MINE_MIN_ANCHOR_DATE: date = _vp_backfill_edge + timedelta(days=2)

# Screening extends past FORWARD_HORIZONS' 20-day cap -- see
# pattern_miner.py v1.2 changelog. Tony's original framing was a
# "6-9 month window"; 180 trading days (~9 months) is the upper bound
# for the SCREENING decision only. Whether a long-duration find
# actually helps BUY/WATCH precision is an empirical question for the
# M-079 staging eval gate (WO-P300-E3.002 Phase 2), not something to
# pre-decide here by excluding it.
MINE_MAX_SCREEN_DAYS: int = 180

# v2.0 -- crossover-gated eligibility (replaces outcome-only screening,
# see pattern_miner.py v2.0 changelog). Measured, not guessed, from 66
# real ground-truth picks (2026-07-13 diagnostic): 95% land within 20
# bars of their own most-recent same-direction MT crossover (mtdiff sign
# flip); max observed was 39 on a confirmed-valid pick, next-highest 28.
# Deliberately reuses the same value as _MAX_STANDARD_HORIZON
# (max(FORWARD_HORIZONS)) -- not a coincidence the diagnostic was checked
# against that number specifically.
MINE_XOVER_MAX_BARS: int = 20

# Ignition vs continuation entry-tier split within MINE_XOVER_MAX_BARS.
# 50% of the 66 real picks land within 3 bars of crossover (median 4,
# p25=1) -- Tony's own style is roughly half ignition-day entries, half
# continuation entries a few bars into the confirmed trend (matches the
# CIEN head-to-head finding that condition 1 -- crossover exactly 1 bar
# ago -- failed on all 5 of his sampled picks there).
MINE_IGNITION_MAX_BARS: int = 3
