#!/usr/bin/env python3
"""
P_010 Daily Posture V4.0
Reads VP Grid XLSX files (exported from TOS) to calculate daily market posture
Creates P_010_RiskConfig.json for position sizing decisions

NEW IN V4: Reads Excel files instead of XML (cleaner, more reliable)
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from shutil import copy2


def read_grid_excel(excel_path):
    """Read Grid Excel file and return the most recent record."""
    # Read Excel file
    df = pd.read_excel(excel_path)
    
    # Skip first row if it's a header row (NaT in Date column)
    if pd.isna(df.iloc[0]['Date']):
        df = df.iloc[1:].reset_index(drop=True)
    
    if len(df) == 0:
        raise ValueError(f"No data found in {excel_path}")
    
    # First row is most recent (Excel ordered newest first)
    row = df.iloc[0]
    
    # Extract key Grid data (handle newlines in column names)
    record = {
        'date': row['Date'],
        'close': float(row['Close\nPrice']),
        'pred_high': float(row['Predicted\nHigh\nPrice']),
        'pred_low': float(row['Predicted\nLow\nPrice']),
        'pred_range': float(row['Predicted\nRange']),
        'medium_diff': float(row['Medium\nTerm\nDifference']),
        'long_diff': float(row['Long\nTerm\nDifference']),
        'short_diff': float(row['Short\nTerm\nDifference']),
    }
    
    return record


def calculate_posture(medium_diff, long_diff):
    """Calculate market posture from Grid medium and long term differences."""
    return (medium_diff + long_diff) / 2.0


def determine_risk_mode(spy_posture, qqq_posture):
    """Determine risk mode based on average posture."""
    avg_posture = (spy_posture + qqq_posture) / 2.0
    
    if avg_posture >= 1.0:
        risk_mode = "FULL"
    elif avg_posture >= 0.0:
        risk_mode = "HALF"
    else:
        risk_mode = "OFF"
    
    return risk_mode, avg_posture


def backup_config(config_file):
    """Backup existing config file with timestamp."""
    if config_file.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = config_file.parent / "data" / "snapshots"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / f"P_010_RiskConfig_{timestamp}.json"
        copy2(config_file, backup_file)
        print(f"Backed up previous config to: {backup_file.name}")


def main():
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data" / "excel_exports"
    
    # Grid Excel files (actual TOS export names)
    spy_excel = data_dir / "History Grid (SPY)_v3.xlsx"
    qqq_excel = data_dir / "History Grid (QQQ)_v3.xlsx"
    
    print("=" * 70)
    print("P_010 DAILY POSTURE ANALYZER V4.0")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verify Excel files exist
    if not spy_excel.exists():
        print(f"ERROR: SPY Grid Excel not found at: {spy_excel}")
        return 1
    
    if not qqq_excel.exists():
        print(f"ERROR: QQQ Grid Excel not found at: {qqq_excel}")
        return 1
    
    print(f"Reading SPY Grid: {spy_excel.name}")
    print(f"Reading QQQ Grid: {qqq_excel.name}")
    print()
    
    # Read Grid Excel files
    try:
        spy_grid = read_grid_excel(spy_excel)
        qqq_grid = read_grid_excel(qqq_excel)
    except Exception as e:
        print(f"ERROR reading Grid Excel: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print(f"SPY Grid Date: {spy_grid['date'].strftime('%m/%d/%Y')}")
    print(f"SPY Close: ${spy_grid['close']:.2f}")
    print(f"SPY PRANGE: ${spy_grid['pred_low']:.2f} - ${spy_grid['pred_high']:.2f}")
    print(f"SPY Medium Diff: {spy_grid['medium_diff']:.4f}")
    print(f"SPY Long Diff: {spy_grid['long_diff']:.4f}")
    print()
    
    print(f"QQQ Grid Date: {qqq_grid['date'].strftime('%m/%d/%Y')}")
    print(f"QQQ Close: ${qqq_grid['close']:.2f}")
    print(f"QQQ PRANGE: ${qqq_grid['pred_low']:.2f} - ${qqq_grid['pred_high']:.2f}")
    print(f"QQQ Medium Diff: {qqq_grid['medium_diff']:.4f}")
    print(f"QQQ Long Diff: {qqq_grid['long_diff']:.4f}")
    print()
    
    # Calculate postures from Grid data
    spy_posture = calculate_posture(spy_grid['medium_diff'], spy_grid['long_diff'])
    qqq_posture = calculate_posture(qqq_grid['medium_diff'], qqq_grid['long_diff'])
    
    print(f"SPY Posture: {spy_posture:.4f}")
    print(f"QQQ Posture: {qqq_posture:.4f}")
    print()
    
    # Determine risk mode
    risk_mode, avg_posture = determine_risk_mode(spy_posture, qqq_posture)
    
    print(f"Average Posture: {avg_posture:.4f}")
    print(f"Risk Mode: {risk_mode}")
    print()
    
    # Create grid snapshot (intermediary for intraday checks)
    grid_snapshot = {
        'timestamp': datetime.now().isoformat(),
        'spy': {
            'date': spy_grid['date'].strftime('%m/%d/%Y'),
            'close': spy_grid['close'],
            'pred_high': spy_grid['pred_high'],
            'pred_low': spy_grid['pred_low'],
            'pred_range': spy_grid['pred_range'],
            'posture': spy_posture
        },
        'qqq': {
            'date': qqq_grid['date'].strftime('%m/%d/%Y'),
            'close': qqq_grid['close'],
            'pred_high': qqq_grid['pred_high'],
            'pred_low': qqq_grid['pred_low'],
            'pred_range': qqq_grid['pred_range'],
            'posture': qqq_posture
        }
    }
    
    snapshot_file = project_root / "grid_snapshot_latest.json"
    with open(snapshot_file, 'w') as f:
        json.dump(grid_snapshot, f, indent=2)
    
    print(f"Created: {snapshot_file.name}")
    
    # Create risk config
    risk_config = {
        'timestamp': datetime.now().isoformat(),
        'spy_posture': spy_posture,
        'qqq_posture': qqq_posture,
        'avg_posture': avg_posture,
        'risk_mode': risk_mode,
        'source': 'Grid_XLSX',
        'spy_grid_date': spy_grid['date'].strftime('%m/%d/%Y'),
        'qqq_grid_date': qqq_grid['date'].strftime('%m/%d/%Y')
    }
    
    config_file = project_root / "P_010_RiskConfig.json"
    
    # Backup existing config
    backup_config(config_file)
    
    # Write new config
    with open(config_file, 'w') as f:
        json.dump(risk_config, f, indent=2)
    
    print(f"Created: {config_file.name}")
    print()
    
    print("=" * 70)
    print("DAILY POSTURE ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Risk Mode: {risk_mode}")
    print(f"Position Sizing: {'100%' if risk_mode == 'FULL' else '50%' if risk_mode == 'HALF' else '0%'}")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
