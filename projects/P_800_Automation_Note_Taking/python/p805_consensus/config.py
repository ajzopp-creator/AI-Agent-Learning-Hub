"""config.py -- P_805 Consensus Dashboard configuration.

Joins P_805 candidate history (ranked.csv) against the P_115/P_118
Tracker Log to populate Dashboard.md's P_805 Consensus section.
Origin: WO-P800-E6.001.
"""

from __future__ import annotations

import os
from pathlib import Path

# -- PATHS -------------------------------------------------------------
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")

RANKED_CSV_DIR = (
    HUB_ROOT / "projects" / "P_805_Email_Trade_Extractor" / "data" / "daily"
)
RANKED_CSV_SUFFIX = "_ranked.csv"

DASHBOARD_PATH = HUB_ROOT / "trading_journal" / "Dashboard.md"
SECTION_START_MARKER = "<!-- P805-CONSENSUS-START -->"
SECTION_END_MARKER = "<!-- P805-CONSENSUS-END -->"

# Real tracker lives in OneDrive -- never hardcode the drive letter.
# Verified live 2026-09-08 (WO-P800-E6.001): resolves to
# D:\OneDrive\Documents\AJZStrategiesLLC\P_115_TrackerAudit\...
if "OneDrive" not in os.environ:
    raise EnvironmentError(
        "OneDrive environment variable not set -- cannot resolve the "
        "Tracker workbook path. Run from a normal user session, not "
        "the Windows-MCP bridge (see WO-P800-E6.001)."
    )

TRACKER_PATH = (
    Path(os.environ["OneDrive"])
    / "Documents"
    / "AJZStrategiesLLC"
    / "P_115_TrackerAudit"
    / "P_115_118_TrackerDashboard_V2.xlsx"
)

TRACKER_SHEET_NAME = "Tracker Log"
TRACKER_DATE_COL = "Date"
TRACKER_SYMBOL_COL = "Symbol"
TRACKER_VERDICT_COL = "Step1Verdict"

# -- JOIN RULES ----------------------------------------------------------
COUNTED_VERDICTS = {"BUY", "ASYM"}
JOIN_WINDOW_TRADING_DAYS = 45  # was 15 (P_115 default); raised 2026-09-21 --
# lag analysis of real Tracker hits (302 source-ticker pairs, 12 hits) showed
# 15 days caught only 17% of real BUY/ASYM confirmations, median lag 36
# trading days -- see WO-P800-E6.001 Occurrence Log. 45 captures ~75%.

# -- TABLE FORMAT ----------------------------------------------------------
TABLE_HEADER = (
    "| Email Source | Today's Symbols | MTD Candidates | YTD Candidates "
    "| MTD BUY/ASYM | YTD BUY/ASYM |"
)
TABLE_DIVIDER = "|---|---|---|---|---|---|"