import sqlite3
import pandas as pd
import numpy as np
import sys
from pathlib import Path

DB_PATH = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db'

def calculate_dtw(s1, s2):
    if len(s1) == 0 or len(s2) == 0: return float('inf')
    n, m = len(s1), len(s2)
    dtw_matrix = np.full((n+1, m+1), np.inf)
    dtw_matrix[0, 0] = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = abs(s1[i-1] - s2[j-1])
            # DTW naturally handles arrays of different lengths (e.g., matching a 15-day pattern to a 20-day analog)
            dtw_matrix[i, j] = cost + min(dtw_matrix[i-1, j], dtw_matrix[i, j-1], dtw_matrix[i-1, j-1])
    return dtw_matrix[n, m]

def get_dynamic_normalized_close(inst_id, conn, max_lookback=20):
    """
    Dynamically fetches up to `max_lookback` days of history. 
    Scales seamlessly for both short-term trades and long-term investments.
    """
    meta = pd.read_sql(f"SELECT symbol_id, anchor_date FROM pattern_instances WHERE pattern_instance_id = {inst_id}", conn)
    if meta.empty: return []
    s_id, anchor = meta.iloc[0]['symbol_id'], meta.iloc[0]['anchor_date']
    prices = pd.read_sql(f"SELECT bar_date, close FROM price_bars WHERE symbol_id = {s_id}", conn)
    prices['dt'] = pd.to_datetime(prices['bar_date'], format='mixed')
    
    history = prices[prices['dt'] <= pd.to_datetime(anchor)].sort_values(by='dt', ascending=False).head(max_lookback)
    closes = history.sort_values(by='dt')['close'].values
    
    if len(closes) < 2: return [] # Need at least 2 points to form a recognizable "shape"
    base = closes[0]
    return [((p - base)/base)*100 if base != 0 else 0 for p in closes]

def get_intelliscan_results(target_id):
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Attempt Standard EAV Feature Match
    features_df = pd.read_sql("SELECT pattern_instance_id, feature_name, feature_value FROM pattern_features", conn)
    features_df = features_df.drop_duplicates(subset=['pattern_instance_id', 'feature_name'], keep='last')
    
    distances = []
    
    if not features_df.empty and target_id in features_df['pattern_instance_id'].values:
        pivot_df = features_df.pivot(index='pattern_instance_id', columns='feature_name', values='feature_value').dropna()
        if target_id in pivot_df.index:
            target_vec = pivot_df.loc[target_id]
            for inst_id, row in pivot_df.iterrows():
                if inst_id == target_id: continue
                distances.append((inst_id, np.linalg.norm(row.values - target_vec.values)))
    
    # 2. Smart Fallback Match (For Daily CSV Grid Snapshots)
    if not distances:
        instances = pd.read_sql("SELECT pattern_instance_id, open_0, close_0 FROM pattern_instances WHERE open_0 IS NOT NULL AND close_0 IS NOT NULL", conn)
        instances = instances.set_index('pattern_instance_id')
        if target_id in instances.index:
            target_vec = instances.loc[target_id]
            for inst_id, row in instances.iterrows():
                if inst_id == target_id: continue
                distances.append((inst_id, np.linalg.norm(row.values - target_vec.values)))
        else:
            conn.close()
            return [] 
            
    distances.sort(key=lambda x: x[1])
    top_50 = [x[0] for x in distances[:50]]
    
    # 3. Dynamic Shape DTW Match (Scales up to 20 days)
    target_shape = get_dynamic_normalized_close(target_id, conn, max_lookback=20)
    final_scores = []
    
    if target_shape: 
        for cand_id in top_50:
            cand_shape = get_dynamic_normalized_close(cand_id, conn, max_lookback=20)
            if cand_shape:
                final_scores.append((cand_id, calculate_dtw(target_shape, cand_shape)))
    else: 
        final_scores = [(cand_id, dist) for cand_id, dist in distances[:50]]
        
    final_scores.sort(key=lambda x: x[1])
    
    # 4. Compile Confidence Report Results
    results = []
    seen = set()
    for cand_id, score in final_scores:
        meta = pd.read_sql(f"SELECT symbol_id, anchor_date FROM pattern_instances WHERE pattern_instance_id = {cand_id}", conn).iloc[0]
        sym = pd.read_sql(f"SELECT ticker FROM symbols WHERE symbol_id = {meta['symbol_id']}", conn).iloc[0]['ticker']
        clean_date = pd.to_datetime(meta['anchor_date']).strftime('%Y-%m-%d')
        
        if f"{sym}_{clean_date}" in seen: continue
        seen.add(f"{sym}_{clean_date}")
        
        labels = pd.read_sql(f"SELECT horizon_days, return_pct FROM forward_labels WHERE pattern_instance_id = {cand_id}", conn)
        labels_dict = dict(zip(labels['horizon_days'], labels['return_pct']))
        
        results.append({
            'id': int(cand_id), 'sym': sym, 'date': clean_date, 'score': float(score),
            'ret_5d': float(labels_dict.get(5, 0) * 100)
        })
        if len(results) >= 5: break
        
    conn.close()
    return results

if __name__ == '__main__':
    pass