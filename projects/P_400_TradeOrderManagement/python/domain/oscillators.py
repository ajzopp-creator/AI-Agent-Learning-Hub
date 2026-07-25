"""oscillators.py -- RSI(14) and MACD for the technical dossier
(WO-P400-E4.003). Pure logic, no I/O.

RSI uses Wilder smoothing -- same recursive pattern as atr.py's ATR
(seed = simple mean of first N periods, then recursive smoothing), for
consistency with the existing shared convention.
"""

from __future__ import annotations

from typing import NamedTuple, Optional, Sequence


class RSIResult(NamedTuple):
    value: float
    interpretation: str   # "overbought" | "oversold" | "neutral"


class MACDResult(NamedTuple):
    macd_line: float
    signal_line: float
    histogram: float
    cross_state: str      # "above signal" | "below signal"


def compute_rsi(closes: Sequence[float], period: int = 14) -> Optional[RSIResult]:
    """Wilder-smoothed RSI. None if fewer than period+1 closes (need one
    prior close to compute the first change).
    """
    if len(closes) < period + 1:
        return None

    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(c, 0.0) for c in changes]
    losses = [max(-c, 0.0) for c in changes]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for g, l in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + l) / period

    if avg_loss == 0:
        rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))

    if rsi >= 70:
        interpretation = "overbought"
    elif rsi <= 30:
        interpretation = "oversold"
    else:
        interpretation = "neutral"

    return RSIResult(value=rsi, interpretation=interpretation)


def _ema_series(values: Sequence[float], period: int) -> list[float]:
    """Full EMA series (not just the final value) -- MACD needs the EMA-12
    and EMA-26 series aligned in time to subtract them at every point,
    and the signal line needs the MACD line's own series to smooth over.
    """
    if len(values) < period:
        return []
    multiplier = 2.0 / (period + 1)
    ema = [sum(values[:period]) / period]  # seed = SMA of first `period` values
    for v in values[period:]:
        ema.append((v - ema[-1]) * multiplier + ema[-1])
    return ema


def compute_macd(
    closes: Sequence[float],
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Optional[MACDResult]:
    """Standard MACD: EMA(fast) - EMA(slow) = MACD line, EMA(signal) of
    that = signal line, histogram = MACD - signal. None if not enough
    history for the slow EMA plus signal smoothing.
    """
    if len(closes) < slow + signal:
        return None

    ema_fast = _ema_series(closes, fast)
    ema_slow = _ema_series(closes, slow)

    # Align: ema_fast is longer (shorter period, starts earlier in the
    # series) -- trim its head so both series line up on the same closes.
    offset = len(ema_fast) - len(ema_slow)
    macd_series = [ema_fast[offset + i] - ema_slow[i] for i in range(len(ema_slow))]

    if len(macd_series) < signal:
        return None
    signal_series = _ema_series(macd_series, signal)
    if not signal_series:
        return None

    macd_line = macd_series[-1]
    signal_line = signal_series[-1]
    histogram = macd_line - signal_line

    return MACDResult(
        macd_line=macd_line,
        signal_line=signal_line,
        histogram=histogram,
        cross_state="above signal" if macd_line >= signal_line else "below signal",
    )