"""One-off: fix a settlement-price swap on the 9/4/2026 NDXP laddered
spread (trade_ids 3152/3153/3154), found investigating why P_020's
reported P&L was running well ahead of the real Schwab account balance.

Root cause (confirmed against raw pull JSON
data\\api_pulls\\ajz_strategies\\P_020_raw_AJZ_Strategies_2026-08-29_to_2026-09-05_20260905_110200.json):
9/4 was two overlapping VERTICAL orders (29520/29530 @.95, then
29530/29540 @1.10 -- the second closed the 29530 leg the first had just
opened). Net real position at end of day: short 29520 (never closed by
a TRD, needs 0DTE settlement) and long 29540 (same). The 29530 leg
closed same-day via a real TRD (trade 3153) and is untouched here.

3152 (29540, entry 4.05) and 3154 (29520, entry 4.50) were closed by
some undocumented manual action on 2026-09-08 -- settlement_price was
never populated (rules out close_expired_options.py, WO-P020-E1.018 --
that path always populates it, confirmed against 3165-3168/3166-3167
which went through it correctly). Whoever/whatever did the manual close
used the CORRECT two closing prices (4.16 and 24.16) but SWAPPED them
between the two contracts:
  3152 (29540, should settle @4.16) got exit_price=24.16 -- wrong, that
    belongs to 29520.
  3154 (29520, should settle @24.16) got exit_price=4.16 -- wrong, that
    belongs to 29540.

Corrected day total: entry credits ($95+$110=$205, trade 3153's real
$160 gain already reflects part of this via its own TRD) + settlement
(29540 @4.16: +$11.00; 29520 @24.16, short: -$1,966.00) = -$1,795.00,
matching the real Schwab statement (2026-09-19-AccountStatement_NDX.csv)
exactly.

Also: this is P_020's very first live P_210 trade (Fri 9/4, per
P_020_Future_Enhancements.md NEXT-3's own trigger note) -- currently
mistagged system='TOS_Import'. Retagged to P_210 and grouped with the
other P_210 spread-groups (WO-P020-E1.021) so it counts as one loss,
not three separate legs.

Dry-run by default. Pass --commit to write.
"""

import sqlite3
import sys

DATABASE_FILE = (
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)

GROUP_ID = "SG_BACKFILL_20260904"

# trade_id -> (correct settlement_price, correct exit_pnl)
# 3152: long 29540, qty 1, entry 4.05 -> (4.16-4.05)*100 = 11.00
# 3154: short 29520, qty 1, entry 4.50 -> (4.50-24.16)*100 = -1966.00
CORRECTIONS = {
    3152: {"settlement_price": 4.16,  "expiration_date": "2026-09-04", "exit_price": 4.16,  "exit_pnl": 11.00},
    3154: {"settlement_price": 24.16, "expiration_date": "2026-09-04", "exit_price": 24.16, "exit_pnl": -1966.00},
}
RETAG_TRADE_IDS = [3152, 3153, 3154]


def main() -> int:
    commit = "--commit" in sys.argv
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row

    print(f"{'COMMIT' if commit else 'DRY RUN'} -- 9/4 NDXP settlement-price swap fix\n")

    trades = {r["trade_id"]: r for r in conn.execute(
        "SELECT trade_id, system, entry_price, status, spread_group_id FROM trades "
        "WHERE trade_id IN (3152,3153,3154)"
    ).fetchall()}
    if len(trades) != 3:
        print(f"FAIL: expected 3 trades, found {len(trades)}")
        return 1
    if any(t["spread_group_id"] is not None for t in trades.values()):
        print("FAIL: one or more trades already has spread_group_id set -- refusing to overwrite")
        return 1

    exits = {r["trade_id"]: r for r in conn.execute(
        "SELECT trade_id, exit_price, exit_pnl FROM exits WHERE trade_id IN (3152,3154)"
    ).fetchall()}

    for tid, fix in CORRECTIONS.items():
        e = exits.get(tid)
        if e is None:
            print(f"FAIL: no exit row found for trade_id={tid}")
            return 1
        print(f"  trade_id={tid}  exit_price {e['exit_price']} -> {fix['exit_price']}   "
              f"exit_pnl {e['exit_pnl']:.2f} -> {fix['exit_pnl']:.2f}")

    print(f"\n  Retag system='TOS_Import' -> 'P_210' for {RETAG_TRADE_IDS}")
    print(f"  Assign spread_group_id='{GROUP_ID}' for {RETAG_TRADE_IDS}")

    old_total = sum(e["exit_pnl"] for e in exits.values()) + conn.execute(
        "SELECT exit_pnl FROM exits WHERE trade_id=3153"
    ).fetchone()[0]
    new_total = sum(fix["exit_pnl"] for fix in CORRECTIONS.values()) + conn.execute(
        "SELECT exit_pnl FROM exits WHERE trade_id=3153"
    ).fetchone()[0]
    print(f"\n  Day total: {old_total:+.2f} -> {new_total:+.2f}  (statement says -1795.00)")

    if not commit:
        print("\nDry run -- no writes. Add --commit to write.")
        return 0

    for tid, fix in CORRECTIONS.items():
        conn.execute(
            "UPDATE trades SET settlement_price=?, expiration_date=? WHERE trade_id=?",
            (fix["settlement_price"], fix["expiration_date"], tid),
        )
        conn.execute(
            "UPDATE exits SET exit_price=?, exit_pnl=? WHERE trade_id=?",
            (fix["exit_price"], fix["exit_pnl"], tid),
        )
    for tid in RETAG_TRADE_IDS:
        conn.execute(
            "UPDATE trades SET system='P_210', spread_group_id=? WHERE trade_id=?",
            (GROUP_ID, tid),
        )
    conn.commit()

    verify = {r["trade_id"]: dict(r) for r in conn.execute(
        "SELECT t.trade_id, t.system, t.spread_group_id, e.exit_price, e.exit_pnl "
        "FROM trades t JOIN exits e ON e.trade_id=t.trade_id "
        "WHERE t.trade_id IN (3152,3153,3154)"
    ).fetchall()}
    print("\nVerified:")
    for tid in (3152, 3153, 3154):
        print(f"  {verify[tid]}")

    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
