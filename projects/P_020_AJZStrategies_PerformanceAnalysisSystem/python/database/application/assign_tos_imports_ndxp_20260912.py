"""Direct system assignment for 5 schwab_api TOS_Import trades -- 2026-09-12 weekly pull.

Tony's rules (2026-09-12): unmatched NDXP trades from the weekly Schwab pull
belong to system P_210; symbol P belongs to P_116. Scoped to this week's
pull only, keyed on trade_id (not date/symbol matching) -- see
P_020_Weekly_Audit_20260912_113954.txt.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\assign_tos_imports_ndxp_20260912.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""

import logging
import sqlite3
import sys

sys.path.insert(0, r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database')
from config import DATABASE_FILE

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# (trade_id, open_date, underlying_symbol, assign_system) -- trade_id is the
# actual match key; the rest is here for readable log lines only.
ASSIGNMENTS = [
    (3159, "2026-09-11", "NDXP", "P_210"),
    (3160, "2026-09-09", "NDXP", "P_210"),
    (3162, "2026-09-09", "NDXP", "P_210"),
    (3163, "2026-09-11", "NDXP", "P_210"),
    (3161, "2026-09-08", "P", "P_116"),
]


def run(dry_run: bool = True) -> None:
    """Apply the NDXP -> P_210 assignments, guarded by trade_id + current system.

    Args:
        dry_run: If True (default), log intended changes without writing.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    updated = 0

    for trade_id, open_date, symbol, system in ASSIGNMENTS:
        cur = conn.execute(
            "SELECT trade_id FROM trades "
            "WHERE trade_id = ? AND system = 'TOS_Import' AND source = 'schwab_api'",
            (trade_id,),
        )
        row = cur.fetchone()

        if row is None:
            logger.info(f"  SKIP (not TOS_Import/schwab_api)  id={trade_id}  {open_date}  {symbol}")
            continue

        logger.info(f"  {'DRY' if dry_run else 'SET'}  {open_date}  {symbol}  -> {system}  (id={trade_id})")
        if not dry_run:
            conn.execute(
                "UPDATE trades SET system = ?, updated_at = CURRENT_TIMESTAMP WHERE trade_id = ?",
                (system, trade_id),
            )
        updated += 1

    if not dry_run:
        conn.commit()
    conn.close()
    logger.info(f"\n{'DRY RUN — ' if dry_run else ''}Updated: {updated} / {len(ASSIGNMENTS)} assignments")


if __name__ == "__main__":
    dry_run_flag = "--commit" not in sys.argv
    if dry_run_flag:
        logger.info("DRY RUN — pass --commit to write\n")
    run(dry_run_flag)
