"""
FILE: domain/utility.py
VERSION: 1.0
DATE: 2026-06-09
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Risk-adjusted utility math for the Certainty-Equivalent (CE) BUY gate.
    Source: Kochenderfer, "Algorithms for Decision Making", Ch. 6
    (maximum expected utility).

    The rest of Pipeline B reasons on the EXPECTED forward return of a
    top-K analog cluster. This module supplies the risk-averse alternative:
    score each analog's forward return through a concave CARA utility,
    average the utilities, and invert back to a certainty-equivalent return.
    The CE is the guaranteed return a risk-averse trader would accept in
    place of the uncertain analog distribution. For any non-degenerate
    spread, CE < arithmetic mean; the gap (mean - CE) IS the risk penalty.
    Fat-tailed / dispersed analog distributions are penalized INSIDE the
    decision rather than merely flagged afterward.

    CARA exponential utility (constant absolute risk aversion):
        u(r)  =  -exp(-lambda * r)
        E[u]  =  mean_i( -exp(-lambda * r_i) )
        CE    =  -(1 / lambda) * ln( mean_i( exp(-lambda * r_i) ) )

    DECIMAL SPACE (M-020): every return here is a decimal fraction
    (0.06 = 6%), matching forward_labels.return_pct storage. lambda is
    calibrated for decimal magnitudes -- see config.RISK_AVERSION_LAMBDA
    for the tuning rationale and the hard warning against percent-space
    lambda. This module never multiplies by 100; that happens only at the
    report-writer display boundary.

    LAYER PURITY (EC-027 / Anti-pattern #6): pure functions only. No I/O,
    no logging, no DB, no imports from infrastructure/ or application/.
    Imports nothing from config either -- lambda is passed in by the caller
    (domain/aggregator.py reads config.RISK_AVERSION_LAMBDA and forwards it),
    so this module stays a self-contained math kernel that the smoke harness
    can exercise with arbitrary lambda.

    NFR-1: deterministic. Same inputs -> same output to full float precision.
    No randomness, no sampling, no LLM. Safe in the BUY/WATCH/PASS path.

CHANGELOG:
    - 2026-06-09 v1.0: Initial release. utility(), expected_utility(),
      certainty_equivalent() with degenerate guards (lambda ~ 0 -> arithmetic
      mean; all-identical returns -> that value, zero penalty) and a built-in
      smoke harness under __main__.
"""
from __future__ import annotations

import math

# Below this absolute lambda the CARA function is numerically indistinguishable
# from risk-neutral; we return the arithmetic mean to avoid 0/0 in the
# -(1/lambda) inversion. Not operator-tunable -- this is a numerical floor,
# not a risk-policy knob.
_LAMBDA_EPSILON: float = 1e-9

# Spread below this (max - min of the return list) is treated as degenerate:
# all analogs effectively identical, so CE == that common value and the risk
# penalty is exactly zero. Guards against ln(very-small) round-off producing
# a spurious non-zero penalty on a flat cluster.
_SPREAD_EPSILON: float = 1e-12


def utility(return_decimal: float, lambda_: float) -> float:
    """
    CARA exponential utility of a single forward return.

        u(r) = -exp(-lambda * r)

    return_decimal : forward return as a decimal fraction (0.06 = 6%).
    lambda_        : risk aversion, applied in decimal space. Larger ->
                     more risk-averse -> harsher penalty on downside.

    Concave and monotonically increasing in r for lambda_ > 0: more return
    is always better, but each additional unit of return buys less utility,
    which is what makes dispersion costly. Returns a negative number (the
    sign is irrelevant -- only relative ordering and the inversion matter).
    """
    return -math.exp(-lambda_ * return_decimal)


def expected_utility(returns_decimal: list[float], lambda_: float) -> float:
    """
    Mean CARA utility across an analog cluster.

        E[u] = mean_i( -exp(-lambda * r_i) )

    returns_decimal : forward returns of the top-K analogs at one horizon,
                      each a decimal fraction.
    lambda_         : risk aversion (decimal space).

    Raises ValueError on an empty list -- an empty cluster has no expected
    utility and the caller (aggregator) must not invoke CE on zero matches.
    """
    if not returns_decimal:
        raise ValueError("expected_utility requires at least one return")
    total = 0.0
    for r in returns_decimal:
        total += utility(r, lambda_)
    return total / len(returns_decimal)


def certainty_equivalent(returns_decimal: list[float], lambda_: float) -> float:
    """
    Certainty-equivalent return of an analog cluster under CARA utility.

        CE = -(1 / lambda) * ln( mean_i( exp(-lambda * r_i) ) )

    Returned in DECIMAL space (same as the inputs). For any non-degenerate
    spread, CE < arithmetic mean of returns_decimal; (mean - CE) is the
    risk penalty.

    Degenerate guards (both return the arithmetic mean, zero penalty):
      1. |lambda| <= _LAMBDA_EPSILON  -> risk-neutral; CE is undefined under
         the -(1/lambda) inversion (0/0), so fall back to the mean.
      2. (max - min) <= _SPREAD_EPSILON -> all analogs identical; CE equals
         that common value, which equals the mean. Returning the mean
         directly avoids ln() round-off manufacturing a fake penalty.

    returns_decimal : non-empty list of decimal-fraction forward returns.
    lambda_         : risk aversion (decimal space).

    Raises ValueError on an empty list (same contract as expected_utility).
    """
    if not returns_decimal:
        raise ValueError("certainty_equivalent requires at least one return")

    arithmetic_mean = sum(returns_decimal) / len(returns_decimal)

    # Guard 1: risk-neutral / numerically-zero lambda.
    if abs(lambda_) <= _LAMBDA_EPSILON:
        return arithmetic_mean

    # Guard 2: degenerate (flat) cluster -- no dispersion to penalize.
    spread = max(returns_decimal) - min(returns_decimal)
    if spread <= _SPREAD_EPSILON:
        return arithmetic_mean

    # General case. mean_exp is a mean of strictly-positive exp() terms, so
    # it is > 0 and math.log is always defined here.
    mean_exp = 0.0
    for r in returns_decimal:
        mean_exp += math.exp(-lambda_ * r)
    mean_exp /= len(returns_decimal)

    return -(1.0 / lambda_) * math.log(mean_exp)


def risk_penalty(returns_decimal: list[float], lambda_: float) -> float:
    """
    Convenience: arithmetic mean minus certainty equivalent.

    The amount of expected return the risk-averse trader "gives up" to the
    dispersion of the analog cluster. Always >= 0 for lambda_ > 0 (Jensen's
    inequality on a concave utility); exactly 0 on a degenerate cluster.
    Not used in the gate itself -- handy for reports and diagnostics.
    """
    mean = sum(returns_decimal) / len(returns_decimal)
    return mean - certainty_equivalent(returns_decimal, lambda_)


# ---------------------------------------------------------------------------
# SMOKE HARNESS -- run directly:  python python\domain\utility.py
# ASCII-only stdout (M-019). Deterministic; no external data.
# ---------------------------------------------------------------------------
def _approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def _smoke() -> None:
    lam = 20.0
    fails = 0

    # 1. Flat cluster: CE == common value, zero penalty.
    flat = [0.05, 0.05, 0.05, 0.05]
    ce_flat = certainty_equivalent(flat, lam)
    if not _approx(ce_flat, 0.05):
        print(f"FAIL flat: CE={ce_flat} expected 0.05")
        fails += 1
    else:
        print(f"ok   flat cluster        CE={ce_flat:.6f} penalty={risk_penalty(flat, lam):.6f}")

    # 2. Dispersed cluster: CE strictly below the mean, penalty > 0.
    spread = [-0.10, 0.02, 0.06, 0.20]
    mean_spread = sum(spread) / len(spread)
    ce_spread = certainty_equivalent(spread, lam)
    if not (ce_spread < mean_spread):
        print(f"FAIL spread: CE={ce_spread} not < mean={mean_spread}")
        fails += 1
    else:
        print(f"ok   dispersed cluster   mean={mean_spread:.6f} CE={ce_spread:.6f} penalty={mean_spread - ce_spread:.6f}")

    # 3. Risk-neutral guard: lambda ~ 0 returns the arithmetic mean.
    ce_neutral = certainty_equivalent(spread, 0.0)
    if not _approx(ce_neutral, mean_spread):
        print(f"FAIL neutral: CE={ce_neutral} expected mean={mean_spread}")
        fails += 1
    else:
        print(f"ok   lambda=0 risk-neutral CE={ce_neutral:.6f} == mean")

    # 4. Monotonic in lambda: higher risk aversion -> lower (or equal) CE.
    ce_lo = certainty_equivalent(spread, 5.0)
    ce_hi = certainty_equivalent(spread, 40.0)
    if not (ce_hi <= ce_lo <= mean_spread):
        print(f"FAIL monotonic: ce_hi={ce_hi} ce_lo={ce_lo} mean={mean_spread}")
        fails += 1
    else:
        print(f"ok   monotonic in lambda  lam5={ce_lo:.6f} >= lam40={ce_hi:.6f}")

    # 5. Single-element cluster: CE == that element (degenerate spread).
    ce_one = certainty_equivalent([0.07], lam)
    if not _approx(ce_one, 0.07):
        print(f"FAIL single: CE={ce_one} expected 0.07")
        fails += 1
    else:
        print(f"ok   single element      CE={ce_one:.6f}")

    # 6. Empty cluster raises.
    try:
        certainty_equivalent([], lam)
        print("FAIL empty: no ValueError raised")
        fails += 1
    except ValueError:
        print("ok   empty cluster raises ValueError")

    print("-" * 52)
    print("SMOKE PASS" if fails == 0 else f"SMOKE FAIL ({fails} failing checks)")


if __name__ == "__main__":
    _smoke()
