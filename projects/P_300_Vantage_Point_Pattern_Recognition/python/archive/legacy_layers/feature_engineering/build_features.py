import sqlite3
import pandas as pd
from pathlib import Path
import json

DB_PATH = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db'
DATA_DIR = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\historical')
MANIFEST_PATH = Path(r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\ingest\ingest_manifest.json')

def build_features():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Clear any broken data and ensure table exists
    cursor.execute("DROP TABLE IF EXISTS pattern_features")
    cursor.execute('''CREATE TABLE pattern_features (
        pattern_feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern_instance_id INTEGER NOT NULL,
        feature_name TEXT NOT NULL,
        feature_value REAL,
        FOREIGN KEY(pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id)
    )''')
    
    # 2. Load Mapping Manifest
    try:
        with open(MANIFEST_PATH, 'r') as f:
            mapping = json.load(f)['mapping']
    except Exception as e:
        print(f"Error loading manifest: {e}")
        return

    symbols_df = pd.read_sql("SELECT symbol_id, ticker FROM symbols", conn)
    symbol_map = dict(zip(symbols_df['ticker'].str.lower(), symbols_df['symbol_id']))
    
    instances_df = pd.read_sql("SELECT pattern_instance_id, symbol_id, anchor_date FROM pattern_instances", conn)
    instances_df['anchor_dt'] = pd.to_datetime(instances_df['anchor_date'], format='mixed')
    
    features_inserted = 0
    target_features = ['psi', 'neuralx', 'stdiff', 'mtdiff', 'ltdiff']
    print("Extracting Predictive Indicators from raw files...")
    
    for file_path in DATA_DIR.glob("Pattern_*.csv"):
        ticker = file_path.stem.split('_')[-1].lower()
        if ticker not in symbol_map: continue
        s_id = symbol_map[ticker]
        
        df = pd.read_csv(file_path)
        
        # 3. Clean and map columns exactly like the ingest script
        df.columns = [c.lower().strip().replace(' ', '').replace('\n', '') for c in df.columns]
        df.rename(columns=mapping, inplace=True)
        
        date_col = 'bar_date' if 'bar_date' in df.columns else next((c for c in df.columns if 'date' in c), None)
        if not date_col: continue
        
        df['dt'] = pd.to_datetime(df[date_col], format='mixed', errors='coerce')
        df_valid = df.dropna(subset=['dt'])
        
        # 4. Merge to find perfect matches on symbol and date
        merged = pd.merge(instances_df[instances_df['symbol_id'] == s_id], df_valid, left_on='anchor_dt', right_on='dt', how='inner')
        
        for _, row in merged.iterrows():
            inst_id = row['pattern_instance_id']
            for feat in target_features:
                if feat in row and pd.notna(row[feat]):
                    try:
                        val = float(row[feat])
                        cursor.execute("INSERT INTO pattern_features (pattern_instance_id, feature_name, feature_value) VALUES (?, ?, ?)", (inst_id, f"{feat}_0", val))
                        features_inserted += 1
                    except ValueError:
                        pass
                        
    conn.commit()
    conn.close()
    print(f"Successfully loaded {features_inserted} predictive features into catalog.")

if __name__ == '__main__':
    build_features()
