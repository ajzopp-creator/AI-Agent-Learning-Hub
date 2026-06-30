"""Direct system assignment for 22 schwab_api TOS_Import trades — 2026 scope."""

import sys
import sqlite3
import logging

sys.path.insert(0, r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database')
from config import DATABASE_FILE

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# (open_date, underlying_symbol, assign_system)
ASSIGNMENTS = [
    ("2026-03-24", "IAU",   "P_300"),
    ("2026-03-27", "QQQ",   "P_115"),
    ("2026-04-13", "DOW",   "P_116"),
    ("2026-04-15", "DOW",   "P_116"),
    ("2026-04-20", "AA",    "P_116"),
    ("2026-04-21", "AEO",   "P_115"),
    ("2026-04-21", "VOD",   "P_300"),
    ("2026-05-08", "EWZ",   "P_115"),
    ("2026-05-14", "SU",    "P_115"),
    ("2026-05-18", "C",     "P_116"),
    ("2026-05-21", "AMZN",  "P_116"),
    ("2026-05-26", "SBUX",  "SNT"),
    ("2026-05-26", "XYZ",   "SNT"),
    ("2026-05-27", "ADM",   "P_116"),
    ("2026-05-27", "GOOGL", "P_116"),
    ("2026-06-01", "COP",   "SNT"),
    ("2026-06-01", "EBAY",  "SNT"),
    ("2026-06-08", "AA",    "SNT"),
    ("2026-06-08", "XYZ",   "SNT"),
    ("2026-06-09", "AAL",   "P_116"),
    ("2026-06-11", "LION",  "P_116"),
]

def run(dry_run=True):
    conn = sqlite3.connect(DATABASE_FILE)
    updated = 0

    for open_date, symbol, system in ASSIGNMENTS:
        cur = conn.execute("""
            SELECT trade_id FROM trades
            WHERE open_date = ? AND underlying_symbol = ?
            AND system = 'TOS_Import' AND source = 'schwab_api'
        """, (open_date, symbol))
        rows = cur.fetchall()

        if not rows:
            logger.info(f"  NOT FOUND  {open_date}  {symbol}")
            continue

        for (trade_id,) in rows:
            logger.info(f"  {'DRY' if dry_run else 'SET'}  {open_date}  {symbol}  ->  {system}  (id={trade_id})")
            if not dry_run:
                conn.execute(
                    "UPDATE trades SET system=?, updated_at=CURRENT_TIMESTAMP WHERE trade_id=?",
                    (system, trade_id)
                )
            updated += 1

    if not dry_run:
        conn.commit()
    conn.close()
    logger.info(f"\n{'DRY RUN — ' if dry_run else ''}Updated: {updated} / {len(ASSIGNMENTS)} assignments")

if __name__ == "__main__":
    dry_run = "--commit" not in sys.argv
    if dry_run:
        logger.info("DRY RUN — pass --commit to write\n")
    run(dry_run)
