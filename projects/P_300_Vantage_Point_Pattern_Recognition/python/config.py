"""
FILE: config.py
VERSION: 1.8
DATE: 2026-06-28
AUTHOR: Anthony Zoppi + Claude
LAYER: config
DESCRIPTION:
    Single source of truth for all paths, constants, and thresholds in P_300.
    Every layer (domain, infrastructure, application) imports values from here.
    No hardcoded paths exist anywhere else in the codebase.

    Per architecture v2.4 §2.4: HUB_ROOT is the only hardcoded path; catalog
    DB resolution flows through db_utils.get_latest_catalog().

CHANGELOG:
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
# LOGGING
# ---------------------------------------------------------------------------
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
