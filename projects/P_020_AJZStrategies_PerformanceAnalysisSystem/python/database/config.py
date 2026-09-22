"""P_020 Configuration â€” all paths and constants for the database layer."""

import json
import logging
import winreg
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
def get_onedrive_root() -> Path:
    """Read the live OneDrive root path from the registry.

    The OneDrive environment variable is set by the OneDrive client after
    logon and is NOT reliably inherited by long-running or non-interactive
    processes (MCP relay processes, scheduled tasks, services) started
    before or outside that logon chain -- confirmed live 2026-09-19: a
    script launched via Start-Process through the windows-mcp relay saw
    os.environ.get("OneDrive") as None even though HKCU\\Environment\\
    OneDrive was set. The registry key itself is always current regardless
    of process lineage, so read it directly instead of trusting the
    environment variable. Never hardcode the drive letter elsewhere --
    call this function.

    Falls back to the last-known path (D:\\OneDrive, confirmed live
    2026-09-19) if the registry read fails for any reason, logging a
    warning so a silently wrong path never goes unnoticed.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
            value, _ = winreg.QueryValueEx(key, "OneDrive")
        return Path(value)
    except OSError as e:
        logger.warning(
            f"Could not read OneDrive path from registry ({e}); "
            f"falling back to last-known path D:\\OneDrive"
        )
        return Path(r"D:\OneDrive")


TRACKER_DASHBOARD = (
    get_onedrive_root()
    / "Documents" / "AJZStrategiesLLC"
    / "P_115_TrackerAudit" / "P_115_118_TrackerDashboard_V2.xlsx"
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

# ThinkLog tags are written by Tony himself at/near order time, usually
# the evening before the fill (real cases: SHEL tag 07-07, fill 07-08;
# MRK tag 07-12, fill 07-13). Same forward-only reasoning as the vault
# window above, smaller default since the gap is Tony's own typing habit
# rather than a multi-day signal-to-fill lag -- 3 days covers a Friday
# evening note landing on a Monday fill.
# tag_date <= open_date <= tag_date + THINKLOG_MATCH_FORWARD_DAYS
THINKLOG_MATCH_FORWARD_DAYS = 3

# P_820 (Order Signal Capture) outranks even ThinkLog -- it is dictated
# live, structured, with no export-lag or re-parsing risk. Same forward-
# only reasoning and default window as ThinkLog above.
P820_MATCH_FORWARD_DAYS = 3

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



# -- Schwab OAuth login operator (WO-P020-E1.010) ---------------------
# P_020 runs the login flow for itself AND P_400 (one app registration,
# Tony's call 2026-07-24). Each project keeps its OWN token file -- no
# sharing one file across projects (schwab-py refresh-race risk).
SCHWAB_TOKEN_FILE = CONFIG_DIR / "P_020_schwab_token.json"

AUTH_TOKEN_PATHS = {
    "P_020": SCHWAB_TOKEN_FILE,
    "P_400": (
        PROJECT_ROOT.parent / "P_400_TradeOrderManagement"
        / "config" / "P_400_schwab_token.json"
    ),
}


# -- P_000 Account Parameters (WO-P020-E1.009) -------------------------
# Owned by P_000, not P_020 -- confirmed path (also referenced by P_400's
# config.py). P_020 writes two reference rows here after every balance
# pull; Tony still hand-maintains Account Balance/Risk/Max monthly.
P000_PARAMS_FILE = (
    PROJECT_ROOT.parent / "P_000_PythonClaudeLocalLLM"
    / "config" / "P_000_Account_Parameters_Current.md"
)


# -- Cash-settled option roots for auto-close-on-expiration (WO-P020-E1.018) --
# 0DTE options on these underlyings settle in cash with no closing Schwab
# transaction -- see domain/expiration_closer.py. DELIBERATELY NOT auto-
# detected: Schwab's own transaction data gives no reliable field to tell a
# cash-settled index option (NDXP) apart from an assignable equity/ETF
# option (SPY) -- assetType is "OPTION" and type is "VANILLA" for both,
# confirmed by scanning every live pull file on disk 2026-09-15. Getting
# this list wrong would misrepresent a real assignment as a cash close and
# silently lose the resulting stock position -- add a symbol here only on
# Tony's explicit confirmation it is cash-settled (SPX/SPXW/RUT/RUTW/XSP/VIX
# are the standard CBOE cash-settled index roots if this list ever grows).
CASH_SETTLED_OPTION_ROOTS = frozenset({"NDXP"})

# Minimum whole days past expiration before a 0DTE position is eligible for
# auto-close. Guards the "hasn't settled yet" false-positive risk named in
# WO-P020-E1.018's own Acceptance Criteria -- same-day is never eligible,
# even if the option's instrument.closingPrice already looks final.
EXPIRATION_CLOSE_BUFFER_DAYS = 1


# -- Analysis start-date defaults (WO-P020-E1.020) ----------------------
# Used by stats_export.py / generate_dashboard.py when --start-date is
# not passed on the command line. A CLI --start-date always overrides
# these. PAPER's 2026-06-01 is Tony's own change-control reset point
# (documented 2026-09-05, WO-P000-E22.001 draft -- never approved, so
# this is the first place it's actually enforced). LIVE stays at
# 2026-01-01 by Tony's explicit choice 2026-09-19: once --start-date
# exists as a real parameter, there is no need to move the default too.
PAPER_ANALYSIS_START_DATE = "2026-06-01"
LIVE_ANALYSIS_START_DATE  = "2026-01-01"
