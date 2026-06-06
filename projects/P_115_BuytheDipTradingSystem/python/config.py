"""config.py — P_115 signal emitter configuration.

All paths, naming patterns, enumerations, and validation regexes for the
P_115 -> P_400 signal packet emitter. No logic and no I/O live here.
"""

from __future__ import annotations

from pathlib import Path

# --- Paths -----------------------------------------------------------------
HUB_ROOT: Path = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
SIGNALS_DIR: Path = (
    HUB_ROOT / "trading_journal" / "TradeOrderManagement" / "signals"
)

# --- Naming ----------------------------------------------------------------
# Schema-doc filename for seq 1: "YYYY-MM-DD_SYMBOL_signal.json".
# Seq >= 2 appends "_NNN" so same-day same-symbol signals never overwrite.
FILENAME_BASE: str = "{date}_{symbol}_signal"
FILENAME_EXT: str = ".json"
SIGNAL_ID_PATTERN: str = "P115-{date}-{symbol}-{seq:03d}"

# --- Enumerations (from signal packet schema v1.0) -------------------------
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

# --- Validation patterns ---------------------------------------------------
TICKER_REGEX: str = r"^[A-Z][A-Z0-9.]{0,5}$"
DATE_REGEX: str = r"^\d{4}-\d{2}-\d{2}$"
# Accepts "3-5 days", "1-2 weeks", "5 days", "2 weeks".
HORIZON_REGEX: str = r"^\d+(-\d+)?\s+(day|days|week|weeks)$"

JSON_INDENT: int = 2