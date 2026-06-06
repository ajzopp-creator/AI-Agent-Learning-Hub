import sqlite3
from pathlib import Path

ledger_db = Path("models/ledger/buy_ledger.db")

if not ledger_db.exists():
    print("❌ Ledger DB does not exist yet")
    exit(1)

with sqlite3.connect(ledger_db) as conn:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fired_signals'")
    if not cur.fetchone():
        print("❌ fired_signals table not found")
        exit(1)
    
    # Count records
    cur.execute("SELECT COUNT(*) as cnt FROM fired_signals")
    count = cur.fetchone()['cnt']
    print(f"\n✅ fired_signals table exists with {count} records\n")
    
    if count > 0:
        # Show all records
        cur.execute("""
            SELECT ledger_id, ticker, signal_date, signal_class, chosen_horizon, n_matches, 
                   win_rate_pct, mean_return_pct, filled_date, fired_at
            FROM fired_signals
            ORDER BY fired_at DESC
        """)
        print("Recent fired signals:")
        print("-" * 120)
        for row in cur.fetchall():
            print(f"  {row['ledger_id']:3d} | {row['ticker']:6s} | {row['signal_date']} | {row['signal_class']:6s} | "
                  f"h={row['chosen_horizon']:2d} | n={row['n_matches']} | wr={row['win_rate_pct']:5.1f}% | "
                  f"ret={row['mean_return_pct']:+6.2f}% | filled={row['filled_date']}")
        print("-" * 120)
    else:
        print("No records in fired_signals yet")
