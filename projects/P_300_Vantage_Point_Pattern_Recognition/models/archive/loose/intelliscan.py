import sqlite3
import pandas as pd
import numpy as np
import os

# IMMUTABLE PATH: C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\
DB_PATH = r'C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\catalog.db'

def calculate_similarity(new_pattern, historical_pattern):
    # Normalize and calculate Euclidean distance
    new_norm = np.array(new_pattern) / new_pattern[0]
    hist_norm = np.array(historical_pattern) / historical_pattern[0]
    return np.linalg.norm(new_norm - hist_norm)

def run_intelliscan(new_pattern_prices):
    conn = sqlite3.connect(DB_PATH)
    instances = pd.read_sql_query("SELECT pattern_instance_id, close_0, close_price FROM pattern_instances", conn)
    
    # Simple matching logic (simplified for demonstration)
    # Comparing first 3 points of the price action
    results = []
    for row in instances.itertuples():
        hist_sample = [row.close_0, row.close_price] # Simplified sample
        score = calculate_similarity(new_pattern_prices, hist_sample)
        results.append((row.pattern_instance_id, score))
    
    conn.close()
    return sorted(results, key=lambda x: x[1])[:3] # Return top 3 matches

if __name__ == "__main__":
    # Example usage: New pattern price action
    my_test_pattern = [150.00, 153.00] 
    matches = run_intelliscan(my_test_pattern)
    print("Top 3 Matches (Instance ID, Score):", matches)