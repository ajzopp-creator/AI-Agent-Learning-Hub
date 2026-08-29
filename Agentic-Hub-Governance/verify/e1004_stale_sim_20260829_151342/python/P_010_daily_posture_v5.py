#!/usr/bin/env python3
"""
P_010 Daily Posture V5.0
Reads VP Grid XLSX files to calculate daily market posture.
Creates P_010_RiskConfig.json for position sizing decisions.

NEW IN V5: VXX (iPath S&P 500 VIX Short-Term Futures) integration
  - Reads History Grid (VXX)_v3.xlsx alongside SPY and QQQ
  - VXX posture is INVERTED: negative = fear declining = bullish confirmation
  - VXX does NOT affect risk_mode (contango decay skews absolute levels)
  - VXX adds vxx_signal as a sentiment overlay field
  - vxx_signal values: BULLISH_CONFIRM | NEUTRAL | CAUTION | WARNING

UNCHANGED FROM V4:
  - SPY/QQQ posture calculation and risk_mode logic are identical
  - P_010_RiskConfig.json fields spy_posture, qqq_posture, avg_posture,
    risk_mode, source, spy_grid_date, qqq_grid_date -- all unchanged
  - grid_snapshot_latest.json structure extended but backward compatible
  - P_115 / P_118 integration unaffected

WO-P010-E1.003 (2026-08-10): added MORNING_RUN_FAILED.flag halt mechanism.
On any failure (unhandled exception OR main()'s existing return-1 paths),
the __main__ block writes MORNING_RUN_FAILED.flag next to P_010_RiskConfig.json
and fires a toast notification. P_010_daily_posture.bat checks this flag
after STEP 1 and skips STEP 2 (note writer) if present, so the note writer
never runs against a failed morning read. Guardian also checks this flag
later as a persistent, cross-process signal. Flag is cleared at the start
of every run, before the attempt -- a leftover flag from a prior failed day
never blocks today's run once today's script actually starts.
main()'s internal logic is UNCHANGED from V5 -- only the __main__ entry
point wrapper is new.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from shutil import copy2

from toast_notify import send_toast
from grid_freshness_check import check_grid_freshness

VXX_SIGNAL_THRESHOLDS = {
    'BULLISH_CONFIRM': -1.0,
    'NEUTRAL_LOW':     -1.0,
    'NEUTRAL_HIGH':    +0.5,
    'CAUTION_HIGH':    +1.5,
}


def read_grid_excel(excel_path):
    df = pd.read_excel(excel_path)
    if pd.isna(df.iloc[0]['Date']):
        df = df.iloc[1:].reset_index(drop=True)
    if len(df) == 0:
        raise ValueError(f"No data found in {excel_path}")
    row = df.iloc[0]
    return {
        'date':        row['Date'],
        'close':       float(row['Close\nPrice']),
        'pred_high':   float(row['Predicted\nHigh\nPrice']),
        'pred_low':    float(row['Predicted\nLow\nPrice']),
        'pred_range':  float(row['Predicted\nRange']),
        'medium_diff': float(row['Medium\nTerm\nDifference']),
        'long_diff':   float(row['Long\nTerm\nDifference']),
        'short_diff':  float(row['Short\nTerm\nDifference']),
    }


def calculate_posture(medium_diff, long_diff):
    return (medium_diff + long_diff) / 2.0


def determine_risk_mode(spy_posture, qqq_posture):
    avg_posture = (spy_posture + qqq_posture) / 2.0
    if avg_posture >= 1.0:
        risk_mode = "FULL"
    elif avg_posture >= 0.0:
        risk_mode = "HALF"
    else:
        risk_mode = "OFF"
    return risk_mode, avg_posture


def determine_vxx_signal(vxx_posture):
    t = VXX_SIGNAL_THRESHOLDS
    if vxx_posture < t['BULLISH_CONFIRM']:
        return "BULLISH_CONFIRM", "VP predicts VXX falling -- fear contracting, bullish equity confirmation"
    elif vxx_posture <= t['NEUTRAL_HIGH']:
        return "NEUTRAL", "VP sees stable/flat volatility -- no directional signal from VXX"
    elif vxx_posture <= t['CAUTION_HIGH']:
        return "CAUTION", "VP predicts modest VXX rise -- watch for increased volatility"
    else:
        return "WARNING", "VP predicts sharp VXX rise -- potential fear spike, reduce exposure"


def backup_config(config_file):
    if config_file.exists():
        timestamp   = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir  = config_file.parent / "data" / "snapshots"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / f"P_010_RiskConfig_{timestamp}.json"
        copy2(config_file, backup_file)
        print(f"  Backed up previous config --> {backup_file.name}")


def main():
    script_dir   = Path(__file__).parent
    project_root = script_dir.parent
    data_dir     = project_root / "data" / "excel_exports"

    spy_excel = data_dir / "History Grid (SPY)_v3.xlsx"
    qqq_excel = data_dir / "History Grid (QQQ)_v3.xlsx"
    vxx_excel = data_dir / "History Grid (VXX)_v3.xlsx"

    print("=" * 70)
    print("P_010 DAILY POSTURE ANALYZER V5.0")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    for f in [spy_excel, qqq_excel]:
        if not f.exists():
            print(f"ERROR: File not found: {f}")
            return 1

    vxx_available = vxx_excel.exists()
    if not vxx_available:
        print("WARNING: VXX Grid not found -- running without VXX sentiment overlay")
        print(f"         Expected: {vxx_excel}")
        print()

    print(f"Reading SPY Grid : {spy_excel.name}")
    print(f"Reading QQQ Grid : {qqq_excel.name}")
    if vxx_available:
        print(f"Reading VXX Grid : {vxx_excel.name}")
    print()

    try:
        spy_grid = read_grid_excel(spy_excel)
        qqq_grid = read_grid_excel(qqq_excel)
        vxx_grid = read_grid_excel(vxx_excel) if vxx_available else None
    except Exception as e:
        print(f"ERROR reading Grid Excel: {e}")
        import traceback; traceback.print_exc()
        return 1

    grid_dates = {'SPY': spy_grid['date'].date(), 'QQQ': qqq_grid['date'].date(),
                  **({'VXX': vxx_grid['date'].date()} if vxx_grid else {})}
    stale, stale_detail = check_grid_freshness(grid_dates, datetime.now().date())
    if stale:
        _write_failure_flag(project_root / "MORNING_RUN_FAILED.flag", stale_detail)
        _notify_failure(stale_detail)
    print(f"SPY Grid Date  : {spy_grid['date'].strftime('%m/%d/%Y')}")
    print(f"SPY Close      : ${spy_grid['close']:.2f}")
    print(f"SPY PRANGE     : ${spy_grid['pred_low']:.2f} - ${spy_grid['pred_high']:.2f}")
    print(f"SPY Medium Diff: {spy_grid['medium_diff']:.4f}")
    print(f"SPY Long Diff  : {spy_grid['long_diff']:.4f}")
    print()

    print(f"QQQ Grid Date  : {qqq_grid['date'].strftime('%m/%d/%Y')}")
    print(f"QQQ Close      : ${qqq_grid['close']:.2f}")
    print(f"QQQ PRANGE     : ${qqq_grid['pred_low']:.2f} - ${qqq_grid['pred_high']:.2f}")
    print(f"QQQ Medium Diff: {qqq_grid['medium_diff']:.4f}")
    print(f"QQQ Long Diff  : {qqq_grid['long_diff']:.4f}")
    print()

    if vxx_grid:
        print(f"VXX Grid Date  : {vxx_grid['date'].strftime('%m/%d/%Y')}")
        print(f"VXX Close      : ${vxx_grid['close']:.2f}")
        print(f"VXX PRANGE     : ${vxx_grid['pred_low']:.2f} - ${vxx_grid['pred_high']:.2f}")
        print(f"VXX Medium Diff: {vxx_grid['medium_diff']:.4f}")
        print(f"VXX Long Diff  : {vxx_grid['long_diff']:.4f}")
        print()

    spy_posture = calculate_posture(spy_grid['medium_diff'], spy_grid['long_diff'])
    qqq_posture = calculate_posture(qqq_grid['medium_diff'], qqq_grid['long_diff'])

    print(f"SPY Posture    : {spy_posture:.4f}")
    print(f"QQQ Posture    : {qqq_posture:.4f}")

    if vxx_grid:
        vxx_posture          = calculate_posture(vxx_grid['medium_diff'], vxx_grid['long_diff'])
        vxx_signal, vxx_note = determine_vxx_signal(vxx_posture)
        print(f"VXX Posture    : {vxx_posture:.4f}  (INVERTED -- negative = bullish)")
        print(f"VXX Signal     : {vxx_signal}")
        print(f"               : {vxx_note}")
    else:
        vxx_posture = vxx_signal = vxx_note = None
    print()

    risk_mode, avg_posture = determine_risk_mode(spy_posture, qqq_posture)
    print(f"Avg Posture    : {avg_posture:.4f}  (SPY + QQQ only)")
    print(f"Risk Mode      : {risk_mode}")
    print()

    grid_snapshot = {
        'timestamp': datetime.now().isoformat(),
        'spy': {
            'date': spy_grid['date'].strftime('%m/%d/%Y'), 'close': spy_grid['close'],
            'pred_high': spy_grid['pred_high'], 'pred_low': spy_grid['pred_low'],
            'pred_range': spy_grid['pred_range'], 'posture': spy_posture,
        },
        'qqq': {
            'date': qqq_grid['date'].strftime('%m/%d/%Y'), 'close': qqq_grid['close'],
            'pred_high': qqq_grid['pred_high'], 'pred_low': qqq_grid['pred_low'],
            'pred_range': qqq_grid['pred_range'], 'posture': qqq_posture,
        },
    }
    if vxx_grid:
        grid_snapshot['vxx'] = {
            'date': vxx_grid['date'].strftime('%m/%d/%Y'), 'close': vxx_grid['close'],
            'pred_high': vxx_grid['pred_high'], 'pred_low': vxx_grid['pred_low'],
            'pred_range': vxx_grid['pred_range'], 'posture': vxx_posture,
            'signal': vxx_signal, 'note': vxx_note,
        }

    snapshot_file = project_root / "grid_snapshot_latest.json"
    with open(snapshot_file, 'w') as f:
        json.dump(grid_snapshot, f, indent=2)
    print(f"Created  : {snapshot_file.name}")

    risk_config = {
        'timestamp':     datetime.now().isoformat(),
        'spy_posture':   round(spy_posture, 6),
        'qqq_posture':   round(qqq_posture, 6),
        'avg_posture':   round(avg_posture, 6),
        'risk_mode':     risk_mode,
        'source':        'Grid_XLSX',
        'spy_grid_date': spy_grid['date'].strftime('%m/%d/%Y'),
        'qqq_grid_date': qqq_grid['date'].strftime('%m/%d/%Y'),
        'vxx_posture':   round(vxx_posture, 6) if vxx_posture is not None else None,
        'vxx_signal':    vxx_signal,
        'vxx_note':      vxx_note,
        'vxx_close':     vxx_grid['close'] if vxx_grid else None,
        'vxx_pred_high': vxx_grid['pred_high'] if vxx_grid else None,
        'vxx_pred_low':  vxx_grid['pred_low'] if vxx_grid else None,
        'vxx_grid_date': vxx_grid['date'].strftime('%m/%d/%Y') if vxx_grid else None,
    }

    config_file = project_root / "P_010_RiskConfig.json"
    backup_config(config_file)
    with open(config_file, 'w') as f:
        json.dump(risk_config, f, indent=2)
    print(f"Created  : {config_file.name}")
    print()

    print("=" * 70)
    print("DAILY POSTURE ANALYSIS COMPLETE")
    print("=" * 70)
    sizing = '100%' if risk_mode == 'FULL' else '50%' if risk_mode == 'HALF' else '0%'
    print(f"  Risk Mode   : {risk_mode}")
    print(f"  Sizing      : {sizing}")
    if vxx_signal:
        print(f"  VXX Signal  : {vxx_signal}")
    print("=" * 70)
    return 0


def _write_failure_flag(flag_path, detail):
    flag_path.write_text(
        f"FAILED: {datetime.now().isoformat()}\n{detail}\n",
        encoding="utf-8"
    )


def _notify_failure(detail):
    # Toast is best-effort -- a notification failure must never mask or
    # crash the real error handling underneath it.
    try:
        send_toast("P_010 Morning Run FAILED", detail)
    except Exception:
        pass


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    flag_path = project_root / "MORNING_RUN_FAILED.flag"

    # Clear any stale flag from a prior failed day before attempting today's run.
    if flag_path.exists():
        flag_path.unlink()

    try:
        exit_code = main()
    except Exception as e:
        import traceback
        detail = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        _write_failure_flag(flag_path, detail)
        _notify_failure(str(e))
        sys.exit(1)

    if exit_code != 0:
        detail = (f"main() returned exit code {exit_code} -- "
                  f"see today's P_010_Daily_*.log for the specific ERROR line")
        _write_failure_flag(flag_path, detail)
        _notify_failure(f"Exit code {exit_code} -- check today's log")

    sys.exit(exit_code)
