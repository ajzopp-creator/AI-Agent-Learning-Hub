#!/usr/bin/env python3
"""
P_020 TOS Parser v2.3
Parses ThinkorSwim Account Statement CSV exports into Excel-ready import files.

Updates in v2.3:
- REQ-020221_01: Filter TRD transactions only
- REQ-020221_02: Position tracking to detect orphaned sells/buys
- REQ-020221_03: Single audit log for dropped/orphaned records
- REQ-020221_04: Combine same-symbol BUY orders within 10-minute window
"""

import pandas as pd
import numpy as np
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# PARSE TOS DESCRIPTION FIELD
# ============================================================

def parse_description(desc):
    if not isinstance(desc, str):
        return None

    option_pattern = r'(BOT|SOLD)\s+([+-])(\d+)\s+([A-Z]+)\s+100\s+(\d{1,2}\s+[A-Z]{3}\s+\d{2})\s+([\d.]+)\s+(CALL|PUT)\s+@([\d.]+)'
    stock_pattern = r'(BOT|SOLD)\s+([+-])(\d+)\s+([A-Z]+)\s+@([\d.]+)'

    match = re.search(option_pattern, desc)
    if match:
        action, sign, qty, symbol, exp_date, strike, opt_type, price = match.groups()
        return {
            'action': action,
            'quantity': int(qty),
            'symbol': symbol,
            'expiration': exp_date,
            'option_type': opt_type,
            'strike': float(strike),
            'price': float(price),
            'trade_type': 'OPTION'
        }

    match = re.search(stock_pattern, desc)
    if match:
        action, sign, qty, symbol, price = match.groups()
        return {
            'action': action,
            'quantity': int(qty),
            'symbol': symbol,
            'price': float(price),
            'trade_type': 'STOCK'
        }

    return None


# ============================================================
# LOAD AND PARSE TOS CSV â€” TRD ONLY (REQ-020221_01)
# ============================================================

def load_tos_csv(filepath):
    print(f"Step 1: Loading TOS account statement...")

    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if line.startswith('DATE,TIME,TYPE'):
                csv_start = i
                break

    df = pd.read_csv(filepath, skiprows=csv_start, on_bad_lines='skip', engine='python')

    # REQ-020221_01: Filter to TRD rows only
    total_rows = len(df)
    df = df[df['TYPE'] == 'TRD'].copy()
    print(f"  Loaded {total_rows} total rows, {len(df)} TRD transactions kept")

    print(f"\nStep 2: Parsing DESCRIPTION fields...")
    trades = []

    for idx, row in df.iterrows():
        parsed = parse_description(row.get('DESCRIPTION', ''))
        if parsed:
            # Combine DATE and TIME for 10-minute window logic
            date_str = str(row['DATE']).strip()
            time_str = str(row.get('TIME', '00:00:00')).strip()
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%y %H:%M:%S")
            except:
                try:
                    dt = datetime.strptime(date_str, "%m/%d/%y")
                except:
                    dt = None

            trades.append({
                'DATE': date_str,
                'DATETIME': dt,
                'REF #': row.get('REF #', ''),
                'Misc Fees': abs(pd.to_numeric(row.get('Misc Fees', 0), errors='coerce') or 0),
                'Commissions & Fees': abs(pd.to_numeric(row.get('Commissions & Fees', 0), errors='coerce') or 0),
                **parsed
            })

    trades_df = pd.DataFrame(trades)

    option_count = len(trades_df[trades_df['trade_type'] == 'OPTION'])
    stock_count = len(trades_df[trades_df['trade_type'] == 'STOCK'])

    print(f"  Option trades: {option_count}")
    print(f"  Stock trades: {stock_count}")
    print(f"  Unparsed TRD rows: {len(df) - len(trades_df)}")

    return trades_df


# ============================================================
# CONSOLIDATE BUY ORDERS WITHIN 10-MINUTE WINDOW (REQ-020221_04)
# ============================================================

def consolidate_buys(entries_df):
    if len(entries_df) <= 1:
        return entries_df

    entries_sorted = entries_df.sort_values('DATETIME').reset_index(drop=True)
    consolidated = []
    used = set()

    for i, row in entries_sorted.iterrows():
        if i in used:
            continue

        group = [row]
        used.add(i)

        if row['DATETIME'] is not None:
            for j, other in entries_sorted.iterrows():
                if j in used or j == i:
                    continue
                if other['DATETIME'] is not None:
                    diff = abs((other['DATETIME'] - row['DATETIME']).total_seconds())
                    if diff <= 600:  # 10 minutes
                        group.append(other)
                        used.add(j)

        if len(group) == 1:
            consolidated.append(row)
        else:
            total_qty = sum(r['quantity'] for r in group)
            total_fees = sum(r['Misc Fees'] + r['Commissions & Fees'] for r in group)
            avg_price = sum(r['price'] * r['quantity'] for r in group) / total_qty

            merged = group[0].copy()
            merged['quantity'] = total_qty
            merged['price'] = round(avg_price, 4)
            merged['Misc Fees'] = 0
            merged['Commissions & Fees'] = round(total_fees, 2)
            consolidated.append(merged)

    return pd.DataFrame(consolidated)


# ============================================================
# MATCH ENTRIES WITH EXITS + POSITION TRACKING (REQ-020221_02)
# ============================================================

def match_entries_exits(trades_df, max_exits, audit_records):
    print(f"\nStep 3: Matching entries with exits...")

    positions = []

    for (symbol, trade_type), group in trades_df.groupby(['symbol', 'trade_type']):

        entries_raw = group[group['action'] == 'BOT'].copy()
        exits = group[group['action'] == 'SOLD'].sort_values('DATETIME').reset_index(drop=True)

        # REQ-020221_04: Consolidate buys within 10-minute window
        entries = consolidate_buys(entries_raw).sort_values('DATETIME').reset_index(drop=True)

        # REQ-020221_02: Track running position
        running_position = 0

        for _, entry in entries.iterrows():
            total_qty = entry['quantity']
            total_fees = entry['Misc Fees'] + entry['Commissions & Fees']
            avg_price = entry['price']

            running_position += total_qty

            position = {
                'symbol': symbol,
                'trade_type': trade_type,
                'option_type': entry.get('option_type', ''),
                'strike': entry.get('strike', 0),
                'entry_date': entry['DATE'],
                'entry_price': round(avg_price, 2),
                'entry_quantity': total_qty,
                'entry_fees': round(total_fees, 2),
                'exits': []
            }

            # Find exits after this entry date
            potential_exits = exits[pd.to_datetime(exits['DATE'], errors='coerce') >= pd.to_datetime(entry['DATE'], errors='coerce')].copy()

            remaining_qty = total_qty

            for exit_num in range(max_exits):
                if remaining_qty <= 0 or len(potential_exits) == 0:
                    break

                exit_trade = potential_exits.iloc[0]

                # REQ-020221_02: Check if this exit would make position go negative
                same_ref_exit = exits[exits['REF #'] == exit_trade['REF #']]
                exit_qty = same_ref_exit['quantity'].sum()

                if running_position - exit_qty < 0:
                    # ORPHAN â€” write to audit log
                    audit_records.append({
                        'Symbol': symbol,
                        'Type': trade_type,
                        'Action': 'SOLD',
                        'Date': exit_trade['DATE'],
                        'Qty': exit_qty,
                        'Price': exit_trade['price'],
                        'Reason': f'ORPHAN - position would go negative (running={running_position}, sell={exit_qty})'
                    })
                    potential_exits = potential_exits.iloc[1:]
                    continue

                exit_fees = same_ref_exit['Misc Fees'].sum() + same_ref_exit['Commissions & Fees'].sum()
                exit_price = (same_ref_exit['price'] * same_ref_exit['quantity']).sum() / same_ref_exit['quantity'].sum()
                exit_qty_used = min(exit_qty, remaining_qty)

                entry_dt = pd.to_datetime(entry['DATE'])
                exit_dt = pd.to_datetime(exit_trade['DATE'])
                days_held = (exit_dt - entry_dt).days

                position['exits'].append({
                    'exit_date': exit_trade['DATE'],
                    'exit_price': round(exit_price, 2),
                    'exit_quantity': exit_qty_used,
                    'exit_fees': round(exit_fees, 2),
                    'days_held': days_held
                })

                running_position -= exit_qty_used
                remaining_qty -= exit_qty_used
                potential_exits = potential_exits.iloc[1:]

            positions.append(position)

    print(f"  Created {len(positions)} position records")
    return positions


# ============================================================
# WRITE AUDIT LOG (REQ-020221_03)
# ============================================================

def write_audit_log(audit_records, output_dir, base_name):
    if not audit_records:
        print(f"  No orphaned records to log")
        return

    audit_path = output_dir / f"{base_name}_AUDIT_LOG.csv"
    audit_df = pd.DataFrame(audit_records)
    audit_df.to_csv(audit_path, index=False)
    print(f"  Audit log: {len(audit_records)} orphaned records -> {audit_path.name}")


# ============================================================
# FORMAT FOR OPTIONS LOG (27 columns)
# ============================================================

def format_options_log(positions):
    options_positions = [p for p in positions if p['trade_type'] == 'OPTION']
    if not options_positions:
        return pd.DataFrame()

    records = []
    for pos in options_positions:
        total_comm = pos['entry_fees'] + sum(ex['exit_fees'] for ex in pos['exits'])
        exit1 = pos['exits'][0] if len(pos['exits']) > 0 else {}
        exit2 = pos['exits'][1] if len(pos['exits']) > 1 else {}
        exit3 = pos['exits'][2] if len(pos['exits']) > 2 else {}

        records.append({
            'Symbol': pos['symbol'],
            'System': 'TOS_Import',
            'Trade Type': pos['option_type'],
            'Long/Short': 'Long',
            'Strike': pos['strike'],
            'Cur Stock $': pos['entry_price'],
            'Trade Date': pos['entry_date'],
            'Entry $$': pos['entry_price'],
            'Contracts': pos['entry_quantity'],
            'Exit #1 $': exit1.get('exit_price', ''),
            '# Exited': exit1.get('exit_quantity', ''),
            'Exit Date': exit1.get('exit_date', ''),
            '# of Days': exit1.get('days_held', ''),
            'Exit #2 $': exit2.get('exit_price', ''),
            '# Exited2': exit2.get('exit_quantity', ''),
            'Exit Date3': exit2.get('exit_date', ''),
            '# of Days4': exit2.get('days_held', ''),
            'Exit #3 $': exit3.get('exit_price', ''),
            '# Exited5': exit3.get('exit_quantity', ''),
            'Exit Date6': exit3.get('exit_date', ''),
            '# of Days7': exit3.get('days_held', ''),
            'Comm.': round(total_comm, 2),
            'Gain/Loss': '',
            'Trade Comments': '',
            'Exit #1': '',
            'Exit #2': '',
            'Exit #3': ''
        })

    return pd.DataFrame(records)


# ============================================================
# FORMAT FOR STOCKS LOG (26 columns)
# ============================================================

def format_stocks_log(positions):
    stock_positions = [p for p in positions if p['trade_type'] == 'STOCK']
    if not stock_positions:
        return pd.DataFrame()

    records = []
    for pos in stock_positions:
        total_comm = pos['entry_fees'] + sum(ex['exit_fees'] for ex in pos['exits'])
        exit1 = pos['exits'][0] if len(pos['exits']) > 0 else {}
        exit2 = pos['exits'][1] if len(pos['exits']) > 1 else {}

        records.append({
            'Symbol': pos['symbol'],
            'System': 'TOS_Import',
            'Long/Short': 'Long',
            'Trade Date': pos['entry_date'],
            'Entry Price': pos['entry_price'],
            'Shares': pos['entry_quantity'],
            'Exit #1': exit1.get('exit_price', ''),
            '# Exited': exit1.get('exit_quantity', ''),
            'Exit Date': exit1.get('exit_date', ''),
            '# of Days': exit1.get('days_held', ''),
            'Exit #2': exit2.get('exit_price', ''),
            '# Exited2': exit2.get('exit_quantity', ''),
            'Exit Date3': exit2.get('exit_date', ''),
            '# of Days4': exit2.get('days_held', ''),
            'Comm.': round(total_comm, 2),
            'Gain/Loss': '',
            'ROI': '',
            'Trade Comments': '',
            'Exit #1 Gain': '',
            'Exit #2 Gain': '',
            'Total Gain': '',
            'Total ROI %': '',
            'R:R Ratio': '',
            'Win/Loss': '',
            'Strategy Notes': '',
            'Review Status': ''
        })

    return pd.DataFrame(records)


# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python P_020_TOS_Parser_v2.3.py <TOS_CSV_FILE>")
        sys.exit(1)

    input_file = sys.argv[1]
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    print("=" * 80)
    print("P_020 TOS PARSER v2.3")
    print("=" * 80)
    print(f"Input: {input_path.name}")

    # Shared audit log â€” collects orphans from both options and stocks
    audit_records = []

    trades_df = load_tos_csv(input_file)

    print(f"\nStep 3: Matching entries with exits...")

    options_positions = match_entries_exits(
        trades_df[trades_df['trade_type'] == 'OPTION'].copy(),
        max_exits=3,
        audit_records=audit_records
    )
    print(f"  Created {len(options_positions)} option position records")

    stock_positions = match_entries_exits(
        trades_df[trades_df['trade_type'] == 'STOCK'].copy(),
        max_exits=2,
        audit_records=audit_records
    )
    print(f"  Created {len(stock_positions)} stock position records")

    all_positions = options_positions + stock_positions

    print(f"\nStep 4: Formatting for Excel logs...")

    options_df = format_options_log(all_positions)
    stocks_df = format_stocks_log(all_positions)

    base_name = input_path.stem
    output_dir = input_path.parent

    if len(options_df) > 0:
        options_output = output_dir / f"{base_name}_OPTIONS_IMPORT.csv"
        options_df.to_csv(options_output, index=False)
        print(f"  Options: {len(options_df)} trades -> {options_output.name}")
    else:
        print(f"  No option trades to export")

    if len(stocks_df) > 0:
        stocks_output = output_dir / f"{base_name}_STOCKS_IMPORT.csv"
        stocks_df.to_csv(stocks_output, index=False)
        print(f"  Stocks: {len(stocks_df)} trades -> {stocks_output.name}")
    else:
        print(f"  No stock trades to export")

    print(f"\nStep 5: Writing audit log...")
    write_audit_log(audit_records, output_dir, base_name)

    print("=" * 80)
    print("SUCCESS!")
    print("=" * 80)


if __name__ == "__main__":
    main()
