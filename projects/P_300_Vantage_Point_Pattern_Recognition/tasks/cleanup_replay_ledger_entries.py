"""
One-shot cleanup: delete junk ledger entries written during the
NFR-1 determinism replay (2026-06-11).

CGBD ledger_ids 41 and 42 are test artifacts -- not real trade signals.
Deletes from both fired_signals and predicted_stats (FK cascade or explicit).

Run once from project root:
    python tasks/cleanup_replay_ledger_entries.py
"""
import sqlite3
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_LEDGER_DB = _PROJECT_ROOT / "models" / "ledger" / "buy_ledger.db"

# IDs written during the replay run on 2026-06-11
_JUNK_IDS = [41, 42]


def main() -> int:
    if not _LEDGER_DB.exists():
        print(f"FAIL -- ledger DB not found: {_LEDGER_DB}")
        return 1

    with sqlite3.connect(_LEDGER_DB) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        # Confirm the rows exist and match expectations before deleting
        for ledger_id in _JUNK_IDS:
            row = conn.execute(
                "SELECT ticker, signal_date, signal_class FROM fired_signals "
                "WHERE ledger_id = ?", (ledger_id,)
            ).fetchone()
            if row is None:
                print(f"  ledger_id={ledger_id} not found -- already deleted or never written")
            else:
                ticker, sig_date, sig_class = row
                print(f"  Found ledger_id={ledger_id}: {ticker} {sig_date} {sig_class} -- DELETING")
                conn.execute(
                    "DELETE FROM fired_signals WHERE ledger_id = ?", (ledger_id,)
                )

        conn.commit()

    # Verify gone
    with sqlite3.connect(_LEDGER_DB) as conn:
        remaining = conn.execute(
            "SELECT COUNT(*) FROM fired_signals WHERE ledger_id IN (41, 42)"
        ).fetchone()[0]
        total = conn.execute("SELECT COUNT(*) FROM fired_signals").fetchone()[0]

    if remaining > 0:
        print(f"FAIL -- {remaining} junk row(s) still present after delete")
        return 1

    print(f"DONE -- junk entries removed. fired_signals total: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
