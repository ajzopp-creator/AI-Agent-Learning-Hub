import sqlite3

DB = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"

NEW_VIEW = """
CREATE VIEW v_trade_summary AS
SELECT
    t.trade_id,
    t.account_id,
    t.system,
    t.underlying_symbol,
    t.asset_type,
    t.direction,
    t.open_date,
    t.qty,
    t.entry_price,
    t.stop_price,
    t.risk_amount,
    t.total_commissions,
    t.status,
    t.tags,
    t.notes,
    t.reason,
    t.signal_strength,
    t.source,
    COALESCE(SUM(e.exit_pnl),   0.0) AS realized_pnl,
    COALESCE(SUM(e.qty_exited), 0)   AS qty_closed,
    t.qty - COALESCE(SUM(e.qty_exited), 0) AS qty_remaining,
    MAX(e.exit_date)                 AS last_exit_date,
    MAX(e.hold_days)                 AS max_hold_days,
    MAX(CASE WHEN e.exit_number = 1 THEN e.exit_price  END) AS exit_1_price,
    MAX(CASE WHEN e.exit_number = 1 THEN e.qty_exited  END) AS exit_1_qty,
    MAX(CASE WHEN e.exit_number = 1 THEN e.exit_date   END) AS exit_1_date,
    MAX(CASE WHEN e.exit_number = 1 THEN e.hold_days   END) AS exit_1_hold_days,
    MAX(CASE WHEN e.exit_number = 2 THEN e.exit_price  END) AS exit_2_price,
    MAX(CASE WHEN e.exit_number = 2 THEN e.qty_exited  END) AS exit_2_qty,
    MAX(CASE WHEN e.exit_number = 2 THEN e.exit_date   END) AS exit_2_date,
    MAX(CASE WHEN e.exit_number = 2 THEN e.hold_days   END) AS exit_2_hold_days,
    MAX(CASE WHEN e.exit_number = 3 THEN e.exit_price  END) AS exit_3_price,
    MAX(CASE WHEN e.exit_number = 3 THEN e.qty_exited  END) AS exit_3_qty,
    MAX(CASE WHEN e.exit_number = 3 THEN e.exit_date   END) AS exit_3_date,
    MAX(CASE WHEN e.exit_number = 3 THEN e.hold_days   END) AS exit_3_hold_days,
    CASE
        WHEN t.risk_amount IS NOT NULL AND t.risk_amount != 0
        THEN ROUND(COALESCE(SUM(e.exit_pnl), 0.0) / t.risk_amount, 2)
        ELSE NULL
    END AS realized_R,
    CASE
        WHEN t.status = 'open'                   THEN 'OPEN'
        WHEN COALESCE(SUM(e.exit_pnl), 0.0) > 0 THEN 'WIN'
        WHEN COALESCE(SUM(e.exit_pnl), 0.0) < 0 THEN 'LOSS'
        ELSE 'SCRATCH'
    END AS outcome
FROM trades t
LEFT JOIN exits e ON t.trade_id = e.trade_id
GROUP BY t.trade_id
"""

conn = sqlite3.connect(DB)
conn.execute("DROP VIEW IF EXISTS v_trade_summary")
conn.execute(NEW_VIEW)
conn.commit()

cols = [r[1] for r in conn.execute("PRAGMA table_info(v_trade_summary)").fetchall()]
conn.close()

print("v_trade_summary rebuilt.")
print("Columns:", cols)
assert "reason" in cols, "MISSING: reason"
assert "signal_strength" in cols, "MISSING: signal_strength"
print("OK: reason and signal_strength confirmed.")
