r"""
FILE: intelliscan.py
VERSION: 3.6 (Deduplication Polish)
PATH: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\matching\intelliscan.py
DESCRIPTION: Compares a live candidate vector against the global DB without symbol bias.
"""
import sqlite3
import pandas as pd
import numpy as np
import re
from pathlib import Path
from scipy.spatial.distance import cdist

def clean_col(name):
    """Reduces a column name to its absolute root for matching."""
    n = str(name).lower().replace('_', '')
    n = n.replace('price', '') 
    n = re.sub(r'0$', '', n)   
    return n

def get_intelliscan_results(target_vector, db_path, top_n=5):
    """
    Performs agnostic matching across the entire catalog.
    target_vector: dict containing the live feature values.
    """
    if not target_vector:
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)
    
    # 1. Agnostic Query: Pull all instances, no symbol filter
    query = "SELECT * FROM pattern_instances"
    catalog_df = pd.read_sql_query(query, conn)
    conn.close()

    if catalog_df.empty:
        return pd.DataFrame()

    # 2. Dynamic Feature Alignment
    exclude_cols = [
        'rowid', 'pattern_instance_id', 'symbol_id', 'anchor_date', 
        'data_type', 'data_origin_type', 
        'forward_label_5d', 'forward_label_7d', 'forward_label_10d'
    ]
    feature_cols = [col for col in catalog_df.columns if col not in exclude_cols]
    
    try:
        live_map = {clean_col(k): k for k in target_vector.keys()}
        
        live_features = []
        for col in feature_cols:
            c_col = clean_col(col)
            
            if c_col in live_map:
                live_features.append(target_vector[live_map[c_col]])
            else:
                matched = False
                for live_c_key, raw_live_key in live_map.items():
                    if c_col in live_c_key or live_c_key in c_col:
                        live_features.append(target_vector[raw_live_key])
                        matched = True
                        break
                
                if not matched:
                    raise KeyError(f"DB wants '{col}' (root: '{c_col}'). Live CSV only has roots: {list(live_map.keys())}")
                
        live_array = np.array([live_features])
    except KeyError as e:
        print(f" [!] Schema Mismatch: {e}")
        return pd.DataFrame()

    catalog_array = catalog_df[feature_cols].values

    # 3. Vector Math: Calculate Euclidean distance across the n-dimensional space
    distances = cdist(live_array, catalog_array, metric='euclidean')[0]
    
    # 4. Rank and Filter
    catalog_df['euclidean_distance'] = distances
    
    # Sort closest to furthest
    catalog_df = catalog_df.sort_values(by='euclidean_distance', ascending=True)
    
    # THE POLISH: Drop duplicate symbols so we get 5 unique market analogs
    catalog_df = catalog_df.drop_duplicates(subset=['symbol_id'], keep='first')
    
    top_matches = catalog_df.head(top_n)
    
    return top_matches[['symbol_id', 'anchor_date', 'euclidean_distance']]