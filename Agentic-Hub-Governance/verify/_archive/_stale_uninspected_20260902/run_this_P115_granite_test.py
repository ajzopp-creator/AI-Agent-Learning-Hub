import sys
import json
import time
import urllib.request

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub")
from shared_resources.python_utils.signal_schemas import SignalV2
from pydantic import ValidationError

SCHEMA_PROMPT = """You are a JSON signal packet generator for a trading system. Given a scored trade setup, emit ONE JSON object matching this exact schema (SignalV2). Output ONLY the JSON object, no markdown fences, no explanation.

Required fields:
signal_id (string, format "P115-YYYY-MM-DD-SYMBOL-001")
signal_timestamp (ISO 8601 UTC string)
signal_source (string, always "P_115")
strategy (string: dip_buy | breakout | mean_reversion | support_bounce)
symbol (uppercase string)
asset_class (string, "stock")
guideline_entry (float, > 0)
guideline_stop (float, > 0, must be < guideline_entry)
guideline_target (float, > 0, must be > guideline_entry)
signal_horizon (string, e.g. "10-15 trading days")
confidence_level (string: HIGH | MEDIUM | LOW)
position_size (integer)
strike_price, underlying_price, option_type, expiration_date: must be null (this is a stock signal)
atr_adjusted_stop, intelliscan_support_1, intelliscan_support_2, target_source: null unless given data for them
context (object): {close_at_signal (float), trailing_volume_30d (float), signal_rationale (string), atm_at_signal (float or null)}
signal_metadata (object): {session_date ("YYYY-MM-DD"), chart_timeframe (string, e.g. "1D"), signal_source_link (string)}
"""

test_cases = [
    {
        "symbol": "STZ",
        "input": ("Symbol: STZ | Entry: 139.18 | Stop: 129.52 | Target: 162.90 | Close: 139.18 | "
                  "Volume(20d avg): 1432261 | ATR: 3.38 | Strategy: dip_buy | Horizon: 10-15 trading days | "
                  "Confidence: MEDIUM | Position size: 11 shares | Session date: 2026-08-17 | Timeframe: 1D | "
                  "Rationale: P_117 outside rec cross-validated via P_115 core engine, came out BUY. "
                  "HybridTier=6. Fund verified clean. 200-MA -4% PULLBACK. No earnings flag. | "
                  "Source link: TradeOrderManagement/P115"),
    },
    {
        "symbol": "SBLK",
        "input": ("Symbol: SBLK | Entry: 29.31 | Stop: 27.06 | Target: 38.27 | Close: 29.84 | "
                  "Volume(20d avg): 440777 | ATR: 0.92 | Strategy: breakout | Horizon: 10-15 trading days | "
                  "Confidence: MEDIUM | Position size: 20 shares | Session date: 2026-08-17 | Timeframe: 1D | "
                  "Rationale: P_118 High Handle pattern, ASYM setup, Fund verified 2/3 criteria. "
                  "200-MA +26.1% NORMAL. No earnings flag. RVOL weak. | Source link: TradeOrderManagement/P115"),
    },
    {
        "symbol": "AXTI",
        "input": ("Symbol: AXTI | Entry: 92.22 | Stop: 59.00 | Target: 107.70 | Close: 92.22 | "
                  "Volume(20d avg): 6490476 | ATR: 10.32 | Strategy: dip_buy | Horizon: 10-15 trading days | "
                  "Confidence: MEDIUM | Position size: 5 shares | Session date: 2026-08-17 | Timeframe: 1D | "
                  "Rationale: P_115 dip_buy ASYM. Fund 1/3 criteria (recomputed~1 vs submitted 2, within "
                  "tolerance). 200-MA +82% NORMAL. No earnings flag. STR=-2 regime signal. | "
                  "Source link: TradeOrderManagement/P115"),
    },
]

results = []

for case in test_cases:
    payload = {
        "model": "granite-4.1-8b",
        "messages": [
            {"role": "system", "content": SCHEMA_PROMPT},
            {"role": "user", "content": case["input"]},
        ],
        "temperature": 0.2,
        "max_tokens": 800,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:1234/v1/chat/completions",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    result = {"symbol": case["symbol"]}
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        elapsed = time.time() - t0
        result["latency_sec"] = round(elapsed, 2)
        raw_content = body["choices"][0]["message"]["content"]
        result["raw_output"] = raw_content
    except Exception as e:
        result["latency_sec"] = round(time.time() - t0, 2)
        result["error"] = "API call failed: " + str(e)
        results.append(result)
        continue

    # Try to extract JSON (strip markdown fences if present)
    cleaned = raw_content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
        result["json_parse"] = "OK"
    except Exception as e:
        result["json_parse"] = "FAILED: " + str(e)
        results.append(result)
        continue

    try:
        validated = SignalV2(**parsed)
        result["schema_validation"] = "PASS -- valid SignalV2 on first pass"
        result["validated_fields"] = validated.model_dump()
    except ValidationError as e:
        result["schema_validation"] = "FAIL"
        result["validation_errors"] = str(e)

    results.append(result)

outp = r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify\granite_test_results.json"
with open(outp, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("done")
for r in results:
    print(r["symbol"], "-", r.get("json_parse"), "-", r.get("schema_validation"), "-", r.get("latency_sec"), "sec")
