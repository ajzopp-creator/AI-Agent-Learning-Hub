"""build_dossier.py -- `dossier` CLI command (WO-P400-E4.003).

Orchestrates domain\moving_averages.py, oscillators.py, levels.py over
daily bars from infrastructure\schwab_market_data.py (E4.002) into one
printed table. Items 1-8 (architecture doc Section 4.2) fully computed.
Item 9 (chart pattern ID) is deliberately absent -- Claude narrates that
over this printed output in STEP 3A, per the WO's WHY (pattern-shape
detection is a judgment call, not arithmetic; never auto-filled).
"""

from __future__ import annotations

from config import (
    BB_PERIOD,
    BB_STDDEV,
    FIB_LOOKBACK_BARS,
    MACD_FAST,
    MACD_SIGNAL,
    MACD_SLOW,
    RSI_PERIOD,
    SCHWAB_CONFIG_PATH,
    SCHWAB_TOKEN_PATH,
    SMA_PERIODS,
)
from domain.levels import compute_bollinger, compute_fibonacci, compute_pivot_levels
from domain.moving_averages import aggregate_bars, compute_trend
from domain.oscillators import compute_macd, compute_rsi


def cmd_dossier(symbol: str) -> int:
    from infrastructure.schwab_market_data import get_daily_bars, get_quote_data

    symbol = symbol.upper()

    quote = get_quote_data(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH, symbol)
    if quote is None:
        print(f"[ERROR] Could not fetch live quote for {symbol}. No dossier printed.")
        return 1

    bars_result = get_daily_bars(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH, symbol, lookback_days=250)
    if bars_result is None:
        print(f"[ERROR] Could not fetch price history for {symbol}. No dossier printed.")
        return 1
    bars, volumes = bars_result
    closes = [b[2] for b in bars]

    print("=" * 70)
    print(f"TECHNICAL DOSSIER -- {symbol}  (price={quote.get('price')})")
    print("=" * 70)

    # 1. Trend -- daily / weekly / monthly
    daily_trend = compute_trend(closes, SMA_PERIODS)
    weekly_bars = aggregate_bars(bars, 5)
    weekly_trend = compute_trend([b[2] for b in weekly_bars], SMA_PERIODS)
    monthly_bars = aggregate_bars(bars, 21)
    monthly_trend = compute_trend([b[2] for b in monthly_bars], SMA_PERIODS)
    print(f"1. TREND       daily={daily_trend.primary_trend}  "
          f"weekly={weekly_trend.primary_trend}  monthly={monthly_trend.primary_trend}")

    # 3. Moving averages (daily) + crossover
    print(f"3. MA          {daily_trend.crossover_state}")
    for m in daily_trend.mas:
        print(f"     SMA{m.period:<4} {m.value:.2f}  (price {m.price_vs_ma})")

    # 4. RSI
    rsi = compute_rsi(closes, RSI_PERIOD)
    if rsi:
        print(f"4. RSI({RSI_PERIOD})     {rsi.value:.2f}  {rsi.interpretation}")
    else:
        print(f"4. RSI({RSI_PERIOD})     insufficient data")

    # 5. MACD
    macd = compute_macd(closes, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    if macd:
        print(f"5. MACD        {macd.macd_line:.2f}  SIG={macd.signal_line:.2f}  "
              f"HIST={macd.histogram:.2f}  {macd.cross_state}")
    else:
        print("5. MACD        insufficient data")

    # 6. Bollinger Bands
    bb = compute_bollinger(closes, BB_PERIOD, BB_STDDEV)
    if bb:
        print(f"6. BB          {bb.lower:.2f}/{bb.middle:.2f}/{bb.upper:.2f}  "
              f"%B={bb.percent_b:.1f}  {bb.band_state.upper()}")
    else:
        print("6. BB          insufficient data")

    # 2. Support/Resistance -- classic pivot from prior completed bar
    if len(bars) >= 2:
        pivots = compute_pivot_levels(bars[-2])
        print(f"2. S/R (pivot) R3={pivots.r3:.2f} R2={pivots.r2:.2f} R1={pivots.r1:.2f} "
              f"| S1={pivots.s1:.2f} S2={pivots.s2:.2f} S3={pivots.s3:.2f}")
    else:
        print("2. S/R (pivot) insufficient data")

    # 7. Volume
    today_volume = quote.get("today_volume")
    avg_20d = sum(volumes[-20:]) / len(volumes[-20:]) if len(volumes) >= 20 else None
    if today_volume is not None and avg_20d:
        ratio = today_volume / avg_20d
        print(f"7. VOLUME      today={today_volume:.0f}  avg20d={avg_20d:.0f}  ratio={ratio:.2f}x")
    else:
        print("7. VOLUME      insufficient data")

    # 8. Fibonacci
    fib = compute_fibonacci(bars, FIB_LOOKBACK_BARS)
    if fib:
        levels_str = "  ".join(f".{int(r*1000):03d}={p:.2f}" for r, p in fib.levels.items())
        print(f"8. FIB({FIB_LOOKBACK_BARS}d {fib.swing_low:.2f}-{fib.swing_high:.2f})  {levels_str}")
    else:
        print(f"8. FIB({FIB_LOOKBACK_BARS}d)  no qualifying swing found")

    print("-" * 70)
    print("9. CHART PATTERN -- narrative only, Claude fills this in-session.")
    print("   Never auto-computed -- geometric pattern ID is a judgment call, not arithmetic.")
    print("=" * 70)
    return 0