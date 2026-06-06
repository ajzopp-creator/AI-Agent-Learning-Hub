from dataclasses import dataclass
from collections import deque
from pathlib import Path
from typing import List, Dict
import json
from datetime import datetime
import yfinance as yf
import sys

#!/usr/bin/env python3
"""
Bullish Trend Pattern Project V2.4
Historical XML processing + live SPY/QQQ posture → risk_config.json

Version History:
  V2.0 - Original scaffold
  V2.1 - Fixed pandas .iloc[-1] for yfinance data
  V2.2 - Fixed yfinance multi-level columns, corrected XML field names
  V2.3 - Added handling for infinity (∞) and special values in XML
  V2.4 - Fixed QQQ record tag (PowerShares_x0020_QQQ)
"""

import xml.etree.ElementTree as ET

try:
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Note: 'pip install yfinance' required for live posture generation")

# ---------- Data structures ----------

@dataclass
class DailyRecord:
    date: str
    short_diff: float
    medium_diff: float
    long_diff: float
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    pred_high: float
    pred_low: float
    volume: float
    williams_emai: float
    psi: float
    roc_pct: float
    neural_x: str
    neural_xmax: float
    triple_short: float
    triple_medium: float
    triple_long: float
    pred_high_diff: float
    pred_low_diff: float
    pred_range: float

# ---------- XML parsing ----------

def parse_history_xml(path: str, record_tag: str) -> List[DailyRecord]:
    tree = ET.parse(path)
    root = tree.getroot()
    records: List[DailyRecord] = []

    for node in root.findall(record_tag):
        def f(tag):
            text = node.findtext(tag)
            if text is None:
                return 0.0  # Default value for missing fields
            # Handle special values
            if text in ('∞', 'inf', 'Inf', 'INF'):
                return float('inf')
            if text in ('-∞', '-inf', '-Inf', '-INF'):
                return float('-inf')
            if text in ('NaN', 'nan', 'NAN', ''):
                return 0.0
            try:
                return float(text)
            except ValueError:
                return 0.0

        rec = DailyRecord(
            date=node.findtext("Date"),
            short_diff=f("Short_Term_Difference"),
            medium_diff=f("Medium_Term_Difference"),
            long_diff=f("Long_Term_Difference"),
            open_price=f("Open_Price"),
            high_price=f("High_Price"),
            low_price=f("Low_Price"),
            close_price=f("Close_Price"),
            pred_high=f("Predicted_High_Price"),
            pred_low=f("Predicted_Low_Price"),
            volume=f("Volume"),
            williams_emai=f("Williams_EMAI"),
            psi=f("Professional_Sentiment_PSI"),
            roc_pct=f("Professional_Sentiment_ROC_x0025_"),
            neural_x=node.findtext("Neural_Index_NeuralX"),
            neural_xmax=f("Neural_Index_NeuralXMax"),
            triple_short=f("Triple_Cross_Short"),
            triple_medium=f("Triple_Cross_Medium"),
            triple_long=f("Triple_Cross_Long"),
            pred_high_diff=f("Predicted_High_Diff"),
            pred_low_diff=f("Predicted_Low_Diff"),
            pred_range=f("Predicted_Range"),
        )
        records.append(rec)

    return records

# ---------- Rolling helpers ----------

def rolling_volume_avg(records: List[DailyRecord], window: int = 20) -> Dict[str, float]:
    vol_queue = deque()
    sums = 0.0
    vol_avgs: Dict[str, float] = {}

    for rec in records:
        vol_queue.append(rec.volume)
        sums += rec.volume
        if len(vol_queue) > window:
            sums -= vol_queue.popleft()

        vol_avgs[rec.date] = sums / len(vol_queue)

    return vol_avgs

def triple_cross_aligned(rec: DailyRecord) -> bool:
    return rec.triple_short > rec.triple_medium > rec.triple_long

def triple_cross_aligned_prior_3(records: List[DailyRecord]) -> Dict[str, bool]:
    aligned_flags: Dict[str, bool] = {}
    window = deque(maxlen=3)

    for rec in records:
        flag = triple_cross_aligned(rec)
        window.append(flag)
        aligned_flags[rec.date] = (len(window) == 3 and all(window))

    return aligned_flags

# ---------- DL Model Score ----------

def compute_dl_score(rec: DailyRecord, vol_20d_avg: float, triple_cross_prior_3: bool, x_sentiment_bullish: float = None) -> float:
    score = 0.0

    vol_ratio = rec.volume / vol_20d_avg if vol_20d_avg > 0 else 1.0
    if vol_ratio > 1.3:
        score += 0.25
    elif 1.2 <= vol_ratio <= 1.3:
        score += 0.10

    nimax = rec.neural_xmax
    if nimax > 70 and vol_ratio > 1.3:
        score += 0.10
    elif 50 <= nimax <= 70:
        score += 0.08
    elif 30 <= nimax < 50:
        score += 0.05
    elif nimax < 30 and nimax >= -50:
        score -= 0.05
    elif nimax < -50:
        score -= 0.10

    mt_lt_avg = (rec.medium_diff + rec.long_diff) / 2.0
    if mt_lt_avg > 8.0:
        score += 0.15

    w = rec.williams_emai
    if w > -10:
        score += 0.15
    elif -20 <= w <= -10:
        score += 0.08

    if x_sentiment_bullish is not None and x_sentiment_bullish >= 70:
        score += 0.20

    if triple_cross_prior_3:
        score += 0.15

    if rec.pred_high_diff > 0:
        score += 0.10
    if rec.pred_range > 0:
        score += 0.05

    return max(0.0, min(score, 1.0))

# ---------- Posture ----------

def compute_posture(rec: DailyRecord) -> float:
    return (rec.medium_diff + rec.long_diff) / 2.0

def combine_posture(spy_posture: float, qqq_posture: float) -> Dict[str, float]:
    avg_posture = (spy_posture + qqq_posture) / 2.0
    if avg_posture >= 1.0:
        risk = "FULL"
    elif avg_posture >= 0.0:
        risk = "HALF"
    else:
        risk = "OFF"
    return {"avg_posture": avg_posture, "risk_mode": risk}

# ---------- Live posture ----------

def generate_live_posture() -> Dict:
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed"}

    spy_qqq_postures = {}
    for symbol in ["SPY", "QQQ"]:
        data = yf.download(symbol, period="1y", progress=False)
        
        # Handle both single and multi-level column formats from yfinance
        close_data = data['Close']
        
        # If it's a DataFrame (multi-level columns), flatten it
        if hasattr(close_data, 'columns'):
            close_data = close_data.squeeze()
        
        # Extract scalar values using float() to ensure no Series ambiguity
        latest_close = float(close_data.iloc[-1])
        sma_short_val = float(close_data.rolling(window=50).mean().iloc[-1])
        sma_long_val = float(close_data.rolling(window=200).mean().iloc[-1])
        
        mt_posture = latest_close / sma_short_val
        lt_posture = latest_close / sma_long_val
        spy_qqq_postures[symbol] = (mt_posture, lt_posture)

    spy_mt, spy_lt = spy_qqq_postures["SPY"]
    qqq_mt, qqq_lt = spy_qqq_postures["QQQ"]

    spy_posture = (spy_mt + spy_lt) / 2.0
    qqq_posture = (qqq_mt + qqq_lt) / 2.0
    posture_info = combine_posture(spy_posture, qqq_posture)

    config = {
        "timestamp": datetime.now().isoformat(),
        "spy_posture": spy_posture,
        "qqq_posture": qqq_posture,
        "avg_posture": posture_info["avg_posture"],
        "risk_mode": posture_info["risk_mode"],
        "prompt_ready": f"Assume current posture mode is {posture_info['risk_mode']}_RISK"
    }

    with open("risk_config.json", "w") as f:
        json.dump(config, f, indent=2)

    return config

# ---------- Main ----------

def main(mode: str = "live"):
    # Base path is the python folder, XML files are in ../data/xml_exports/
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data" / "xml_exports"
    
    if mode == "live":
        config = generate_live_posture()
        print("Live posture generated:")
        print(json.dumps(config, indent=2))
    
    elif mode == "historical":
        # Match your actual filenames: "History Grid (SPY)_v2.xml" and "History Grid (QQQ)_v2 .xml"
        spy_xml = data_dir / "History Grid (SPY)_v2.xml"
        qqq_xml = data_dir / "History Grid (QQQ)_v2 .xml"
        
        print(f"Looking for SPY XML: {spy_xml}")
        print(f"Looking for QQQ XML: {qqq_xml}")
        
        spy_records = parse_history_xml(spy_xml, record_tag="SPDRs")
        qqq_records = parse_history_xml(qqq_xml, record_tag="PowerShares_x0020_QQQ")
        
        # Debug: Show what was parsed
        print(f"\nSPY records parsed: {len(spy_records)}")
        print(f"QQQ records parsed: {len(qqq_records)}")
        
        if spy_records:
            print(f"SPY first 3 dates: {[r.date for r in spy_records[:3]]}")
        if qqq_records:
            print(f"QQQ first 3 dates: {[r.date for r in qqq_records[:3]]}")
        
        spy_vol_avg = rolling_volume_avg(spy_records)
        qqq_vol_avg = rolling_volume_avg(qqq_records)
        spy_triple3 = triple_cross_aligned_prior_3(spy_records)
        qqq_triple3 = triple_cross_aligned_prior_3(qqq_records)
        
        spy_by_date = {r.date: r for r in spy_records}
        qqq_by_date = {r.date: r for r in qqq_records}
        
        results = []
        for date, spy_rec in spy_by_date.items():
            if date not in qqq_by_date:
                continue
            qqq_rec = qqq_by_date[date]
            
            spy_score = compute_dl_score(spy_rec, spy_vol_avg[date], spy_triple3[date])
            qqq_score = compute_dl_score(qqq_rec, qqq_vol_avg[date], qqq_triple3[date])
            
            spy_posture = compute_posture(spy_rec)
            qqq_posture = compute_posture(qqq_rec)
            posture_info = combine_posture(spy_posture, qqq_posture)
            
            results.append({
                "date": date,
                "spy_score": spy_score,
                "qqq_score": qqq_score,
                "spy_posture": spy_posture,
                "qqq_posture": qqq_posture,
                "avg_posture": posture_info["avg_posture"],
                "risk_mode": posture_info["risk_mode"],
            })
        
        print(f"Processed {len(results)} historical days")
    
    else:
        print("Usage: python script.py [live|historical]")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "live"
    main(mode)
