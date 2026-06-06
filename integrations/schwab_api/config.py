# config.py
# AI-Agent-Learning-Hub — Schwab API Integration
# Shared configuration for all projects using Schwab API

from pathlib import Path

# ── Hub Root ───────────────────────────────────────────────────────────────────
HUB_ROOT        = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
SCHWAB_ROOT     = HUB_ROOT / "integrations" / "schwab_api"
CREDENTIALS_DIR = SCHWAB_ROOT / "credentials"

# ── Schwab App ─────────────────────────────────────────────────────────────────
SCHWAB_APP_NAME     = "AJZ-Strategies-P020"
SCHWAB_CALLBACK_URL = "https://127.0.0.1"

# ── Token Config File (gitignored) ─────────────────────────────────────────────
SCHWAB_CONFIG_FILE = CREDENTIALS_DIR / "P_020_schwab_config.json"

# ── Token Expiry Windows ───────────────────────────────────────────────────────
ACCESS_TOKEN_EXPIRY_SECONDS = 1800   # 30 minutes
REFRESH_TOKEN_EXPIRY_DAYS   = 7

# ── P_020 Excel Log Paths ──────────────────────────────────────────────────────
LIVE_OPTIONS_LOG = Path(r"C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Options_Log_v1.xlsx")
LIVE_STOCK_LOG   = Path(r"C:\Users\Trader\Documents\AJZStrategiesLLC\2026_Operations\P_020_2026_AJZ_Strategies_Stock_Log_v1.xlsx")

# ── Tracker Dashboard ──────────────────────────────────────────────────────────
TRACKER_DASHBOARD = Path(r"C:\Users\Trader\Documents\AJZStrategiesLLC\P_115_TrackerAudit\P_115_118_TtrackerDashboard_V2.xlsx")

# ── P_020 Formula Column Protection ───────────────────────────────────────────
OPTIONS_FORMULA_COLS = ["M", "Q", "U", "W", "Y", "Z", "AA"]
STOCK_FORMULA_COLS   = ["J", "N", "P", "Q", "S", "T"]

# ── Defaults ───────────────────────────────────────────────────────────────────
DEFAULT_SYSTEM_NAME = "TOS_Import"

# ── Ensure credentials directory exists ───────────────────────────────────────
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
