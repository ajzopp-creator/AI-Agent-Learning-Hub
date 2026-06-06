"""
FILE: intelliscan.py
VERSION: 3.0 (Library-Wide Agnostic Matching)
PATH: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\matching\intelliscan.py
DESCRIPTION: Compares a live candidate vector against the global DB without symbol bias.
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.spatial.distance import cdist

def get_intelliscan_results(target_vector, db_path, top_n=5):
    """
    Performs agnostic matching across the entire catalog.
    target_vector: dict containing the live feature values.
    """
    if not target_vector:
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)
    
    # 1. Agnostic Query: Pull all instances, no symbol filter
    # Assuming columns ending in '_0', '_1', '_2', etc., are the standardized features
    query = "SELECT * FROM pattern_instances"
    catalog_df = pd.read_sql_query(query, conn)
    conn.close()

    if catalog_df.empty:
        return pd.DataFrame()

    # 2. Dynamic Feature Alignment
    # Extract only the numerical feature columns used for math (ignoring metadata)
    exclude_cols = ['rowid', 'symbol_id', 'anchor_date', 'forward_label_5d', 'forward_label_7d', 'forward_label_10d']
    feature_cols = [col for col in catalog_df.columns if col not in exclude_cols]
    
    # Ensure target vector aligns exactly with the catalog feature schema
    try:
        live_array = np.array([[target_vector[col] for col in feature_cols]])
    except KeyError as e:
        print(f" [!] Schema Mismatch in Live Vector: Missing {e}")
        return pd.DataFrame()

    catalog_array = catalog_df[feature_cols].values

    # 3. Vector Math: Calculate Euclidean distance across the n-dimensional space
    # cdist computes the distance between every pair; we take the first (and only) row
    distances = cdist(live_array, catalog_array, metric='euclidean')[0]
    
    # 4. Rank and Filter
    catalog_df['euclidean_distance'] = distances
    
    # Sort closest to furthest
    top_matches = catalog_df.sort_values(by='euclidean_distance', ascending=True).head(top_n)
    
    # Return the metadata of the closest matches to feed the Reporting module
    return top_matches[['symbol_id', 'anchor_date', 'euclidean_distance']]