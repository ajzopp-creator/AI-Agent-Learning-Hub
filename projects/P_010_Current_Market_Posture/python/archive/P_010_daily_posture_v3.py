#!/usr/bin/env python3
"""
P_010 Daily Posture V3.0
Reads VP Grid XML files (exported at 6:30 PM) to calculate daily market posture
Creates P_010_RiskConfig.json for position sizing decisions

Daily Workflow:
  1. Read Grid XML files from data/xml_exports/
  2. Extract latest Grid predictions and posture data
  3. Calculate market posture from Grid medium/long term differences
  4. Create grid_snapshot_latest.json (intermediary for intraday checks)
  5. Create P_010_RiskConfig.json (backed up with timestamp)
"""

import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from shutil import copy2


def parse_grid_xml(xml_path, record_tag):
    """Parse Grid XML and return the latest (most recent) record by date."""
    from datetime import datetime
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Get all records
    records = root.findall(record_tag)
    
    if not records:
        raise ValueError(f"No records found with tag: {record_tag}")
    
    # Find the record with the most recent date
    latest = None
    latest_date = None
    
    for record in records:
        date_str = record.findtext("Date")
        if date_str:
            try:
                # Parse date (format: M/D/YYYY)
                record_date = datetime.strptime(date_str, "%m/%d/%Y")
                if latest_date is None or record_date > latest_date:
                    latest_date = record_date
                    latest = record
            except:
                continue
    
    if latest is None:
        latest = records[0]  # First record is most recent (XML ordered newest first) if date parsing fails
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
    data_dir = project_root / "data" / "xml_exports"
    
    # Grid XML files
    spy_xml = data_dir / "History Grid (SPY)_V2.xml"
    qqq_xml = data_dir / "History Grid (QQQ)_v2.xml"
    
    print("=" * 70)
    print("P_010 DAILY POSTURE ANALYZER V3.0")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verify XML files exist
    if not spy_xml.exists():
        print(f"ERROR: SPY Grid XML not found at: {spy_xml}")
        return 1
    
    if not qqq_xml.exists():
        print(f"ERROR: QQQ Grid XML not found at: {qqq_xml}")
        return 1
    
    print(f"Reading SPY Grid: {spy_xml.name}")
    print(f"Reading QQQ Grid: {qqq_xml.name}")
    print()
    
    # Parse Grid XML files
    try:
        spy_grid = parse_grid_xml(spy_xml, record_tag="SPDRs")
        qqq_grid = parse_grid_xml(qqq_xml, record_tag="PowerShares_x0020_QQQ")
    except Exception as e:
        print(f"ERROR parsing Grid XML: {e}")
        return 1
    
    print(f"SPY Grid Date: {spy_grid['date']}")
    print(f"SPY Close: ${spy_grid['close']:.2f}")
    print(f"SPY PRANGE: ${spy_grid['pred_low']:.2f} - ${spy_grid['pred_high']:.2f}")
    print()
    
    print(f"QQQ Grid Date: {qqq_grid['date']}")
    print(f"QQQ Close: ${qqq_grid['close']:.2f}")
    print(f"QQQ PRANGE: ${qqq_grid['pred_low']:.2f} - ${qqq_grid['pred_high']:.2f}")
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
            'date': spy_grid['date'],
            'close': spy_grid['close'],
            'pred_high': spy_grid['pred_high'],
            'pred_low': spy_grid['pred_low'],
            'pred_range': spy_grid['pred_range'],
            'posture': spy_posture
        },
        'qqq': {
            'date': qqq_grid['date'],
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
        'source': 'Grid_XML',
        'spy_grid_date': spy_grid['date'],
        'qqq_grid_date': qqq_grid['date']
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

