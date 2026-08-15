"""P_400 Signal Reader ? configuration.

All constants, paths, and thresholds. No logic, no I/O.
"""

from pathlib import Path
from enum import Enum
from datetime import time

# --- Market hours (WO-P400-E4.005) ------------------------------------------
# Regular US equity session, Eastern time. No holiday calendar -- accepted
# limitation, same pattern as WO-P400-E2.023's weekday-count approximation.
MARKET_OPEN_TIME_ET: time = time(9, 30)
MARKET_CLOSE_TIME_ET: time = time(16, 0)

# --- Spread plausibility (WO-P400-E4.004) ------------------------------------
# Half-spread wider than this pct of price is treated as untrustworthy quote
# data (off-hours/illiquid), not a real fill-quality signal -- BLOCK before it
# corrupts realistic-fill R:R math. Found live 2026-07-26: CAE 18.6%, CDPYF
# 6.9%, both off-hours. Real liquid-stock spreads are well under 1%.
MAX_PLAUSIBLE_SPREAD_PCT: float = 2.0

# --- Hub roots --------------------------------------------------------------
HUB_ROOT: Path = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
VAULT_ROOT: Path = HUB_ROOT / "trading_journal"

# --- Signal source ----------------------------------------------------------
# P_800 routes SIGNAL_V2 packets here as *_v2.0.json (flat folder; signal_source
# field is authoritative - no per-source subfolders).
SIGNALS_DIR: Path = VAULT_ROOT / "TradeOrderManagement" / "signals"

# --- Signal archive ---------------------------------------------------------
# After evaluate_signal() completes, the source JSON is appended to the monthly
# zip here and deleted from SIGNALS_DIR. Filename pattern: YYMM_ProcessedJson.zip
SIGNALS_PROCESSED_DIR: Path = SIGNALS_DIR / "processed"

# --- Open-position book -----------------------------------------------------
BOOK_DIR: Path = VAULT_ROOT / "TradeOrderManagement" / "P400"  # moved WO-P800-E3.003 -- TradeManagement/P400 is now the dead folder (E2.012 fix superseded by vault rename)
PAPER_BOOK_DIR: Path = VAULT_ROOT / "TradeOrderManagement" / "P400" / "paper"  # WO-P800-E3.003: moved with BOOK_DIR root

# --- Cross-project config sources -------------------------------------------
PARAMS_PATH: Path = (
    HUB_ROOT
    / "projects"
    / "P_000_PythonClaudeLocalLLM"
    / "config"
    / "P_000_Account_Parameters_Current.md"
)
# P_010 RiskConfig.json is glob-discovered at read time (folder name drifts).
P010_GLOB_PATTERN: str = "**/P_010_RiskConfig.json"
# --- Schwab API (WO-P400-E4.001) --------------------------------------------
# app_key/app_secret point at P_020's existing config, not a duplicate P_400
# copy -- Tony's call 2026-07-24: one app registration, one place to rotate/
# secure it. P_020's file is untouched, still owns and runs it (Saturday
# weekly job unaffected). Only the TOKEN stays P_400-local (schwab-py
# rewrites the token file on every refresh -- two projects sharing one
# token file risks a race if both run near-simultaneously).
SCHWAB_CONFIG_PATH: Path = (
    HUB_ROOT / "projects" / "P_020_AJZStrategies_PerformanceAnalysisSystem"
    / "config" / "P_020_schwab_config.json"
)
SCHWAB_TOKEN_PATH: Path = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "config" / "P_400_schwab_token.json"

# --- Glob patterns ----------------------------------------------------------
V2_PATTERN: str = "*_v2.0.json"
LEGACY_PATTERN: str = "*_signal.json"  # P400SIG legacy, dual-read compat window

# --- Compat window ----------------------------------------------------------
# True  -> count legacy packets, do not parse them (tolerate during window).
# False -> ignore legacy entirely (post-cutover).
TOLERATE_LEGACY: bool = True

# --- Trade mode -------------------------------------------------------------
class TradeMode(str, Enum):
    REAL = "REAL"
    PAPER = "PAPER"

DEFAULT_TRADE_MODE: TradeMode = TradeMode.REAL

# --- Sizing / risk constants (Architecture v2.0 Section 8.1) ----------------
BASE_RISK_PCT: float = 1.5          # percent; P_000 authoritative - read live
MAX_POSITION_PCT: float = 5.0       # percent
MIN_ACCEPTABLE_RR: float = 2.0      # T1 minimum; LOCKED v2.0 (Section 3.6)
PORTFOLIO_HEAT_MAX_PCT: float = 12.0
MAX_CONCURRENT_POSITIONS: int = 8
DAILY_LOSS_CIRCUIT_BREAKER_PCT: float = 3.0
MAX_SECTOR_EXPOSURE: int = 2

# --- Signal / data freshness ------------------------------------------------
PRICE_STALENESS_THRESHOLD_SEC: int = 120
SIGNAL_AGE_MAX_TRADING_DAYS: int = 3  # flag signals older than N trading days

# --- Post-earnings stabilization (WO-P400-E2.023) ---------------------------
# CAUTION-only, never BLOCK (Tony directive 2026-07-24) -- backward-looking
# risk (gap-fade, spread/IV settling, invalidated structure) is a different
# kind than the forward-looking earnings-in-window BLOCK below; Tony wants
# to eyeball the chart, not get hard-stopped every time. Default matches
# P_115's V110.3 precedent (3-session stabilization window).
POST_EARNINGS_STABILIZATION_SESSIONS: int = 3

# --- Forward-looking earnings-in-window (MACRO BLOCK) -----------------------
# Was hardcoded as a single 14-calendar-day forward-only check inside
# evaluate_signal.py's _earnings_in_window(), with no backward bound at all
# (a past earnings date never aged out of the check). Split into explicit
# forward/backward windows and moved here 2026-07-28, Tony's call: 3 days
# forward, 2 days back.
EARNINGS_WINDOW_FORWARD_DAYS: int = 3
EARNINGS_WINDOW_BACKWARD_DAYS: int = 2
# --- Entry drift ------------------------------------------------------------
ENTRY_DRIFT_THRESHOLD_PCT: float = 1.5   # entry missed if drift > this % above guideline (Section 6.5)
# Favorable drift (live < guideline) never blocks -- R:R improves; use live price unconditionally.

# --- Stop constraints -------------------------------------------------------
MIN_STOP_ATR_MULTIPLE: float = 1.0
STOP_ATR_TOLERANCE: float = 0.005  # floating point buffer when stop == exactly 1xATR

# --- Options ----------------------------------------------------------------
OPTION_IV_RANK_SPREAD_PREF: float = 50.0  # IV rank above this -> prefer spread
OPTION_OI_MINIMUM: int = 150              # open interest floor (viability gate)
OPTION_SPREAD_MAX_PCT: float = 10.0       # max (ask-bid)/mid * 100 (viability gate)
OPTION_ATR_FLOOR_MULTIPLE: float = 2.0    # 2xATR floor for Risk-Budget-First method
OPTION_RR_PARITY_MIN: float = 1.0         # option R:R must be >= stock R:R * this

# --- Risk mode multipliers (OFF/CORRECTION=0.50, HALF=0.75, else 1.00) ------
RISK_MODE_MULTIPLIERS: dict = {
    "OFF": 0.50,
    "CORRECTION": 0.50,
    "HALF": 0.75,
    "STANDARD": 1.00,
    "FULL": 1.00,
    "HOT": 1.00,
}

# --- Council verdict tiers (WO-P400-E3.010) ---------------------------------
# Verdicts that reach STEP 6 (spec) in the SIP -- anything the pipeline
# considers a real trade, not just RISK-role annotation. cmd_evaluate uses
# this to decide whether to cache spec text (vs eval-fields only) so `spec`
# never cache-misses on an exact-string check again. Any future Council
# verdict tier addition that should also reach spec MUST be added here.
SPEC_CACHEABLE_VERDICTS: frozenset = frozenset({
    "APPROVED",
    "APPROVED_WITH_CAUTION",
    "APPROVED_WITH_SEVERE_WARNING",
})

# --- Logging ----------------------------------------------------------------
LOGGER_NAME: str = "p400.signal_reader"
LOG_DIR: Path = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "outputs" / "logs"  # session log file, WO-P400 session-log request 2026-07-30

# --- Option chain auto-selection (WO-P400-E4.002) ---------------------------
OPTION_SELECTION_TARGET_DELTA: float = 0.50   # Tony's explicit call, 2026-07-24
OPTION_SELECTION_MIN_DTE: int = 21            # research default, accepted
OPTION_SELECTION_MAX_DTE: int = 45            # research default, accepted

# --- Technical Dossier (WO-P400-E4.003) --------------------------------------
SMA_PERIODS: list = [20, 50, 100, 200]
RSI_PERIOD: int = 14
MACD_FAST: int = 12
MACD_SLOW: int = 26
MACD_SIGNAL: int = 9
BB_PERIOD: int = 20
BB_STDDEV: float = 2.0
FIB_LOOKBACK_BARS: int = 60   # matches TOS ThinkScript source exactly (confirmed 2026-07-24): swingHigh = Highest(high, 60), swingLow = Lowest(low, 60)

# --- Tier-2B batch runner (WO-P400-E5.003) ---------------------------------
# Ranking is a deterministic composite SCORE, never a probability. P_400 has
# no probability model. Weights sum to 1.0 and are tuning parameters, not
# calibrated estimates -- treat any change as a judgment call, not a fix.
BATCH_RANK_WEIGHT_RR: float = 0.35            # R:R at T1, normalized
BATCH_RANK_WEIGHT_ATR_HEADROOM: float = 0.30  # stop distance / ATR, above the 1.0x floor
BATCH_RANK_WEIGHT_SPREAD: float = 0.15        # tighter half-spread scores higher
BATCH_RANK_WEIGHT_LIQUIDITY: float = 0.10     # avg_volume_20d, log-scaled
BATCH_RANK_WEIGHT_DRIFT: float = 0.10         # smaller |drift| scores higher

# Normalization ceilings -- values at or above these score 1.0 on that factor.
# RR ceiling deliberately low: a 22.78 R:R off a 0.05 stop (INDI, 2026-08-05)
# must not dominate the sort just because the denominator was tiny.
BATCH_RANK_RR_CEILING: float = 6.0
BATCH_RANK_ATR_HEADROOM_CEILING: float = 3.0   # 3x ATR stop = full headroom credit
BATCH_RANK_SPREAD_CEILING_PCT: float = 1.0     # half-spread >= 1% of price scores 0
BATCH_RANK_VOLUME_FLOOR: float = 100_000       # at or below this, liquidity scores 0
BATCH_RANK_VOLUME_CEILING: float = 20_000_000  # log-scaled between floor and this

BATCH_MAX_SYMBOLS: int = 25                 # hard cap per batch-2b run
BATCH_EARNINGS_FILE_PATTERN: str = "earnings_{date}.json"  # session-scoped, python\
BATCH_EARNINGS_DIR: Path = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "python"

# --- Tier-2B batch report persistence (WO-P400-E5.003) ---------------------
BATCH_REPORT_DIR: Path = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "outputs" / "batch_reports"
BATCH_REPORT_FILE_PATTERN: str = "batch2b_{date}_{ts}.json"

# --- Earnings calendar automation (WO-P400-E5.002) --------------------------
# Nasdaq's public, unauthenticated endpoints -- not FMP. FMP's free tier
# proved too narrow to use (bulk earnings-calendar capped at ~73 large-cap
# symbols regardless of date range; CGON, a real live signal 2026-08-08 that
# HAD reported inside the pulled window, was absent; per-symbol fallback is
# paywalled, 402). Nasdaq's public calendar returned 585 companies for a
# single day (2026-08-06) including CGON, and its company-profile endpoint
# carries Sector for free, no key. Confirmed live 2026-08-08.
#
# Accepted risk: these are undocumented public endpoints (used widely by
# scrapers, not an official rate-limited developer API) -- no published SLA
# or rate limit. A User-Agent header is required or Nasdaq blocks the
# request; no API key exists to rotate.
#
# Per-DATE, not per-range (unlike FMP) -- the monthly refresh loops one call
# per day across the window, not one bulk call.
NASDAQ_API_BASE_URL: str = "https://api.nasdaq.com/api"
NASDAQ_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
EARNINGS_CALENDAR_CACHE_PATH: Path = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "python" / "earnings_calendar_cache.json"
LAST_SPREAD_CACHE_PATH: Path = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "python" / "last_spread_cache.json"  # WO-P400-E5.005
# Forward window + backward buffer -- no 3-month API cap to respect now (that
# was FMP-specific), kept at the same size since it still comfortably covers
# MACRO's tight 3-day-forward/2-day-back gate window with margin.
EARNINGS_CALENDAR_LOOKAHEAD_DAYS: int = 83
EARNINGS_CALENDAR_LOOKBACK_BUFFER_DAYS: int = 7
# Fixed-monthly-schedule staleness check (Tony's call, 2026-08-08): trust the
# pull date, don't spot-check symbols against the live API. ~30-day cadence
# + 5-day grace before earnings_lookup.py warns.
EARNINGS_CALENDAR_MAX_STALENESS_DAYS: int = 35