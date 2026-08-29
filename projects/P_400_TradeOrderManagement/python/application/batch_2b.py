"""batch_2b.py -- Tier-2B batch runner, options-first, ranked output.

Application layer: orchestration only. Composes read_signals -> screen_all
-> dispose_failed -> batch_2b_scoring.evaluate_pass_symbols() ->
batch_2b_scoring.assemble_report() -> print + persist. Per-symbol pipeline,
vehicle comparison, and ranking live in batch_2b_scoring.py (split out to
stay under the 300-line cap -- see that file's docstring).

WO-P400-E5.003. Collapses N manual round-trips (screen-all, then
fetch-snapshot/fetch-chain/evaluate per symbol) into one CLI invocation --
PEH requires Tony to run every Python command in his own terminal, so
round-trip count is the structural bottleneck, not compute time.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
from zoneinfo import ZoneInfo

from config import (
    BATCH_MAX_SYMBOLS,
    BATCH_REPORT_DIR,
    BATCH_REPORT_FILE_PATTERN,
    MAX_CONCURRENT_POSITIONS,
    PORTFOLIO_HEAT_MAX_PCT,
    TradeMode,
)
from application.batch_2b_scoring import assemble_report, evaluate_pass_symbols
from application.dispose_failed import dispose_failed
from application.read_signals import read_signals
from domain.market_hours import is_market_open_now
from domain.portfolio import build_portfolio_state
from domain.screen import screen_all
from infrastructure.book_loader import load_book
from application.earnings_lookup import (
    EarningsCacheMissing,
    build_entries_for_symbols,
)
from infrastructure.params_reader import read_params
from infrastructure.posture_reader import read_posture
from schemas import BatchReport

EASTERN = ZoneInfo("America/New_York")


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _today_session_date() -> str:
    """Today's date in Eastern time, ISO YYYY-MM-DD -- matches the earnings
    file's session-scoped naming (earnings_YYYY-MM-DD.json)."""
    return datetime.now(timezone.utc).astimezone(EASTERN).date().isoformat()


def _build_screen_context(posture, params, port) -> dict:
    """Same shape cmd_screen_all builds in commands.py -- duplicated here,
    not imported, because commands.py stays untouched (WO-P400-E5.003's
    NOT PURELY ADDITIVE note: only fetch-chain gets an edit)."""
    return {
        "risk_mode": posture.risk_mode,
        "base_risk_dollars": params.risk_per_trade,
        "current_heat_dollars": port.heat_dollars,
        "heat_cap_dollars": params.account_balance * (PORTFOLIO_HEAT_MAX_PCT / 100.0),
        "open_position_count": port.open_position_count,
        "max_positions": MAX_CONCURRENT_POSITIONS,
        "open_symbols": list(port.open_symbols),
    }


def _build_signal_dicts(packets) -> List[dict]:
    return [
        {"symbol": s.symbol, "signal_file": s.signal_id,
         "entry": s.guideline_entry, "stop": s.guideline_stop,
         "target": s.guideline_target, "signal_date_str": s.signal_timestamp}
        for s in packets
    ]


# ---------------------------------------------------------------------------
# Tier-1 screen phase
# ---------------------------------------------------------------------------

def _run_tier1_screen(trade_mode: TradeMode) -> Tuple[list, list, object, object]:
    """Read, screen, print, dispose -- identical shape to cmd_screen_all()
    in commands.py. Returns (screen_results, packets, posture, params)."""
    result = read_signals()
    posture = read_posture()
    params = read_params()
    port = build_portfolio_state(load_book())
    packets = result.load.valid

    context = _build_screen_context(posture, params, port)
    signals = _build_signal_dicts(packets)
    screen_results = screen_all(signals, context)

    print("=" * 70)
    print(f"TIER-1 SCREEN  |  posture={posture.risk_mode}  |  {len(signals)} packets")
    print("=" * 70)
    for r in screen_results:
        print(" ", r.summary_line())
    print("=" * 70)

    disposals = dispose_failed(screen_results, packets, trade_mode)
    if disposals:
        print("DISPOSAL SUMMARY (auto -- WO-P400-E2.018)")
        for d in disposals:
            print(d.summary_line())
        print("=" * 70)

    return screen_results, packets, posture, params


def _select_pass_symbols(screen_results) -> List[str]:
    pass_symbols = [r.symbol for r in screen_results if r.is_pass()]
    if len(pass_symbols) > BATCH_MAX_SYMBOLS:
        print(f"[WARN] {len(pass_symbols)} PASS symbols exceeds BATCH_MAX_SYMBOLS "
              f"({BATCH_MAX_SYMBOLS}) -- evaluating first {BATCH_MAX_SYMBOLS} only.")
        pass_symbols = pass_symbols[:BATCH_MAX_SYMBOLS]
    return pass_symbols


# ---------------------------------------------------------------------------
# Orchestration entry points
# ---------------------------------------------------------------------------

def run_batch_2b(cash: float, session_date: Optional[str] = None,
                  trade_mode: TradeMode = TradeMode.REAL) -> BatchReport:
    """Orchestrate the full Tier-2B batch. WO-P400-E5.003."""
    if not is_market_open_now():
        print("!" * 60)
        print("  MARKET CLOSED -- Tier-2B live-snapshot data is unreliable")
        print("  after hours (wide spreads corrupt realistic-fill R:R).")
        print("  Proceeding, but treat this run's numbers with caution.")
        print("!" * 60)

    session_date = session_date or _today_session_date()
    screen_results, packets, posture, params = _run_tier1_screen(trade_mode)
    pass_symbols = _select_pass_symbols(screen_results)
    entries = build_entries_for_symbols(pass_symbols)  # WO-P400-E5.002: Nasdaq cache, not the manual file

    scored, skipped = evaluate_pass_symbols(
        pass_symbols, packets, entries, cash, trade_mode, params, posture,
    )

    return assemble_report(
        cash, session_date, posture, len(packets), len(pass_symbols),
        scored, skipped, params,
    )


def _print_ranked_table(report: BatchReport) -> None:
    print("=" * 70)
    print(f"TIER-2B BATCH RESULTS  |  {report.session_date}  |  "
          f"posture={report.posture}  |  cash=${report.cash_available:.2f}")
    print("=" * 70)
    if not report.candidates:
        print("  No APPROVED candidates this run.")
    else:
        header = (f"  {'#':<3}{'SYM':<7}{'SCORE':<7}{'VEHICLE':<10}{'QTY':<6}"
                  f"{'R:R':<7}{'ATR_HR':<8}{'DRIFT%':<8}{'RISK$':<10}")
        print(header)
        print("  " + "-" * (len(header) - 2))
        for c in report.candidates:
            print(f"  {c.rank:<3}{c.symbol:<7}{c.score:<7.3f}{c.vehicle:<10}{c.quantity:<6}"
                  f"{c.rr_at_t1:<7.2f}{c.atr_headroom:<8.2f}{c.drift_pct:<8.2f}${c.dollar_risk:<9.2f}")
            print(f"        -> {c.vehicle_reason}")
    print("=" * 70)
    if report.heat_warning:
        print(f"  HEAT: {report.heat_warning}")
        print("=" * 70)
    if report.skipped:
        print("  SKIPPED:")
        for s in report.skipped:
            print(f"    {s['symbol']:<7} {s['reason']}")
        print("=" * 70)


def _write_report(report: BatchReport) -> Path:
    BATCH_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).astimezone(EASTERN).strftime("%Y%m%d_%H%M%S")
    out_path = BATCH_REPORT_DIR / BATCH_REPORT_FILE_PATTERN.format(date=report.session_date, ts=ts)
    out_path.write_text(json.dumps(report.model_dump(), indent=2), encoding="utf-8")
    return out_path


def cmd_batch_2b(cash: float, earnings_date: Optional[str] = None,
                  trade_mode: TradeMode = TradeMode.REAL) -> int:
    """`batch-2b` CLI entry point. WO-P400-E5.003."""
    try:
        report = run_batch_2b(cash, session_date=earnings_date, trade_mode=trade_mode)
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        return 1
    except EarningsCacheMissing as exc:
        print(f"[ERROR] {exc}")
        return 1
    except ValueError as exc:
        print(f"[ERROR] earnings file invalid: {exc}")
        return 1

    _print_ranked_table(report)
    out_path = _write_report(report)
    print(f"[OK] batch report written: {out_path}")
    return 0
