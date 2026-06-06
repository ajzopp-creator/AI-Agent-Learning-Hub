"""
FILE: intelliscan.py
VERSION: 2.1
DATE: 2026-05-06
DESCRIPTION: Core logic for distance-weighted pattern matching.
CHANGELOG:
    - v2.1: Added version header. Hardcoded absolute DB path to prevent import-time resolution errors.
    - v2.0: Optimized SQL fetch logic to use DISTINCT instance IDs.
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# Hardcoded absolute path to ensure connectivity regardless of execution context
DB_PATH = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050626geminicatalog.db")

WEIGHTS = {
    'psi': 0.40,
    'neuralx': 0.40,
    'close': 0.05,
    'stdiff': 0.05,
    'mtdiff': 0.05,
    'ltdiff': 0.05
}

def get_weighted_distance(vec1, vec2):
    norm1 = {k.split('_')[0]: v for k, v in vec1.items()}
    norm2 = {k.split('_')[0]: v for k, v in vec2.items()}
    
    distance = 0
    for feature, weight in WEIGHTS.items():
        if feature in norm1 and feature in norm2:
            val1 = norm1[feature]
            val2 = norm2[feature]
            distance += weight * ((val1 - val2) ** 2)
    return np.sqrt(distance)

def get_intelliscan_results(anchor_id):
    conn = sqlite3.connect(DB_PATH)
    anchor_df = pd.read_sql(f"SELECT feature_name, feature_value FROM pattern_features WHERE pattern_instance_id = {anchor_id}", conn)
    anchor_vec = dict(zip(anchor_df['feature_name'], anchor_df['feature_value']))
    
    query = f"""
    SELECT DISTINCT p.pattern_instance_id 
    FROM pattern_instances p
    JOIN pattern_features f ON p.pattern_instance_id = f.pattern_instance_id
    WHERE p.pattern_instance_id != {anchor_id}
    GROUP BY p.pattern_instance_id
    HAVING COUNT(f.feature_name) >= 3
    """
    candidates = pd.read_sql(query, conn)
    
    results = []
    for _, row in candidates.iterrows():
        cand_id = row['pattern_instance_id']
        cand_df = pd.read_sql(f"SELECT feature_name, feature_value FROM pattern_features WHERE pattern_instance_id = {cand_id}", conn)
        cand_vec = dict(zip(cand_df['feature_name'], cand_df['feature_value']))
        dist = get_weighted_distance(anchor_vec, cand_vec)
        results.append({'instance_id': cand_id, 'distance': dist})
    
    conn.close()
    return pd.DataFrame(results)