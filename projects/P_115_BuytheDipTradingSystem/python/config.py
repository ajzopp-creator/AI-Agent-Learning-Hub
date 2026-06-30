"""config.py -- P_115 signal emitter configuration.

All paths, naming patterns, enumerations, and validation regexes for the
P_115 -> P_400 signal packet emitter. No logic and no I/O live here.

CHANGELOG:
  v2.0  2026-06-11  SIGNAL_V2 migration (WO-P115-E1.001 / WO-P800-E2.001).
                    VAULT_SCHEMA updated to SIGNAL_V2. Filename pattern updated
                    to _v2.0.json. P400SIG / v1.0 constants retired.
  v1.0  (legacy)    P400SIG / _signal.json naming.
"""

from __future__ import annotations

from pathlib import Path

# --- Paths ------------------------------------------------------------------
HUB_ROOT: Path = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
SIGNALS_DIR: Path = (
    HUB_ROOT / "trading_journal" / "TradeOrderManagement" / "signals"
)

# --- Vault schema -----------------------------------------------------------
# SIGNAL_V2 is the canonical unified stock+option packet (WO-P800-E2.001).
# P400SIG (v1.0 legacy) is retired -- do not use.
VAULT_SCHEMA: str = "SIGNAL_V2"

# --- Naming -----------------------------------------------------------------
# v2.0 filename: "YYYY-MM-DD_SYMBOL_v2.0.json"
FILENAME_BASE: str = "{date}_{symbol}_v2.0"
FILENAME_EXT: str = ".json"
SIGNAL_ID_PATTERN: str = "P115-{date}-{symbol}-{seq:03d}"

# --- Enumerations -----------------------------------------------------------
DEFAULT_SOURCE: str = "P_115"
VALID_SOURCES: frozenset[str] = frozenset({"P_115", "P_300", "manual"})
VALID_CONFIDENCE: frozenset[str] = frozenset({"HIGH", "MEDIUM", "LOW"})
KNOWN_STRATEGIES: tuple[str, ...] = (
    "dip_buy",
    "breakout",
    "mean_reversion",
    "support_bounce",
)
KNOWN_TIMEFRAMES: tuple[str, ...] = ("1D", "4H", "1H", "30m", "15m")

# --- Validation patterns ----------------------------------------------------
TICKER_REGEX: str = r"^[A-Z][A-Z0-9.]{0,5}$"
DATE_REGEX: str = r"^\d{4}-\d{2}-\d{2}$"
HORIZON_REGEX: str = r"^\d+(-\d+)?\s+(day|days|week|weeks)$"

JSON_INDENT: int = 2