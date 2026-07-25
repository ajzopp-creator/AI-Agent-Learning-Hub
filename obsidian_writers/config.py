"""config.py — All paths and constants for the obsidian_writers package.

CHANGELOG:
  v2.5  2026-07-24  Added APPROVED_WITH_SEVERE_WARNING to VERDICT_MAP -> "BUY"
                    (WO-P400-E3.011). Gap found live: SEVERE_WARNING verdict tier
                    added to P_400 council.py 2026-07-20, never propagated here --
                    defaulted to PASS via the no-mapping fallback until now. Tony
                    confirmed BUY (treat like plain APPROVED, since RISK-role
                    SEVERE_WARNING can never actually block a trade). P_800 Ack received 2026-07-24.
  v2.4  2026-07-10  Comment-only updates: references to the normalized
                    'verdict' field reworded to 'write_route' following the
                    WO-P400-E2.020 rename (see write_handler.py, vault_schemas.py,
                    frontmatter_builder.py, vault_writer.py). VERDICT_MAP itself
                    (name + mapping values) is unchanged — this file has no
                    functional change.
  v2.2  2026-06-07  Added SIGNAL_V2 (unified stock+option signal packet) alongside
                    P400SIG: OUTPUT_FORMAT, VAULT_FOLDER_MAP, SCHEMA_VERSIONS, and
                    JSON_FILENAME_SUFFIX (distinct filenames so v1.0 + v2.0 coexist
                    during the dual-emit window). P400SIG retired at cutover. (WO-P800-E2.001)
  v2.1  2026-06-02  Added P400SIG signal-packet support: OUTPUT_FORMAT map,
                    SIGNALS_DIR, P400SIG folder + schema version. Enables the
                    JSON emit path for P_115 -> P_400 signal packets (Enh. 1).
  v2.3  2026-06-16  Added APPROVED, APPROVED_WITH_CAUTION, BLOCKED, REVIEWED_NO_TRADE
                    to VERDICT_MAP (WO-P800-E2.004). Legacy Title Case keys retained as fallback.
                    Hub-root copy synced to P_800 project copy (editable install picks up Hub root).
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
    "P115":     "TradeManagement/P115",
    "P300":     "TradeManagement/P300",
    "P400":     "TradeManagement/P400",
    "P400_PAPER": "TradeManagement/P400/paper",
    "P400SIG":  "TradeOrderManagement/signals",
    "SIGNAL_V2": "TradeOrderManagement/signals",
    "P020":     "TradeManagement/P020",
    "KB":       "KnowledgeBase",
}

# ── OUTPUT FORMAT MAP ────────────────────────────────────────────────────────
# Per-schema write format selected by write_handler.
#   "md"   → frontmatter note via vault_writer (write_route normalization + provenance)
#   "json" → raw JSON packet via json_writer (no frontmatter, no provenance)
OUTPUT_FORMAT: dict[str, str] = {
    "P115":     "md",
    "P300":     "md",
    "P400":     "md",
    "P400_PAPER": "md",
    "P400SIG":  "json",
    "SIGNAL_V2": "json",
    "P020":     "md",
    "KB":       "md",
}

# ── JSON FILENAME SUFFIX MAP ──────────────────────────────────────────────────
# JSON signal schemas only. Appended before ".json" so legacy v1.0 and new v2.0
# packets coexist in the flat signals/ folder during the dual-emit window:
#   P400SIG    → YYYY-MM-DD_SYMBOL_signal.json   (legacy v1.0)
#   SIGNAL_V2  → YYYY-MM-DD_SYMBOL_v2.0.json      (unified stock+option)
JSON_FILENAME_SUFFIX: dict[str, str] = {
    "P400SIG":  "_signal",
    "SIGNAL_V2": "_v2.0",
}

# ── SCHEMA VERSIONS ───────────────────────────────────────────────────────────
# v2.0 — Note Standard v1.1 fields added (signal_date, run_date, run_ts,
#         write_route, written_by, note_version, write_route_history).
# P_400 stays at 0.1 draft until P_400 project schema is locked.
SCHEMA_VERSIONS: dict[str, str] = {
    "P115":     "2.0",
    "P300":     "2.0",
    "P400":     "0.1",   # draft — evolves with P_400 build
    "P400_PAPER": "0.1",   # same shape as P400, paper-book routing (WO-P400-E2.019)
    "P400SIG":  "1.0",   # signal packet — locked per P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0
    "SIGNAL_V2": "2.0",  # unified signal packet — P_115_P400_SIGNAL_PACKET_SCHEMA_v2_0
    "P020":     "2.0",
    "KB":       "2.0",
}

# ── VERDICT MAP ───────────────────────────────────────────────────────────────
# Maps each system's native classification value to the normalized write_route.
# Sending systems pass their native value; write_handler applies this map.
# All cross-system Dataview queries target the normalized 'write_route' field only.
VERDICT_MAP: dict[str, str] = {
    # P_300 native values (vocabulary already matches normalized set)
    "BUY":                  "BUY",
    "WATCH":                "WATCH",
    "PASS":                 "PASS",
    # P_115 native values
    "ASYM":                 "WATCH",
    # P_400 council verdicts (UPPER_SNAKE — values emitted by P_400 cli.py)
    "APPROVED":             "BUY",
    "APPROVED_WITH_CAUTION": "WATCH",
    "APPROVED_WITH_SEVERE_WARNING": "BUY",
    "BLOCKED":              "PASS",
    "REVIEWED_NO_TRADE":    "PASS",
    # P_400 legacy Title Case (pre-E2.004 fallback; keep until confirmed retired)
    "Approve":              "BUY",
    "Approve with Caution": "WATCH",
    "Block":                "PASS",
    "Override Required":    "WATCH",
    # P_020 — TBD; confirm when P_020 wired
}
