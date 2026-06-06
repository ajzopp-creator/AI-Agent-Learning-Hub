"""config.py — All paths and constants for the obsidian_writers package.

CHANGELOG:
  v2.1  2026-06-02  Added P400SIG signal-packet support: OUTPUT_FORMAT map,
                    SIGNALS_DIR, P400SIG folder + schema version. Enables the
                    JSON emit path for P_115 -> P_400 signal packets (Enh. 1).
  v2.0  2026-06-01  Bumped all SCHEMA_VERSIONS to 2.0 (Note Standard v1.1).
                    Added VERDICT_MAP for normalized cross-system verdict field.
  v1.0  2026-05-22  Initial version.
"""

from pathlib import Path

# ── HUB & VAULT PATHS ────────────────────────────────────────────────────────
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")

VAULT_ROOT = HUB_ROOT / "trading_journal"

# Raw JSON signal packets (P_115 -> P_400 handoff). Not Obsidian notes.
SIGNALS_DIR = VAULT_ROOT / "TradeOrderManagement" / "signals"

# ── SOURCE DATA PATHS ────────────────────────────────────────────────────────
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
    "P115":    "TradeManagement/P115",
    "P300":    "TradeManagement/P300",
    "P400":    "TradeManagement/P400",
    "P400SIG": "TradeOrderManagement/signals",
    "P020":    "TradeManagement/P020",
    "KB":      "KnowledgeBase",
}

# ── OUTPUT FORMAT MAP ────────────────────────────────────────────────────────
# Per-schema write format selected by write_handler.
#   "md"   → frontmatter note via vault_writer (verdict normalization + provenance)
#   "json" → raw JSON packet via json_writer (no frontmatter, no provenance)
OUTPUT_FORMAT: dict[str, str] = {
    "P115":    "md",
    "P300":    "md",
    "P400":    "md",
    "P400SIG": "json",
    "P020":    "md",
    "KB":      "md",
}

# ── SCHEMA VERSIONS ───────────────────────────────────────────────────────────
# v2.0 — Note Standard v1.1 fields added (signal_date, run_date, run_ts,
#         verdict, written_by, note_version, verdict_history).
# P_400 stays at 0.1 draft until P_400 project schema is locked.
SCHEMA_VERSIONS: dict[str, str] = {
    "P115":    "2.0",
    "P300":    "2.0",
    "P400":    "0.1",   # draft — evolves with P_400 build
    "P400SIG": "1.0",   # signal packet — locked per P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0
    "P020":    "2.0",
    "KB":      "2.0",
}

# ── VERDICT MAP ───────────────────────────────────────────────────────────────
# Maps each system's native classification value to the normalized verdict.
# Sending systems pass their native value; write_handler applies this map.
# All cross-system Dataview queries target the normalized 'verdict' field only.
VERDICT_MAP: dict[str, str] = {
    # P_300 native values (vocabulary already matches normalized set)
    "BUY":                  "BUY",
    "WATCH":                "WATCH",
    "PASS":                 "PASS",
    # P_115 native values
    "ASYM":                 "WATCH",
    # P_400 council verdicts
    "Approve":              "BUY",
    "Approve with Caution": "WATCH",
    "Block":                "PASS",
    "Override Required":    "WATCH",
    # P_020 — TBD; confirm when P_020 wired
}

# v2.0 Signal Schema — Compat Window Configuration
from datetime import datetime, date
from typing import Optional

COMPAT_WINDOW_DAYS = 14
CUTOVER_DATE: Optional[str] = None
DUAL_EMIT_ENABLED = True
SIGNAL_SCHEMA_VERSION = "v2.0"
SIGNAL_FOLDER = "TradeManagement/signals"

def cutover_passed() -> bool:
    """Check if cutover date has passed."""
    if not CUTOVER_DATE:
        return False
    try:
        cutover = datetime.strptime(CUTOVER_DATE, "%Y-%m-%d").date()
        return date.today() >= cutover
    except ValueError:
        raise ValueError(f"CUTOVER_DATE must be YYYY-MM-DD format, got {CUTOVER_DATE}")

def get_dual_emit_status() -> bool:
    """Get current dual-emit status."""
    return DUAL_EMIT_ENABLED and not cutover_passed()