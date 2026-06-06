import sqlite3
import pandas as pd
from pathlib import Path

# Path configured to project hub standards
DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\catalog.db")

def generate_windows(window_size=5):
    """
    Generates sliding windows from price_bars and persists them 
    to the pattern_instances table. Cleans warm-up period rows.
    """
    conn = sqlite3.connect(DB_PATH)
    
    # Fetch symbols to iterate
    symbols = pd.read_sql("SELECT symbol_id, ticker FROM symbols", conn)
    
    # Feature columns as verified in price_bars table
    feature_cols = ['open', 'high', 'low', 'close', 'volume', 'stdiff', 'mtdiff', 
                    'ltdiff', 'neuralx', 'neuralx_max', 'pred_high', 'pred_low', 
                    'pred_range', 'williams_emai', 'psi', 'roc', 'triple_cross_short', 
                    'triple_cross_medium', 'triple_cross_long']
    
    for _, row in symbols.iterrows():
        print(f"Generating windows for {row['ticker']}...")
        
        # Load historical data for the specific symbol
        query = f"SELECT * FROM price_bars WHERE symbol_id={row['symbol_id']} ORDER BY bar_date ASC"
        df = pd.read_sql(query, conn)
        
        # --- CLEANING STEP ---
        # Remove any rows where indicators couldn't be calculated (the warm-up period)
        df = df.dropna(subset=feature_cols)
        # ---------------------
        
        if len(df) < window_size:
            print(f"Not enough clean data for {row['ticker']}. Skipping.")
            continue
            
        # Sliding window logic
        windows = []
        for i in range(len(df) - window_size + 1):
            window_df = df.iloc[i:i+window_size][feature_cols]
            
            # Create dict with metadata
            row_data = {
                'symbol_id': int(row['symbol_id']),
                'anchor_date': str(df.iloc[i+window_size-1]['bar_date'])
            }
            
            # Map features with explicit names
            for col in feature_cols:
                for idx in range(window_size):
                    row_data[f"{col}_{idx}"] = window_df.iloc[idx][col]
            
            windows.append(row_data)
            
        # Persistence Logic
        if windows:
            df_windows = pd.DataFrame(windows)
            
            # Save to pattern_instances
            df_windows.to_sql('pattern_instances', conn, if_exists='append', index=False)
            conn.commit()
            print(f"Successfully saved {len(windows)} cleaned windows for {row['ticker']}.")
        else:
            print(f"No windows generated for {row['ticker']}.")

    conn.close()
    print("Pipeline Window Generation Complete.")

if __name__ == "__main__":
    generate_windows()