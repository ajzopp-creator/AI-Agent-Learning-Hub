import sqlite3
import pandas as pd
from datetime import timedelta

class LabelingEngine:
    """
    P_300 Labeling Engine
    Responsibility: Compute forward returns (5d, 7d, 10d) with deterministic 
    next-available-bar lookup.
    """
    def __init__(self, db_path='catalog.db'):
        self.conn = sqlite3.connect(db_path)

    def get_next_available_date(self, anchor_date, days_ahead):
        """Finds the next trading bar date, bypassing non-trading days."""
        target_date = pd.to_datetime(anchor_date) + timedelta(days=days_ahead)
        query = "SELECT date FROM price_bars WHERE date >= ? ORDER BY date ASC LIMIT 1"
        result = pd.read_sql_query(query, self.conn, params=(target_date.strftime('%Y-%m-%d'),))
        return result.iloc[0]['date'] if not result.empty else None

    def process_ticker(self, ticker):
        instances = pd.read_sql_query(
            "SELECT pattern_instance_id, anchor_date, close_price FROM pattern_instances WHERE ticker = ?", 
            self.conn, params=(ticker,)
        )
        
        labels = []
        for _, row in instances.iterrows():
            for horizon in [5, 7, 10]:
                future_date = self.get_next_available_date(row['anchor_date'], horizon)
                if not future_date: continue
                
                future_price = pd.read_sql_query(
                    "SELECT close FROM price_bars WHERE date = ? AND ticker = ?", 
                    self.conn, params=(future_date, ticker)
                ).iloc[0]['close']
                
                pct_return = (future_price - row['close_price']) / row['close_price']
                labels.append({
                    'pattern_instance_id': row['pattern_instance_id'],
                    'horizon_days': horizon,
                    'future_date': future_date,
                    'return_pct': pct_return,
                    'is_profitable': 1 if pct_return > 0 else 0
                })
        
        if labels:
            pd.DataFrame(labels).to_sql('forward_labels', self.conn, if_exists='append', index=False)
        print(f"Processed {len(labels)} labels for {ticker}.")

if __name__ == "__main__":
    engine = LabelingEngine()
    engine.process_ticker('SPY')