"""
run_this_P300_20260831_110833.py
P_300 -- h5-chosen trajectory check: for the same rows where
chosen_horizon=5, do trades that read badly at day 5 look better by
day 10/15/20 (wherever those columns are already filled)? Direct
follow-up to run_this_P300_20260831_093649.py (h5 gap diagnosis).
Read-only against buy_ledger.db.

Tests whether the h5 shortfall is a "wrong horizon" artifact (the
classifier's shortest-horizon tiebreak cashing out before an edge
shows up) rather than a "the patterns themselves don't work" problem.

M-120 applied directly: the baseline h5 numbers are asserted against
the known calibration-report values, not just printed as a claimed
match -- loosened tolerances (population +-range, not exact n) so
benign new ledger-fill activity doesn't cause a false FAIL, but tight
enough that a real bug (wrong query, wrong scaling) still trips it.
M-020 applied: every *_return_pct value goes through one pct() helper
(x100) at the point of display -- one place to get it right, not four.
"""
import statistics
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\ledger\buy_ledger.db")
OUT_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\outputs\reports\ledger")
STAMP = "20260831_110833"


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def pct(x):
    """M-020: *_return_pct columns are decimal fractions. x100 here, ONLY here."""
    return x * 100.0


def win_rate(values):
    return 100.0 * sum(1 for v in values if v > 0) / len(values)


def main():
    if not DB_PATH.exists():
        fail(f"ledger DB not found at {DB_PATH}")

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT ticker, signal_date, h5_return_pct, h7_return_pct, "
        "h10_return_pct, h15_return_pct, h20_return_pct "
        "FROM fired_signals WHERE chosen_horizon = 5 AND h5_return_pct IS NOT NULL"
    ).fetchall()
    conn.close()

    if not rows:
        fail("0 rows returned for chosen_horizon=5 with h5_return_pct filled")

    n = len(rows)
    h5_vals = [r["h5_return_pct"] for r in rows]
    h5_wr = win_rate(h5_vals)
    h5_avg = pct(statistics.mean(h5_vals))

    print(f"=== Baseline (all {n} chosen_horizon=5 rows) ===")
    print(f"n={n} win_rate={h5_wr:.1f}% avg_ret={h5_avg:+.2f}%")

    # M-120: real assertions, not a printed claim. Tolerances allow for
    # benign new ledger-fill activity between the last check and this run;
    # a real bug (wrong query, missed x100) would blow well past these.
    if not (400 <= n <= 600):
        fail(f"population size {n} is far from the known ~472 -- re-check the WHERE clause")
    if abs(h5_wr - 51.1) >= 2.0:
        fail(f"h5 win_rate {h5_wr:.1f}% is far from the known 51.1% -- something's wrong upstream")
    if abs(h5_avg - (-0.75)) >= 0.15:
        fail(f"h5 avg_ret {h5_avg:+.3f}% is far from the known -0.75% -- check the x100 scaling first")
    print("Baseline matches known calibration-report values within tolerance (asserted, not assumed).\n")

    # --- Trajectory: same rows' h5 outcome vs. their later-horizon outcome ---
    print("=== Trajectory: same rows, h5 outcome vs. later-horizon outcome ===")
    print("(population shrinks per horizon -- only rows old enough to have that column filled)")
    print(f"{'horizon':8}{'n':>5}{'h5_win%':>9}{'h5_avg%':>9}{'->win%':>9}{'->avg%':>9}{'d_win':>8}{'d_avg':>8}")
    horizon_cols = [("h7", "h7_return_pct"), ("h10", "h10_return_pct"),
                     ("h15", "h15_return_pct"), ("h20", "h20_return_pct")]
    trajectory_summary = []
    for label, col in horizon_cols:
        matched = [r for r in rows if r[col] is not None]
        mn = len(matched)
        if mn == 0:
            print(f"{label:8}{mn:>5}  -- no rows with this horizon filled yet --")
            continue
        m_h5 = [r["h5_return_pct"] for r in matched]
        m_h5_wr = win_rate(m_h5)
        m_h5_avg = pct(statistics.mean(m_h5))
        m_target = [r[col] for r in matched]
        m_t_wr = win_rate(m_target)
        m_t_avg = pct(statistics.mean(m_target))
        d_win = m_t_wr - m_h5_wr
        d_avg = m_t_avg - m_h5_avg
        trajectory_summary.append((label, mn, m_h5_wr, m_h5_avg, m_t_wr, m_t_avg, d_win, d_avg))
        flag = "  (n<15, weak)" if mn < 15 else ""
        print(f"{label:8}{mn:>5}{m_h5_wr:>8.1f}%{m_h5_avg:>+8.2f}%"
              f"{m_t_wr:>8.1f}%{m_t_avg:>+8.2f}%{d_win:>+7.1f}{d_avg:>+7.2f}{flag}")

    # --- Complete-case panel: same exact rows, all 5 horizons filled ---
    complete = [r for r in rows if all(r[c] is not None for _, c in horizon_cols)]
    cn = len(complete)
    print(f"\n=== Complete-case panel: {cn} rows with ALL FIVE horizons filled "
          f"(cleanest comparison -- same trades, 5 time points, no population drift) ===")
    if cn == 0:
        print("No rows have all five horizons filled yet -- too early to run this specific check.")
    else:
        dates = sorted(r["signal_date"] for r in complete)
        print(f"Date range: {dates[0]} to {dates[-1]} (necessarily the oldest signals -- "
              f"only they've had 20 trading days to accumulate all five)")
        print(f"{'horizon':8}{'win%':>8}{'avg_ret%':>10}")
        for label, col in [("h5", "h5_return_pct")] + horizon_cols:
            vals = [r[col] for r in complete]
            print(f"{label:8}{win_rate(vals):>7.1f}%{pct(statistics.mean(vals)):>+9.2f}%")
        if cn < 15:
            print(f"(n={cn} is thin -- directional only, not conclusive on its own)")

    print(f"\n=== Read this as ===")
    print(f"d_win/d_avg growing positive with horizon length: supports 'edge is real, cashed out")
    print(f"too early by the shortest-horizon tiebreak' over 'the patterns themselves are wrong.'")
    print(f"Flat or negative trajectory: the h5 shortfall isn't a timing artifact.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"h5_trajectory_check_{STAMP}.txt"
    lines = [f"h5-chosen trajectory check -- {STAMP}",
             f"Baseline: n={n} win={h5_wr:.1f}% avg={h5_avg:+.2f}% (asserted vs known values)"]
    for label, mn, m_h5_wr, m_h5_avg, m_t_wr, m_t_avg, d_win, d_avg in trajectory_summary:
        lines.append(f"{label}: n={mn} h5[win {m_h5_wr:.1f}% avg {m_h5_avg:+.2f}%] "
                      f"{label}[win {m_t_wr:.1f}% avg {m_t_avg:+.2f}%] "
                      f"delta[win {d_win:+.1f} avg {d_avg:+.2f}]")
    lines.append(f"Complete-case panel: n={cn}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nSummary also written to {out_path}")

    done_path = Path(__file__).with_suffix(".done")
    done_path.write_text("PASS\n0\n", encoding="utf-8")
    print("PASS")


if __name__ == "__main__":
    main()
