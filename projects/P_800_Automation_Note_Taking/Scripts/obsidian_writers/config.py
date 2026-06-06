"""config.py — All paths and constants for the obsidian_writers package."""

from pathlib import Path

# ── HUB & VAULT PATHS ────────────────────────────────────────────────────────
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")

VAULT_ROOT = HUB_ROOT / "trading_journal"

# ── SOURCE DATA PATHS ─────────────────────────────────────────────────────────
P115_TRACKER_PATH = (
    HUB_ROOT
    / "projects"
    / "P_115_BuytheDipTradingSystem"
    / "data"
    / "P_115_TrackerDashboard_V3.xlsx"
)

P300_REPORTS_DIR = (
    HUB_ROOT
    / "projects"
    / "P_300_Vantage_Point_Pattern_Recognition"
    / "data"
    / "reports"
)

# P_020 uses SQLite — path supplied by p020_writer at call time
# P_400 uses TXT files — path supplied by p400_writer at call time

# ── VAULT FOLDER MAP ──────────────────────────────────────────────────────────
# Maps schema_name → vault subfolder relative to VAULT_ROOT
VAULT_FOLDER_MAP: dict[str, str] = {
    "P115": "TradeManagement/P115",
    "P300": "TradeManagement/P300",
    "P400": "TradeManagement/P400",
    "P020": "TradeManagement/P020",
    "KB":   "KnowledgeBase",
}

# ── SCHEMA VERSIONS ───────────────────────────────────────────────────────────
SCHEMA_VERSIONS: dict[str, str] = {
    "P115": "1.0",
    "P300": "1.0",
    "P400": "0.1",   # draft — evolves with P_400 build
    "P020": "1.0",
    "KB":   "1.0",
}
