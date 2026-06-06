"""Generate a manual review CSV for TOS_Import trades awaiting system assignment."""

import sys
import csv
import logging
import sqlite3
from datetime import date
from pathlib import Path

sys.path.insert(0, r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database')

from config import DATABASE_FILE, EXPORTS_DIR

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

REVIEW_CSV  = EXPORTS_DIR / "tos_import_review.csv"
IMPORT_CSV  = EXPORTS_DIR / "tos_import_review_updated.csv"
VALID_SYSTEMS = {"P_115","P_116","P_117","P_118","P_300","P_910","P_920","SNT","Day","DAY","TOS_Import"}


def load_tos_imports(conn):
    c = conn.cursor()
    c.execute("""
        SELECT trade_id, open_date, underlying_symbol, asset_type, direction
        FROM trades
        WHERE system = 'TOS_Import'
        AND source = 'tos_import'
        ORDER BY open_date
    """)
    cols = [d[0] for d in c.description]
    return [dict(zip(cols, row)) for row in c.fetchall()]


def generate_review():
    """Write blank review CSV for manual classification."""
    conn = sqlite3.connect(DATABASE_FILE)
    trades = load_tos_imports(conn)
    conn.close()

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(REVIEW_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["trade_id","open_date","symbol","asset_type","direction","assign_system"])
        writer.writeheader()
        for t in trades:
            writer.writerow({
                "trade_id"      : t["trade_id"],
                "open_date"     : t["open_date"],
                "symbol"        : t["underlying_symbol"],
                "asset_type"    : t["asset_type"],
                "direction"     : t["direction"],
                "assign_system" : "",
            })

    logger.info(f"Review CSV written: {REVIEW_CSV}")
    logger.info(f"Rows to classify: {len(trades)}")
    logger.info(f"Valid system values: {sorted(VALID_SYSTEMS)}")
    logger.info("Fill in assign_system column, then run: --import")


def import_classifications(dry_run=False):
    """Read completed review CSV and update DB."""
    if not IMPORT_CSV.exists():
        logger.error(f"Review CSV not found: {IMPORT_CSV}")
        return

    conn = sqlite3.connect(DATABASE_FILE)
    updated = skipped = errors = 0

    with open(IMPORT_CSV, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            system = row["assign_system"].strip()
            trade_id = int(row["trade_id"])

            if not system:
                skipped += 1
                continue
            if system not in VALID_SYSTEMS:
                logger.warning(f"  INVALID system '{system}' for trade_id {trade_id} ({row['symbol']}) — skipping")
                errors += 1
                continue
            if system == "TOS_Import":
                skipped += 1
                continue

            if not dry_run:
                conn.execute(
                    "UPDATE trades SET system=?, updated_at=CURRENT_TIMESTAMP WHERE trade_id=?",
                    (system, trade_id)
                )
            updated += 1
            logger.info(f"  {'DRY' if dry_run else 'SET'} {row['symbol']} {row['open_date']} -> {system}")

    if not dry_run:
        conn.commit()
    conn.close()

    logger.info(f"Updated: {updated}  Skipped: {skipped}  Errors: {errors}")


if __name__ == "__main__":
    if "--import" in sys.argv:
        dry_run = "--dry-run" in sys.argv
        if dry_run:
            logger.info("DRY RUN — no DB writes")
        import_classifications(dry_run=dry_run)
    else:
        generate_review()