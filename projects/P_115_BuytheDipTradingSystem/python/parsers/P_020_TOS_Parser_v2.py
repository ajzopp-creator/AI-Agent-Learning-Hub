#!/usr/bin/env python3
"""
P_115_TOS_Parser_v2.py - Enhanced TOS Account Statement Parser
Parses ThinkorSwim CSV exports and maps to P_115 Stock/Options log format

Author: Anthony (AJZ Strategies)
Version: 2.0
Date: 2026-01-28
"""

import pandas as pd
import numpy as np
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================================
# REGEX PATTERNS for TOS DESCRIPTION field
# ============================================================================

# Options: BOT +2 QBTS 100 16 JAN 26 27 CALL @2.32 CBOE
OPTION_PATTERN = r'^(BOT|SOLD)\s+([+-]?\d+)\s+([A-Z]{1,6})\s+100\s+(\d{2})\s+([A-Z]{3})\s+(\d{2})\s+([\d.]+)\s+(CALL|PUT)\s+@([\d.]+)'

# Stocks: SOLD -7 TWLO @136.10
STOCK_PATTERN = r'^(BOT|SOLD)\s+([+-]?\d+)\s+([A-Z]{1,6})\s+@([\d.]+)'


# ============================================================================
# PARSING FUNCTIONS
# ============================================================================

def parse_tos_description(description):
    """
    Parse TOS DESCRIPTION field into structured data.
    
    Returns dict with keys: trade_type, action, quantity, symbol, 
                           strike, option_type, expiration, price
    """
    desc = str(description).strip()
    
    # Try OPTIONS pattern first
    opt_match = re.match(OPTION_PATTERN, desc)
    if opt_match:
        return {
            'trade_type': 'OPTION',
            'action': opt_match.group(1),
            'quantity': abs(int(opt_match.group(2))),
            'symbol': opt_match.group(3),
            'exp_day': opt_match.group(4),
            'exp_month': opt_match.group(5),
            'exp_year': opt_match.group(6),
            'strike': float(opt_match.group(7)),
            'option_type': opt_match.group(8),
            'price': float(opt_match.group(9)),
            'expiration': f"{opt_match.group(4)} {opt_match.group(5)} {opt_match.group(6)}"
        }
    
    # Try STOCK pattern
    stock_match = re.match(STOCK_PATTERN, desc)
    if stock_match:
        return {
            'trade_type': 'STOCK',
            'action': stock_match.group(1),
            'quantity': abs(int(stock_match.group(2))),
            'symbol': stock_match.group(3),
            'price': float(stock_match.group(4)),
            'strike': None,
            'option_type': None,
            'expiration': None
        }
    
    # Unparseable
    return {
        'trade_type': 'UNKNOWN',
        'action': None,
        'quantity': None,
        'symbol': None,
        'price': None,
        'description_raw': desc
    }


def load_tos_csv(filepath):
    """
    Load TOS CSV account statement.
    Handles the 3 header rows and BOM characters.
    """
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    # Find where CSV data starts (line with DATE,TIME,TYPE...)
    csv_start = None
    for i, line in enumerate(lines):
        if 'DATE,TIME,TYPE' in line:
            csv_start = i
            break
    
    if csv_start is None:
        raise ValueError("Could not find CSV header row starting with 'DATE,TIME,TYPE'")
    
    # Read CSV from that point
    import csv
    trades = []
    reader = csv.DictReader(lines[csv_start:])
    for row in reader:
        trades.append(row)
    
    return pd.DataFrame(trades)


def parse_all_trades(df):
    """
    Parse all DESCRIPTION fields and add structured columns.
    """
    parsed = df['DESCRIPTION'].apply(parse_tos_description)
    parsed_df = pd.DataFrame(parsed.tolist())
    
    # Combine with original
    result = pd.concat([df, parsed_df], axis=1)
    
    # Clean up numeric columns
    result['Commissions & Fees'] = pd.to_numeric(result['Commissions & Fees'], errors='coerce').fillna(0)
    result['Misc Fees'] = pd.to_numeric(result['Misc Fees'], errors='coerce').fillna(0)
    result['AMOUNT'] = pd.to_numeric(result['AMOUNT'], errors='coerce').fillna(0)
    
    # Calculate total commission
    result['total_commission'] = result['Commissions & Fees'] + result['Misc Fees']
    
    return result


# ============================================================================
# TRADE GROUPING (Match BUYs with SELLs)
# ============================================================================

def group_trades_into_positions(df):
    """
    Group individual TOS trades into complete positions.
    Matches BOT (entries) with SOLD (exits).
    """
    # Filter to only parsed trades
    df = df[df['trade_type'].isin(['STOCK', 'OPTION'])].copy()
    
    # Sort by date/time
    df['datetime'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'])
    df = df.sort_values('datetime').reset_index(drop=True)
    
    positions = []
    
    # Group by symbol + option details (for options) or just symbol (for stocks)
    for symbol in df['symbol'].unique():
        symbol_trades = df[df['symbol'] == symbol].copy()
        
        # Further group options by strike/exp/type
        if symbol_trades.iloc[0]['trade_type'] == 'OPTION':
            for (strike, opt_type, exp), group in symbol_trades.groupby(['strike', 'option_type', 'expiration']):
                positions.extend(_match_entries_exits(group))
        else:
            positions.extend(_match_entries_exits(symbol_trades))
    
    return pd.DataFrame(positions)


def _match_entries_exits(trades_df):
    """
    Match BOT trades with SOLD trades for a specific symbol/option.
    Uses FIFO (First In First Out) matching.
    """
    entries = trades_df[trades_df['action'] == 'BOT'].copy()
    exits = trades_df[trades_df['action'] == 'SOLD'].copy()
    
    if entries.empty:
        return []
    
    positions = []
    
    for _, entry in entries.iterrows():
        position = {
            # Entry info
            'Symbol': entry['symbol'],
            'Trade Type': entry['option_type'] if entry['trade_type'] == 'OPTION' else 'Stock',
            'Long': 'Long',  # TOS exports are from long perspective
            'Trade Date': entry['DATE'],
            'Entry Price': entry['price'],
            'Contracts': entry['quantity'] if entry['trade_type'] == 'OPTION' else None,
            'Shares': entry['quantity'] if entry['trade_type'] == 'STOCK' else None,
            
            # Option-specific
            'Strike': entry['strike'],
            'Expiration': entry['expiration'],
            
            # Exit info (will be filled if matched)
            'Exit #1': None,
            '# Exited': None,
            'Exit Date': None,
            '# of Days': None,
            
            # Financial
            'Comm.': abs(entry['total_commission']),
            'Entry Amount': entry['AMOUNT'],
            
            # Meta
            'Trade Type Flag': entry['trade_type'],
            'REF #': entry['REF #']
        }
        
        # Try to match with an exit
        matching_exits = exits[
            (exits['symbol'] == entry['symbol']) &
            (exits['datetime'] >= entry['datetime'])
        ]
        
        if not matching_exits.empty:
            exit_trade = matching_exits.iloc[0]
            
            position['Exit #1'] = exit_trade['price']
            position['# Exited'] = exit_trade['quantity']
            position['Exit Date'] = exit_trade['DATE']
            
            # Calculate days
            entry_date = pd.to_datetime(entry['DATE'])
            exit_date = pd.to_datetime(exit_trade['DATE'])
            position['# of Days'] = (exit_date - entry_date).days
            
            # Add exit commission
            position['Comm.'] += abs(exit_trade['total_commission'])
            position['Exit Amount'] = exit_trade['AMOUNT']
        
        positions.append(position)
    
    return positions


# ============================================================================
# OUTPUT FORMATTING for Excel Logs
# ============================================================================

def format_for_options_log(positions_df):
    """
    Format parsed positions to match Options Log columns.
    
    Options Log Columns (20):
    Symbol | System | Trade Type | Long | Trade Date | Entry Price | Contracts |
    Exit #1 | # Exited | Exit Date | # of Days | Exit #2 | # Exited2 | 
    Exit Date3 | # of Days4 | Comm. | Gain/Loss | Trade Comments | 
    Exit #1 Gain | Exit #2 Gain
    """
    options_df = positions_df[positions_df['Trade Type Flag'] == 'OPTION'].copy()
    
    if options_df.empty:
        return pd.DataFrame()
    
    output = pd.DataFrame({
        'Symbol': options_df['Symbol'],
        'System': 'TOS_Import',  # User will update manually
        'Trade Type': options_df['Trade Type'],
        'Long': options_df['Long'],
        'Trade Date': options_df['Trade Date'],
        'Entry Price': options_df['Entry Price'],
        'Contracts': options_df['Contracts'],
        'Exit #1': options_df['Exit #1'],
        '# Exited': options_df['# Exited'],
        'Exit Date': options_df['Exit Date'],
        '# of Days': options_df['# of Days'],
        'Exit #2': '',  # Placeholder
        '# Exited2': '',
        'Exit Date3': '',
        '# of Days4': '',
        'Comm.': options_df['Comm.'],
        'Gain/Loss': '',  # Will be calculated by Excel formula
        'Trade Comments': options_df['Strike'].apply(lambda x: f"Strike: ${x}" if pd.notna(x) else ''),
        'Exit #1 Gain': '',  # Will be calculated by Excel formula
        'Exit #2 Gain': ''
    })
    
    return output


def format_for_stock_log(positions_df):
    """
    Format parsed positions to match Stock Log columns (TradeLog table).
    
    Stock Log Columns (26):
    Symbol | System | Long/Short | Trade Date | Entry Price | Shares |
    Exit #1 | # Exited | Exit Date | # of Days | Exit #2 | # Exited2 |
    Exit Date3 | # of Days4 | Comm. | Gain/Loss | ROI | Trade Comments |
    Exit #1 Gain | Exit #2 Gain | Total Gain | Total ROI % | R:R Ratio |
    Win/Loss | Strategy Notes | Review Status
    """
    stocks_df = positions_df[positions_df['Trade Type Flag'] == 'STOCK'].copy()
    
    if stocks_df.empty:
        return pd.DataFrame()
    
    output = pd.DataFrame({
        'Symbol': stocks_df['Symbol'],
        'System': 'TOS_Import',  # User will update manually (P_115/P_116/P_117/P_118/P_300)
        'Long/Short': stocks_df['Long'],
        'Trade Date': stocks_df['Trade Date'],
        'Entry Price': stocks_df['Entry Price'],
        'Shares': stocks_df['Shares'],
        'Exit #1': stocks_df['Exit #1'],
        '# Exited': stocks_df['# Exited'],
        'Exit Date': stocks_df['Exit Date'],
        '# of Days': stocks_df['# of Days'],
        'Exit #2': '',  # Placeholder for second exit
        '# Exited2': '',  # Placeholder
        'Exit Date3': '',  # Placeholder
        '# of Days4': '',  # Placeholder
        'Comm.': stocks_df['Comm.'],
        'Gain/Loss': '',  # Excel formula: =IF(OR($F2=0, SUM($H2, $L2)<$F2), "", IF($C2="Long", (IFERROR($G2*$H2,0) + IFERROR($K2*$L2,0)) - ($E2*$F2), ($E2*$F2) - (IFERROR($G2*$H2,0) + IFERROR($K2*$L2,0))) - IFERROR($O2,0))
        'ROI': '',  # Excel formula: =IF($P2="","",IF($F2=0,"",($P2/($E2*$F2))))
        'Trade Comments': '',  # User adds notes
        'Exit #1 Gain': '',  # Excel formula: =IF($C2="Long",(($G2-$E2)*$H2),(($E2-$G2)*$H2))
        'Exit #2 Gain': '',  # Excel formula: =IF($C2="Long",(($K2-$E2)*$L2),(($E2-$K2)*$L2))
        'Total Gain': '',  # Excel formula: =S2+T2
        'Total ROI %': '',  # Excel formula: =IF($F2=0,"",($U2/($E2*$F2)))
        'R:R Ratio': '',  # User calculates or formula
        'Win/Loss': '',  # Excel formula: =IF($P2>0,"Win",IF($P2<0,"Loss",""))
        'Strategy Notes': '',  # User adds strategy-specific notes
        'Review Status': 'Pending'  # Default status
    })
    
    return output


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    
    if len(sys.argv) < 2:
        print("Usage: python P_115_TOS_Parser_v2.py <tos_account_statement.csv>")
        print("\nExample:")
        print("  python P_115_TOS_Parser_v2.py 2026-01-28_AJZ_Strategies_YTD_AccountStatement.csv")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)
    
    print("="*80)
    print("P_115 TOS PARSER v2.0")
    print("="*80)
    print(f"\nInput: {input_file.name}\n")
    
    # Step 1: Load TOS CSV
    print("Step 1: Loading TOS account statement...")
    df = load_tos_csv(input_file)
    print(f"  ✓ Loaded {len(df)} transactions")
    
    # Step 2: Parse all trades
    print("\nStep 2: Parsing DESCRIPTION fields...")
    parsed_df = parse_all_trades(df)
    
    options_count = len(parsed_df[parsed_df['trade_type'] == 'OPTION'])
    stocks_count = len(parsed_df[parsed_df['trade_type'] == 'STOCK'])
    unknown_count = len(parsed_df[parsed_df['trade_type'] == 'UNKNOWN'])
    
    print(f"  ✓ Option trades: {options_count}")
    print(f"  ✓ Stock trades: {stocks_count}")
    if unknown_count > 0:
        print(f"  ⚠ Unparsed: {unknown_count}")
    
    # Step 3: Group into positions
    print("\nStep 3: Matching entries with exits...")
    positions_df = group_trades_into_positions(parsed_df)
    print(f"  ✓ Created {len(positions_df)} position records")
    
    # Step 4: Format outputs
    print("\nStep 4: Formatting for Excel logs...")
    
    # Options output
    options_output = format_for_options_log(positions_df)
    if not options_output.empty:
        options_file = input_file.with_name(f"{input_file.stem}_OPTIONS_IMPORT.csv")
        options_output.to_csv(options_file, index=False)
        print(f"  ✓ Options: {len(options_output)} trades → {options_file.name}")
    else:
        print(f"  - No option trades to export")
    
    # Stock output
    stocks_output = format_for_stock_log(positions_df)
    if not stocks_output.empty:
        stocks_file = input_file.with_name(f"{input_file.stem}_STOCKS_IMPORT.csv")
        stocks_output.to_csv(stocks_file, index=False)
        print(f"  ✓ Stocks: {len(stocks_output)} trades → {stocks_file.name}")
    else:
        print(f"  - No stock trades to export")
    
    # Summary
    print("\n" + "="*80)
    print("✅ SUCCESS!")
    print("="*80)
    print(f"\nOutput files created:")
    if not options_output.empty:
        print(f"  📊 {options_file.name}")
        print(f"     → Paste into: P115__Paper_Options_Log_v2.xlsx")
    if not stocks_output.empty:
        print(f"  📈 {stocks_file.name}")
        print(f"     → Paste into: P_115__Paper_Stock_Log-V4.xlsx")
    
    print("\n💡 TIP: Open CSV files, copy all rows, paste into Excel starting at next empty row")
    print()


if __name__ == "__main__":
    main()
