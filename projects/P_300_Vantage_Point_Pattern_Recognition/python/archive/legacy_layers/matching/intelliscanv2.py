"""
FILE: intelliscan.py
VERSION: 2.2
DATE: 2026-05-07
DESCRIPTION: Core logic for distance-weighted pattern matching.
CHANGELOG:
    - v2.2: Fixed Feature Scaling failure (applied percentage normalization) and temporal sequence flattening bug. Migrated to dynamic DB pathing.
    - v2.1: Added version header. Hardcoded absolute DB path.
    - v2.0: Optimized SQL fetch logic to use DISTINCT instance IDs.
"""
import sys
import os
import sqlite3
import pandas as pd
import numpy as np

# Absolute Path Injection
PROJECT_ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
sys.path.insert(0, os.path.join(PROJECT_ROOT, "python"))

from utilities.db_utils import get_latest_catalog

# Base metric weights
WEIGHTS = {
    'psi': 0.40,
    'neuralx': 0.40,
    'close': 0.05,
    'stdiff': 0.05,
    'mtdiff': 0.05,
    'ltdiff': 0.05
}

def get_weighted_distance(vec1, vec2):
    # 1. Identify base price for normalization (anchor to day 0 close)
    # Fallback to 1.0 to prevent division by zero if data is anomalous
    base1 = vec1.get('close_0', 1.0)
    base2 = vec2.get('close_0', 1.0)
    if base1 == 0: base1 = 1.0
    if base2 == 0: base2 = 1.0

    distance = 0
    features_compared = 0

    # 2. Iterate through all temporal features without flattening the sequence
    for key, val1 in vec1.items():
        if key in vec2:
            val2 = vec2[key]
            base_metric = key.split('_')[0]
            
            if base_metric in WEIGHTS:
                weight = WEIGHTS[base_metric]
                
                # 3. PERCENTAGE NORMALIZATION
                # Convert absolute dollar variances into relative percentages
                if base_metric in ['close', 'stdiff', 'mtdiff', 'ltdiff']:
                    n_val1 = (val1 / base1) * 100.0
                    n_val2 = (val2 / base2) * 100.0
                else:
                    # VP indicators (psi, neuralx) are pre-scaled oscillators
                    n_val1 = val1
                    n_val2 = val2
                    
                distance += weight * ((n_val1 - n_val2) ** 2)
                features_compared += 1
                
    # Max penalty if no overlapping features exist
    if features_compared == 0:
        return 999.0 
        
    return np.sqrt(distance)

def get_intelliscan_results(anchor_id):
    db_path = get_latest_catalog()
    conn = sqlite3.connect(db_path)
    
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
        
        # Convert Euclidean distance to a 0-100 Confidence Score
        conf = max(0.0, 100.0 - (dist * 10)) 
        
        results.append({
            'instance_id': cand_id,
            'distance': dist,
            'confidence_score': conf
        })
        
    conn.close()
    return pd.DataFrame(results)