"""moving_averages.py -- SMA/trend computation for the technical dossier
(WO-P400-E4.003). Pure logic, no I/O.

Bars are (high, low, close) tuples, oldest-first -- same convention as
atr.py. Callers pass daily bars; weekly/monthly are aggregated here from
the same daily series (no new data source, per the WO's Out of Scope).
"""

from __future__ import annotations

from typing import NamedTuple, Optional, Sequence

Bar = tuple[float, float, float]


class MAResult(NamedTuple):
    period: int
    value: float
    price_vs_ma: str   # "above" | "below"


class TrendResult(NamedTuple):
    mas: list[MAResult]
    crossover_state: str        # e.g. "50>200 BULLISH", "50<200 BEARISH", "insufficient data"
    primary_trend: str          # "bullish" | "bearish" | "neutral"


def sma(closes: Sequence[float], period: int) -> Optional[float]:
    """Simple moving average of the last `period` closes. None if not enough data."""
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def aggregate_bars(bars: Sequence[Bar], bars_per_group: int) -> list[Bar]:
    """Aggregate daily bars into coarser (high, low, close) groups.

    e.g. bars_per_group=5 for a rough weekly bar from daily bars. Trailing
    partial group (fewer than bars_per_group bars) is dropped -- an
    incomplete period isn't a real one, never fabricated as if complete.
    """
    groups: list[Bar] = []
    for i in range(0, len(bars) - bars_per_group + 1, bars_per_group):
        chunk = bars[i:i + bars_per_group]
        high = max(b[0] for b in chunk)
        low = min(b[1] for b in chunk)
        close = chunk[-1][2]
        groups.append((high, low, close))
    return groups


def compute_moving_averages(closes: Sequence[float], periods: Sequence[int]) -> list[MAResult]:
    """Compute SMA for each period, with price-vs-MA classification.

    Periods with insufficient data are silently omitted -- never a
    fabricated/partial-window average.
    """
    if not closes:
        return []
    current_price = closes[-1]
    results = []
    for period in periods:
        value = sma(closes, period)
        if value is None:
            continue
        results.append(MAResult(
            period=period, value=value,
            price_vs_ma="above" if current_price >= value else "below",
        ))
    return results


def compute_trend(closes: Sequence[float], periods: Sequence[int] = (20, 50, 100, 200)) -> TrendResult:
    """Full trend picture: per-period MAs, 50/200 crossover state, primary trend.

    primary_trend is "neutral" whenever the 50 or 200 MA isn't available
    (not enough history) -- never guessed from a shorter-period proxy.
    """
    mas = compute_moving_averages(closes, periods)
    by_period = {m.period: m.value for m in mas}

    ma50 = by_period.get(50)
    ma200 = by_period.get(200)
    if ma50 is None or ma200 is None:
        crossover_state = "insufficient data"
        primary_trend = "neutral"
    elif ma50 > ma200:
        crossover_state = f"50>200 BULLISH ({ma50:.2f} > {ma200:.2f})"
        primary_trend = "bullish"
    elif ma50 < ma200:
        crossover_state = f"50<200 BEARISH ({ma50:.2f} < {ma200:.2f})"
        primary_trend = "bearish"
    else:
        crossover_state = f"50=200 FLAT ({ma50:.2f})"
        primary_trend = "neutral"

    return TrendResult(mas=mas, crossover_state=crossover_state, primary_trend=primary_trend)