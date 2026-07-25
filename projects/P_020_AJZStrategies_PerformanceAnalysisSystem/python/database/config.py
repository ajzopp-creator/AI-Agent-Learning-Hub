"""P_020 Configuration â€” all paths and constants for the database layer."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# â”€â”€ Project root â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PROJECT_ROOT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem"
)

# â”€â”€ Config paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CONFIG_DIR         = PROJECT_ROOT / "config"
PARAMS_FILE        = CONFIG_DIR   / "P_020_Account_Params.json"
SCHWAB_CONFIG_FILE = CONFIG_DIR   / "P_020_schwab_config.json"

# â”€â”€ Data paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DATA_DIR       = PROJECT_ROOT / "data"
DATABASE_DIR   = DATA_DIR     / "database"
DATABASE_FILE  = DATABASE_DIR / "P_020_trades.db"
API_PULLS_DIR  = DATA_DIR     / "api_pulls"
EXPORTS_DIR    = DATA_DIR     / "exports"
AI_REVIEW_DIR  = EXPORTS_DIR  / "ai_review"

# â”€â”€ Audit logs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
AUDIT_LOGS_DIR = PROJECT_ROOT / "audit_logs"

# â”€â”€ Last run tracker â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
LAST_RUN_FILE  = API_PULLS_DIR / "P_020_last_run.json"

# â”€â”€ Master analytics files (Power Query view layer) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
LIVE_OPTIONS_LOG = (
    EXPORTS_DIR
    / "P_020_Master_Query_2026_AJZ_Strategies_Options_Analytics_V1.xlsx"
)
LIVE_STOCK_LOG = (
    EXPORTS_DIR
    / "P_020_Master_Query_2026_AJZ_Strategies_Stock_Analytics_V1.xlsx"
)

# â”€â”€ Tracker Dashboard (signal source lookup) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# V2 is the master â€” 998 rows, correct SignalSource column
TRACKER_DASHBOARD = Path(
    r"D:\OneDrive\Documents\AJZStrategiesLLC"
    r"\P_115_TrackerAudit\P_115_118_TrackerDashboard_V2.xlsx"
)

# â”€â”€ Power Query CSV export files â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
OPTIONS_EXPORT_FILE = EXPORTS_DIR / "P_020_options_export.csv"
STOCKS_EXPORT_FILE  = EXPORTS_DIR / "P_020_stocks_export.csv"

# â”€â”€ Python executable â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"

# -- Obsidian vault export scope (WO-P020-E1.005) ---------------------
# Pre-2026 backlog (324 rows) stays frozen unless Tony overrides with --all-history
VAULT_EXPORT_START_DATE = "2026-01-01"


# -- P_400 vault system attribution (WO-P020-E1.007 / shadow mode) ----
# Folder is resolved at read time via P_800's obsidian_writers config
# (VAULT_ROOT + VAULT_FOLDER_MAP) -- never hardcoded here, so the pending
# WO-P800-E3.003 rename (TradeManagement -> TradeOrderManagement) does not
# break this project.
VAULT_P400_SCHEMAS = ("P400", "P400_PAPER")

# SHADOW MODE: vault result is computed and logged, never written to
# trades.system. Tracker Dashboard stays authoritative until shadow data
# justifies the cutover. Flip to False only under a new work order.
VAULT_SHADOW_MODE = True

# Signal date always precedes the fill, so the window is forward-only --
# the Tracker's symmetric +/-3 day walk is wrong for vault records.
# signal_date <= open_date <= signal_date + VAULT_MATCH_FORWARD_DAYS
VAULT_MATCH_FORWARD_DAYS = 7

# Only records representing real intent can match. DROPPED is excluded:
# a BLOCKED/dropped signal means the trade was NOT taken, so matching it
# to a later fill of the same symbol attributes a trade to a signal that
# was passed on (verified 2026-07-25: MS dropped 07-02, filled 07-23).
VAULT_MATCHABLE_STATUSES = frozenset(
    {"PAPER", "SUBMITTED", "FILLED", "OPEN", "CLOSED"}
)

# Frontmatter keys checked for system attribution, in priority order.
# p115_linked / p300_linked are deliberately NOT used: 189 of 191 records
# carry p300_linked=true, which is a schema default rather than real
# attribution, and would generate confident wrong matches.
VAULT_ATTRIBUTION_FIELDS = ("why_code", "signal_source")


def load_params() -> dict:
    """Load business parameters from P_020_Account_Params.json.

    Returns:
        dict: Parsed parameter values.

    Raises:
        FileNotFoundError: If the params file does not exist.
    """
    if not PARAMS_FILE.exists():
        raise FileNotFoundError(
            f"Params file not found: {PARAMS_FILE}\n"
            f"Expected at: config\\P_020_Account_Params.json"
        )
    with open(PARAMS_FILE, "r", encoding="utf-8") as f:
        params = json.load(f)
    logger.debug(f"Params loaded from: {PARAMS_FILE}")
    return params

