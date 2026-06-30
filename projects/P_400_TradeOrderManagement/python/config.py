"""P_400 Signal Reader ? configuration.

All constants, paths, and thresholds. No logic, no I/O.
"""

from pathlib import Path
from enum import Enum

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
BOOK_DIR: Path = VAULT_ROOT / "TradeManagement" / "P400"  # fixed WO-P400-E2.012 -- was pointing at a dead folder
PAPER_BOOK_DIR: Path = VAULT_ROOT / "TradeOrderManagement" / "P400" / "paper"

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

# --- Logging ----------------------------------------------------------------
LOGGER_NAME: str = "p400.signal_reader"
