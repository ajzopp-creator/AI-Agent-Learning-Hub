"""Re-match TOS_Import trades sourced from Schwab API against the Tracker Dashboard."""

import sys
import sqlite3
import logging
from pathlib import Path

sys.path.insert(0, r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database')

from config import DATABASE_FILE
from infrastructure.tracker_reader import load_tracker_lookup, match_system

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

DEFAULT_SINCE = "2026-01-01"


def get_since():
    for arg in sys.argv:
        if arg.startswith("--since="):
            return arg.split("=", 1)[1]
    return DEFAULT_SINCE


def load_unmatched(conn, since):
    c = conn.cursor()
    c.execute("""
        SELECT trade_id, open_date, underlying_symbol
        FROM trades
        WHERE system = 'TOS_Import'
        AND source = 'schwab_api'
        AND open_date >= ?
        ORDER BY open_date
    """, (since,))
    cols = [d[0] for d in c.description]
    return [dict(zip(cols, row)) for row in c.fetchall()]


def rematch(dry_run=False):
    since = get_since()
    conn = sqlite3.connect(DATABASE_FILE)
    trades = load_unmatched(conn, since)

    if not trades:
        logger.info(f"No schwab_api TOS_Import trades found since {since} — nothing to do.")
        conn.close()
        return

    logger.info(f"{'DRY RUN — ' if dry_run else ''}Rematching {len(trades)} trades since {since}...")
    logger.info("")

    lookup = load_tracker_lookup()
    if lookup is None:
        logger.error("Tracker Dashboard could not be loaded — aborting.")
        conn.close()
        return

    matched = unmatched = 0

    for t in trades:
        system = match_system(lookup, t["underlying_symbol"], t["open_date"])
        if system == "TOS_Import":
            logger.info(f"  NO MATCH  {t['open_date']}  {t['underlying_symbol']}")
            unmatched += 1
        else:
            logger.info(f"  {'DRY' if dry_run else 'SET'}  {t['open_date']}  {t['underlying_symbol']}  ->  {system}")
            if not dry_run:
                conn.execute(
                    "UPDATE trades SET system=?, updated_at=CURRENT_TIMESTAMP WHERE trade_id=?",
                    (system, t["trade_id"])
                )
            matched += 1

    if not dry_run:
        conn.commit()

    conn.close()
    logger.info("")
    logger.info(f"Matched: {matched}  Unmatched: {unmatched}")
    if unmatched:
        logger.info("Unmatched trades not in Tracker — likely DAY/SNT or missing from Tracker.")


if __name__ == "__main__":
    dry_run = "--commit" not in sys.argv
    if dry_run:
        logger.info("DRY RUN — pass --commit to write changes")
    rematch(dry_run=dry_run)
