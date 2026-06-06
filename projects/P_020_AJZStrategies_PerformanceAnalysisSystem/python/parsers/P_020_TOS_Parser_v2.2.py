#!/usr/bin/env python3
"""
P_020 TOS Parser v2.2
Parses ThinkorSwim Account Statement CSV exports into Excel-ready import files.

Updates in v2.2:
- Added Exit #3 support for options (3 exits vs 2 for stocks)
- Extract Strike price from option symbols
- Cur Stock $ populated with Entry Price
- Fixed column names to match Excel templates exactly
- Options: 27 columns, Stocks: 26 columns
"""

import pandas as pd
import numpy as np
import re
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# PARSE TOS DESCRIPTION FIELD
# ============================================================

def parse_description(desc):
    """
    Parse TOS DESCRIPTION field to extract trade details.
    
    Examples:
    "BOT +2 QBTS 01/17/26 PUT 25 @2.32"
    "SOLD -2 QBTS 01/17/26 PUT 25 @3.14"
    "BOT +100 AAPL @180.50"
    "SOLD -50 AAPL @182.00"
    """
    if not isinstance(desc, str):
        return None
    
    # Option pattern: BOT/SOLD +/-qty SYMBOL 100 DD MMM YY strike CALL/PUT @price
    option_pattern = r'(BOT|SOLD)\s+([+-])(\d+)\s+([A-Z]+)\s+100\s+(\d{1,2}\s+[A-Z]{3}\s+\d{2})\s+([\d.]+)\s+(CALL|PUT)\s+@([\d.]+)'
    
    # Stock pattern: BOT/SOLD +/-qty SYMBOL @price
    stock_pattern = r'(BOT|SOLD)\s+([+-])(\d+)\s+([A-Z]+)\s+@([\d.]+)'
    
    # Try option first
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
    
    # Try stock
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
# LOAD AND PARSE TOS CSV
# ============================================================

def load_tos_csv(filepath):
    """Load TOS CSV and parse all BOT/SOLD transactions."""
    
    print(f"Step 1: Loading TOS account statement...")
    
    # Find the header row (starts with "DATE,TIME,TYPE")
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if line.startswith('DATE,TIME,TYPE'):
                csv_start = i
                break
    
    # Load CSV from header row (with error handling for malformed rows)
    df = pd.read_csv(filepath, skiprows=csv_start, on_bad_lines='skip', engine='python')
    print(f"  âœ“ Loaded {len(df)} transactions")
    
    # Parse DESCRIPTION field
    print(f"\nStep 2: Parsing DESCRIPTION fields...")
    trades = []
    
    for idx, row in df.iterrows():
        parsed = parse_description(row.get('DESCRIPTION', ''))
        if parsed:
            trades.append({
                'DATE': row['DATE'],
                'REF #': row.get('REF #', ''),
                'MISC FEES': row.get('MISC FEES', 0),
                'COMMISSIONS': row.get('COMMISSIONS', 0),
                **parsed
            })
    
    trades_df = pd.DataFrame(trades)
    
    option_count = len(trades_df[trades_df['trade_type'] == 'OPTION'])
    stock_count = len(trades_df[trades_df['trade_type'] == 'STOCK'])
    
    print(f"  âœ“ Option trades: {option_count}")
    print(f"  âœ“ Stock trades: {stock_count}")
    print(f"  âš  Unparsed: {len(df) - len(trades_df)}")
    
    return trades_df


# ============================================================
# MATCH ENTRIES WITH EXITS
# ============================================================

def match_entries_exits(trades_df, max_exits=2):
    """
    Match BOT (entry) trades with SOLD (exit) trades.
    Supports up to max_exits partial exits.
    """
    
    print(f"\nStep 3: Matching entries with exits...")
    
    positions = []
    
    # Group by symbol and trade type
    for (symbol, trade_type), group in trades_df.groupby(['symbol', 'trade_type']):
        
        # Separate entries and exits
        entries = group[group['action'] == 'BOT'].copy()
        exits = group[group['action'] == 'SOLD'].copy()
        
        entries = entries.sort_values('DATE').reset_index(drop=True)
        exits = exits.sort_values('DATE').reset_index(drop=True)
        
        # Match each entry with its exits
        for _, entry in entries.iterrows():
            
            # Aggregate multiple fills with same REF #
            same_ref = entries[entries['REF #'] == entry['REF #']]
            total_qty = same_ref['quantity'].sum()
            total_fees = same_ref['MISC FEES'].sum() + same_ref['COMMISSIONS'].sum()
            avg_price = (same_ref['price'] * same_ref['quantity']).sum() / total_qty
            
            # Find exits after this entry
            potential_exits = exits[exits['DATE'] > entry['DATE']].copy()
            
            # Build position record
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
            
            remaining_qty = total_qty
            
            # Match up to max_exits
            for exit_num in range(max_exits):
                if remaining_qty <= 0 or len(potential_exits) == 0:
                    break
                
                exit_trade = potential_exits.iloc[0]
                
                # Aggregate fills for this exit REF #
                same_ref_exit = exits[exits['REF #'] == exit_trade['REF #']]
                exit_qty = min(same_ref_exit['quantity'].sum(), remaining_qty)
                exit_fees = same_ref_exit['MISC FEES'].sum() + same_ref_exit['COMMISSIONS'].sum()
                exit_price = (same_ref_exit['price'] * same_ref_exit['quantity']).sum() / same_ref_exit['quantity'].sum()
                
                # Calculate days held
                entry_dt = pd.to_datetime(entry['DATE'])
                exit_dt = pd.to_datetime(exit_trade['DATE'])
                days_held = (exit_dt - entry_dt).days
                
                position['exits'].append({
                    'exit_date': exit_trade['DATE'],
                    'exit_price': round(exit_price, 2),
                    'exit_quantity': exit_qty,
                    'exit_fees': round(exit_fees, 2),
                    'days_held': days_held
                })
                
                remaining_qty -= exit_qty
                potential_exits = potential_exits.iloc[1:]  # Remove used exit
            
            positions.append(position)
    
    print(f"  âœ“ Created {len(positions)} position records")
    
    return positions


# ============================================================
# FORMAT FOR OPTIONS LOG (27 columns)
# ============================================================

def format_options_log(positions):
    """
    Format positions for Options Excel log.
    
    Columns (27):
    Symbol | System | Trade Type | Long/Short | Strike | Cur Stock $ | 
    Trade Date | Entry $$ | Contracts | Exit #1 $ | # Exited | Exit Date | # of Days |
    Exit #2 $ | # Exited2 | Exit Date3 | # of Days4 | Exit #3 $ | # Exited5 | 
    Exit Date6 | # of Days7 | Comm. | Gain/Loss | Trade Comments | Exit #1 | Exit #2 | Exit #3
    """
    
    options_positions = [p for p in positions if p['trade_type'] == 'OPTION']
    
    if len(options_positions) == 0:
        return pd.DataFrame()
    
    records = []
    
    for pos in options_positions:
        
        # Total commission (entry + all exits)
        total_comm = pos['entry_fees']
        for ex in pos['exits']:
            total_comm += ex['exit_fees']
        
        # Extract exit data (up to 3 exits)
        exit1 = pos['exits'][0] if len(pos['exits']) > 0 else {}
        exit2 = pos['exits'][1] if len(pos['exits']) > 1 else {}
        exit3 = pos['exits'][2] if len(pos['exits']) > 2 else {}
        
        record = {
            'Symbol': pos['symbol'],
            'System': 'TOS_Import',
            'Trade Type': pos['option_type'],  # CALL or PUT
            'Long/Short': 'Long',
            'Strike': pos['strike'],
            'Cur Stock $': pos['entry_price'],  # Use entry price as placeholder
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
            'Gain/Loss': '',  # Formula column
            'Trade Comments': '',
            'Exit #1': '',  # Formula column
            'Exit #2': '',  # Formula column
            'Exit #3': ''   # Formula column
        }
        
        records.append(record)
    
    return pd.DataFrame(records)


# ============================================================
# FORMAT FOR STOCKS LOG (26 columns)
# ============================================================

def format_stocks_log(positions):
    """
    Format positions for Stocks Excel log.
    
    Columns (26):
    Symbol | System | Long/Short | Trade Date | Entry Price | Shares |
    Exit #1 | # Exited | Exit Date | # of Days | Exit #2 | # Exited2 |
    Exit Date3 | # of Days4 | Comm. | Gain/Loss | ROI | Trade Comments |
    Exit #1 Gain | Exit #2 Gain | Total Gain | Total ROI % | R:R Ratio |
    Win/Loss | Strategy Notes | Review Status
    """
    
    stock_positions = [p for p in positions if p['trade_type'] == 'STOCK']
    
    if len(stock_positions) == 0:
        return pd.DataFrame()
    
    records = []
    
    for pos in stock_positions:
        
        # Total commission
        total_comm = pos['entry_fees']
        for ex in pos['exits']:
            total_comm += ex['exit_fees']
        
        # Extract exit data (up to 2 exits for stocks)
        exit1 = pos['exits'][0] if len(pos['exits']) > 0 else {}
        exit2 = pos['exits'][1] if len(pos['exits']) > 1 else {}
        
        record = {
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
            'Gain/Loss': '',  # Formula column
            'ROI': '',  # Formula column
            'Trade Comments': '',
            'Exit #1 Gain': '',  # Formula column
            'Exit #2 Gain': '',  # Formula column
            'Total Gain': '',
            'Total ROI %': '',
            'R:R Ratio': '',
            'Win/Loss': '',
            'Strategy Notes': '',
            'Review Status': ''
        }
        
        records.append(record)
    
    return pd.DataFrame(records)


# ============================================================
# MAIN
# ============================================================

def main():
    
    if len(sys.argv) < 2:
        print("Usage: python P_020_TOS_Parser_v2.2.py <TOS_CSV_FILE>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("P_020 TOS PARSER v2.2")
    print("=" * 80)
    print(f"Input: {input_path.name}")
    
    # Load and parse TOS CSV
    trades_df = load_tos_csv(input_file)
    
    # Match entries with exits
    # Options get 3 exits, stocks get 2  
    options_positions = match_entries_exits(
        trades_df[trades_df['trade_type'] == 'OPTION'], 
        max_exits=3
    )
    stock_positions = match_entries_exits(
        trades_df[trades_df['trade_type'] == 'STOCK'], 
        max_exits=2
    )
    
    all_positions = options_positions + stock_positions
    
    # Format outputs
    print(f"\nStep 4: Formatting for Excel logs...")
    
    options_df = format_options_log(all_positions)
    stocks_df = format_stocks_log(all_positions)
    
    # Determine output paths
    base_name = input_path.stem
    output_dir = input_path.parent
    
    # Write output files
    if len(options_df) > 0:
        options_output = output_dir / f"{base_name}_OPTIONS_IMPORT.csv"
        options_df.to_csv(options_output, index=False)
        print(f"  âœ“ Options: {len(options_df)} trades â†’ {options_output.name}")
    else:
        print(f"  âš  No option trades to export")
    
    if len(stocks_df) > 0:
        stocks_output = output_dir / f"{base_name}_STOCKS_IMPORT.csv"
        stocks_df.to_csv(stocks_output, index=False)
        print(f"  âœ“ Stocks: {len(stocks_df)} trades â†’ {stocks_output.name}")
    else:
        print(f"  âš  No stock trades to export")
    
    print("=" * 80)
    print("âœ… SUCCESS!")
    print("=" * 80)


if __name__ == "__main__":
    main()