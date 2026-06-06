# vantagepoint_batch_xlsx_to_csv_and_mark_done.py
# Converts ALL .xlsx files in the folder to .csv, then renames original to .xlsx.conv
# Requirements: pip install pandas openpyxl

import pandas as pd

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CONFIGURATION
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

import os
from pathlib import Path

# ── PATH CONFIGURATION ──────────────────────────────────────────────────────
# Uses %OneDrive% environment variable — survives OneDrive folder moves.
# To change the target folder, update %OneDrive% via:
#   System Properties → Environment Variables → User Variables → OneDrive
FOLDER_PATH = Path(os.environ["OneDrive"]) / "Documents" / "AJZStrategiesLLC" / "P_300_ Vantage Point Up Trend Pattern Recognitonr"
# ────────────────────────────────────────────────────────────────────────────

# Set to True if you also want to process files in subfolders
RECURSIVE = False

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def clean_column_name(name):
    """Remove newlines, extra spaces, make clean for CSV"""
    if pd.isna(name):
        return "Unnamed"
    return (
        str(name)
        .replace('\n', ' ')
        .replace('\r', '')
        .strip()
        .replace('  ', ' ')
    )

def convert_and_mark_done(xlsx_path):
    xlsx_path = Path(xlsx_path)
    csv_path = xlsx_path.with_suffix('.csv')
    done_path = xlsx_path.with_suffix('.xlsx.conv')

    if csv_path.exists():
        print(f"CSV already exists, skipping: {xlsx_path.name}")
        # Still rename to .conv if not already done
        if not done_path.exists():
            xlsx_path.rename(done_path)
            print(f"  â†’ Renamed original to {done_path.name}")
        return

    try:
        # Read Excel
        df = pd.read_excel(xlsx_path, header=None)

        # Auto-detect header row (look for 'Date' or 'Short Term' etc.)
        header_row = None
        for i in range(min(10, len(df))):
            row_str = df.iloc[i].astype(str).str.lower().str.cat(sep=' ')
            if 'date' in row_str or 'short' in row_str or 'difference' in row_str:
                header_row = i
                break

        if header_row is None:
            print(f"  Warning: No header detected in {xlsx_path.name} â€” using row 0")
            header_row = 0

        # Set header and remove header rows
        df.columns = [clean_column_name(c) for c in df.iloc[header_row]]
        df = df.iloc[header_row + 1:].reset_index(drop=True)

        # Try to convert numeric columns
        potential_numeric = [
            'Short Term Difference', 'Medium Term Difference', 'Long Term Difference',
            'Open Price', 'High Price', 'Low Price', 'Close Price',
            'Predicted High Price', 'Predicted Low Price', 'Volume',
            'Williams EMAI', 'PSI', 'ROC%', 'NeuralXMax',
            'Predicted High Diff', 'Predicted Low Diff', 'Predicted Range'
        ]
        for col in df.columns:
            if col in potential_numeric or any(p in col for p in potential_numeric):
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Sort by Date if present
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.sort_values('Date').reset_index(drop=True)

        # Save CSV
        df.to_csv(csv_path, index=False, float_format='%.8f')
        print(f"Converted: {xlsx_path.name} â†’ {csv_path.name}  ({len(df)} rows)")

        # Rename original to .conv
        xlsx_path.rename(done_path)
        print(f"  â†’ Renamed original to {done_path.name}")

    except Exception as e:
        print(f"Error processing {xlsx_path.name}: {e}")


def process_folder(folder_path, recursive=False):
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"Folder not found: {folder}")
        return

    pattern = "**/*.xlsx" if recursive else "*.xlsx"
    xlsx_files = list(folder.glob(pattern))

    if not xlsx_files:
        print("No .xlsx files found.")
        return

    print(f"Found {len(xlsx_files)} .xlsx files. Processing...\n")

    for file in xlsx_files:
        # Skip already processed files
        if file.suffix == '.xlsx' and not file.with_suffix('.xlsx.conv').exists():
            convert_and_mark_done(file)


if __name__ == "__main__":
    print("VantagePoint Excel â†’ CSV Batch Converter + Mark Done")
    print(f"Target folder: {FOLDER_PATH}\n")

    process_folder(FOLDER_PATH, recursive=RECURSIVE)

    print("\nDone. You can now upload the .csv files here without truncation issues.")
