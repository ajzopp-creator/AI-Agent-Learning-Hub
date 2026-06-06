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

